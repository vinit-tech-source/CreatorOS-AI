"""create_media_assets_table

Revision ID: 007
Revises: 006
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "media_assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "post_id",
            UUID(as_uuid=True),
            sa.ForeignKey("posts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("storage_url", sa.String(length=1024), nullable=True),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column(
            "media_type",
            sa.Enum(
                "IMAGE", "VIDEO", "GIF", "DOCUMENT",
                name="mediatype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=255), nullable=True),
        sa.Column("alt_text", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("storage_key", name="uq_media_assets_storage_key"),
    )

    op.create_index("ix_media_assets_workspace_id", "media_assets", ["workspace_id"])
    op.create_index("ix_media_assets_post_id", "media_assets", ["post_id"])
    op.create_index("ix_media_assets_media_type", "media_assets", ["media_type"])
    op.create_index("ix_media_assets_created_at", "media_assets", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_media_assets_created_at", table_name="media_assets")
    op.drop_index("ix_media_assets_media_type", table_name="media_assets")
    op.drop_index("ix_media_assets_post_id", table_name="media_assets")
    op.drop_index("ix_media_assets_workspace_id", table_name="media_assets")
    op.drop_table("media_assets")
    
    # Drop enum
    sa.Enum(name="mediatype").drop(op.get_bind(), checkfirst=True)
