"""
app/mcp/adapters/bluesky_social_adapter.py

Bluesky Social Adapter.
Retrieves read-only social media data using the AT Protocol API.
Decrypts tokens internally to guarantee they do not leak outside this boundary.
"""
from typing import List, Dict, Any
import logging
from datetime import datetime, timezone
import httpx

from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.schemas.social import SocialAccountData, SocialPostData, SocialMetrics
from app.mcp.exceptions.exceptions import MCPProviderError, MCPAuthenticationError
from app.core.encryption import decrypt_secret

logger = logging.getLogger(__name__)


class BlueskySocialAdapter(SocialAdapter):
    """
    Adapter for Bluesky Social MCP Tools.
    """

    def __init__(
        self,
        access_token_encrypted: str,
        platform_user_id: str,
        refresh_token_encrypted: str | None = None
    ):
        self._access_token_encrypted = access_token_encrypted
        self._refresh_token_encrypted = refresh_token_encrypted
        self._platform_user_id = platform_user_id
        
        # Bluesky endpoints
        self.profile_url = "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile"
        self.feed_url = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
        
        # We can use the public API for reading profile/feed, 
        # but to use authenticated rate limits and private info, 
        # we attach the Bearer token.
        self.base_url = "https://bsky.social"

    def _get_access_token(self) -> str:
        """Decrypt the token at the time of use."""
        try:
            return decrypt_secret(self._access_token_encrypted)
        except Exception:
            raise MCPAuthenticationError("Failed to decrypt access token for Bluesky.")

    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an authenticated request to the provider."""
        # Using a context manager so token doesn't persist in memory longer than needed
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code in (401, 403):
                    raise MCPAuthenticationError("Bluesky credentials expired or unauthorized.")
                
                if response.status_code == 429:
                    raise MCPProviderError("Bluesky API rate limit exceeded.")
                    
                if response.status_code != 200:
                    raise MCPProviderError("Bluesky API returned an error.")
                    
                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"Bluesky HTTP error: {e}")
                raise MCPProviderError("Bluesky API is unavailable or timed out.")

    async def get_account_info(self, platform_user_id: str) -> SocialAccountData:
        """Fetch normalized account profile information."""
        # Note: We must use the DID or handle to get the profile
        params = {"actor": platform_user_id}
        data = await self._make_request(self.profile_url, params=params)
        
        return SocialAccountData(
            platform="BLUESKY",
            platform_user_id=data.get("did", platform_user_id),
            username=data.get("handle", ""),
            display_name=data.get("displayName") or data.get("handle", ""),
            followers=data.get("followersCount"),
            following=data.get("followsCount"),
            profile_url=f"https://bsky.app/profile/{data.get('handle', '')}"
        )

    async def get_profile_metrics(self, platform_user_id: str) -> SocialMetrics:
        """Fetch general account metrics."""
        params = {"actor": platform_user_id}
        data = await self._make_request(self.profile_url, params=params)
        
        # Bluesky does not provide aggregate impressions/engagement via the standard profile API
        return SocialMetrics(
            followers=data.get("followersCount"),
            # The following are unsupported on the basic profile endpoint, use nullable
            impressions=None,
            engagement_rate=None,
            likes=None,
            comments=None,
            shares=None
        )

    async def get_recent_posts(self, platform_user_id: str, limit: int = 10) -> List[SocialPostData]:
        """Fetch recent posts from the account."""
        # Bounded limit parameter
        actual_limit = min(max(1, limit), 100)
        
        params = {
            "actor": platform_user_id,
            "limit": actual_limit,
            "filter": "posts_no_replies"
        }
        
        data = await self._make_request(self.feed_url, params=params)
        feed = data.get("feed", [])
        
        posts = []
        for item in feed:
            post = item.get("post", {})
            record = post.get("record", {})
            author = post.get("author", {})
            
            # Construct URL manually if needed
            uri = post.get("uri", "")
            post_id = uri.split("/")[-1] if uri else ""
            handle = author.get("handle", "")
            
            url = f"https://bsky.app/profile/{handle}/post/{post_id}" if handle and post_id else None
            
            # Parse datetime
            created_at_str = record.get("createdAt")
            published_at = None
            if created_at_str:
                try:
                    # 'Z' represents UTC
                    if created_at_str.endswith('Z'):
                        created_at_str = created_at_str[:-1] + '+00:00'
                    published_at = datetime.fromisoformat(created_at_str)
                except ValueError:
                    published_at = datetime.now(timezone.utc)
            
            posts.append(SocialPostData(
                post_id=uri,  # Full URI is safest unique ID
                platform="BLUESKY",
                text=record.get("text", ""),
                published_at=published_at,
                likes=post.get("likeCount", 0),
                comments=post.get("replyCount", 0),
                shares=post.get("repostCount", 0),
                impressions=None,  # Not natively available per post in public API
                url=url
            ))
            
        return posts
