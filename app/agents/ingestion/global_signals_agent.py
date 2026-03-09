"""
Global Signals Agent — fetches SGX Nifty, Crude, Gold, Dow Futures.
"""

import hashlib
from typing import Any

import httpx
from loguru import logger

from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResult


# Ticker symbols (Yahoo Finance compatible)
GLOBAL_TICKERS = {
    "sgx_nifty": "^NSEI",       # Proxy — real SGX Nifty needs a paid feed
    "dow_futures": "YM=F",
    "sp500_futures": "ES=F",
    "crude_oil": "CL=F",
    "gold": "GC=F",
    "usd_inr": "INR=X",
    "us_10y": "^TNX",
}


class GlobalSignalsAgent(BaseAgent):
    """Fetches global market signals — SGX Nifty, Crude, Gold, Dow Futures, USD/INR."""

    name = "GlobalSignalsAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        signals: dict[str, dict] = {}

        try:
            # yfinance is sync — run in a thread pool in production.
            # For now, use the Yahoo finance v8 JSON endpoint directly.
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            async with httpx.AsyncClient(timeout=20, headers=headers) as client:
                for label, ticker in GLOBAL_TICKERS.items():
                    try:
                        data = await self._fetch_quote(client, ticker)
                        signals[label] = data
                    except Exception as exc:
                        logger.warning(f"  ⚠️  {label} ({ticker}) failed: {exc}")
                        signals[label] = {"error": str(exc)}

        except Exception as exc:
            logger.error(f"Global signals fetch failed: {exc}")
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

        # Also produce a summary headline for the news feed
        headline = self._build_summary(signals)
        items = [
            {
                "source": "global_signals",
                "headline": headline,
                "body": str(signals),
                "url": "",
                "published_at": None,
                "content_hash": hashlib.sha256(headline.encode()).hexdigest(),
            }
        ]

        logger.info(f"  🌍  Global signals fetched for {len(signals)} tickers")
        return AgentResult(
            agent_name=self.name,
            data={"signals": signals, "items": items},
        )

    async def _fetch_quote(self, client: httpx.AsyncClient, ticker: str) -> dict:
        """Quick-and-dirty quote from Yahoo Finance v8 API."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        resp = await client.get(url, params={"interval": "1d", "range": "1d"})
        resp.raise_for_status()
        result = resp.json()["chart"]["result"][0]
        meta = result["meta"]

        return {
            "symbol": ticker,
            "price": meta.get("regularMarketPrice"),
            "previous_close": meta.get("chartPreviousClose"),
            "change_pct": round(
                ((meta.get("regularMarketPrice", 0) - meta.get("chartPreviousClose", 1))
                 / meta.get("chartPreviousClose", 1))
                * 100,
                2,
            ),
            "currency": meta.get("currency"),
        }

    @staticmethod
    def _build_summary(signals: dict) -> str:
        parts = []
        for label, data in signals.items():
            if "error" not in data:
                direction = "🟢" if data.get("change_pct", 0) >= 0 else "🔴"
                parts.append(
                    f"{direction} {label.replace('_', ' ').title()}: "
                    f"{data.get('price')} ({data.get('change_pct'):+.2f}%)"
                )
        return " | ".join(parts) if parts else "Global signals unavailable"
