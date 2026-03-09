"""
APScheduler-based scheduler for the daily pre-market pipeline run.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.config import settings


scheduler = AsyncIOScheduler()


async def _run_pre_market_pipeline():
    """Wrapper that imports and runs the orchestrator pipeline."""
    from app.agents.orchestrator import Orchestrator

    logger.info("⏰  Scheduled pre-market pipeline triggered")
    orchestrator = Orchestrator()
    result = await orchestrator.run()
    logger.info(f"✅  Pipeline finished — {len(result.data.get('picks', []))} picks generated")


def start_scheduler():
    """Parse the cron expression from settings and register the job."""
    cron_parts = settings.pre_market_run_cron.split()
    trigger = CronTrigger(
        minute=cron_parts[0],
        hour=cron_parts[1],
        day=cron_parts[2],
        month=cron_parts[3],
        day_of_week=cron_parts[4],
        timezone="Asia/Kolkata",
    )
    scheduler.add_job(_run_pre_market_pipeline, trigger, id="pre_market_run")
    scheduler.start()
    logger.info(f"🕐  Scheduler started — cron: {settings.pre_market_run_cron}")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("🛑  Scheduler stopped")
