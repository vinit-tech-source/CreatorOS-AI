"""
tests/test_social_account_service.py

Unit tests for SocialAccountService and core.encryption.

All tests use mocked repositories.
Validates business logic, authorization boundaries, information hiding,
and symmetric encryption behavior.
"""
import uuid
import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from cryptography.fernet import Fernet

from app.core.config import settings
from app.core.encryption import (
    EncryptionConfigError,
    EncryptionError,
    decrypt_secret,
    encrypt_secret,
)
from app.core.exceptions import (
    SocialAccountAlreadyExistsError,
    SocialAccountNotFoundError,
)
from app.models.social_account import SocialAccount, SocialPlatform
from app.models.workspace import Workspace
from app.schemas.social_account import SocialAccountCreate, SocialAccountUpdate
from app.services.social_account_service import SocialAccountService

# ─────────────────────────────────────────────
# Test encryption utility
# ─────────────────────────────────────────────

def test_encryption_roundtrip():
    """A secret can be encrypted and decrypted back to the original plaintext."""
    secret = "my-oauth-access-token-123"
    # Temporarily set a valid key for this test
    key = Fernet.generate_key().decode()
    settings.ENCRYPTION_KEY = key
    
    ciphertext = encrypt_secret(secret)
    assert ciphertext != secret
    assert len(ciphertext) > len(secret)
    
    plaintext = decrypt_secret(ciphertext)
    assert plaintext == secret


def test_encryption_missing_key_raises():
    """Missing ENCRYPTION_KEY raises EncryptionConfigError."""
    settings.ENCRYPTION_KEY = ""
    with pytest.raises(EncryptionConfigError):
        encrypt_secret("secret")
    with pytest.raises(EncryptionConfigError):
        decrypt_secret("ciphertext")


def test_encryption_invalid_key_raises():
    """Invalid ENCRYPTION_KEY raises EncryptionConfigError."""
    settings.ENCRYPTION_KEY = "invalid-key-format"
    with pytest.raises(EncryptionConfigError):
        encrypt_secret("secret")
    with pytest.raises(EncryptionConfigError):
        decrypt_secret("ciphertext")


def test_decryption_invalid_ciphertext_raises():
    """Invalid ciphertext raises EncryptionError."""
    settings.ENCRYPTION_KEY = Fernet.generate_key().decode()
    with pytest.raises(EncryptionError):
        decrypt_secret("not-a-valid-fernet-token")


def test_decryption_wrong_key_raises():
    """Ciphertext encrypted with key A cannot be decrypted with key B."""
    key_a = Fernet.generate_key().decode()
    settings.ENCRYPTION_KEY = key_a
    ciphertext = encrypt_secret("secret")

    key_b = Fernet.generate_key().decode()
    settings.ENCRYPTION_KEY = key_b
    with pytest.raises(EncryptionError):
        decrypt_secret(ciphertext)


# ─────────────────────────────────────────────
# Helpers for Service Tests
# ─────────────────────────────────────────────

def make_workspace(owner_id: uuid.UUID | None = None) -> Workspace:
    ws = Workspace()
    ws.id = uuid.uuid4()
    ws.name = "Test Workspace"
    ws.slug = "test-ws"
    ws.owner_id = owner_id or uuid.uuid4()
    return ws


def make_social_account(workspace_id: uuid.UUID | None = None) -> SocialAccount:
    sa = SocialAccount()
    sa.id = uuid.uuid4()
    sa.workspace_id = workspace_id or uuid.uuid4()
    sa.platform = SocialPlatform.X
    sa.account_name = "My X Account"
    sa.platform_user_id = "12345"
    sa.access_token_encrypted = "encrypted_access_token"
    sa.refresh_token_encrypted = None
    sa.token_expires_at = None
    sa.scopes = "read write"
    sa.is_active = True
    sa.connected_at = datetime.now(timezone.utc)
    sa.updated_at = datetime.now(timezone.utc)
    return sa


def make_sa_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_workspace_id = AsyncMock(return_value=[])
    repo.get_by_platform = AsyncMock(return_value=[])
    repo.get_by_platform_user_id = AsyncMock(return_value=None)
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=None)
    return repo


def make_ws_repo(workspace: Workspace | None = None) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=workspace)
    return repo


def make_service(sa_repo: AsyncMock, ws_repo: AsyncMock) -> SocialAccountService:
    return SocialAccountService(social_account_repository=sa_repo, workspace_repository=ws_repo)


