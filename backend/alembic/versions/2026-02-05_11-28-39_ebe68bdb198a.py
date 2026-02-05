"""add travel_route table

Revision ID: ebe68bdb198a
Revises: f9e912c11707
Create Date: 2026-02-05 11:28:39.986365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = 'ebe68bdb198a'
down_revision: Union[str, Sequence[str], None] = 'f9e912c11707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('travel_route',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('polyline', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, dimension=2, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
    sa.Column('station_ids', postgresql.ARRAY(sa.String(length=36)), server_default=sa.text("'{}'::varchar[]"), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['staff.user_id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_travel_route_created_by'), 'travel_route', ['created_by'], unique=False)
    op.create_index(op.f('ix_travel_route_id'), 'travel_route', ['id'], unique=False)
    op.create_index(op.f('ix_travel_route_name'), 'travel_route', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_travel_route_name'), table_name='travel_route')
    op.drop_index(op.f('ix_travel_route_id'), table_name='travel_route')
    op.drop_index(op.f('ix_travel_route_created_by'), table_name='travel_route')
    op.drop_table('travel_route')
    # ### end Alembic commands ###
