"""
app/schemas/brand_kit.py

Pydantic v2 schemas for BrandKit request/response payloads.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class BrandKitCreate(BaseModel):
    """Schema for creating a new Brand Kit."""

    brand_name: str = Field(
        ..., min_length=1, max_length=255, description="Primary brand name."
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Optional brand description."
    )
    website_url: Optional[str] = Field(
        None, max_length=2048, description="Brand website URL."
    )
    logo_url: Optional[str] = Field(
        None, max_length=2048, description="URL to the brand logo image."
    )
    primary_color: Optional[str] = Field(
        None,
        max_length=7,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Primary brand color as a CSS hex code (e.g. '#FF5733').",
    )
    secondary_color: Optional[str] = Field(
        None,
        max_length=7,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Secondary brand color as a CSS hex code.",
    )
    accent_color: Optional[str] = Field(
        None,
        max_length=7,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Accent brand color as a CSS hex code.",
    )
    default_tone: Optional[str] = Field(
        None,
        max_length=100,
        description="Default writing tone (e.g. 'professional', 'friendly', 'witty').",
    )
    target_audience: Optional[str] = Field(
        None, max_length=2000, description="Description of the intended audience."
    )
    brand_values: Optional[str] = Field(
        None, max_length=2000, description="Core brand values or mission statement."
    )
    preferred_language: str = Field(
        "en",
        max_length=10,
        description="BCP-47 language code for preferred content language (e.g. 'en', 'hi').",
    )


class BrandKitUpdate(BaseModel):
    """Schema for partially updating a Brand Kit.

    All fields are optional.

    Note: workspace_id is immutable after creation.

    Null handling:
      - Omitted field  -> left unchanged (exclude_unset semantics in repository)
      - Explicit null  -> clears the nullable field
    """

    brand_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    website_url: Optional[str] = Field(None, max_length=2048)
    logo_url: Optional[str] = Field(None, max_length=2048)
    primary_color: Optional[str] = Field(
        None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    secondary_color: Optional[str] = Field(
        None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    accent_color: Optional[str] = Field(
        None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    default_tone: Optional[str] = Field(None, max_length=100)
    target_audience: Optional[str] = Field(None, max_length=2000)
    brand_values: Optional[str] = Field(None, max_length=2000)
    preferred_language: Optional[str] = Field(None, max_length=10)


# ─────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────

class BrandKitResponse(BaseModel):
    """Full Brand Kit response returned from API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(description="Unique UUID identifier for the Brand Kit.")
    workspace_id: uuid.UUID = Field(description="UUID of the workspace this Brand Kit belongs to.")
    brand_name: str = Field(description="Primary brand name.")
    description: Optional[str] = Field(description="Optional brand description.")
    website_url: Optional[str] = Field(description="Brand website URL.")
    logo_url: Optional[str] = Field(description="URL to the brand logo image.")
    primary_color: Optional[str] = Field(description="Primary brand color (hex).")
    secondary_color: Optional[str] = Field(description="Secondary brand color (hex).")
    accent_color: Optional[str] = Field(description="Accent brand color (hex).")
    default_tone: Optional[str] = Field(description="Default writing tone.")
    target_audience: Optional[str] = Field(description="Target audience description.")
    brand_values: Optional[str] = Field(description="Core brand values.")
    preferred_language: str = Field(description="Preferred content language.")
    created_at: datetime = Field(description="Timestamp when this Brand Kit was created.")
    updated_at: datetime = Field(description="Timestamp when this Brand Kit was last updated.")
