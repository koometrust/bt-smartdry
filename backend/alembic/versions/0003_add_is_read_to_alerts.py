"""add_is_read_to_alerts

Revision ID: 0003_add_is_read_to_alerts
Revises: 0002_add_avoided_loss_to_batches
Create Date: 2026-11-20 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0003_add_is_read_to_alerts'
down_revision: Union[str, None] = '0002_add_avoided_loss_to_batches'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('alerts', 'is_read')

