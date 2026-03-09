"""
Exchange Agent — fetches BSE/NSE announcements and bulk/block deals.
"""

import hashlib
from typing import Any

import httpx
from loguru import logger

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.schemas.agent import AgentResult


class ExchangeAgent(BaseAgent):
    """Fetches corporate announcements and bulk/block deals from BSE & NSE."""

    name = "ExchangeAgent"

    NSE_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    async def run(self, **kwargs: Any) -> AgentResult:
        items: list[dict] = []

        async with httpx.AsyncClient(
            timeout=30, headers=self.NSE_HEADERS, follow_redirects=True
        ) as client:
            # NSE corporate announcements
            nse_ann = await self._fetch_nse_announcements(client)
            items.extend(nse_ann)

            # NSE bulk deals
            nse_bulk = await self._fetch_nse_bulk_deals(client)
            items.extend(nse_bulk)

            # BSE announcements
            bse_ann = await self._fetch_bse_announcements(client)
            items.extend(bse_ann)

        logger.info(f"  📥  Exchange data: {len(items)} items")
        return AgentResult(agent_name=self.name, data={"items": items})

    # ── NSE ──────────────────────────────────────────────────────────────
    async def _fetch_nse_announcements(self, client: httpx.AsyncClient) -> list[dict]:
        try:
            # NSE requires a session cookie — first hit the homepage
            await client.get("https://www.nseindia.com")

            resp = await client.get(
                f"{settings.nse_api_url}/corporate-announcements?index=equities"
            )
            resp.raise_for_status()
            data = resp.json()

            return [
                {
                    "source": "nse_announcement",
                    "headline": item.get("desc", "")[:256],
                    "body": item.get("desc", ""),
                    "url": item.get("attchmntFile", ""),
                    "published_at": item.get("an_dt"),
                    "content_hash": hashlib.sha256(
                        item.get("desc", "").encode()
                    ).hexdigest(),
                }
                for item in data[:20]
            ]
        except Exception as exc:
            logger.warning(f"  ⚠️  NSE announcements failed: {exc}")
            return []

    async def _fetch_nse_bulk_deals(self, client: httpx.AsyncClient) -> list[dict]:
        try:
            resp = await client.get(f"{settings.nse_api_url}/snapshot-capital-market-largedeal")
            resp.raise_for_status()
            data = resp.json().get("BLOCK_DEALS_DATA", [])

            return [
                {
                    "source": "nse_bulk_deal",
                    "headline": (
                        f"{deal.get('clientName', 'Unknown')} "
                        f"{'bought' if deal.get('buySell') == 'BUY' else 'sold'} "
                        f"{deal.get('symbol', '')} — {deal.get('qty', '')} shares"
                    ),
                    "body": str(deal),
                    "url": "",
                    "published_at": None,
                    "content_hash": hashlib.sha256(str(deal).encode()).hexdigest(),
                }
                for deal in data[:15]
            ]
        except Exception as exc:
            logger.warning(f"  ⚠️  NSE bulk deals failed: {exc}")
            return []

    # ── BSE ──────────────────────────────────────────────────────────────
    async def _fetch_bse_announcements(self, client: httpx.AsyncClient) -> list[dict]:
        try:
            # BSE API often requires a Referer or specific headers
            headers = self.NSE_HEADERS.copy()
            headers.update({
                "Referer": "https://www.bseindia.com/",
                "Origin": "https://www.bseindia.com",
            })
            resp = await client.get(
                f"{settings.bse_api_url}/BseIndiaAPI/api/AnnSubCategoryGetData/GetData",
                params={"strCat": "-1", "strPrevDate": "", "strScrip": "", "strSearch": "P", "strType": "C"},
                headers=headers
            )
            resp.raise_for_status()
            
            try:
                data = resp.json().get("Table", [])
            except Exception:
                logger.warning(f"  ⚠️  BSE response was not JSON: {resp.text[:100]}...")
                return []

            return [
                {
                    "source": "bse_announcement",
                    "headline": item.get("NEWSSUB", "")[:256],
                    "body": item.get("NEWSSUB", ""),
                    "url": item.get("NSURL", ""),
                    "published_at": item.get("NEWS_DT"),
                    "content_hash": hashlib.sha256(
                        item.get("NEWSSUB", "").encode()
                    ).hexdigest(),
                }
                for item in data[:20]
            ]
        except Exception as exc:
            logger.warning(f"  ⚠️  BSE announcements failed: {exc}")
            return []
