"""
app/mcp/adapters/social_base.py

Abstract base class for social media provider adapters.
"""
from abc import ABC, abstractmethod
from typing import List

from app.mcp.schemas.social import SocialAccountData, SocialPostData, SocialMetrics, SocialPublishResult


class SocialAdapter(ABC):
    """
    Abstract adapter for social providers (e.g. X, LinkedIn, Instagram).
    Subclasses must map provider-specific data to normalized schemas.
    """
    
    @abstractmethod
    async def get_account_info(self, platform_user_id: str) -> SocialAccountData:
        """Fetch account profile information."""
        pass
        
    @abstractmethod
    async def get_profile_metrics(self, platform_user_id: str) -> SocialMetrics:
        """Fetch general account metrics."""
        pass
        
    @abstractmethod
    async def get_recent_posts(self, platform_user_id: str, limit: int = 10) -> List[SocialPostData]:
        """Fetch recent posts from the account."""
        pass

    @abstractmethod
    async def publish_post(self, content: str, idempotency_key: str, media: List[str] = None) -> SocialPublishResult:
        """Publish a post to the account."""
        pass
