"""Create tables

Revision ID: ecee6749e5ea
Revises: 
Create Date: 2024-10-10 21:51:31.283829

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ecee6749e5ea'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('surname', sa.String(length=50), nullable=False),
    sa.Column('credit_card', sa.String(length=50), nullable=False),
    sa.Column('car_number', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=False),
    sa.Column('opened', sa.Boolean(), nullable=False),
    sa.Column('count_places', sa.Integer(), nullable=False),
    sa.Column('count_available_places', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('client_parking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('parking_id', sa.Integer(), nullable=False),
    sa.Column('time_in', sa.DateTime(), nullable=False),
    sa.Column('time_out', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.ForeignKeyConstraint(['parking_id'], ['parking.id'], ),
    sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:

    op.drop_table('client_parking')
    op.drop_table('parking')
    op.drop_table('client')

