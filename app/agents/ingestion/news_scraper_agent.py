"""
News Scraper Agent — scrapes ET, MoneyControl, Business Standard.
"""

import hashlib
from typing import Any

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.schemas.agent import AgentResult


# Source configurations
NEWS_SOURCES = [
    {
        "name": "moneycontrol",
        "url": f"{settings.moneycontrol_base_url}/news/business/markets/",
        "headline_selector": "li h2 a",
    },
    {
        "name": "economictimes",
        "url": f"{settings.et_base_url}/markets/stocks/news",
        "headline_selector": ".eachStory h3 a",
    },
    {
        "name": "business_standard",
        "url": f"{settings.business_standard_base_url}/markets/news",
        "headline_selector": ".listing-txt h2 a",
    },
]


class NewsScraperAgent(BaseAgent):
    """Scrapes financial news headlines from major Indian business publications."""

    name = "NewsScraperAgent"

    async def run(self, **kwargs: Any) -> AgentResult:
        items: list[dict] = []

        async with httpx.AsyncClient(
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
            follow_redirects=True,
        ) as client:
            for source in NEWS_SOURCES:
                try:
                    articles = await self._scrape_source(client, source)
                    items.extend(articles)
                    logger.info(f"  📰  {source['name']}: {len(articles)} articles")
                except Exception as exc:
                    logger.warning(f"  ⚠️  {source['name']} failed: {exc}")

        logger.info(f"  📥  Total scraped: {len(items)} articles")
        return AgentResult(agent_name=self.name, data={"items": items})

    async def _scrape_source(
        self, client: httpx.AsyncClient, source: dict
    ) -> list[dict]:
        resp = await client.get(source["url"])
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select(source["headline_selector"])[:15]

        articles = []
        for link in links:
            headline = link.get_text(strip=True)
            href = link.get("href", "")
            if not headline:
                continue

            # Normalise relative URLs
            if href and not href.startswith("http"):
                href = source["url"].rstrip("/") + "/" + href.lstrip("/")

            articles.append(
                {
                    "source": source["name"],
                    "headline": headline,
                    "body": None,  # Body can be fetched lazily if needed
                    "url": href,
                    "published_at": None,
                    "content_hash": hashlib.sha256(headline.encode()).hexdigest(),
                }
            )

        return articles
