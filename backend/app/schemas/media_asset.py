"""
app/schemas/media_asset.py

Pydantic v2 schemas for Media Asset request/response payloads.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.media_asset import MediaType


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class MediaAssetCreate(BaseModel):
    """Schema for creating a new Media Asset record."""

    post_id: Optional[uuid.UUID] = Field(None, description="Optional associated post.")
    file_name: str = Field(..., min_length=1, max_length=255, description="Original filename.")
    storage_key: str = Field(..., min_length=1, max_length=1024, description="Storage provider key.")
    storage_url: Optional[str] = Field(None, max_length=1024, description="Public or presigned URL.")
    mime_type: str = Field(..., min_length=1, max_length=255, description="MIME type.")
    media_type: MediaType = Field(..., description="Classification of the media.")
    file_size: int = Field(..., gt=0, description="Size in bytes. Must be positive.")
    width: Optional[int] = Field(None, gt=0, description="Width in pixels.")
    height: Optional[int] = Field(None, gt=0, description="Height in pixels.")
    duration_seconds: Optional[int] = Field(None, gt=0, description="Duration in seconds.")
    checksum: Optional[str] = Field(None, max_length=255, description="File checksum (e.g., md5 or sha256).")
    alt_text: Optional[str] = Field(None, description="Accessibility text.")


class MediaAssetUpdate(BaseModel):
    """Schema for partially updating a Media Asset.

    All fields are optional.
    Null handling:
      - Omitted field  -> left unchanged (exclude_unset semantics in repository)
      - Explicit null  -> clears the nullable field
    """

    post_id: Optional[uuid.UUID] = Field(None)
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    storage_key: Optional[str] = Field(None, min_length=1, max_length=1024)
    storage_url: Optional[str] = Field(None, max_length=1024)
    mime_type: Optional[str] = Field(None, min_length=1, max_length=255)
    media_type: Optional[MediaType] = Field(None)
    file_size: Optional[int] = Field(None, gt=0)
    width: Optional[int] = Field(None, gt=0)
    height: Optional[int] = Field(None, gt=0)
    duration_seconds: Optional[int] = Field(None, gt=0)
    checksum: Optional[str] = Field(None, max_length=255)
    alt_text: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


# ─────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────

class MediaAssetResponse(BaseModel):
    """Full MediaAsset response returned from API endpoints.
    
    Safe metadata only. No raw credentials.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    post_id: Optional[uuid.UUID]
    file_name: str
    storage_key: str
    storage_url: Optional[str]
    mime_type: str
    media_type: MediaType
    file_size: int
    width: Optional[int]
    height: Optional[int]
    duration_seconds: Optional[int]
    checksum: Optional[str]
    alt_text: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
