"""create_social_accounts_table

Revision ID: 004
Revises: 003
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "social_accounts",
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
        # Platform Enum (SQLAlchemy 2.0 Enum maps to VARCHAR in simple setups,
        # but we use a native ENUM if configured. We'll use VARCHAR for max compatibility
        # if create_type isn't fully executing, but Alembic usually handles this).
        sa.Column(
            "platform",
            sa.Enum(
                "X", "LINKEDIN", "INSTAGRAM", "FACEBOOK", "THREADS",
                name="socialplatform",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("account_name", sa.String(255), nullable=False),
        sa.Column("platform_user_id", sa.String(255), nullable=False),
        # Encrypted Tokens
        sa.Column("access_token_encrypted", sa.Text(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        # Token Metadata
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.Text(), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        # Timestamps
        sa.Column(
            "connected_at",
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

    # Indexes
    op.create_index("ix_social_accounts_workspace_id", "social_accounts", ["workspace_id"])
    op.create_index("ix_social_accounts_platform", "social_accounts", ["platform"])
    op.create_index("ix_social_accounts_platform_user_id", "social_accounts", ["platform_user_id"])

    # Composite Unique Constraint: One account per platform per workspace
    op.create_unique_constraint(
        "uq_social_account_workspace_platform_user",
        "social_accounts",
        ["workspace_id", "platform", "platform_user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_social_account_workspace_platform_user", "social_accounts", type_="unique"
    )
    op.drop_index("ix_social_accounts_platform_user_id", table_name="social_accounts")
    op.drop_index("ix_social_accounts_platform", table_name="social_accounts")
    op.drop_index("ix_social_accounts_workspace_id", table_name="social_accounts")
    op.drop_table("social_accounts")
