"""
app/models/social_account.py

SocialAccount model for CreatorOS AI.

Stores the OAuth credentials for a connected social media account, belonging
to a Workspace. Tokens are stored encrypted; this model never exposes plaintext
token values.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SocialPlatform(str, enum.Enum):
    """Supported social media platforms."""
    X = "X"
    LINKEDIN = "LINKEDIN"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    THREADS = "THREADS"
    BLUESKY = "BLUESKY"


class SocialAccount(Base):
    """
    A connected social media account belonging to a Workspace.

    SECURITY: access_token_encrypted and refresh_token_encrypted store
    Fernet-encrypted ciphertext only. Plaintext tokens must never appear
    in this model, its logs, or any API response.
    """
    __tablename__ = "social_accounts"

    # One workspace cannot connect the same platform account twice
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "platform",
            "platform_user_id",
            name="uq_social_account_workspace_platform_user",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Platform identity
    platform: Mapped[SocialPlatform] = mapped_column(
        SAEnum(SocialPlatform, name="socialplatform", create_type=True),
        nullable=False,
        index=True,
    )
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # OAuth tokens — stored encrypted, never plaintext
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Token metadata
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
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
        back_populates="social_accounts",
        foreign_keys=[workspace_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        # NOTE: no token values in __repr__
        return (
            f"<SocialAccount id={self.id} platform={self.platform.value} "
            f"workspace={self.workspace_id}>"
        )
