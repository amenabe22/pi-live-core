"""Add public schema business tables (vehicles, stations, travels, etc.)

Revision ID: a1b2c3d4e5f6
Revises: f4b87701b582
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f4b87701b582'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS public")

    # vehicles
    op.create_table(
        'vehicles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plate_number', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE', name='vehiclestatus'), nullable=False, server_default='ACTIVE'),
        sa.Column('driver_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['auth.users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_vehicles_plate_number'), 'vehicles', ['plate_number'], unique=True, schema='public')
    op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'], schema='public')

    # stations
    op.create_table(
        'stations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('radius', sa.Float(), nullable=True, server_default='100.0'),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_stations_id'), 'stations', ['id'], schema='public')

    # travels
    op.create_table(
        'travels',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('vehicle_id', sa.String(length=36), nullable=False),
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('origin_station_id', sa.String(length=36), nullable=False),
        sa.Column('destination_station_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='travelstatus'), nullable=False, server_default='SCHEDULED'),
        sa.Column('scheduled_departure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_departure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['public.vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['driver_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['origin_station_id'], ['public.stations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_station_id'], ['public.stations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_travels_id'), 'travels', ['id'], schema='public')

    # travel_history
    op.create_table(
        'travel_history',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('travel_id', sa.String(length=36), nullable=False),
        sa.Column('vehicle_id', sa.String(length=36), nullable=False),
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('origin_station_id', sa.String(length=36), nullable=False),
        sa.Column('destination_station_id', sa.String(length=36), nullable=False),
        sa.Column('departure_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('arrival_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('COMPLETED', 'CANCELLED', name='historystatus'), nullable=False, server_default='COMPLETED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['travel_id'], ['public.travels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['public.vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['driver_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['origin_station_id'], ['public.stations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_station_id'], ['public.stations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('travel_id'),
        schema='public'
    )
    op.create_index(op.f('ix_travel_history_id'), 'travel_history', ['id'], schema='public')

    # reviews
    op.create_table(
        'reviews',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('travel_id', sa.String(length=36), nullable=True),
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('reviewer_id', sa.String(length=36), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('review_type', sa.Enum('DRIVER', 'TRIP', 'SERVICE', name='reviewtype'), nullable=False, server_default='TRIP'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['travel_id'], ['public.travels.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['driver_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], schema='public')

    # live_tracking
    op.create_table(
        'live_tracking',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('vehicle_id', sa.String(length=36), nullable=False),
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['public.vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['driver_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_live_tracking_vehicle_id'), 'live_tracking', ['vehicle_id'], schema='public')
    op.create_index(op.f('ix_live_tracking_timestamp'), 'live_tracking', ['timestamp'], schema='public')


def downgrade() -> None:
    op.drop_index(op.f('ix_live_tracking_timestamp'), table_name='live_tracking', schema='public')
    op.drop_index(op.f('ix_live_tracking_vehicle_id'), table_name='live_tracking', schema='public')
    op.drop_table('live_tracking', schema='public')
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews', schema='public')
    op.drop_table('reviews', schema='public')
    op.drop_index(op.f('ix_travel_history_id'), table_name='travel_history', schema='public')
    op.drop_table('travel_history', schema='public')
    op.drop_index(op.f('ix_travels_id'), table_name='travels', schema='public')
    op.drop_table('travels', schema='public')
    op.drop_index(op.f('ix_stations_id'), table_name='stations', schema='public')
    op.drop_table('stations', schema='public')
    op.drop_index(op.f('ix_vehicles_id'), table_name='vehicles', schema='public')
    op.drop_index(op.f('ix_vehicles_plate_number'), table_name='vehicles', schema='public')
    op.drop_table('vehicles', schema='public')

    op.execute("DROP TYPE IF EXISTS public.vehiclestatus")
    op.execute("DROP TYPE IF EXISTS public.travelstatus")
    op.execute("DROP TYPE IF EXISTS public.historystatus")
    op.execute("DROP TYPE IF EXISTS public.reviewtype")
