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
    followers: Optional[int] = Field(default=None, description="Number of followers")
    following: Optional[int] = Field(default=None, description="Number of accounts followed")
    profile_url: Optional[str] = Field(None, description="URL to the user's profile")

class SocialPostData(BaseModel):
    """Normalized data for a single social media post."""
    post_id: str = Field(..., description="Platform-specific post ID")
    platform: str = Field(..., description="e.g., 'X', 'LINKEDIN'")
    text: str = Field(..., description="Text content of the post")
    published_at: datetime = Field(..., description="When the post was published")
    likes: Optional[int] = Field(default=None, description="Number of likes")
    comments: Optional[int] = Field(default=None, description="Number of comments/replies")
    shares: Optional[int] = Field(default=None, description="Number of shares/retweets")
    impressions: Optional[int] = Field(default=None, description="Number of impressions/views")
    url: Optional[str] = Field(None, description="URL to the specific post")

class SocialMetrics(BaseModel):
    """Normalized social metrics for an account."""
    followers: Optional[int] = Field(default=None)
    impressions: Optional[int] = Field(default=None)
    engagement_rate: Optional[float] = Field(default=None)
    likes: Optional[int] = Field(default=None)
    comments: Optional[int] = Field(default=None)
    shares: Optional[int] = Field(default=None)
    collected_at: datetime = Field(default_factory=datetime.utcnow)

class SocialPublishResult(BaseModel):
    """Normalized data representing the result of publishing a post."""
    platform: str = Field(..., description="e.g., 'X', 'LINKEDIN', 'BLUESKY'")
    external_post_id: Optional[str] = Field(None, description="Platform-specific post ID if successful")
    published_at: Optional[datetime] = Field(None, description="When the post was published")
    post_url: Optional[str] = Field(None, description="URL to the specific post")
    status: str = Field(..., description="PublishStatus as a string, e.g., 'SUCCESS', 'FAILED'")
    error_message: Optional[str] = Field(None, description="Error message if failed")
