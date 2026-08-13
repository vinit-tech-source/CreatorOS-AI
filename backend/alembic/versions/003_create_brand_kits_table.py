"""create_brand_kits_table

Revision ID: 003
Revises: 002
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "brand_kits",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Brand identity
        sa.Column("brand_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(2048), nullable=True),
        sa.Column("logo_url", sa.String(2048), nullable=True),
        # Brand colors
        sa.Column("primary_color", sa.String(7), nullable=True),
        sa.Column("secondary_color", sa.String(7), nullable=True),
        sa.Column("accent_color", sa.String(7), nullable=True),
        # Content/AI parameters
        sa.Column("default_tone", sa.String(100), nullable=True),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("brand_values", sa.Text(), nullable=True),
        sa.Column(
            "preferred_language",
            sa.String(10),
            nullable=False,
            server_default="en",
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # One Brand Kit per Workspace — unique constraint on workspace_id
    op.create_unique_constraint(
        "uq_brand_kits_workspace_id", "brand_kits", ["workspace_id"]
    )

    # Index for fast workspace-based lookups
    op.create_index(
        "ix_brand_kits_workspace_id", "brand_kits", ["workspace_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_brand_kits_workspace_id", table_name="brand_kits")
    op.drop_constraint("uq_brand_kits_workspace_id", "brand_kits", type_="unique")
    op.drop_table("brand_kits")
