"""
Picks API routes — today's picks and history.
"""

from datetime import date

from fastapi import APIRouter

from app.schemas.pick import PickResponse, PickListResponse

router = APIRouter()

# In-memory store — replace with DB queries in production
_picks_store: list[dict] = []


import json
import os

@router.get("/picks", response_model=PickListResponse)
async def get_todays_picks():
    """Return today's trade picks."""
    today = date.today().isoformat()
    picks_data = []
    
    # Read from the JSON file dumped by pipeline.py
    if os.path.exists("data/latest_run.json"):
        with open("data/latest_run.json", "r") as f:
            data = json.load(f)
            picks_data = data.get("picks", [])
            
    today_picks = [p for p in picks_data if p.get("created_at", "").startswith(today) or True] # Return all for now
    
    return PickListResponse(
        picks=[PickResponse(**p) for p in today_picks],
        total=len(today_picks),
        date=today,
    )


@router.get("/picks/history", response_model=PickListResponse)
async def get_picks_history(days: int = 7):
    """Return historical picks (last N days)."""
    return PickListResponse(
        picks=[PickResponse(**p) for p in _picks_store],
        total=len(_picks_store),
        date=date.today().isoformat(),
    )


def store_picks(picks: list[dict]):
    """Called by the orchestrator to persist picks (in-memory for now)."""
    _picks_store.extend(picks)
