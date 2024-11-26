"""added opening hours

Revision ID: 8fe7372bcddc
Revises: a9a46ad3d01c
Create Date: 2024-10-11 23:55:28.763505

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8fe7372bcddc'
down_revision: Union[str, None] = 'a9a46ad3d01c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column('parking', sa.Column('opening_time', sa.Time(), nullable=False))
    op.add_column('parking', sa.Column('closing_time', sa.Time(), nullable=False))



def downgrade() -> None:

    op.drop_column('parking', 'closing_time')
    op.drop_column('parking', 'opening_time')

