"""
Master pipeline entry-point — can be run from CLI or cron.

Usage:
    python pipeline.py
"""

import asyncio
import sys

from loguru import logger


async def main():
    from app.agents.orchestrator import Orchestrator

    logger.info("═══════════════════════════════════════")
    logger.info("  📈  AlphaDawn Pipeline")
    logger.info("═══════════════════════════════════════")

    orchestrator = Orchestrator()
    result = await orchestrator.run()

    if result.success:
        import json
        import os

        # Save to disk so the dashboard can read it
        os.makedirs("data", exist_ok=True)
        with open("data/latest_run.json", "w") as f:
            json.dump(result.data, f, default=str)

        picks = result.data.get("picks", [])
        logger.info(f"✅  Pipeline complete — {len(picks)} trade setups generated")
        for pick in picks:
            logger.info(f"   • {pick}")
    else:
        logger.error(f"❌  Pipeline failed — {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
