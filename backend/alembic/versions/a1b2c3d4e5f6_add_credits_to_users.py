"""Add credits column to users table

Revision ID: a1b2c3d4e5f6
Revises: 503a4262653c
Create Date: 2026-08-06 08:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str | Sequence[str] | None = '503a4262653c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add missing credits column to users table."""
    # Use op.execute for safety - only adds if column doesn't already exist
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS credits INTEGER NOT NULL DEFAULT 100;
    """)


def downgrade() -> None:
    """Remove credits column from users table."""
    op.drop_column('users', 'credits')
