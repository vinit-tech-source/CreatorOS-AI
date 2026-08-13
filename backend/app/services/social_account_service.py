"""
app/services/social_account_service.py

SocialAccount business logic for CreatorOS AI.

Responsibilities:
  - Connect a social account (encrypting tokens before persistence).
  - List connected social accounts for a workspace.
  - Retrieve details of a specific social account.
  - Update account metadata (omits tokens).
  - Disconnect (delete) a social account.

Security Rules:
  - Tokens are accepted as plaintext ONLY in the create_social_account payload.
  - Tokens are encrypted immediately using app.core.encryption.
  - Plaintext tokens are NEVER stored or logged.
  - API schemas and this service never return decrypted tokens to the API layer.
  - The requesting user must own the workspace. Non-ownership returns 404 (info hiding).
"""
import uuid
import logging
from typing import Optional

from app.core.encryption import encrypt_secret
from app.core.exceptions import (
    SocialAccountAlreadyExistsError,
    SocialAccountNotFoundError,
    WorkspaceNotFoundError,
)
from app.repositories.social_account_repository_interface import AbstractSocialAccountRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.social_account import (
    SocialAccountCreate,
    SocialAccountResponse,
    SocialAccountUpdate,
)

logger = logging.getLogger(__name__)


class SocialAccountService:
    """
    Handles Social Account business logic.

    Depends on SocialAccountRepository for data access and WorkspaceRepository
    to verify workspace ownership.
    """

    def __init__(
        self,
        social_account_repository: AbstractSocialAccountRepository,
        workspace_repository: AbstractWorkspaceRepository,
    ) -> None:
        self._sa_repo = social_account_repository
        self._ws_repo = workspace_repository

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    async def _assert_workspace_owner(
        self, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        """
        Verify that the workspace exists and is owned by the requesting user.
        Raises SocialAccountNotFoundError to avoid confirming existence.
        """
        workspace = await self._ws_repo.get_by_id(workspace_id)
        if workspace is None or workspace.owner_id != requesting_user_id:
            if workspace is None:
                logger.warning(
                    f"Social Account operation denied: workspace={workspace_id} does not exist"
                )
            else:
                logger.warning(
                    f"Social Account operation denied: user={requesting_user_id} does not own "
                    f"workspace={workspace_id}"
                )
            raise SocialAccountNotFoundError()

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_social_account(
        self,
        workspace_id: uuid.UUID,
        data: SocialAccountCreate,
        requesting_user_id: uuid.UUID,
    ) -> SocialAccountResponse:
        """
        Connect a new social media account for the workspace.

        Security:
          - Tokens provided in `data` are encrypted before persistence.
          - Tokens are NOT returned in SocialAccountResponse.

        Args:
            workspace_id:       UUID of the workspace.
            data:               Validated SocialAccountCreate schema (contains plaintext tokens).
            requesting_user_id: UUID of the authenticated user.

        Raises:
            SocialAccountNotFoundError:      If workspace non-existent/not owned.
            SocialAccountAlreadyExistsError: If this platform+user is already connected.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        # Enforce unique platform+user per workspace
        existing = await self._sa_repo.get_by_platform_user_id(
            workspace_id, data.platform, data.platform_user_id
        )
        if existing is not None:
            logger.warning(
                f"Social account already exists: workspace={workspace_id} "
                f"platform={data.platform.value} user={data.platform_user_id}"
            )
            raise SocialAccountAlreadyExistsError()

        # Encrypt the sensitive tokens
        access_token_enc = encrypt_secret(data.access_token)
        refresh_token_enc = None
        if data.refresh_token:
            refresh_token_enc = encrypt_secret(data.refresh_token)

        account = await self._sa_repo.create(
            data=data,
            workspace_id=workspace_id,
            access_token_encrypted=access_token_enc,
            refresh_token_encrypted=refresh_token_enc,
        )

        return SocialAccountResponse.model_validate(account)

    # ─────────────────────────────────────────────
    # Read (Single)
    # ─────────────────────────────────────────────

    async def get_social_account(
        self,
        workspace_id: uuid.UUID,
        account_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> SocialAccountResponse:
        """
        Retrieve details for a specific social account.

        Args:
            workspace_id:       UUID of the workspace.
            account_id:         UUID of the social account.
            requesting_user_id: UUID of the authenticated user.

        Raises:
            SocialAccountNotFoundError: If workspace/account does not exist or unauthorized.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        account = await self._sa_repo.get_by_id(account_id)
        if account is None or account.workspace_id != workspace_id:
            raise SocialAccountNotFoundError()

        return SocialAccountResponse.model_validate(account)

    # ─────────────────────────────────────────────
    # Read (List)
    # ─────────────────────────────────────────────

    async def list_social_accounts(
        self,
        workspace_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> list[SocialAccountResponse]:
        """
        List all connected social accounts for the workspace.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        accounts = await self._sa_repo.get_by_workspace_id(workspace_id)
        return [SocialAccountResponse.model_validate(a) for a in accounts]

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_social_account(
        self,
        workspace_id: uuid.UUID,
        account_id: uuid.UUID,
        data: SocialAccountUpdate,
        requesting_user_id: uuid.UUID,
    ) -> SocialAccountResponse:
        """
        Update metadata for a connected social account.
        Token fields are excluded from this flow.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        account = await self._sa_repo.get_by_id(account_id)
        if account is None or account.workspace_id != workspace_id:
            raise SocialAccountNotFoundError()

        updated = await self._sa_repo.update(account, data)
        return SocialAccountResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_social_account(
        self,
        workspace_id: uuid.UUID,
        account_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        """
        Disconnect (delete) a social account.
        """
        await self._assert_workspace_owner(workspace_id, requesting_user_id)

        account = await self._sa_repo.get_by_id(account_id)
        if account is None or account.workspace_id != workspace_id:
            raise SocialAccountNotFoundError()

        await self._sa_repo.delete(account)
