"""
app/repositories/media_asset_repository.py

Concrete SQLAlchemy 2.0 async implementation of the MediaAsset repository.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media_asset import MediaAsset
from app.repositories.media_asset_repository_interface import AbstractMediaAssetRepository
from app.schemas.media_asset import MediaAssetCreate, MediaAssetUpdate

logger = logging.getLogger(__name__)


class MediaAssetRepository(AbstractMediaAssetRepository):
    """Concrete repository for MediaAsset database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: MediaAssetCreate, workspace_id: uuid.UUID) -> MediaAsset:
        """Persist a new MediaAsset to the database."""
        media_asset = MediaAsset(
            workspace_id=workspace_id,
            post_id=data.post_id,
            file_name=data.file_name,
            storage_key=data.storage_key,
            storage_url=data.storage_url,
            mime_type=data.mime_type,
            media_type=data.media_type,
            file_size=data.file_size,
            width=data.width,
            height=data.height,
            duration_seconds=data.duration_seconds,
            checksum=data.checksum,
            alt_text=data.alt_text,
            is_active=True,
        )
        self.session.add(media_asset)
        await self.session.commit()
        await self.session.refresh(media_asset)
        logger.info(
            f"MediaAsset created: id={media_asset.id} workspace={workspace_id} "
            f"type={media_asset.media_type.value}"
        )
        return media_asset

    async def get_by_id(self, media_id: uuid.UUID) -> Optional[MediaAsset]:
        """Return a MediaAsset by its UUID primary key."""
        result = await self.session.execute(
            select(MediaAsset).where(MediaAsset.id == media_id)
        )
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[MediaAsset]:
        """Return MediaAssets for a specific workspace with pagination, ordered newest first."""
        result = await self.session.execute(
            select(MediaAsset)
            .where(MediaAsset.workspace_id == workspace_id)
            .order_by(MediaAsset.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_post(self, post_id: uuid.UUID) -> list[MediaAsset]:
        """Return all MediaAssets linked to a specific post."""
        result = await self.session.execute(
            select(MediaAsset)
            .where(MediaAsset.post_id == post_id)
            .order_by(MediaAsset.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, media_asset: MediaAsset, data: MediaAssetUpdate) -> MediaAsset:
        """Apply partial updates from MediaAssetUpdate schema.

        Uses exclude_unset=True so that:
          - Omitted fields are left unchanged.
          - Explicitly provided null values clear nullable fields.
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(media_asset, field, value)

        self.session.add(media_asset)
        await self.session.commit()
        await self.session.refresh(media_asset)
        logger.info(f"MediaAsset updated: id={media_asset.id}")
        return media_asset

    async def delete(self, media_asset: MediaAsset) -> None:
        """Permanently remove a MediaAsset record."""
        await self.session.delete(media_asset)
        await self.session.commit()
        logger.info(
            f"MediaAsset deleted: id={media_asset.id} workspace={media_asset.workspace_id}"
        )
