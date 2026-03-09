"""
News API routes — latest curated news feed.
"""

from fastapi import APIRouter, Query

from app.schemas.news import NewsResponse, NewsFeedResponse

router = APIRouter()

# In-memory store — replace with DB queries in production
_news_store: list[dict] = []


import json
import os

@router.get("/news", response_model=NewsFeedResponse)
async def get_news_feed(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: str | None = None,
):
    """Return the latest curated news feed, optionally filtered by source."""
    news_data = []
    if os.path.exists("data/latest_run.json"):
        with open("data/latest_run.json", "r") as f:
            data = json.load(f)
            news_data = data.get("news", [])
            
    filtered = news_data
    if source:
        filtered = [n for n in filtered if n.get("source") == source]

    start = (page - 1) * per_page
    end = start + per_page
    page_items = filtered[start:end]

    return NewsFeedResponse(
        items=[NewsResponse(**n) for n in page_items],
        total=len(filtered),
        page=page,
        per_page=per_page,
    )


def store_news(news_items: list[dict]):
    """Called by the orchestrator to persist news items (in-memory for now)."""
    _news_store.extend(news_items)
