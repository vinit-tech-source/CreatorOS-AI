"""
app/mcp/schemas/social.py

Normalized Pydantic schemas for Social MCP tools.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SocialAccountData(BaseModel):
    """Normalized data for a social account profile."""
    platform: str = Field(..., description="e.g., 'X', 'LINKEDIN', 'INSTAGRAM'")
    platform_user_id: str = Field(..., description="The ID of the user on the platform")
    username: str = Field(..., description="The handle or username")
    display_name: str = Field(..., description="The display name")
    followers: int = Field(default=0, description="Number of followers")
    following: int = Field(default=0, description="Number of accounts followed")
    profile_url: Optional[str] = Field(None, description="URL to the user's profile")

class SocialPostData(BaseModel):
    """Normalized data for a single social media post."""
    post_id: str = Field(..., description="Platform-specific post ID")
    platform: str = Field(..., description="e.g., 'X', 'LINKEDIN'")
    text: str = Field(..., description="Text content of the post")
    published_at: datetime = Field(..., description="When the post was published")
    likes: int = Field(default=0, description="Number of likes")
    comments: int = Field(default=0, description="Number of comments/replies")
    shares: int = Field(default=0, description="Number of shares/retweets")
    impressions: int = Field(default=0, description="Number of impressions/views")
    url: Optional[str] = Field(None, description="URL to the specific post")

class SocialMetrics(BaseModel):
    """Normalized social metrics for an account."""
    followers: int = Field(default=0)
    impressions: int = Field(default=0)
    engagement_rate: float = Field(default=0.0)
    likes: int = Field(default=0)
    comments: int = Field(default=0)
    shares: int = Field(default=0)
    collected_at: datetime = Field(default_factory=datetime.utcnow)
