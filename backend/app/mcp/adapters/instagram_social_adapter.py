"""
app/mcp/adapters/instagram_social_adapter.py

Instagram Social Adapter using the Meta Graph API Instagram Content Publishing API.

Handles:
  - Publishing photos/videos via Media Container + Publish (2-step API)
  - Fetching post metrics via /{media-id}/insights
  - Fetching profile info via /me?fields=id,username,name,followers_count

Requires a Business or Creator Instagram account linked to a Facebook Page.
Personal accounts are NOT supported by the Graph API.

Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-media
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

GRAPH_BASE = "https://graph.facebook.com/v19.0"


class InstagramSocialAdapter(SocialAdapter):
    """
    Adapter for Instagram Business/Creator accounts via Meta Graph API.

    Publishing requires a 2-step process:
      1. Create a media container (returns media_id)
      2. Publish the container (returns published media_id)
    """

    def __init__(
        self,
        access_token_encrypted: str,
        refresh_token_encrypted: Optional[str] = None,
        platform_user_id: Optional[str] = None,
    ):
        self._access_token_encrypted = access_token_encrypted
        self._refresh_token_encrypted = refresh_token_encrypted
        self._platform_user_id = platform_user_id  # Instagram Business Account ID

    def _get_access_token(self) -> str:
        try:
            return decrypt_secret(self._access_token_encrypted)
        except Exception:
            raise MCPAuthenticationError("Failed to decrypt Instagram access token.")

    def _params(self, extra: Dict = None) -> Dict[str, str]:
        """Base params with access token appended."""
        p = {"access_token": self._get_access_token()}
        if extra:
            p.update(extra)
        return p

    async def _get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GRAPH_BASE}{path}",
                params=self._params(params),
            )
            if response.status_code in (401, 403):
                raise MCPAuthenticationError("Instagram credentials expired or unauthorized.")
            if response.status_code == 429:
                raise MCPProviderError("Instagram/Meta API rate limit exceeded.")
            if response.status_code not in (200, 201):
                logger.error(f"Instagram API error {response.status_code}: {response.text}")
                raise MCPProviderError(f"Instagram API error: {response.status_code}")
            return response.json()

    async def _post(self, path: str, data: Dict) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GRAPH_BASE}{path}",
                data=self._params(data),
            )
            if response.status_code in (401, 403):
                raise MCPAuthenticationError("Instagram credentials expired or unauthorized.")
            if response.status_code not in (200, 201):
                logger.error(f"Instagram API error {response.status_code}: {response.text}")
                raise MCPProviderError(f"Instagram API error: {response.status_code}")
            return response.json()

    async def get_account_info(self, platform_user_id: str) -> SocialAccountData:
        """Fetch Instagram Business account info."""
        data = await self._get(
            f"/{platform_user_id}",
            params={"fields": "id,username,name,followers_count,follows_count,biography"},
        )
        return SocialAccountData(
            platform="INSTAGRAM",
            platform_user_id=data.get("id", platform_user_id),
            username=data.get("username", ""),
            display_name=data.get("name", data.get("username", "")),
            followers=data.get("followers_count"),
            following=data.get("follows_count"),
            profile_url=f"https://www.instagram.com/{data.get('username', '')}",
        )

    async def get_profile_metrics(self, platform_user_id: str) -> SocialMetrics:
        """Fetch aggregate account metrics."""
        data = await self._get(
            f"/{platform_user_id}",
            params={"fields": "followers_count,media_count"},
        )
        return SocialMetrics(
            followers=data.get("followers_count"),
            impressions=None,
            engagement_rate=None,
            likes=None,
            comments=None,
            shares=None,
        )

    async def get_recent_posts(self, platform_user_id: str, limit: int = 10) -> List[SocialPostData]:
        """Fetch recent media posts from the Instagram Business account."""
        actual_limit = min(max(1, limit), 100)
        try:
            data = await self._get(
                f"/{platform_user_id}/media",
                params={
                    "fields": "id,caption,timestamp,like_count,comments_count,permalink",
                    "limit": actual_limit,
                },
            )
            items = data.get("data", [])
            posts = []
            for item in items:
                published_at = None
                if item.get("timestamp"):
                    try:
                        published_at = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                    except ValueError:
                        published_at = datetime.now(timezone.utc)

                posts.append(SocialPostData(
                    post_id=item.get("id"),
                    platform="INSTAGRAM",
                    text=item.get("caption", ""),
                    published_at=published_at,
                    likes=item.get("like_count", 0),
                    comments=item.get("comments_count", 0),
                    shares=None,  # Instagram Graph API doesn't expose shares directly
                    impressions=None,
                    url=item.get("permalink"),
                ))
            return posts
        except Exception as exc:
            logger.warning(f"Instagram get_recent_posts failed: {exc}")
            return []

    async def publish_post(self, content: str, idempotency_key: str, media: List[str] = None) -> SocialPublishResult:
        """
        Publish content to Instagram via the 2-step Container → Publish flow.

        Step 1: Create a media container (requires either image_url for IMAGE posts,
                or the container is for a TEXT/REELS post).
        Step 2: Publish the container.

        Note: Instagram does NOT support text-only posts via Graph API.
              At minimum one image_url must be provided for feed posts.
        """
        ig_user_id = self._platform_user_id

        if not media:
            logger.warning(
                "Instagram requires at least one image/video to publish a feed post. "
                "Text-only posts are not supported by the Graph API. Aborting publish."
            )
            raise MCPProviderError(
                "Instagram publishing requires media (image or video URL). "
                "Text-only posts are not supported."
            )

        # Step 1: Create container (single image post)
        image_url = media[0]  # Use the first media asset as the primary image
        container_data = {
            "image_url": image_url,
            "caption": content,
        }

        container_response = await self._post(f"/{ig_user_id}/media", container_data)
        creation_id = container_response.get("id")
        if not creation_id:
            raise MCPProviderError("Instagram: Failed to create media container — no ID returned.")

        # Step 2: Publish the container
        publish_response = await self._post(
            f"/{ig_user_id}/media_publish",
            {"creation_id": creation_id},
        )
        media_id = publish_response.get("id")
        if not media_id:
            raise MCPProviderError("Instagram: Failed to publish media container.")

        return SocialPublishResult(
            platform="INSTAGRAM",
            external_post_id=media_id,
            published_at=datetime.now(timezone.utc),
            post_url=f"https://www.instagram.com/p/{media_id}/",
            status="SUCCESS",
        )

    async def get_post_metrics(self, external_post_id: str) -> SocialPostMetrics:
        """Fetch insights for a specific Instagram media object."""
        try:
            data = await self._get(
                f"/{external_post_id}/insights",
                params={
                    "metric": "impressions,reach,likes,comments,shares,saved",
                },
            )
            metrics_list = data.get("data", [])
            metrics: Dict[str, int] = {}
            for metric in metrics_list:
                metrics[metric["name"]] = metric.get("values", [{}])[-1].get("value", 0)
        except Exception as exc:
            logger.warning(f"Instagram get_post_metrics failed: {exc}. Returning zeros.")
            metrics = {}

        return SocialPostMetrics(
            likes=metrics.get("likes"),
            comments=metrics.get("comments"),
            shares=metrics.get("shares"),
            impressions=metrics.get("impressions"),
            views=metrics.get("reach"),
            saves=metrics.get("saved"),
            clicks=None,
            followers_at_time=None,
            engagement_rate=None,
            collected_at=datetime.now(timezone.utc),
        )
