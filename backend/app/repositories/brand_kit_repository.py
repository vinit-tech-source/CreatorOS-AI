import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand_kit import BrandKit
from app.repositories.brand_kit_repository_interface import AbstractBrandKitRepository
from app.schemas.brand_kit import BrandKitCreate, BrandKitUpdate

logger = logging.getLogger(__name__)


class BrandKitRepository(AbstractBrandKitRepository):
    """
    Concrete SQLAlchemy 2.0 async implementation of the BrandKit repository.
    All database access for the BrandKit model is handled here.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: BrandKitCreate, workspace_id: uuid.UUID) -> BrandKit:
        """Create and persist a new BrandKit record."""
        brand_kit = BrandKit(
            workspace_id=workspace_id,
            brand_name=data.brand_name,
            description=data.description,
            website_url=data.website_url,
            logo_url=data.logo_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color,
            accent_color=data.accent_color,
            default_tone=data.default_tone,
            target_audience=data.target_audience,
            brand_values=data.brand_values,
            preferred_language=data.preferred_language,
        )
        self.session.add(brand_kit)
        await self.session.commit()
        await self.session.refresh(brand_kit)
        logger.info(f"BrandKit created: id={brand_kit.id} workspace={workspace_id}")
        return brand_kit

    async def get_by_id(self, brand_kit_id: uuid.UUID) -> Optional[BrandKit]:
        """Return a BrandKit by primary key, or None if not found."""
        result = await self.session.execute(
            select(BrandKit).where(BrandKit.id == brand_kit_id)
        )
        return result.scalar_one_or_none()

    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> Optional[BrandKit]:
        """Return the BrandKit for a given workspace, or None if not found."""
        result = await self.session.execute(
            select(BrandKit).where(BrandKit.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def update(self, brand_kit: BrandKit, data: BrandKitUpdate) -> BrandKit:
        """Apply partial updates from BrandKitUpdate schema.

        Uses exclude_unset=True so that:
          - Omitted fields are left unchanged.
          - Explicitly provided null values clear nullable fields.
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand_kit, field, value)
        self.session.add(brand_kit)
        await self.session.commit()
        await self.session.refresh(brand_kit)
        logger.info(f"BrandKit updated: id={brand_kit.id}")
        return brand_kit

    async def delete(self, brand_kit: BrandKit) -> None:
        """Permanently remove a BrandKit record from the database."""
        await self.session.delete(brand_kit)
        await self.session.commit()
        logger.info(f"BrandKit deleted: id={brand_kit.id} workspace={brand_kit.workspace_id}")
