"""
app/api/media.py

Media Asset API endpoints for CreatorOS AI.
"""
import hashlib
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import get_current_user_id, get_media_asset_service
from app.integrations.storage.local_provider import LocalStorageProvider
from app.models.media_asset import MediaType
from app.schemas.media_asset import (
    MediaAssetCreate,
    MediaAssetResponse,
    MediaAssetUpdate,
)
from app.schemas.response import ApiResponse
from app.services.media_asset_service import MediaAssetService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/media",
    tags=["Media Assets"],
)


def _infer_media_type(mime_type: str) -> MediaType:
    """Infer MediaType enum from a MIME type string."""
    mime = mime_type.lower()
    if mime.startswith("image/gif"):
        return MediaType.GIF
    if mime.startswith("image/"):
        return MediaType.IMAGE
    if mime.startswith("video/"):
        return MediaType.VIDEO
    if mime in ("application/pdf", "text/plain", "application/msword"):
        return MediaType.DOCUMENT
    return MediaType.DOCUMENT


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
    limit: int = 50,
    offset: int = 0,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[list[MediaAssetResponse]]:
    medias = await service.list_media_assets(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
        limit=limit,
        offset=offset,
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


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[MediaAssetResponse],
    summary="Upload Media File",
    description=(
        "Upload a binary file (image, video, GIF, document) to the workspace. "
        "The file is stored on the server and a MediaAsset record is returned."
    ),
)
async def upload_media_file(
    workspace_id: uuid.UUID,
    file: UploadFile = File(..., description="The file to upload."),
    post_id: Optional[uuid.UUID] = Form(None, description="Optionally link to a post."),
    alt_text: Optional[str] = Form(None, description="Accessibility alt text."),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: MediaAssetService = Depends(get_media_asset_service),
) -> ApiResponse[MediaAssetResponse]:
    """
    Accepts a multipart file upload, saves it to local storage, then
    creates a MediaAsset DB record with full metadata resolved server-side.
    """
    # Validate MIME type early to give a clear error
    mime_type = file.content_type or "application/octet-stream"
    allowed_prefixes = ("image/", "video/", "application/pdf", "text/plain")
    if not any(mime_type.startswith(p) for p in allowed_prefixes):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported MIME type: {mime_type}. Allowed: image/*, video/*, PDF, plain text.",
        )

    # Read file content
    file_data = await file.read()
    file_size = len(file_data)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Compute checksum for deduplication / integrity
    checksum = hashlib.sha256(file_data).hexdigest()

    # Save to storage
    storage = LocalStorageProvider()
    storage_key = await storage.upload(
        file_data=file_data,
        file_name=file.filename or "upload",
        mime_type=mime_type,
    )
    storage_url = await storage.get_url(storage_key)

    # Build the create schema with all metadata resolved
    create_data = MediaAssetCreate(
        post_id=post_id,
        file_name=file.filename or "upload",
        storage_key=storage_key,
        storage_url=storage_url,
        mime_type=mime_type,
        media_type=_infer_media_type(mime_type),
        file_size=file_size,
        checksum=checksum,
        alt_text=alt_text,
    )

    media = await service.create_media_asset(
        workspace_id=workspace_id,
        data=create_data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=media, message="File uploaded successfully.")
