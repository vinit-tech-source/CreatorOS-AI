import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(100), nullable=False, default="UTC"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
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
    owner: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="workspaces", foreign_keys=[owner_id], lazy="selectin"
    )
    brand_kit: Mapped["BrandKit | None"] = relationship(  # noqa: F821
        "BrandKit", back_populates="workspace", uselist=False, cascade="all, delete-orphan"
    )
    social_accounts: Mapped[list["SocialAccount"]] = relationship(  # noqa: F821
        "SocialAccount", back_populates="workspace", cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(  # noqa: F821
        "Project", back_populates="workspace", cascade="all, delete-orphan"
    )
    media_assets: Mapped[list["MediaAsset"]] = relationship(  # noqa: F821
        "MediaAsset", back_populates="workspace", cascade="all, delete-orphan"
    )
    knowledge_sources: Mapped[list["KnowledgeSource"]] = relationship(  # noqa: F821
        "KnowledgeSource", back_populates="workspace", cascade="all, delete-orphan"
    )
    automation_rules: Mapped[list["AutomationRule"]] = relationship(  # noqa: F821
        "AutomationRule", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workspace id={self.id} slug={self.slug} owner={self.owner_id}>"