# ─────────────────────────────────────────────
# 1. Create Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_social_account_success():
    """Owner can create a social account. Tokens are encrypted and not in response."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    account = make_social_account(workspace_id=workspace.id)

    sa_repo = make_sa_repo()
    sa_repo.get_by_platform_user_id.return_value = None
    sa_repo.create.return_value = account

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    # Set valid key for this test
    settings.ENCRYPTION_KEY = Fernet.generate_key().decode()

    data = SocialAccountCreate(
        platform=SocialPlatform.X,
        account_name="My Account",
        platform_user_id="123",
        access_token="plain-access-token",
        refresh_token="plain-refresh-token",
    )

    result = await service.create_social_account(
        workspace_id=workspace.id,
        data=data,
        requesting_user_id=owner_id,
    )

    # Assert repo called with encrypted tokens, not plaintext
    sa_repo.create.assert_awaited_once()
    _, kwargs = sa_repo.create.call_args
    assert kwargs["access_token_encrypted"] != "plain-access-token"
    assert kwargs["refresh_token_encrypted"] != "plain-refresh-token"
    assert len(kwargs["access_token_encrypted"]) > 20

    # Assert API response model does not contain token fields
    assert not hasattr(result, "access_token")
    assert not hasattr(result, "access_token_encrypted")
    assert not hasattr(result, "refresh_token")
    assert not hasattr(result, "refresh_token_encrypted")


# ─────────────────────────────────────────────
# 2. Get own Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_social_account_owner_succeeds():
    """Owner can retrieve account metadata."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    account = make_social_account(workspace_id=workspace.id)

    sa_repo = make_sa_repo()
    sa_repo.get_by_id.return_value = account

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    result = await service.get_social_account(
        workspace_id=workspace.id,
        account_id=account.id,
        requesting_user_id=owner_id,
    )

    assert result.id == account.id
    assert not hasattr(result, "access_token_encrypted")


# ─────────────────────────────────────────────
# 3. List own Social Accounts
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_social_accounts_owner_succeeds():
    """Owner can list all their social accounts."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    accounts = [make_social_account(workspace_id=workspace.id) for _ in range(3)]

    sa_repo = make_sa_repo()
    sa_repo.get_by_workspace_id.return_value = accounts

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    result = await service.list_social_accounts(
        workspace_id=workspace.id,
        requesting_user_id=owner_id,
    )

    assert len(result) == 3


# ─────────────────────────────────────────────
# 4. Get another user's Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_social_account_non_owner_raises_not_found():
    """A non-owner receives 404 (info hiding)."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    sa_repo = make_sa_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    with pytest.raises(SocialAccountNotFoundError):
        await service.get_social_account(
            workspace_id=workspace.id,
            account_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )

    sa_repo.get_by_id.assert_not_awaited()


# ─────────────────────────────────────────────
# 5. Update own Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_social_account_owner_succeeds():
    """Owner can update account metadata."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    original = make_social_account(workspace_id=workspace.id)
    updated = make_social_account(workspace_id=workspace.id)
    updated.account_name = "New Name"

    sa_repo = make_sa_repo()
    sa_repo.get_by_id.return_value = original
    sa_repo.update.return_value = updated

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    result = await service.update_social_account(
        workspace_id=workspace.id,
        account_id=original.id,
        data=SocialAccountUpdate(account_name="New Name"),
        requesting_user_id=owner_id,
    )

    sa_repo.update.assert_awaited_once()
    assert result.account_name == "New Name"


# ─────────────────────────────────────────────
# 6. Update another user's Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_social_account_non_owner_raises():
    """Non-owner receives 404 when trying to update."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    sa_repo = make_sa_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    with pytest.raises(SocialAccountNotFoundError):
        await service.update_social_account(
            workspace_id=workspace.id,
            account_id=uuid.uuid4(),
            data=SocialAccountUpdate(account_name="Hacked"),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# 7. Delete own Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_social_account_owner_succeeds():
    """Owner can delete social account."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    account = make_social_account(workspace_id=workspace.id)

    sa_repo = make_sa_repo()
    sa_repo.get_by_id.return_value = account

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    await service.delete_social_account(
        workspace_id=workspace.id,
        account_id=account.id,
        requesting_user_id=owner_id,
    )

    sa_repo.delete.assert_awaited_once_with(account)


# ─────────────────────────────────────────────
# 8. Delete another user's Social Account
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_social_account_non_owner_raises():
    """Non-owner receives 404 when trying to delete."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    sa_repo = make_sa_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    with pytest.raises(SocialAccountNotFoundError):
        await service.delete_social_account(
            workspace_id=workspace.id,
            account_id=uuid.uuid4(),
            requesting_user_id=attacker_id,
        )


# ─────────────────────────────────────────────
# 9. Duplicate Platform Account Rejected
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_social_account_duplicate_raises():
    """Connecting the same platform user twice raises 409."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    account = make_social_account(workspace_id=workspace.id)

    sa_repo = make_sa_repo()
    sa_repo.get_by_platform_user_id.return_value = account  # Already exists

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(sa_repo, ws_repo)

    data = SocialAccountCreate(
        platform=SocialPlatform.X,
        account_name="My Account",
        platform_user_id="12345",
        access_token="token",
    )

    with pytest.raises(SocialAccountAlreadyExistsError):
        await service.create_social_account(
            workspace_id=workspace.id,
            data=data,
            requesting_user_id=owner_id,
        )

    sa_repo.create.assert_not_awaited()
