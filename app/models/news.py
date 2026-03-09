"""
NewsItem ORM model.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False, index=True)          # e.g. "moneycontrol", "twitter", "bse"
    headline = Column(String(512), nullable=False)
    body = Column(Text, nullable=True)
    url = Column(String(1024), nullable=True)
    published_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    # Processing fields
    sentiment_score = Column(Float, nullable=True)                   # -1.0 … +1.0
    relevance_score = Column(Float, nullable=True)                   # 0.0 … 1.0
    is_catalyst = Column(String(16), nullable=True)                  # "catalyst" | "noise" | None
    related_symbols = Column(String(512), nullable=True)             # comma-separated tickers

    # Dedup
    content_hash = Column(String(64), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<NewsItem id={self.id} source={self.source!r} headline={self.headline[:40]!r}>"
