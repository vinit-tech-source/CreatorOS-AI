"""
app/api/brand_kit.py

Brand Kit API endpoints for CreatorOS AI.

Brand Kits are nested under their parent Workspace resource.
All endpoints enforce workspace ownership via the service layer.

Endpoints:
  POST   /api/v1/workspaces/{workspace_id}/brand-kit   - Create Brand Kit
  GET    /api/v1/workspaces/{workspace_id}/brand-kit   - Get Brand Kit
  PATCH  /api/v1/workspaces/{workspace_id}/brand-kit   - Update Brand Kit
  DELETE /api/v1/workspaces/{workspace_id}/brand-kit   - Delete Brand Kit
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_brand_kit_service, get_current_user_id
from app.schemas.brand_kit import BrandKitCreate, BrandKitResponse, BrandKitUpdate
from app.schemas.response import ApiResponse
from app.services.brand_kit_service import BrandKitService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/brand-kit",
    tags=["Brand Kit"],
)


# ─────────────────────────────────────────────
# POST /workspaces/{workspace_id}/brand-kit
# ─────────────────────────────────────────────

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[BrandKitResponse],
    summary="Create Brand Kit",
    description=(
        "Create a Brand Kit for the specified workspace. "
        "Only the workspace owner can perform this action. "
        "Returns **409** if a Brand Kit already exists for this workspace. "
        "Returns **404** if the workspace does not exist or is not owned by the caller."
    ),
)
async def create_brand_kit(
    workspace_id: uuid.UUID,
    data: BrandKitCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    brand_kit_service: BrandKitService = Depends(get_brand_kit_service),
) -> ApiResponse[BrandKitResponse]:
    brand_kit = await brand_kit_service.create_brand_kit(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=brand_kit, message="Brand Kit created successfully.")


# ─────────────────────────────────────────────
# GET /workspaces/{workspace_id}/brand-kit
# ─────────────────────────────────────────────

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[BrandKitResponse],
    summary="Get Brand Kit",
    description=(
        "Retrieve the Brand Kit for the specified workspace. "
        "Only the workspace owner can perform this action. "
        "Returns **404** if the workspace or Brand Kit does not exist, "
        "or if the workspace is not owned by the caller."
    ),
)
async def get_brand_kit(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    brand_kit_service: BrandKitService = Depends(get_brand_kit_service),
) -> ApiResponse[BrandKitResponse]:
    brand_kit = await brand_kit_service.get_brand_kit(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=brand_kit)


# ─────────────────────────────────────────────
# PATCH /workspaces/{workspace_id}/brand-kit
# ─────────────────────────────────────────────

@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[BrandKitResponse],
    summary="Update Brand Kit",
    description=(
        "Apply partial updates to the workspace's Brand Kit. "
        "Only the workspace owner can perform this action. "
        "Omitted fields are left unchanged. "
        "Send an explicit null to clear a nullable field (e.g. logo_url). "
        "Returns **404** if the workspace or Brand Kit does not exist, "
        "or if the workspace is not owned by the caller."
    ),
)
async def update_brand_kit(
    workspace_id: uuid.UUID,
    data: BrandKitUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    brand_kit_service: BrandKitService = Depends(get_brand_kit_service),
) -> ApiResponse[BrandKitResponse]:
    brand_kit = await brand_kit_service.update_brand_kit(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=brand_kit, message="Brand Kit updated successfully.")


# ─────────────────────────────────────────────
# DELETE /workspaces/{workspace_id}/brand-kit
# ─────────────────────────────────────────────

@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Brand Kit",
    description=(
        "Permanently delete the workspace's Brand Kit. "
        "Only the workspace owner can perform this action. "
        "Returns **404** if the workspace or Brand Kit does not exist, "
        "or if the workspace is not owned by the caller."
    ),
)
async def delete_brand_kit(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    brand_kit_service: BrandKitService = Depends(get_brand_kit_service),
) -> ApiResponse[None]:
    await brand_kit_service.delete_brand_kit(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Brand Kit deleted successfully.")
