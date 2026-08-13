"""
app/repositories/social_account_repository.py

Concrete SQLAlchemy 2.0 async implementation of the SocialAccount repository.

SECURITY: This repository handles encrypted token ciphertext only.
Plaintext tokens are never passed to or returned from this layer.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_account import SocialAccount, SocialPlatform
from app.repositories.social_account_repository_interface import AbstractSocialAccountRepository
from app.schemas.social_account import SocialAccountCreate, SocialAccountUpdate

logger = logging.getLogger(__name__)


class SocialAccountRepository(AbstractSocialAccountRepository):
    """
    Concrete repository for SocialAccount database operations.
    All token values passed in are already encrypted ciphertext.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        data: SocialAccountCreate,
        workspace_id: uuid.UUID,
        access_token_encrypted: str,
        refresh_token_encrypted: Optional[str],
    ) -> SocialAccount:
        """Persist a new SocialAccount with pre-encrypted token values."""
        account = SocialAccount(
            workspace_id=workspace_id,
            platform=data.platform,
            account_name=data.account_name,
            platform_user_id=data.platform_user_id,
            access_token_encrypted=access_token_encrypted,
            refresh_token_encrypted=refresh_token_encrypted,
            token_expires_at=data.token_expires_at,
            scopes=data.scopes,
            is_active=True,
        )
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        # NOTE: token values intentionally excluded from log
        logger.info(
            f"SocialAccount created: id={account.id} platform={account.platform.value} "
            f"workspace={workspace_id}"
        )
        return account

    async def get_by_id(self, account_id: uuid.UUID) -> Optional[SocialAccount]:
        """Return a SocialAccount by primary key, or None."""
        result = await self.session.execute(
            select(SocialAccount).where(SocialAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> list[SocialAccount]:
        """Return all social accounts for a workspace, ordered by platform then account_name."""
        result = await self.session.execute(
            select(SocialAccount)
            .where(SocialAccount.workspace_id == workspace_id)
            .order_by(SocialAccount.platform, SocialAccount.account_name)
        )
        return list(result.scalars().all())

    async def get_by_platform(
        self, workspace_id: uuid.UUID, platform: SocialPlatform
    ) -> list[SocialAccount]:
        """Return all social accounts for a workspace filtered by platform."""
        result = await self.session.execute(
            select(SocialAccount)
            .where(
                SocialAccount.workspace_id == workspace_id,
                SocialAccount.platform == platform,
            )
            .order_by(SocialAccount.account_name)
        )
        return list(result.scalars().all())

    async def get_by_platform_user_id(
        self,
        workspace_id: uuid.UUID,
        platform: SocialPlatform,
        platform_user_id: str,
    ) -> Optional[SocialAccount]:
        """Return a specific account by workspace + platform + platform_user_id, or None."""
        result = await self.session.execute(
            select(SocialAccount).where(
                SocialAccount.workspace_id == workspace_id,
                SocialAccount.platform == platform,
                SocialAccount.platform_user_id == platform_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, account: SocialAccount, data: SocialAccountUpdate) -> SocialAccount:
        """Apply partial updates from SocialAccountUpdate.

        Uses exclude_unset=True so that:
          - Omitted fields are left unchanged.
          - Explicitly provided null values clear nullable fields.
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        logger.info(f"SocialAccount updated: id={account.id}")
        return account

    async def delete(self, account: SocialAccount) -> None:
        """Permanently remove a SocialAccount record."""
        await self.session.delete(account)
        await self.session.commit()
        logger.info(
            f"SocialAccount deleted: id={account.id} platform={account.platform.value} "
            f"workspace={account.workspace_id}"
        )
