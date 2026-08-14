"""
app/mcp/adapters/fake_social_adapter.py

Fake Social Adapter for offline testing and foundation validation.
"""
from typing import List
from datetime import datetime
import uuid

from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.schemas.social import (
    SocialAccountData, 
    SocialPostData, 
    SocialMetrics, 
    SocialPublishResult,
    SocialPostMetrics
)
from app.mcp.exceptions.exceptions import MCPProviderError


class FakeSocialAdapter(SocialAdapter):
    """
    A fake implementation of the SocialAdapter for testing.
    """
    
    def __init__(self, platform: str = "FAKE"):
        self.platform = platform
        
    async def get_account_info(self, platform_user_id: str) -> SocialAccountData:
        if platform_user_id == "error_user":
            raise MCPProviderError("Simulated provider error")
            
        return SocialAccountData(
            platform=self.platform,
            platform_user_id=platform_user_id,
            username=f"{self.platform.lower()}_{platform_user_id}",
            display_name=f"Fake {platform_user_id}",
            followers=1000,
            following=500,
            profile_url=f"https://{self.platform.lower()}.com/{platform_user_id}"
        )
        
    async def get_profile_metrics(self, platform_user_id: str) -> SocialMetrics:
        if platform_user_id == "error_user":
            raise MCPProviderError("Simulated provider error")
            
        return SocialMetrics(
            followers=1000,
            impressions=5000,
            engagement_rate=2.5,
            likes=200,
            comments=50,
            shares=10
        )
        
    async def get_recent_posts(self, platform_user_id: str, limit: int = 10) -> List[SocialPostData]:
        if platform_user_id == "error_user":
            raise MCPProviderError("Simulated provider error")
            
        posts = []
        actual_limit = min(limit, 50) # Sane bound
        for i in range(actual_limit):
            posts.append(
                SocialPostData(
                    post_id=f"post_{i}",
                    platform=self.platform,
                    text=f"Fake post {i} from {platform_user_id}",
                    published_at=datetime.utcnow(),
                    likes=10 * i,
                    comments=i,
                    shares=0,
                    impressions=100 * i,
                    url=f"https://{self.platform.lower()}.com/posts/post_{i}"
                )
            )
        return posts

    async def publish_post(self, content: str, idempotency_key: str, media: List[str] = None) -> SocialPublishResult:
        if "error" in content:
            raise MCPProviderError("Simulated provider error on publish")
            
        return SocialPublishResult(
            platform=self.platform,
            external_post_id=f"fake_post_{uuid.uuid4().hex[:8]}",
            published_at=datetime.utcnow(),
            post_url=f"https://fake-{self.platform.lower()}.com/post/mock",
            status="SUCCESS"
        )

    async def get_post_metrics(self, external_post_id: str) -> SocialPostMetrics:
        import random
        from datetime import datetime, timezone
        
        return SocialPostMetrics(
            impressions=random.randint(100, 10000),
            views=random.randint(100, 5000),
            likes=random.randint(10, 1000),
            comments=random.randint(0, 100),
            shares=random.randint(0, 50),
            saves=random.randint(0, 20),
            clicks=random.randint(0, 200),
            followers_at_time=random.randint(100, 50000),
            engagement_rate=None,
            collected_at=datetime.now(timezone.utc)
        )
