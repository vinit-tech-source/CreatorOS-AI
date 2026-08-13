import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.social_account import SocialAccount, SocialPlatform
from app.schemas.social_account import SocialAccountCreate, SocialAccountUpdate


class AbstractSocialAccountRepository(ABC):
    """Abstract interface for the SocialAccount repository."""

    @abstractmethod
    async def create(
        self,
        data: SocialAccountCreate,
        workspace_id: uuid.UUID,
        access_token_encrypted: str,
        refresh_token_encrypted: Optional[str],
    ) -> SocialAccount:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, account_id: uuid.UUID) -> Optional[SocialAccount]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> list[SocialAccount]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_platform(
        self, workspace_id: uuid.UUID, platform: SocialPlatform
    ) -> list[SocialAccount]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_platform_user_id(
        self, workspace_id: uuid.UUID, platform: SocialPlatform, platform_user_id: str
    ) -> Optional[SocialAccount]:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, account: SocialAccount, data: SocialAccountUpdate
    ) -> SocialAccount:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, account: SocialAccount) -> None:
        raise NotImplementedError
