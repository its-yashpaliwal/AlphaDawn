"""
Trade Setup Agent — generates entry, target, and stop-loss via LLM.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.schemas.agent import AgentResult


PROMPT_TEMPLATE = (Path(__file__).resolve().parents[2] / "prompts" / "trade_setup.txt").read_text()


class TradeSetupAgent(BaseAgent):
    """Generates trade setups (entry, target, SL) by combining catalysts with technicals."""

    name = "TradeSetupAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        catalysts: list[dict] = kwargs.get("catalysts", [])
        technicals: dict[str, dict] = kwargs.get("technicals", {})

        if not catalysts:
            logger.info("  ⚠️  No catalysts — skipping trade setup generation")
            return AgentResult(agent_name=self.name, data={"picks": []})

        picks: list[dict] = []

        tasks = []
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
                tasks.append(self._generate_setup(item, tech))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, Exception):
                logger.warning(f"  ⚠️  Trade setup failed: {res}")
            elif isinstance(res, dict):
                picks.append(res)

        logger.info(f"  ✅  Generated {len(picks)} trade setups")
        return AgentResult(agent_name=self.name, data={"picks": picks})

    async def _generate_setup(self, catalyst: dict, technicals: dict) -> dict | None:
        prompt = PROMPT_TEMPLATE.format(
            symbol=technicals["symbol"],
            headline=catalyst.get("headline", ""),
            catalyst_confidence=catalyst.get("catalyst_confidence", 0.5),
            current_price=technicals.get("current_price", 0),
            high_52w=technicals.get("high_52w", 0),
            low_52w=technicals.get("low_52w", 0),
            dma_50=technicals.get("dma_50", 0),
            dma_200=technicals.get("dma_200", 0),
            rsi=technicals.get("rsi", 50),
            avg_volume=technicals.get("avg_volume", 0),
            prev_close=technicals.get("prev_close", 0),
            supports=technicals.get("supports", []),
            resistances=technicals.get("resistances", []),
        )

        if settings.openai_api_key and settings.openai_api_key != "sk-...":
            return await self._call_openai(prompt)
        elif settings.gemini_api_key and not settings.gemini_api_key.startswith("AI..."):
            return await self._call_gemini(prompt)
        elif settings.groq_api_key and not settings.groq_api_key.startswith("gsk_..."):
            return await self._call_groq(prompt)
        else:
            return self._heuristic_setup(catalyst, technicals)

    async def _call_openai(self, prompt: str) -> dict:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        resp = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
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
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)

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
            "reasoning": "Heuristic setup — no LLM configured.",
        }
