"""
Feedback API routes — user feedback on picks.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store
_feedback_store: list[dict] = []


class FeedbackCreate(BaseModel):
    pick_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    action_taken: str | None = None  # "traded" | "skipped" | "watched"


@router.post("/feedback", status_code=201)
async def submit_feedback(payload: FeedbackCreate):
    """Submit user feedback on a trade pick."""
    entry = payload.model_dump()
    _feedback_store.append(entry)
    return {"message": "Feedback recorded", "id": len(_feedback_store)}


@router.get("/feedback")
async def get_feedback(pick_id: int | None = None):
    """Get feedback entries, optionally filtered by pick_id."""
    items = _feedback_store
    if pick_id is not None:
        items = [f for f in items if f.get("pick_id") == pick_id]
    return {"items": items, "total": len(items)}
