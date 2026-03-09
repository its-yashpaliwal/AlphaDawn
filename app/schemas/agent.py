"""
AgentResult — the standard payload every agent returns.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Uniform result envelope returned by every agent."""

    agent_name: str
    success: bool = True
    data: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"<AgentResult {status} {self.agent_name} ({self.duration_ms:.0f}ms)>"
