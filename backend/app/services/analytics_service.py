import uuid
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.post import Post
from app.models.post_analytics import PostAnalytics
from app.schemas.analytics import AnalyticsSummary, AnalyticsSnapshot
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.post_repository import PostRepository
from app.mcp.client.client import MCPClient

class AnalyticsService:
    def __init__(self, session: AsyncSession, mcp_client: MCPClient):
        self.session = session
        self.analytics_repo = AnalyticsRepository(session)
        self.post_repo = PostRepository(session)
        self.mcp_client = mcp_client

    def calculate_engagement_rate(self, snapshot: AnalyticsSnapshot, followers: Optional[int]) -> Optional[float]:
        """Deterministic Python logic to calculate engagement rate."""
        engagements = 0
        if snapshot.likes: engagements += snapshot.likes
        if snapshot.comments: engagements += snapshot.comments
        if snapshot.shares: engagements += snapshot.shares
        if snapshot.saves: engagements += snapshot.saves
        if snapshot.clicks: engagements += snapshot.clicks
        
        # If we have impressions, prefer impressions as denominator
        if snapshot.impressions and snapshot.impressions > 0:
            return round((engagements / snapshot.impressions) * 100, 2)
            
        # If we have views, use views
        if snapshot.views and snapshot.views > 0:
            return round((engagements / snapshot.views) * 100, 2)
            
        # Fall back to followers if available
        if followers and followers > 0:
            return round((engagements / followers) * 100, 2)
            
        return None

    async def record_snapshot(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> PostAnalytics:
        """
        Fetches metrics via MCP for a published post and records a snapshot.
        """
        post = await self.post_repo.get_by_id(post_id)
        if not post or post.project.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or unauthorized"
            )

        if str(post.status) != "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot fetch analytics for unpublished post"
            )
            
        # We need the publishing log or the post's external_post_id to know where it is
        if not post.external_post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post does not have an external_post_id"
            )

        # Assuming post has platform and we know social_account_id? 
        # Actually in CreatorOS, publishing goes to an account. 
        # But wait, post model doesn't have social_account_id directly. 
        # Let's get the latest publishing log to find the social_account_id
        from app.models.publishing_log import PublishingLog, PublishStatus
        from sqlalchemy import select, desc
        
        stmt = (
            select(PublishingLog)
            .where(
                PublishingLog.workspace_id == workspace_id,
                PublishingLog.external_post_id == post.external_post_id,
                PublishingLog.status == PublishStatus.SUCCESS
            )
            .order_by(desc(PublishingLog.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        pub_log = result.scalar_one_or_none()
        
        if not pub_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No successful publishing log found for this post"
            )
            
        social_account_id = pub_log.social_account_id
        
        # Call Social MCP to get post metrics
        tool_input = {
            "workspace_id": str(workspace_id),
            "social_account_id": str(social_account_id),
            "external_post_id": post.external_post_id
        }
        
        tool_result = await self.mcp_client.call_tool(
            server_name="social_server",
            tool_name="get_post_metrics",
            tool_arguments=tool_input
        )
        
        if not tool_result.success:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch metrics: {tool_result.error_message or 'Unknown error'}"
            )
            
        metrics_data = tool_result.data.get("metrics", {})
        snapshot = AnalyticsSnapshot(**metrics_data)
        
        # Calculate engagement rate
        followers = snapshot.followers_at_time  # provided by tool if possible
        if not followers:
            # We could do a second MCP call to get_profile_metrics to find current followers
            # But let's keep it simple. If we don't have it, we calculate without it if possible.
            pass
            
        engagement_rate = self.calculate_engagement_rate(snapshot, followers)
        
        analytics = PostAnalytics(
            post_id=post.id,
            workspace_id=workspace_id,
            social_account_id=social_account_id,
            platform=pub_log.platform.value if hasattr(pub_log.platform, 'value') else str(pub_log.platform),
            external_post_id=post.external_post_id,
            impressions=snapshot.impressions,
            views=snapshot.views,
            likes=snapshot.likes,
            comments=snapshot.comments,
            shares=snapshot.shares,
            saves=snapshot.saves,
            clicks=snapshot.clicks,
            followers_at_time=followers,
            engagement_rate=engagement_rate,
            collected_at=datetime.now(timezone.utc)
        )
        
        return await self.analytics_repo.create_snapshot(analytics)

    async def get_post_analytics(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> List[PostAnalytics]:
        post = await self.post_repo.get_by_id(post_id)
        if not post or post.project.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or unauthorized"
            )
        return await self.analytics_repo.list_snapshots_by_post(post_id, workspace_id)

    async def get_workspace_summary(self, workspace_id: uuid.UUID) -> AnalyticsSummary:
        return await self.analytics_repo.aggregate_workspace_metrics(workspace_id)
