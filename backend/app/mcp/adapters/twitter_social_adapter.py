"""
app/mcp/adapters/twitter_social_adapter.py

Twitter/X Social Adapter using the Twitter API v2.

Handles:
  - Publishing tweets via POST /2/tweets
  - Fetching tweet metrics via GET /2/tweets/{id}
  - Fetching account profile info via GET /2/users/me
  - Fetching recent tweets via GET /2/users/{id}/tweets

Tokens are stored encrypted and decrypted inline — they never persist in memory.
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import httpx

from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.schemas.social import (
    SocialAccountData,
    SocialPostData,
    SocialMetrics,
    SocialPublishResult,
    SocialPostMetrics,
)
from app.mcp.exceptions.exceptions import MCPProviderError, MCPAuthenticationError
from app.core.encryption import decrypt_secret

logger = logging.getLogger(__name__)

API_BASE = "https://api.twitter.com/2"


class TwitterSocialAdapter(SocialAdapter):
    """
    Adapter for Twitter/X platform via Twitter API v2.
    """

    def __init__(
        self,
        access_token_encrypted: str,
        refresh_token_encrypted: Optional[str] = None,
        platform_user_id: Optional[str] = None,
    ):
        self._access_token_encrypted = access_token_encrypted
        self._refresh_token_encrypted = refresh_token_encrypted
        self._platform_user_id = platform_user_id

    def _get_access_token(self) -> str:
        try:
            return decrypt_secret(self._access_token_encrypted)
        except Exception:
            raise MCPAuthenticationError("Failed to decrypt Twitter access token.")

    def _auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._get_access_token()}"}

    async def _get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}{path}",
                params=params,
                headers=self._auth_headers(),
            )
            if response.status_code in (401, 403):
                raise MCPAuthenticationError("Twitter credentials expired or unauthorized.")
            if response.status_code == 429:
                raise MCPProviderError("Twitter API rate limit exceeded.")
            if response.status_code not in (200, 201):
                logger.error(f"Twitter API error {response.status_code}: {response.text}")
                raise MCPProviderError(f"Twitter API error: {response.status_code}")
            return response.json()

    async def get_account_info(self, platform_user_id: str) -> SocialAccountData:
        """Fetch user profile using Twitter API v2 /users/:id."""
        data = await self._get(
            f"/users/{platform_user_id}",
            params={"user.fields": "id,name,username,public_metrics,profile_image_url"},
        )
        user = data.get("data", {})
        metrics = user.get("public_metrics", {})
        return SocialAccountData(
            platform="X",
            platform_user_id=user.get("id", platform_user_id),
            username=user.get("username", ""),
            display_name=user.get("name", ""),
            followers=metrics.get("followers_count"),
            following=metrics.get("following_count"),
            profile_url=f"https://x.com/{user.get('username', '')}",
        )

    async def get_profile_metrics(self, platform_user_id: str) -> SocialMetrics:
        """Fetch aggregate account metrics."""
        data = await self._get(
            f"/users/{platform_user_id}",
            params={"user.fields": "public_metrics"},
        )
        user = data.get("data", {})
        metrics = user.get("public_metrics", {})
        return SocialMetrics(
            followers=metrics.get("followers_count"),
            impressions=None,   # Not available at account level via v2
            engagement_rate=None,
            likes=metrics.get("like_count"),
            comments=None,
            shares=metrics.get("tweet_count"),
        )

    async def get_recent_posts(self, platform_user_id: str, limit: int = 10) -> List[SocialPostData]:
        """Fetch recent tweets from the account."""
        actual_limit = min(max(1, limit), 100)
        data = await self._get(
            f"/users/{platform_user_id}/tweets",
            params={
                "max_results": actual_limit,
                "tweet.fields": "created_at,public_metrics,text",
            },
        )
        tweets = data.get("data", [])
        posts = []
        for tweet in tweets:
            metrics = tweet.get("public_metrics", {})
            created_at = None
            if tweet.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
                except ValueError:
                    created_at = datetime.now(timezone.utc)

            posts.append(SocialPostData(
                post_id=tweet.get("id"),
                platform="X",
                text=tweet.get("text", ""),
                published_at=created_at,
                likes=metrics.get("like_count", 0),
                comments=metrics.get("reply_count", 0),
                shares=metrics.get("retweet_count", 0),
                impressions=metrics.get("impression_count"),
                url=f"https://x.com/i/web/status/{tweet.get('id')}",
            ))
        return posts

    async def publish_post(self, content: str, idempotency_key: str, media: List[str] = None) -> SocialPublishResult:
        """Publish a tweet via Twitter API v2 POST /2/tweets."""
        if not content or not content.strip():
            raise MCPProviderError("Tweet content cannot be empty.")

        if len(content) > 280:
            logger.warning(f"Tweet content exceeds 280 chars ({len(content)}). Truncating.")
            content = content[:277] + "..."

        payload: Dict[str, Any] = {"text": content}

        # If media URLs are provided, note: Twitter v2 requires uploading media first via v1.1
        # For now log a warning; full media upload support requires additional /1.1/media/upload calls
        if media:
            logger.warning(
                f"Twitter adapter: {len(media)} media assets provided but media upload "
                "via API v1.1 is not yet implemented. Posting text only."
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/tweets",
                json=payload,
                headers={**self._auth_headers(), "Content-Type": "application/json"},
            )
            if response.status_code in (401, 403):
                raise MCPAuthenticationError("Twitter credentials expired or insufficient permissions.")
            if response.status_code == 429:
                raise MCPProviderError("Twitter API rate limit exceeded.")
            if response.status_code not in (200, 201):
                logger.error(f"Twitter publish failed ({response.status_code}): {response.text}")
                raise MCPProviderError(f"Twitter API publish error: {response.status_code}")

            resp_data = response.json().get("data", {})
            tweet_id = resp_data.get("id")
            username = self._platform_user_id or ""

            return SocialPublishResult(
                platform="X",
                external_post_id=tweet_id,
                published_at=datetime.now(timezone.utc),
                post_url=f"https://x.com/i/web/status/{tweet_id}",
                status="SUCCESS",
            )

    async def get_post_metrics(self, external_post_id: str) -> SocialPostMetrics:
        """Fetch metrics for a specific tweet via Twitter API v2."""
        data = await self._get(
            f"/tweets/{external_post_id}",
            params={"tweet.fields": "public_metrics,created_at"},
        )
        tweet = data.get("data", {})
        metrics = tweet.get("public_metrics", {})

        return SocialPostMetrics(
            likes=metrics.get("like_count"),
            comments=metrics.get("reply_count"),
            shares=metrics.get("retweet_count"),
            impressions=metrics.get("impression_count"),
            views=None,
            saves=metrics.get("bookmark_count"),
            clicks=None,
            followers_at_time=None,
            engagement_rate=None,
            collected_at=datetime.now(timezone.utc),
        )
