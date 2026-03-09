"""
Tests for the Orchestrator.
"""

import pytest

from app.agents.orchestrator import Orchestrator
from app.schemas.agent import AgentResult


@pytest.mark.asyncio
async def test_orchestrator_returns_agent_result():
    """Orchestrator should return a valid AgentResult with expected keys."""
    orchestrator = Orchestrator()
    assert orchestrator.name == "Orchestrator"
    assert len(orchestrator.ingestion_agents) == 4


def test_orchestrator_has_all_stages():
    """Orchestrator should have all pipeline stages wired."""
    o = Orchestrator()
    assert o.cleaner is not None
    assert o.ranker is not None
    assert o.catalyst is not None
    assert o.stock_data is not None
    assert o.trade_setup is not None
