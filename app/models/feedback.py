"""
Feedback ORM model — user feedback on generated picks.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.models.news import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pick_id = Column(Integer, ForeignKey("picks.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)                         # 1-5 stars
    comment = Column(Text, nullable=True)
    action_taken = Column(String(32), nullable=True)                 # "traded" | "skipped" | "watched"
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback id={self.id} pick_id={self.pick_id} rating={self.rating}>"
