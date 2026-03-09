import json
import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/signals")
async def get_signals():
    """Return the latest global market signals."""
    if os.path.exists("data/latest_run.json"):
        with open("data/latest_run.json", "r") as f:
            data = json.load(f)
            return data.get("global_signals", {})
    return {}
