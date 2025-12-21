"""Initial migration - create refuelings table

Revision ID: 001
Revises: 
Create Date: 2024-12-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('refuelings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('station_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('fuel_type', sa.String(), nullable=False),
    sa.Column('price_per_liter', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('volume_liters', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('driver_cpf', sa.String(), nullable=False),
    sa.Column('improper_data', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refuelings_id'), 'refuelings', ['id'], unique=False)
    op.create_index(op.f('ix_refuelings_station_id'), 'refuelings', ['station_id'], unique=False)
    op.create_index(op.f('ix_refuelings_timestamp'), 'refuelings', ['timestamp'], unique=False)
    op.create_index(op.f('ix_refuelings_fuel_type'), 'refuelings', ['fuel_type'], unique=False)
    op.create_index(op.f('ix_refuelings_driver_cpf'), 'refuelings', ['driver_cpf'], unique=False)
    op.create_index('idx_fuel_type_timestamp', 'refuelings', ['fuel_type', 'timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_fuel_type_timestamp', table_name='refuelings')
    op.drop_index(op.f('ix_refuelings_driver_cpf'), table_name='refuelings')
    op.drop_index(op.f('ix_refuelings_fuel_type'), table_name='refuelings')
    op.drop_index(op.f('ix_refuelings_timestamp'), table_name='refuelings')
    op.drop_index(op.f('ix_refuelings_station_id'), table_name='refuelings')
    op.drop_index(op.f('ix_refuelings_id'), table_name='refuelings')
    op.drop_table('refuelings')

