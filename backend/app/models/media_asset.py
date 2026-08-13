"""
app/models/media_asset.py

MediaAsset model for CreatorOS AI.
Represents a media file (image, video, etc.) uploaded to a Workspace.
Can optionally be linked to a Post.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MediaType(str, enum.Enum):
    """Type of the media asset."""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    GIF = "GIF"
    DOCUMENT = "DOCUMENT"


class MediaAsset(Base):
    """
    A Media Asset belonging to a Workspace.
    """
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    storage_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)

    media_type: Mapped[MediaType] = mapped_column(
        SAEnum(MediaType, name="mediatype", create_type=True),
        nullable=False,
        index=True,
    )

    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(  # noqa: F821
        "Workspace",
        back_populates="media_assets",
        foreign_keys=[workspace_id],
        lazy="selectin",
    )
    post: Mapped["Post | None"] = relationship(  # noqa: F821
        "Post",
        back_populates="media_assets",
        foreign_keys=[post_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<MediaAsset id={self.id} workspace={self.workspace_id} type={self.media_type.value}>"
