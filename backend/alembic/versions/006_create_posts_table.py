"""create_posts_table

Revision ID: 006
Revises: 005
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "content_type",
            sa.Enum(
                "TEXT", "IMAGE", "VIDEO", "CAROUSEL", "THREAD",
                name="contenttype",
                create_type=False,
            ),
            nullable=False,
            server_default="TEXT",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT", "PENDING_REVIEW", "APPROVED", "SCHEDULED", "PUBLISHED", "FAILED", "ARCHIVED",
                name="poststatus",
                create_type=False,
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column(
            "platform",
            sa.Enum(
                "X", "LINKEDIN", "INSTAGRAM", "FACEBOOK", "THREADS",
                name="socialplatform",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_post_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_index("ix_posts_project_id", "posts", ["project_id"])
    op.create_index("ix_posts_status", "posts", ["status"])
    op.create_index("ix_posts_platform", "posts", ["platform"])
    op.create_index("ix_posts_scheduled_at", "posts", ["scheduled_at"])


def downgrade() -> None:
    op.drop_index("ix_posts_scheduled_at", table_name="posts")
    op.drop_index("ix_posts_platform", table_name="posts")
    op.drop_index("ix_posts_status", table_name="posts")
    op.drop_index("ix_posts_project_id", table_name="posts")
    op.drop_table("posts")
