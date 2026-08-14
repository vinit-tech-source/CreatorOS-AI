import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class AnalyticsSnapshot(BaseModel):
    """Normalized metrics returned from providers or stored in DB."""
    impressions: Optional[int] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    clicks: Optional[int] = None
    followers_at_time: Optional[int] = None
    engagement_rate: Optional[float] = None

class PostAnalyticsResponse(AnalyticsSnapshot):
    """Full API response for a single snapshot."""
    id: uuid.UUID
    post_id: uuid.UUID
    workspace_id: uuid.UUID
    social_account_id: uuid.UUID
    platform: str
    external_post_id: str
    collected_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AnalyticsSummary(BaseModel):
    """Aggregated metrics for a workspace or project."""
    total_impressions: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_saves: int = 0
    total_clicks: int = 0
    average_engagement_rate: float = 0.0
    post_count: int = 0
