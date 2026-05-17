"""
Ranker Agent — ranks news by relevance and recency.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResult


# Keywords that boost relevance score (matched with word boundaries)
HIGH_RELEVANCE_KEYWORDS = [
    "bonus", "split", "buyback", "acquisition", "merger",
    "results", "earnings", "profit", "revenue", "guidance",
    "fii", "dii", "block deal", "bulk deal",
    "sebi", "rbi", "policy", "rate cut", "rate hike",
    "order win", "contract", "expansion", "capex",
    "upgrade", "downgrade", "target price",
    "dividend", "rights issue", "ipo", "ofs",
    "board meeting", "outcome", "bought", "sold",
]

# Pre-compile keyword patterns for word-boundary matching
_KEYWORD_PATTERNS = [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in HIGH_RELEVANCE_KEYWORDS]

# Date formats that our ingestion agents produce
_DATE_FORMATS = [
    "%d-%b-%Y %H:%M:%S",   # NSE: "17-May-2026 22:34:46"
    "%d-%b-%Y",             # NSE short: "17-May-2026"
    "%Y-%m-%dT%H:%M:%S",   # ISO without tz
    "%Y-%m-%d %H:%M:%S",   # Standard datetime
]


class RankerAgent(BaseAgent):
    """Ranks cleaned news items by a composite score of relevance + recency."""

    name = "RankerAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        items: list[dict] = kwargs.get("items", [])
        logger.info(f"  📊  Ranking {len(items)} items")

        scored_items = [self._score_item(item) for item in items]
        scored_items.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        # Keep top 50 most relevant
        top_items = scored_items[:50]
        if top_items:
            logger.info(
                f"  ✅  Top {len(top_items)} items ranked "
                f"(best score: {top_items[0].get('relevance_score', 0):.2f})"
            )
        else:
            logger.warning("  ⚠️  No items to rank")

        return AgentResult(agent_name=self.name, data={"items": top_items})

    def _score_item(self, item: dict) -> dict:
        """Compute composite relevance score (0.0 – 1.0)."""
        text = (item.get("headline", "") + " " + (item.get("body", "") or "")).lower()

        # ── Keyword relevance (0 – 0.6) ──
        keyword_hits = sum(1 for pat in _KEYWORD_PATTERNS if pat.search(text))
        keyword_score = min(keyword_hits * 0.15, 0.6)

        # ── Recency boost (0 – 0.3) ──
        recency_score = 0.15  # default for items without timestamp
        pub = item.get("published_at")
        if pub:
            parsed = self._parse_date(pub)
            if parsed:
                age = datetime.now(timezone.utc) - parsed
                if age < timedelta(hours=2):
                    recency_score = 0.3
                elif age < timedelta(hours=6):
                    recency_score = 0.2
                elif age < timedelta(hours=12):
                    recency_score = 0.1
                else:
                    recency_score = 0.05

        # ── Source quality (0 – 0.1) ──
        source = item.get("source", "")
        source_score = {
            "nse_announcement": 0.10,
            "bse_announcement": 0.10,
            "nse_bulk_deal": 0.08,
            "moneycontrol": 0.07,
            "economictimes": 0.07,
            "business_standard": 0.06,
            "twitter": 0.04,
            "global_signals": 0.05,
        }.get(source, 0.03)

        total = round(keyword_score + recency_score + source_score, 3)
        item["relevance_score"] = total
        return item

    @staticmethod
    def _parse_date(pub) -> datetime | None:
        """Try multiple date formats to parse a date string."""
        if isinstance(pub, datetime):
            if pub.tzinfo is None:
                return pub.replace(tzinfo=timezone.utc)
            return pub

        if not isinstance(pub, str):
            return None

        # Try ISO format first (handles "2026-05-17T22:34:46+00:00")
        try:
            return datetime.fromisoformat(pub.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

        # Try known date formats from our ingestion agents
        for fmt in _DATE_FORMATS:
            try:
                dt = datetime.strptime(pub, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue

        return None
