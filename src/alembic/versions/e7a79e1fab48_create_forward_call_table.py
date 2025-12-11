"""create history table

Revision ID: e7a79e1fab48
Revises: 
Create Date: 2025-12-11 14:02:41.398358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a79e1fab48'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "forward_call",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("start_time", sa.DateTime, nullable=False),
        sa.Column("finish_time", sa.DateTime, nullable=False)
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
