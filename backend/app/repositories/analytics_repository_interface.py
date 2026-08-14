from abc import ABC, abstractmethod
import uuid
from typing import List, Optional

from app.models.post_analytics import PostAnalytics
from app.schemas.analytics import AnalyticsSummary

class AbstractAnalyticsRepository(ABC):
    @abstractmethod
    async def create_snapshot(self, analytics: PostAnalytics) -> PostAnalytics:
        pass

    @abstractmethod
    async def get_latest_snapshot(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[PostAnalytics]:
        pass

    @abstractmethod
    async def list_snapshots_by_post(self, post_id: uuid.UUID, workspace_id: uuid.UUID) -> List[PostAnalytics]:
        pass

    @abstractmethod
    async def list_snapshots_by_workspace(self, workspace_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[PostAnalytics]:
        pass

    @abstractmethod
    async def aggregate_workspace_metrics(self, workspace_id: uuid.UUID) -> AnalyticsSummary:
        pass
