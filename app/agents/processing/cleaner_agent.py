"""
Cleaner Agent — deduplicates and normalises news items across all sources.
"""

from typing import Any

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResult


class CleanerAgent(BaseAgent):
    """Deduplicates, normalises, and cleans raw news items from all ingestion agents."""

    name = "CleanerAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        raw_items: list[dict] = kwargs.get("items", [])
        logger.info(f"  🧹  Cleaning {len(raw_items)} raw items")

        seen_hashes: set[str] = set()
        cleaned: list[dict] = []

        for item in raw_items:
            content_hash = item.get("content_hash", "")

            # ── Dedup by content hash ──
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            # ── Normalise fields ──
            item["headline"] = self._normalise_text(item.get("headline", ""))
            if item.get("body"):
                item["body"] = self._normalise_text(item["body"])

            # ── Drop empty headlines ──
            if not item["headline"]:
                continue

            cleaned.append(item)

        removed = len(raw_items) - len(cleaned)
        logger.info(f"  ✅  Cleaned: {len(cleaned)} items ({removed} duplicates/empty removed)")

        return AgentResult(agent_name=self.name, data={"items": cleaned})

    @staticmethod
    def _normalise_text(text: str) -> str:
        """Strip whitespace, collapse multiple spaces, remove control characters."""
        import re
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
        return text
