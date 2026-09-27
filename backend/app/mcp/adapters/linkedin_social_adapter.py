"""
app/mcp/adapters/linkedin_social_adapter.py

LinkedIn Social Adapter using the LinkedIn UGC Post API.

Handles:
  - Publishing posts via POST /v2/ugcPosts
  - Fetching share statistics via GET /v2/shares
  - Fetching profile info via GET /v2/userinfo (OpenID Connect)

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

API_BASE = "https://api.linkedin.com/v2"


class LinkedInSocialAdapter(SocialAdapter):
    """
    Adapter for LinkedIn platform via LinkedIn UGC Post API.
    """

    def __init__(
        self,
        access_token_encrypted: str,
        refresh_token_encrypted: Optional[str] = None,
        platform_user_id: Optional[str] = None,
    ):
        self._access_token_encrypted = access_token_encrypted
        self._refresh_token_encrypted = refresh_token_encrypted
        self._platform_user_id = platform_user_id  # LinkedIn member URN (urn:li:person:{id})

    def _get_access_token(self) -> str:
        try:
            return decrypt_secret(self._access_token_encrypted)
        except Exception:
            raise MCPAuthenticationError("Failed to decrypt LinkedIn access token.")

    def _auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    async def _get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}{path}",
                params=params,
                headers=self._auth_headers(),
            )
            if response.status_code in (401, 403):
                raise MCPAuthenticationError("LinkedIn credentials expired or unauthorized.")
            if response.status_code == 429:
                raise MCPProviderError("LinkedIn API rate limit exceeded.")
            if response.status_code not in (200, 201):
                logger.error(f"LinkedIn API error {response.status_code}: {response.text}")
                raise MCPProviderError(f"LinkedIn API error: {response.status_code}")
            return response.json()

    def _get_author_urn(self) -> str:
        """Return the LinkedIn member URN for the authenticated user."""
        user_id = self._platform_user_id or ""
        # If it's already a full URN, return as-is
        if user_id.startswith("urn:li:"):
            return user_id
        # Otherwise build it
        return f"urn:li:person:{user_id}"

    async def get_account_info(self, platform_user_id: str) -> SocialAccountData:
        """Fetch profile info using OpenID Connect userinfo endpoint."""
        data = await self._get("/userinfo")
        username = data.get("email", platform_user_id)
        display_name = data.get("name", username)
        return SocialAccountData(
            platform="LINKEDIN",
            platform_user_id=data.get("sub", platform_user_id),
            username=username,
            display_name=display_name,
            followers=None,  # Not available via standard API
            following=None,
            profile_url=f"https://www.linkedin.com/in/{platform_user_id}",
        )

    async def get_profile_metrics(self, platform_user_id: str) -> SocialMetrics:
        """Return minimal metrics (LinkedIn restricts follower data to partner API)."""
        return SocialMetrics(
            followers=None,
            impressions=None,
            engagement_rate=None,
            likes=None,
            comments=None,
            shares=None,
        )

    async def get_recent_posts(self, platform_user_id: str, limit: int = 10) -> List[SocialPostData]:
        """Fetch recent UGC posts for the member."""
        author_urn = self._get_author_urn()
        try:
            data = await self._get(
                "/ugcPosts",
                params={
                    "q": "authors",
                    "authors": f"List({author_urn})",
                    "count": min(max(1, limit), 100),
                },
            )
            elements = data.get("elements", [])
            posts = []
            for post in elements:
                post_id = post.get("id", "")
                media = post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {})
                text = ""
                commentary = media.get("shareCommentaryV2", {})
                if isinstance(commentary, dict):
                    text = commentary.get("text", "")

                posts.append(SocialPostData(
                    post_id=post_id,
                    platform="LINKEDIN",
                    text=text,
                    published_at=datetime.now(timezone.utc),  # created_at parsing varies
                    likes=None,
                    comments=None,
                    shares=None,
                    impressions=None,
                    url=f"https://www.linkedin.com/feed/update/{post_id}",
                ))
            return posts
        except Exception as exc:
            logger.warning(f"LinkedIn get_recent_posts failed: {exc}")
            return []

    async def publish_post(self, content: str, idempotency_key: str, media: List[str] = None) -> SocialPublishResult:
        """Publish a LinkedIn UGC post via POST /v2/ugcPosts."""
        if not content or not content.strip():
            raise MCPProviderError("LinkedIn post content cannot be empty.")

        author_urn = self._get_author_urn()

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentaryV2": {"text": content},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        if media:
            logger.warning(
                f"LinkedIn adapter: {len(media)} media assets provided. "
                "Media upload via LinkedIn API requires additional /v2/assets registration. Posting text only."
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/ugcPosts",
                json=payload,
                headers=self._auth_headers(),
            )
            if response.status_code in (401, 403):
                raise MCPAuthenticationError("LinkedIn credentials expired or insufficient permissions.")
            if response.status_code == 429:
                raise MCPProviderError("LinkedIn API rate limit exceeded.")
            if response.status_code not in (200, 201):
                logger.error(f"LinkedIn publish failed ({response.status_code}): {response.text}")
                raise MCPProviderError(f"LinkedIn API publish error: {response.status_code}")

            post_id = response.headers.get("x-restli-id", "")
            return SocialPublishResult(
                platform="LINKEDIN",
                external_post_id=post_id,
                published_at=datetime.now(timezone.utc),
                post_url=f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None,
                status="SUCCESS",
            )

    async def get_post_metrics(self, external_post_id: str) -> SocialPostMetrics:
        """Fetch metrics for a specific LinkedIn post."""
        try:
            # URL-encode the URN for use as a path parameter
            encoded_id = external_post_id.replace(":", "%3A").replace(",", "%2C")
            data = await self._get(
                f"/socialActions/{encoded_id}",
                params={"projection": "(likesSummary,commentsSummary)"},
            )
            likes = data.get("likesSummary", {}).get("totalLikes", 0)
            comments = data.get("commentsSummary", {}).get("totalFirstLevelComments", 0)
        except Exception as exc:
            logger.warning(f"LinkedIn get_post_metrics failed: {exc}. Returning zeros.")
            likes, comments = 0, 0

        return SocialPostMetrics(
            likes=likes,
            comments=comments,
            shares=None,
            impressions=None,
            views=None,
            saves=None,
            clicks=None,
            followers_at_time=None,
            engagement_rate=None,
            collected_at=datetime.now(timezone.utc),
        )
