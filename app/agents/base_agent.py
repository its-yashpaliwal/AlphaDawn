"""
Abstract base class that all agents inherit.
"""

import time
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from app.schemas.agent import AgentResult


class BaseAgent(ABC):
    """
    Every agent must implement `run()`.
    The base class provides timing, logging, and error handling.
    """

    name: str = "BaseAgent"

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Public entry-point — wraps `run()` with timing & error handling."""
        logger.info(f"🤖  [{self.name}] Starting …")
        start = time.perf_counter()

        try:
            result = await self.run(**kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            result.duration_ms = elapsed
            logger.info(f"✅  [{self.name}] Done in {elapsed:.0f} ms")
            return result

        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(f"❌  [{self.name}] Failed after {elapsed:.0f} ms — {exc}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(exc),
                duration_ms=elapsed,
            )

    @abstractmethod
    async def run(self, **kwargs: Any) -> AgentResult:
        """Override in each concrete agent."""
        ...
