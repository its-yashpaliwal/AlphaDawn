"""
Pydantic schemas for trade picks.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PickBase(BaseModel):
    symbol: str
    exchange: str = "NSE"
    direction: str = "LONG"
    entry_price: float
    target_price: float
    stop_loss: float
    catalyst: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class PickCreate(PickBase):
    news_ids: Optional[str] = None


class PickResponse(PickBase):
    id: Optional[int] = None
    news_ids: Optional[str] = None
    outcome: Optional[str] = None
    actual_return_pct: Optional[float] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PickListResponse(BaseModel):
    """List of today's picks or historical picks."""
    picks: list[PickResponse]
    total: int
    date: str  # ISO-8601 date string
