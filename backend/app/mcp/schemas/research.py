"""
app/mcp/schemas/research.py

Normalized schemas for research data returned by MCP tools.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EngagementMetrics(BaseModel):
    """
    Optional engagement metrics for a piece of content.
    """
    views: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    reposts: Optional[int] = None


class ResearchItem(BaseModel):
    """
    A normalized piece of research gathered from any provider.
    """
    id: str = Field(..., description="Unique identifier for the item from the provider.")
    title: Optional[str] = Field(None, description="Title of the content (e.g., video title, post title).")
    content: str = Field(..., description="The main text/excerpt or description of the content.")
    url: str = Field(..., description="Direct URL to the content.")
    source_name: str = Field(..., description="The name of the provider (e.g., YouTube, Bluesky).")
    platform: str = Field(..., description="The platform it originated from.")
    author: Optional[str] = Field(None, description="The creator/author of the content.")
    published_at: Optional[str] = Field(None, description="ISO timestamp of when it was published.")
    engagement: Optional[EngagementMetrics] = Field(None, description="Available engagement signals.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Any additional provider-specific safe metadata.")
