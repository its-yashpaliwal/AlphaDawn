"""
Tests for NewsScraperAgent.
"""

import pytest

from app.agents.ingestion.news_scraper_agent import NewsScraperAgent
from app.schemas.agent import AgentResult


@pytest.mark.asyncio
async def test_news_agent_returns_agent_result():
    """Agent should return a valid AgentResult."""
    agent = NewsScraperAgent()
    result = await agent.execute()

    assert isinstance(result, AgentResult)
    assert result.agent_name == "NewsScraperAgent"
    assert "items" in result.data


@pytest.mark.asyncio
async def test_news_agent_name():
    agent = NewsScraperAgent()
    assert agent.name == "NewsScraperAgent"
