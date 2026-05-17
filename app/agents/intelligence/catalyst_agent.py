"""
Catalyst Agent — uses LLM to classify each news item as CATALYST or NOISE.

Uses batched LLM calls to reduce API usage: instead of 1 call per item,
sends ~10 items per call, reducing 50 calls to ~5.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.schemas.agent import AgentResult


# Single-item prompt (kept as fallback)
PROMPT_TEMPLATE = (Path(__file__).resolve().parents[2] / "prompts" / "catalyst_classifier.txt").read_text()

# Batch prompt
BATCH_PROMPT_TEMPLATE = (Path(__file__).resolve().parents[2] / "prompts" / "catalyst_classifier_batch.txt").read_text()

# Number of items per LLM batch call
BATCH_SIZE = 10

# Max retries on rate-limit errors
_MAX_RETRIES = 3


class CatalystAgent(BaseAgent):
    """LLM-powered agent that classifies news items as Catalyst or Noise."""

    name = "CatalystAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        items: list[dict] = kwargs.get("items", [])
        logger.info(f"  🔬  Classifying {len(items)} items in batches of {BATCH_SIZE}")

        catalysts: list[dict] = []
        noise_count = 0

        # Split items into batches
        batches = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
        logger.info(f"  📦  {len(batches)} batch(es) to process")

        for batch_idx, batch in enumerate(batches):
            try:
                classifications = await self._classify_batch_with_retry(batch)

                for i, classification in enumerate(classifications):
                    if i >= len(batch):
                        break
                    item = batch[i]
                    item["is_catalyst"] = classification.get("classification", "NOISE")
                    item["catalyst_confidence"] = classification.get("confidence", 0.0)
                    item["catalyst_reasoning"] = classification.get("reasoning", "")
                    item["related_symbols"] = ",".join(
                        classification.get("related_symbols", [])
                    )

                    if item["is_catalyst"] == "CATALYST":
                        catalysts.append(item)
                    else:
                        noise_count += 1

                logger.info(f"  ✅  Batch {batch_idx + 1}/{len(batches)} classified")

            except Exception as exc:
                logger.warning(f"  ⚠️  Batch {batch_idx + 1} failed: {exc} — falling back to heuristic")
                # Fallback: classify the entire failed batch with heuristics
                for item in batch:
                    classification = self._heuristic_classify(item)
                    item["is_catalyst"] = classification.get("classification", "NOISE")
                    item["catalyst_confidence"] = classification.get("confidence", 0.0)
                    item["catalyst_reasoning"] = classification.get("reasoning", "")
                    item["related_symbols"] = ",".join(
                        classification.get("related_symbols", [])
                    )
                    if item["is_catalyst"] == "CATALYST":
                        catalysts.append(item)
                    else:
                        noise_count += 1

        logger.info(f"  ✅  {len(catalysts)} catalysts, {noise_count} noise")
        return AgentResult(
            agent_name=self.name,
            data={"catalysts": catalysts, "all_items": items},
        )

    # ── Batch classification ────────────────────────────────────────────

    async def _classify_batch_with_retry(self, batch: list[dict], retries: int = _MAX_RETRIES) -> list[dict]:
        """Classify a batch of items with retry logic."""
        for attempt in range(retries):
            try:
                return await self._classify_batch(batch)
            except Exception as exc:
                error_str = str(exc).lower()
                is_retryable = any(kw in error_str for kw in ["rate_limit", "429", "too many", "overloaded"])
                if is_retryable and attempt < retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"  ⏳  Rate limited on batch, retrying in {wait}s…")
                    await asyncio.sleep(wait)
                else:
                    raise
        # Should not reach here, but fallback
        return [self._heuristic_classify(item) for item in batch]

    async def _classify_batch(self, batch: list[dict]) -> list[dict]:
        """Send a batch of items to the LLM in a single call."""
        # Build the items block for the prompt
        items_lines = []
        for idx, item in enumerate(batch):
            items_lines.append(f"### Item {idx}")
            items_lines.append(f"Source: {item.get('source', 'unknown')}")
            items_lines.append(f"Headline: {item.get('headline', '')}")
            items_lines.append(f"Body: {item.get('body', '') or ''}")
            items_lines.append("")

        items_block = "\n".join(items_lines)
        prompt = BATCH_PROMPT_TEMPLATE.format(items_block=items_block)

        # Call the LLM
        raw_response = await self._call_llm(prompt)

        # Parse the JSON array response
        classifications = self._parse_batch_response(raw_response, len(batch))
        return classifications

    def _parse_batch_response(self, raw: str, expected_count: int) -> list[dict]:
        """Parse the LLM's JSON array response, handling edge cases."""
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON array from the response
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
            else:
                logger.warning("  ⚠️  Could not parse batch response as JSON array")
                raise ValueError(f"Invalid JSON response: {raw[:200]}")

        if isinstance(parsed, list):
            # Pad with NOISE if LLM returned fewer items than expected
            while len(parsed) < expected_count:
                parsed.append({
                    "classification": "NOISE",
                    "confidence": 0.5,
                    "related_symbols": [],
                    "reasoning": "Missing from LLM batch response",
                })
            return parsed
        elif isinstance(parsed, dict):
            # LLM returned a single object instead of an array
            return [parsed]
        else:
            raise ValueError(f"Unexpected response type: {type(parsed)}")

    # ── LLM provider dispatch ───────────────────────────────────────────

    async def _call_llm(self, prompt: str) -> str:
        """Route to the configured LLM provider and return raw text."""
        if settings.openai_api_key and settings.openai_api_key != "sk-...":
            return await self._call_openai(prompt)
        elif settings.gemini_api_key and not settings.gemini_api_key.startswith("AI..."):
            return await self._call_gemini(prompt)
        elif settings.groq_api_key and not settings.groq_api_key.startswith("gsk_..."):
            return await self._call_groq(prompt)
        else:
            raise RuntimeError("No LLM API key configured")

    async def _call_openai(self, prompt: str) -> str:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    async def _call_gemini(self, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        # Run sync Gemini call in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            ),
        )
        return resp.text

    async def _call_groq(self, prompt: str) -> str:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.groq_api_key)
        resp = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    # ── Heuristic fallback ──────────────────────────────────────────────

    @staticmethod
    def _heuristic_classify(item: dict) -> dict:
        """Simple keyword-based fallback when no LLM key is configured or batch fails."""
        text = (item.get("headline", "") + " " + (item.get("body", "") or "")).lower()
        catalyst_keywords = [
            "bonus", "split", "buyback", "acquisition", "merger",
            "result", "earnings", "beat", "miss", "block deal", "bulk deal",
            "order win", "sebi", "rbi", "upgrade", "downgrade",
            "board meeting", "outcome", "dividend", "bought", "sold",
        ]
        hits = sum(1 for kw in catalyst_keywords if kw in text)

        # Try to extract stock symbols from enriched body
        symbols = []
        symbol_match = re.findall(r"Symbol:\s*([A-Z][A-Z0-9]+)", item.get("body", "") or "")
        if symbol_match:
            symbols = symbol_match

        if hits >= 2:
            return {"classification": "CATALYST", "confidence": 0.6, "related_symbols": symbols, "reasoning": "Multiple catalyst keywords detected (heuristic)"}
        elif hits == 1:
            return {"classification": "CATALYST", "confidence": 0.4, "related_symbols": symbols, "reasoning": "Single catalyst keyword detected (heuristic)"}
        return {"classification": "NOISE", "confidence": 0.7, "related_symbols": symbols, "reasoning": "No catalyst keywords found (heuristic)"}
