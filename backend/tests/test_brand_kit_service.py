"""
tests/test_brand_kit_service.py

Unit tests for BrandKitService.

All tests use mocked repositories — no database or network connections required.
The tests validate:
  - Business logic (one Brand Kit per workspace, workspace ownership)
  - Authorization boundaries (owner-only CRUD)
  - Information hiding (non-ownership returns 404, not 403)
  - Null field clearing via explicit null in update
  - Unauthenticated access rejected at the security layer
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    BrandKitAlreadyExistsError,
    BrandKitNotFoundError,
)
from app.models.brand_kit import BrandKit
from app.models.workspace import Workspace
from app.schemas.brand_kit import BrandKitCreate, BrandKitUpdate
from app.services.brand_kit_service import BrandKitService


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_workspace(owner_id: uuid.UUID | None = None) -> Workspace:
    """Return a minimal Workspace ORM object."""
    ws = Workspace()
    ws.id = uuid.uuid4()
    ws.name = "Test Workspace"
    ws.slug = "test-workspace"
    ws.description = None
    ws.logo_url = None
    ws.timezone = "UTC"
    ws.is_active = True
    ws.owner_id = owner_id or uuid.uuid4()
    ws.created_at = datetime.now(timezone.utc)
    ws.updated_at = datetime.now(timezone.utc)
    return ws


def make_brand_kit(workspace_id: uuid.UUID | None = None) -> BrandKit:
    """Return a minimal BrandKit ORM object."""
    bk = BrandKit()
    bk.id = uuid.uuid4()
    bk.workspace_id = workspace_id or uuid.uuid4()
    bk.brand_name = "Test Brand"
    bk.description = "A great brand."
    bk.website_url = "https://example.com"
    bk.logo_url = "https://example.com/logo.png"
    bk.primary_color = "#FF5733"
    bk.secondary_color = None
    bk.accent_color = None
    bk.default_tone = "professional"
    bk.target_audience = "Small businesses"
    bk.brand_values = "Innovation, Quality"
    bk.preferred_language = "en"
    bk.created_at = datetime.now(timezone.utc)
    bk.updated_at = datetime.now(timezone.utc)
    return bk


def make_bk_repo() -> AsyncMock:
    """Return a mock AbstractBrandKitRepository with safe defaults."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_workspace_id = AsyncMock(return_value=None)
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=None)
    return repo


def make_ws_repo(workspace: Workspace | None = None) -> AsyncMock:
    """Return a mock AbstractWorkspaceRepository with safe defaults."""
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=workspace)
    repo.get_by_slug = AsyncMock(return_value=None)
    repo.list_by_owner = AsyncMock(return_value=[])
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=None)
    return repo


def make_service(bk_repo: AsyncMock, ws_repo: AsyncMock) -> BrandKitService:
    return BrandKitService(brand_kit_repository=bk_repo, workspace_repository=ws_repo)


def make_create_data(**kwargs) -> BrandKitCreate:
    defaults = {"brand_name": "My Brand", "preferred_language": "en"}
    defaults.update(kwargs)
    return BrandKitCreate(**defaults)


# ─────────────────────────────────────────────
# 1. Create Brand Kit — success
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_brand_kit_success():
    """Owner can create a Brand Kit for their workspace."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    brand_kit = make_brand_kit(workspace_id=workspace.id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = None  # no existing Brand Kit
    bk_repo.create.return_value = brand_kit

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    data = make_create_data(brand_name="My Brand", primary_color="#FF5733")
    result = await service.create_brand_kit(
        workspace_id=workspace.id,
        data=data,
        requesting_user_id=owner_id,
    )

    bk_repo.create.assert_awaited_once_with(data, workspace.id)
    assert result.workspace_id == workspace.id
    assert result.brand_name == brand_kit.brand_name


# ─────────────────────────────────────────────
# 2. Get own Brand Kit — success
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_brand_kit_owner_succeeds():
    """The workspace owner can retrieve the Brand Kit."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    brand_kit = make_brand_kit(workspace_id=workspace.id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = brand_kit

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    result = await service.get_brand_kit(
        workspace_id=workspace.id,
        requesting_user_id=owner_id,
    )

    assert result.id == brand_kit.id
    assert result.workspace_id == workspace.id


# ─────────────────────────────────────────────
# 3. Get another user's Brand Kit — rejected
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_brand_kit_non_owner_raises_not_found():
    """A non-owner gets BrandKitNotFoundError (404) — not a 403."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    bk_repo = make_bk_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.get_brand_kit(
            workspace_id=workspace.id,
            requesting_user_id=attacker_id,
        )

    # Brand Kit repo must NOT have been queried — access denied at workspace check
    bk_repo.get_by_workspace_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_brand_kit_non_existent_workspace_raises_not_found():
    """Accessing a Brand Kit for a non-existent workspace returns 404."""
    bk_repo = make_bk_repo()
    ws_repo = make_ws_repo(workspace=None)  # workspace does not exist
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.get_brand_kit(
            workspace_id=uuid.uuid4(),
            requesting_user_id=uuid.uuid4(),
        )


# ─────────────────────────────────────────────
# 4. Update own Brand Kit — success
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_brand_kit_owner_succeeds():
    """The workspace owner can update the Brand Kit."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    original = make_brand_kit(workspace_id=workspace.id)

    updated_bk = make_brand_kit(workspace_id=workspace.id)
    updated_bk.id = original.id
    updated_bk.brand_name = "Updated Brand"

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = original
    bk_repo.update.return_value = updated_bk

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    data = BrandKitUpdate(brand_name="Updated Brand")
    result = await service.update_brand_kit(
        workspace_id=workspace.id,
        data=data,
        requesting_user_id=owner_id,
    )

    bk_repo.update.assert_awaited_once_with(original, data)
    assert result.brand_name == "Updated Brand"


