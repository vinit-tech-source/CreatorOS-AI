import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.media_asset import MediaAsset
from app.schemas.media_asset import MediaAssetCreate, MediaAssetUpdate


class AbstractMediaAssetRepository(ABC):
    """Abstract interface for the MediaAsset repository."""

    @abstractmethod
    async def create(self, data: MediaAssetCreate, workspace_id: uuid.UUID) -> MediaAsset:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, media_id: uuid.UUID) -> Optional[MediaAsset]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID) -> list[MediaAsset]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_post(self, post_id: uuid.UUID) -> list[MediaAsset]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, media_asset: MediaAsset, data: MediaAssetUpdate) -> MediaAsset:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, media_asset: MediaAsset) -> None:
        raise NotImplementedError
