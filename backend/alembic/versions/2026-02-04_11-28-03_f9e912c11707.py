"""add station table

Revision ID: f9e912c11707
Revises: f4b87701b582
Create Date: 2026-02-04 11:28:03.055801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9e912c11707'
down_revision: Union[str, Sequence[str], None] = 'f4b87701b582'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('station',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=1024), nullable=False),
    sa.Column('address', sa.String(length=1024), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['staff.user_id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_station_created_by'), 'station', ['created_by'], unique=False)
    op.create_index(op.f('ix_station_id'), 'station', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_station_id'), table_name='station')
    op.drop_index(op.f('ix_station_created_by'), table_name='station')
    op.drop_table('station')
    # ### end Alembic commands ###
