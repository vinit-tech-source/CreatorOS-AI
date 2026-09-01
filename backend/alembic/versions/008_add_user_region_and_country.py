"""add user region and country

Revision ID: 008
Revises: 0e972d71f54b
Create Date: 2026-09-01 19:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, Sequence[str], None] = '0e972d71f54b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'region' not in columns:
        op.add_column('users', sa.Column('region', sa.String(length=100), nullable=True))
    if 'country' not in columns:
        op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'country')
    op.drop_column('users', 'region')