# ─────────────────────────────────────────────
# 5. Update another user's Brand Kit — rejected
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_brand_kit_non_owner_raises():
    """A non-owner cannot update another user's Brand Kit."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    bk_repo = make_bk_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.update_brand_kit(
            workspace_id=workspace.id,
            data=BrandKitUpdate(brand_name="Hacked"),
            requesting_user_id=attacker_id,
        )

    bk_repo.update.assert_not_awaited()


# ─────────────────────────────────────────────
# 6. Delete own Brand Kit — success
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_brand_kit_owner_succeeds():
    """The workspace owner can delete the Brand Kit."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    brand_kit = make_brand_kit(workspace_id=workspace.id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = brand_kit

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    await service.delete_brand_kit(
        workspace_id=workspace.id,
        requesting_user_id=owner_id,
    )

    bk_repo.delete.assert_awaited_once_with(brand_kit)


# ─────────────────────────────────────────────
# 7. Delete another user's Brand Kit — rejected
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_brand_kit_non_owner_raises():
    """A non-owner cannot delete another user's Brand Kit."""
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    bk_repo = make_bk_repo()
    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.delete_brand_kit(
            workspace_id=workspace.id,
            requesting_user_id=attacker_id,
        )

    bk_repo.delete.assert_not_awaited()


# ─────────────────────────────────────────────
# 8. Duplicate Brand Kit — rejected
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_brand_kit_duplicate_raises():
    """Creating a second Brand Kit for the same workspace raises BrandKitAlreadyExistsError."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    existing_bk = make_brand_kit(workspace_id=workspace.id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = existing_bk  # already exists

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitAlreadyExistsError):
        await service.create_brand_kit(
            workspace_id=workspace.id,
            data=make_create_data(),
            requesting_user_id=owner_id,
        )

    bk_repo.create.assert_not_awaited()


# ─────────────────────────────────────────────
# 9. Explicit null clears nullable field
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_brand_kit_explicit_null_clears_field():
    """Sending logo_url=null explicitly clears the field."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)
    original = make_brand_kit(workspace_id=workspace.id)
    original.logo_url = "https://example.com/logo.png"

    cleared = make_brand_kit(workspace_id=workspace.id)
    cleared.id = original.id
    cleared.logo_url = None

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = original
    bk_repo.update.return_value = cleared

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    update_data = BrandKitUpdate(logo_url=None)
    result = await service.update_brand_kit(
        workspace_id=workspace.id,
        data=update_data,
        requesting_user_id=owner_id,
    )

    bk_repo.update.assert_awaited_once_with(original, update_data)
    assert result.logo_url is None


@pytest.mark.asyncio
async def test_update_brand_kit_omitted_field_unchanged():
    """Omitting a field from the update payload leaves it unchanged in the model dump."""
    # BrandKitUpdate with no fields set should produce an empty model_dump(exclude_unset=True)
    empty_update = BrandKitUpdate()
    dumped = empty_update.model_dump(exclude_unset=True)
    assert dumped == {}, f"Expected empty dict for omitted fields, got: {dumped}"


# ─────────────────────────────────────────────
# 10. Unauthenticated access — JWT layer
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_jwt_token_rejected():
    """
    An invalid JWT is rejected before reaching any service method.
    Validates the decode_access_token security guard directly.
    """
    from app.core.security import decode_access_token

    with pytest.raises(Exception):
        decode_access_token("not.a.valid.jwt")


# ─────────────────────────────────────────────
# 11. Additional edge cases
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_brand_kit_no_brand_kit_raises():
    """get_brand_kit raises BrandKitNotFoundError when workspace has no Brand Kit."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = None  # no Brand Kit yet

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.get_brand_kit(
            workspace_id=workspace.id,
            requesting_user_id=owner_id,
        )


@pytest.mark.asyncio
async def test_update_brand_kit_no_brand_kit_raises():
    """update_brand_kit raises BrandKitNotFoundError when workspace has no Brand Kit."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = None

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.update_brand_kit(
            workspace_id=workspace.id,
            data=BrandKitUpdate(brand_name="X"),
            requesting_user_id=owner_id,
        )


@pytest.mark.asyncio
async def test_delete_brand_kit_no_brand_kit_raises():
    """delete_brand_kit raises BrandKitNotFoundError when workspace has no Brand Kit."""
    owner_id = uuid.uuid4()
    workspace = make_workspace(owner_id=owner_id)

    bk_repo = make_bk_repo()
    bk_repo.get_by_workspace_id.return_value = None

    ws_repo = make_ws_repo(workspace=workspace)
    service = make_service(bk_repo, ws_repo)

    with pytest.raises(BrandKitNotFoundError):
        await service.delete_brand_kit(
            workspace_id=workspace.id,
            requesting_user_id=owner_id,
        )
