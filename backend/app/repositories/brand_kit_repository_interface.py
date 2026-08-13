import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.brand_kit import BrandKit
from app.schemas.brand_kit import BrandKitCreate, BrandKitUpdate


class AbstractBrandKitRepository(ABC):
    """Abstract interface for the BrandKit repository."""

    @abstractmethod
    async def create(self, data: BrandKitCreate, workspace_id: uuid.UUID) -> BrandKit:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, brand_kit_id: uuid.UUID) -> Optional[BrandKit]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> Optional[BrandKit]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, brand_kit: BrandKit, data: BrandKitUpdate) -> BrandKit:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, brand_kit: BrandKit) -> None:
        raise NotImplementedError
