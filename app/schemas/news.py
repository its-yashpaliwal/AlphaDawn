"""
Pydantic schemas for news items.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NewsBase(BaseModel):
    source: str
    headline: str
    body: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None


class NewsCreate(NewsBase):
    content_hash: str


class NewsResponse(NewsBase):
    id: Optional[int] = None
    scraped_at: Optional[str] = None
    sentiment_score: Optional[float] = None
    relevance_score: Optional[float] = None
    is_catalyst: Optional[str] = None
    related_symbols: Optional[str] = None

    model_config = {"from_attributes": True}


class NewsFeedResponse(BaseModel):
    """Paginated news feed response."""
    items: list[NewsResponse]
    total: int
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
