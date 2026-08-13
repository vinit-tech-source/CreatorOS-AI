"""
app/models/post.py

Post model for CreatorOS AI.
Represents a Content Post within a Project.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.social_account import SocialPlatform


class ContentType(str, enum.Enum):
    """Type of the content."""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL = "CAROUSEL"
    THREAD = "THREAD"


class PostStatus(str, enum.Enum):
    """Lifecycle status of a Content Post."""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class Post(Base):
    """
    A Content Post belonging to a Project.
    """
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    content_type: Mapped[ContentType] = mapped_column(
        SAEnum(ContentType, name="contenttype", create_type=True),
        nullable=False,
        default=ContentType.TEXT,
    )

    status: Mapped[PostStatus] = mapped_column(
        SAEnum(PostStatus, name="poststatus", create_type=True),
        nullable=False,
        default=PostStatus.DRAFT,
        index=True,
    )

    platform: Mapped[SocialPlatform] = mapped_column(
        SAEnum(SocialPlatform, name="socialplatform", create_type=True),
        nullable=False,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    external_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project",
        back_populates="posts",
        foreign_keys=[project_id],
        lazy="selectin",
    )
    media_assets: Mapped[list["MediaAsset"]] = relationship(  # noqa: F821
        "MediaAsset", back_populates="post"
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id} project={self.project_id} platform={self.platform.value} status={self.status.value}>"
