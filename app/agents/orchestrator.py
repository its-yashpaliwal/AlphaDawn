"""
Orchestrator — the master agent that coordinates the full pipeline.

Flow:  Ingestion (concurrent) → Cleaning → Ranking → Catalyst → Stock Data → Trade Setup
"""

import asyncio
from typing import Any

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResult

# Ingestion
from app.agents.ingestion.twitter_agent import TwitterAgent
from app.agents.ingestion.news_scraper_agent import NewsScraperAgent
from app.agents.ingestion.exchange_agent import ExchangeAgent
from app.agents.ingestion.global_signals_agent import GlobalSignalsAgent

# Processing
from app.agents.processing.cleaner_agent import CleanerAgent
from app.agents.processing.ranker_agent import RankerAgent

# Intelligence
from app.agents.intelligence.catalyst_agent import CatalystAgent
from app.agents.intelligence.stock_data_agent import StockDataAgent
from app.agents.intelligence.trade_setup_agent import TradeSetupAgent


class Orchestrator(BaseAgent):
    """Master agent — runs the entire pre-market pipeline end-to-end."""

    name = "Orchestrator"

    def __init__(self):
        # Ingestion agents run concurrently
        self.ingestion_agents = [
            TwitterAgent(),
            NewsScraperAgent(),
            ExchangeAgent(),
            GlobalSignalsAgent(),
        ]
        # Sequential pipeline stages
        self.cleaner = CleanerAgent()
        self.ranker = RankerAgent()
        self.catalyst = CatalystAgent()
        self.stock_data = StockDataAgent()
        self.trade_setup = TradeSetupAgent()

    async def run(self, **kwargs: Any) -> AgentResult:
        # ── Stage 1: Ingestion (concurrent) ─────────────────────────────
        logger.info("─── Stage 1: Ingestion ───")
        ingestion_tasks = [agent.execute() for agent in self.ingestion_agents]
        ingestion_results: list[AgentResult] = await asyncio.gather(*ingestion_tasks)

        # Merge all items
        all_items: list[dict] = []
        for result in ingestion_results:
            all_items.extend(result.data.get("items", []))

        logger.info(f"   Total raw items: {len(all_items)}")

        # ── Stage 2: Cleaning ───────────────────────────────────────────
        logger.info("─── Stage 2: Cleaning ───")
        clean_result = await self.cleaner.execute(items=all_items)
        cleaned_items = clean_result.data.get("items", [])

        # ── Stage 3: Ranking ────────────────────────────────────────────
        logger.info("─── Stage 3: Ranking ───")
        rank_result = await self.ranker.execute(items=cleaned_items)
        ranked_items = rank_result.data.get("items", [])

        # ── Stage 4: Catalyst classification ────────────────────────────
        logger.info("─── Stage 4: Catalyst Classification ───")
        catalyst_result = await self.catalyst.execute(items=ranked_items)
        catalysts = catalyst_result.data.get("catalysts", [])

        # ── Stage 5: Fetch technicals ───────────────────────────────────
        logger.info("─── Stage 5: Stock Data ───")
        stock_result = await self.stock_data.execute(catalysts=catalysts)
        technicals = stock_result.data.get("technicals", {})

        # ── Stage 6: Generate trade setups ──────────────────────────────
        logger.info("─── Stage 6: Trade Setup ───")
        setup_result = await self.trade_setup.execute(
            catalysts=catalysts, technicals=technicals
        )
        picks = setup_result.data.get("picks", [])

        # ── Collect global signals for the dashboard ────────────────────
        global_signals = {}
        for result in ingestion_results:
            if result.agent_name == "GlobalSignalsAgent":
                global_signals = result.data.get("signals", {})

        return AgentResult(
            agent_name=self.name,
            data={
                "picks": picks,
                "news": ranked_items,
                "catalysts": catalysts,
                "global_signals": global_signals,
                "stats": {
                    "total_raw": len(all_items),
                    "after_cleaning": len(cleaned_items),
                    "after_ranking": len(ranked_items),
                    "catalysts_found": len(catalysts),
                    "picks_generated": len(picks),
                },
            },
        )
