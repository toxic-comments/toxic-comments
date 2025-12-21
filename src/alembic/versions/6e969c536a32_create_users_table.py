"""create users table

Revision ID: 6e969c536a32
Revises: 97709b04d42b
Create Date: 2025-12-21 18:00:30.440726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e969c536a32'
down_revision: Union[str, Sequence[str], None] = '97709b04d42b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
    "users",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("username", sa.String(length=100), nullable=False),
    sa.Column("password_hash", sa.String(length=255), nullable=False),
    sa.Column("role", sa.String(length=50), nullable=False),
    sa.UniqueConstraint("username"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
