"""
Twitter/X Ingestion Agent — scrapes financial Twitter accounts.
"""

import hashlib
from typing import Any

import httpx
from loguru import logger

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.schemas.agent import AgentResult


# Curated list of Indian financial Twitter handles to track
FINANCIAL_HANDLES = [
    "ABORISHADE",
    "QuantMumbai",
    "markaborishade",
    "cnaborishade",
    "ETMarkets",
    "baborishade",
    "MoneyaborishadeIn",
    "NSEIndia",
    "BSEIndia",
]


class TwitterAgent(BaseAgent):
    """Ingests recent tweets from curated financial handles."""

    name = "TwitterAgent"

    def __init__(self):
        self.bearer_token = settings.twitter_bearer_token
        self.base_url = "https://api.twitter.com/2"

    async def run(self, **kwargs: Any) -> AgentResult:
        if not self.bearer_token:
            logger.warning("⚠️  Twitter bearer token not set — skipping")
            return AgentResult(agent_name=self.name, data={"items": []})

        items: list[dict] = []
        headers = {"Authorization": f"Bearer {self.bearer_token}"}

        async with httpx.AsyncClient(headers=headers, timeout=30) as client:
            for handle in FINANCIAL_HANDLES:
                try:
                    tweets = await self._fetch_recent_tweets(client, handle)
                    items.extend(tweets)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 401:
                        logger.warning(f"  ⚠️  Twitter 401 Unauthorized — check TWITTER_BEARER_TOKEN in .env")
                        break # No point continuing if token is bad
                    logger.warning(f"  ⚠️  Failed to fetch @{handle}: {exc}")
                except Exception as exc:
                    logger.warning(f"  ⚠️  Failed to fetch @{handle}: {exc}")

        logger.info(f"  📥  Fetched {len(items)} tweets from {len(FINANCIAL_HANDLES)} handles")
        return AgentResult(agent_name=self.name, data={"items": items})

    async def _fetch_recent_tweets(
        self, client: httpx.AsyncClient, handle: str
    ) -> list[dict]:
        """Fetch recent tweets for a single handle via Twitter API v2."""
        # Step 1: resolve handle → user ID
        user_resp = await client.get(
            f"{self.base_url}/users/by/username/{handle}",
        )
        user_resp.raise_for_status()
        user_id = user_resp.json()["data"]["id"]

        # Step 2: recent tweets
        tweets_resp = await client.get(
            f"{self.base_url}/users/{user_id}/tweets",
            params={"max_results": 10, "tweet.fields": "created_at,text"},
        )
        tweets_resp.raise_for_status()

        raw_tweets = tweets_resp.json().get("data", [])
        return [
            {
                "source": "twitter",
                "headline": tweet["text"][:256],
                "body": tweet["text"],
                "url": f"https://twitter.com/{handle}/status/{tweet['id']}",
                "published_at": tweet.get("created_at"),
                "content_hash": hashlib.sha256(tweet["text"].encode()).hexdigest(),
            }
            for tweet in raw_tweets
        ]
