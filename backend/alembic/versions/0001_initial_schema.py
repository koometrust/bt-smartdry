"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'hubs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('dryer_capacity_kg', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hubs_name'), 'hubs', ['name'], unique=True)

    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('hub_id', sa.Uuid(), nullable=True),
        sa.Column('preferred_language', sa.String(length=10), nullable=False),
        sa.Column('phone_number', sa.String(length=30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['hub_id'], ['hubs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'batches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('hub_id', sa.Uuid(), nullable=False),
        sa.Column('crop_type', sa.String(length=50), nullable=False),
        sa.Column('initial_weight_kg', sa.Float(), nullable=False),
        sa.Column('target_moisture_pct', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_user_id', sa.Uuid(), nullable=True),
        sa.Column('predicted_remaining_hours', sa.Float(), nullable=True),
        sa.Column('predicted_quality_grade', sa.String(length=20), nullable=True),
        sa.Column('latest_advisory', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['hub_id'], ['hubs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batches_hub_id'), 'batches', ['hub_id'], unique=False)
    op.create_index(op.f('ix_batches_status'), 'batches', ['status'], unique=False)

    op.create_table(
        'readings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('batch_id', sa.Uuid(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('vpd', sa.Float(), nullable=False),
        sa.Column('current_moisture', sa.Float(), nullable=False),
        sa.Column('ambient_temperature', sa.Float(), nullable=False),
        sa.Column('ambient_humidity', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_readings_batch_id'), 'readings', ['batch_id'], unique=False)
    op.create_index(op.f('ix_readings_timestamp'), 'readings', ['timestamp'], unique=False)

    op.create_table(
        'alerts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('batch_id', sa.Uuid(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('phone_number', sa.String(length=30), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_id', 'alert_type', name='uq_batch_alert_type')
    )
    op.create_index(op.f('ix_alerts_batch_id'), 'alerts', ['batch_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alerts_batch_id'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_readings_timestamp'), table_name='readings')
    op.drop_index(op.f('ix_readings_batch_id'), table_name='readings')
    op.drop_table('readings')
    op.drop_index(op.f('ix_batches_status'), table_name='batches')
    op.drop_index(op.f('ix_batches_hub_id'), table_name='batches')
    op.drop_table('batches')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_hubs_name'), table_name='hubs')
    op.drop_table('hubs')

