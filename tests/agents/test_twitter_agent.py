"""
Tests for TwitterAgent.
"""

import pytest

from app.agents.ingestion.twitter_agent import TwitterAgent
from app.schemas.agent import AgentResult


@pytest.mark.asyncio
async def test_twitter_agent_no_token():
    """When no bearer token is set, agent should return empty items gracefully."""
    agent = TwitterAgent()
    agent.bearer_token = ""
    result = await agent.execute()

    assert isinstance(result, AgentResult)
    assert result.success is True
    assert result.data["items"] == []


@pytest.mark.asyncio
async def test_twitter_agent_name():
    agent = TwitterAgent()
    assert agent.name == "TwitterAgent"
