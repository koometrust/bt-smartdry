"""add_avoided_loss_to_batches

Revision ID: 0002_add_avoided_loss_to_batches
Revises: 0001_initial_schema
Create Date: 2026-11-20 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0002_add_avoided_loss_to_batches'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('batches', sa.Column('avoided_loss_kg', sa.Float(), nullable=True))
    op.add_column('batches', sa.Column('avoided_loss_kes', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('batches', 'avoided_loss_kes')
    op.drop_column('batches', 'avoided_loss_kg')

