"""
Catalyst Agent — uses LLM to classify each news item as CATALYST or NOISE.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.schemas.agent import AgentResult


PROMPT_TEMPLATE = (Path(__file__).resolve().parents[2] / "prompts" / "catalyst_classifier.txt").read_text()


class CatalystAgent(BaseAgent):
    """LLM-powered agent that classifies news items as Catalyst or Noise."""

    name = "CatalystAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        items: list[dict] = kwargs.get("items", [])
        logger.info(f"  🔬  Classifying {len(items)} items")

        catalysts: list[dict] = []
        noise_count = 0

        # Process all items in parallel
        tasks = [self._classify_and_update(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"  ⚠️  Classification failed for: {items[i].get('headline', '')[:60]} — {result}")
                noise_count += 1
            elif result:
                catalysts.append(items[i])
            else:
                noise_count += 1

        logger.info(f"  ✅  {len(catalysts)} catalysts, {noise_count} noise")
        return AgentResult(
            agent_name=self.name,
            data={"catalysts": catalysts, "all_items": items},
        )

    async def _classify_and_update(self, item: dict) -> bool:
        """Helper to classify a single item and update it. Returns True if catalyst."""
        try:
            classification = await self._classify(item)
            item["is_catalyst"] = classification.get("classification", "NOISE")
            item["catalyst_confidence"] = classification.get("confidence", 0.0)
            item["related_symbols"] = ",".join(
                classification.get("related_symbols", [])
            )
            return item["is_catalyst"] == "CATALYST"
        except Exception:
            raise

    async def _classify(self, item: dict) -> dict:
        """Call the LLM with the catalyst classifier prompt."""
        prompt = PROMPT_TEMPLATE.format(
            source=item.get("source", "unknown"),
            headline=item.get("headline", ""),
            body=item.get("body", "") or "",
        )

        if settings.openai_api_key and settings.openai_api_key != "sk-...":
            return await self._call_openai(prompt)
        elif settings.gemini_api_key and not settings.gemini_api_key.startswith("AI..."):
            return await self._call_gemini(prompt)
        elif settings.groq_api_key and not settings.groq_api_key.startswith("gsk_..."):
            return await self._call_groq(prompt)
        else:
            # Fallback heuristic when no LLM key is set
            return self._heuristic_classify(item)

    async def _call_openai(self, prompt: str) -> dict:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)

    async def _call_gemini(self, prompt: str) -> dict:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        resp = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(resp.text)

    async def _call_groq(self, prompt: str) -> dict:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.groq_api_key)
        resp = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)

    @staticmethod
    def _heuristic_classify(item: dict) -> dict:
        """Simple keyword-based fallback when no LLM key is configured."""
        text = (item.get("headline", "") + " " + (item.get("body", "") or "")).lower()
        catalyst_keywords = [
            "bonus", "split", "buyback", "acquisition", "merger",
            "result", "earnings", "beat", "miss", "block deal", "bulk deal",
            "order win", "sebi", "rbi", "upgrade", "downgrade",
        ]
        hits = sum(1 for kw in catalyst_keywords if kw in text)
        if hits >= 2:
            return {"classification": "CATALYST", "confidence": 0.6, "related_symbols": []}
        elif hits == 1:
            return {"classification": "CATALYST", "confidence": 0.4, "related_symbols": []}
        return {"classification": "NOISE", "confidence": 0.7, "related_symbols": []}
