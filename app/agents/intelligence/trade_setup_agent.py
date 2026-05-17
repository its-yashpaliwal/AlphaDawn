"""
Trade Setup Agent — generates entry, target, and stop-loss via LLM.

Uses batched LLM calls to reduce API usage: instead of 1 call per setup,
sends ~10 setups per call.
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
PROMPT_TEMPLATE = (Path(__file__).resolve().parents[2] / "prompts" / "trade_setup.txt").read_text()

# Batch prompt
BATCH_PROMPT_TEMPLATE = (Path(__file__).resolve().parents[2] / "prompts" / "trade_setup_batch.txt").read_text()

# Number of items per LLM batch call
BATCH_SIZE = 10

# Max retries on rate-limit errors
_MAX_RETRIES = 3


class TradeSetupAgent(BaseAgent):
    """Generates trade setups (entry, target, SL) by combining catalysts with technicals."""

    name = "TradeSetupAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        catalysts: list[dict] = kwargs.get("catalysts", [])
        technicals: dict[str, dict] = kwargs.get("technicals", {})

        if not catalysts:
            logger.info("  ⚠️  No catalysts — skipping trade setup generation")
            return AgentResult(agent_name=self.name, data={"picks": []})

        # Prepare items for processing
        setup_requests = []
        for item in catalysts:
            symbols = [
                s.strip().upper()
                for s in (item.get("related_symbols", "") or "").split(",")
                if s.strip()
            ]
            for symbol in symbols:
                tech = technicals.get(symbol)
                if not tech or "error" in tech:
                    # Fallback so we can still generate a setup based purely on the catalyst
                    tech = {
                        "symbol": symbol,
                        "current_price": 0,
                        "rsi": 50,
                        "dma_50": 0,
                        "dma_200": 0,
                        "avg_volume": 0,
                        "supports": [],
                        "resistances": []
                    }
                setup_requests.append({"catalyst": item, "tech": tech})

        logger.info(f"  📈  Generating {len(setup_requests)} trade setups in batches of {BATCH_SIZE}")

        picks: list[dict] = []
        batches = [setup_requests[i:i + BATCH_SIZE] for i in range(0, len(setup_requests), BATCH_SIZE)]
        
        for batch_idx, batch in enumerate(batches):
            try:
                setups = await self._generate_setup_batch_with_retry(batch)
                for setup in setups:
                    if setup and "error" not in setup:
                        picks.append(setup)
                logger.info(f"  ✅  Batch {batch_idx + 1}/{len(batches)} generated")
            except Exception as exc:
                logger.warning(f"  ⚠️  Batch {batch_idx + 1} failed: {exc} — falling back to heuristic")
                for req in batch:
                    picks.append(self._heuristic_setup(req["catalyst"], req["tech"]))

        logger.info(f"  ✅  Generated {len(picks)} trade setups")
        return AgentResult(agent_name=self.name, data={"picks": picks})

    # ── Batch setup generation ──────────────────────────────────────────

    async def _generate_setup_batch_with_retry(self, batch: list[dict], retries: int = _MAX_RETRIES) -> list[dict]:
        """Generate setups for a batch with retry logic."""
        for attempt in range(retries):
            try:
                return await self._generate_setup_batch(batch)
            except Exception as exc:
                error_str = str(exc).lower()
                is_retryable = any(kw in error_str for kw in ["rate_limit", "429", "too many", "overloaded"])
                if is_retryable and attempt < retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"  ⏳  Rate limited on setup batch, retrying in {wait}s…")
                    await asyncio.sleep(wait)
                else:
                    raise
        # Should not reach here, but fallback
        return [self._heuristic_setup(req["catalyst"], req["tech"]) for req in batch]

    async def _generate_setup_batch(self, batch: list[dict]) -> list[dict]:
        """Send a batch of catalyst-technical pairs to the LLM."""
        setups_lines = []
        for idx, req in enumerate(batch):
            cat = req["catalyst"]
            tech = req["tech"]
            
            setups_lines.append(f"### Item {idx}")
            setups_lines.append(f"Symbol: {tech['symbol']}")
            setups_lines.append(f"Headline: {cat.get('headline', '')}")
            setups_lines.append(f"Catalyst Confidence: {cat.get('catalyst_confidence', 0.5)}")
            setups_lines.append(f"Catalyst Reasoning: {cat.get('catalyst_reasoning', '')}")
            setups_lines.append(f"Current Price: {tech.get('current_price', 0)}")
            setups_lines.append(f"52w High: {tech.get('high_52w', 0)} | 52w Low: {tech.get('low_52w', 0)}")
            setups_lines.append(f"50-DMA: {tech.get('dma_50', 0)} | 200-DMA: {tech.get('dma_200', 0)}")
            setups_lines.append(f"RSI: {tech.get('rsi', 50)} | Avg Vol: {tech.get('avg_volume', 0)}")
            setups_lines.append(f"Supports: {tech.get('supports', [])}")
            setups_lines.append(f"Resistances: {tech.get('resistances', [])}")
            setups_lines.append("")

        setups_block = "\n".join(setups_lines)
        prompt = BATCH_PROMPT_TEMPLATE.format(setups_block=setups_block)

        raw_response = await self._call_llm(prompt)
        setups = self._parse_batch_response(raw_response, len(batch))
        return setups

    def _parse_batch_response(self, raw: str, expected_count: int) -> list[dict]:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
            else:
                logger.warning("  ⚠️  Could not parse setup batch response as JSON array")
                raise ValueError(f"Invalid JSON response: {raw[:200]}")

        if isinstance(parsed, list):
            # Pad if missing
            while len(parsed) < expected_count:
                parsed.append({"error": "Missing from LLM batch response"})
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        else:
            raise ValueError(f"Unexpected response type: {type(parsed)}")

    # ── LLM provider dispatch ───────────────────────────────────────────

    async def _call_llm(self, prompt: str) -> str:
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
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    async def _call_gemini(self, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
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
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    # ── Heuristic fallback ──────────────────────────────────────────────

    @staticmethod
    def _heuristic_setup(catalyst: dict, tech: dict) -> dict:
        """Fallback trade setup when no LLM key is configured."""
        price = tech.get("current_price", 0)
        if not price:
            return {}

        # Simple 2:1 RR setup
        sl_pct = 0.03  # 3% SL
        target_pct = 0.06  # 6% target
        direction = "LONG" if price > tech.get("dma_50", price) else "SHORT"

        if direction == "LONG":
            entry = round(price, 2)
            sl = round(price * (1 - sl_pct), 2)
            target = round(price * (1 + target_pct), 2)
        else:
            entry = round(price, 2)
            sl = round(price * (1 + sl_pct), 2)
            target = round(price * (1 - target_pct), 2)

        return {
            "symbol": tech["symbol"],
            "exchange": "NSE",
            "direction": direction,
            "entry_price": entry,
            "target_price": target,
            "stop_loss": sl,
            "confidence": 0.5,
            "catalyst_summary": catalyst.get("headline", "")[:120],
            "reasoning": "Heuristic setup — batch LLM call failed or no API key.",
        }
