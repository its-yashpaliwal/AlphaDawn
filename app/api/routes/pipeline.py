import json
import logging
from fastapi import APIRouter, BackgroundTasks

from app.agents.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/run")
async def run_pipeline():
    """Trigger a manual run of the pipeline synchronously."""
    logger.info("Starting manual pipeline execution from API.")
    try:
        orchestrator = Orchestrator()
        result = await orchestrator.run()
        if result.success and result.data:
            with open("data/latest_run.json", "w") as f:
                json.dump(result.data, f, indent=4, default=str)
            logger.info("Pipeline execution completed successfully.")
            return {"status": "success", "message": "Pipeline execution finished successfully."}
        else:
            logger.error(f"Pipeline execution failed: {result.error}")
            return {"status": "error", "message": result.error}
    except Exception as e:
        logger.exception(f"Unexpected error during pipeline execution: {str(e)}")
        return {"status": "error", "message": str(e)}
