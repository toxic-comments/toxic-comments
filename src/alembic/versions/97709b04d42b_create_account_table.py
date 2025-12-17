"""create account table

Revision ID: 97709b04d42b
Revises: e7a79e1fab48
Create Date: 2025-12-17 18:19:14.865248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97709b04d42b'
down_revision: Union[str, Sequence[str], None] = 'e7a79e1fab48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('forward_call', sa.Column('message', sa.Text, nullable=False, server_default=''))
    op.add_column('forward_call', sa.Column('result', sa.String, nullable=False, server_default='pending'))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('forward_call', 'message')
    op.drop_column('forward_call', 'result')
