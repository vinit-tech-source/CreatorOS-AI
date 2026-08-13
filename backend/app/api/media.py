"""
app/api/media.py

Media Asset API endpoints for CreatorOS AI.
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_media_asset_service
from app.schemas.response import ApiResponse
from app.schemas.media_asset import (
    MediaAssetCreate,
    MediaAssetResponse,
    MediaAssetUpdate,
)
from app.services.media_asset_service import MediaAssetService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/media",
    tags=["Media Assets"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[MediaAssetResponse],
    summary="Create Media Asset",
    description="Create a new Media Asset record within a workspace.",
)
async def create_media_asset(
    workspace_id: uuid.UUID,
    data: MediaAssetCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[MediaAssetResponse]:
    media = await service.create_media_asset(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=media, message="Media asset created successfully.")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[MediaAssetResponse]],
    summary="List Media Assets",
    description="List all Media Assets in the workspace.",
)
async def list_media_assets(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[list[MediaAssetResponse]]:
    medias = await service.list_media_assets(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=medias)


@router.get(
    "/{media_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[MediaAssetResponse],
    summary="Get Media Asset",
    description="Retrieve details of a specific Media Asset.",
)
async def get_media_asset(
    workspace_id: uuid.UUID,
    media_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[MediaAssetResponse]:
    media = await service.get_media_asset(
        workspace_id=workspace_id,
        media_id=media_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=media)


@router.patch(
    "/{media_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[MediaAssetResponse],
    summary="Update Media Asset",
    description="Apply partial updates to a Media Asset.",
)
async def update_media_asset(
    workspace_id: uuid.UUID,
    media_id: uuid.UUID,
    data: MediaAssetUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[MediaAssetResponse]:
    media = await service.update_media_asset(
        workspace_id=workspace_id,
        media_id=media_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=media, message="Media asset updated successfully.")


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Media Asset",
    description="Permanently delete a Media Asset.",
)
async def delete_media_asset(
    workspace_id: uuid.UUID,
    media_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[None]:
    await service.delete_media_asset(
        workspace_id=workspace_id,
        media_id=media_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Media asset deleted successfully.")
