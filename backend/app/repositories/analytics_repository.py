import uuid
from typing import List, Optional
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_analytics import PostAnalytics
from app.schemas.analytics import AnalyticsSummary
from app.repositories.analytics_repository_interface import AbstractAnalyticsRepository

class AnalyticsRepository(AbstractAnalyticsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_snapshot(self, analytics: PostAnalytics) -> PostAnalytics:
        self.session.add(analytics)
        await self.session.commit()
        await self.session.refresh(analytics)
        return analytics

    async def get_latest_snapshot(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[PostAnalytics]:
        stmt = (
            select(PostAnalytics)
            .where(
                and_(
                    PostAnalytics.post_id == post_id,
                    PostAnalytics.workspace_id == workspace_id
                )
            )
            .order_by(desc(PostAnalytics.collected_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_snapshots_by_post(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> List[PostAnalytics]:
        stmt = (
            select(PostAnalytics)
            .where(
                and_(
                    PostAnalytics.post_id == post_id,
                    PostAnalytics.workspace_id == workspace_id
                )
            )
            .order_by(desc(PostAnalytics.collected_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_snapshots_by_workspace(self, workspace_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[PostAnalytics]:
        stmt = (
            select(PostAnalytics)
            .where(PostAnalytics.workspace_id == workspace_id)
            .order_by(desc(PostAnalytics.collected_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def aggregate_workspace_metrics(self, workspace_id: uuid.UUID) -> AnalyticsSummary:
        # Get the latest snapshot for each post
        subq = (
            select(
                PostAnalytics.post_id,
                func.max(PostAnalytics.collected_at).label("latest_collected_at")
            )
            .where(PostAnalytics.workspace_id == workspace_id)
            .group_by(PostAnalytics.post_id)
            .subquery()
        )
        
        stmt = (
            select(
                func.sum(PostAnalytics.impressions).label("total_impressions"),
                func.sum(PostAnalytics.views).label("total_views"),
                func.sum(PostAnalytics.likes).label("total_likes"),
                func.sum(PostAnalytics.comments).label("total_comments"),
                func.sum(PostAnalytics.shares).label("total_shares"),
                func.sum(PostAnalytics.saves).label("total_saves"),
                func.sum(PostAnalytics.clicks).label("total_clicks"),
                func.avg(PostAnalytics.engagement_rate).label("average_engagement_rate"),
                func.count(PostAnalytics.id).label("post_count")
            )
            .join(subq, and_(
                PostAnalytics.post_id == subq.c.post_id,
                PostAnalytics.collected_at == subq.c.latest_collected_at,
                PostAnalytics.workspace_id == workspace_id
            ))
        )
        
        result = await self.session.execute(stmt)
        row = result.first()
        
        if not row or not row.post_count:
            return AnalyticsSummary()
            
        return AnalyticsSummary(
            total_impressions=row.total_impressions or 0,
            total_views=row.total_views or 0,
            total_likes=row.total_likes or 0,
            total_comments=row.total_comments or 0,
            total_shares=row.total_shares or 0,
            total_saves=row.total_saves or 0,
            total_clicks=row.total_clicks or 0,
            average_engagement_rate=float(row.average_engagement_rate) if row.average_engagement_rate is not None else 0.0,
            post_count=row.post_count or 0
        )
