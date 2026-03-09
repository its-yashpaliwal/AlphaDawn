"""
Pick ORM model — a generated trade setup.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.models.news import Base


class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), nullable=False, index=True)          # e.g. "RELIANCE"
    exchange = Column(String(8), nullable=False, default="NSE")      # NSE | BSE
    direction = Column(String(8), nullable=False, default="LONG")    # LONG | SHORT

    # Trade levels
    entry_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)

    # Context
    catalyst = Column(Text, nullable=True)                           # Why this pick?
    confidence = Column(Float, nullable=True)                        # 0.0 … 1.0
    news_ids = Column(String(256), nullable=True)                    # comma-separated NewsItem ids

    # Outcome tracking
    outcome = Column(String(16), nullable=True)                      # "hit_target" | "hit_sl" | "open"
    actual_return_pct = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return (
            f"<Pick id={self.id} {self.direction} {self.symbol} "
            f"entry={self.entry_price} target={self.target_price} sl={self.stop_loss}>"
        )
