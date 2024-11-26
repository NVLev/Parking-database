"""changed ClientParking attributes

Revision ID: 3ad7a89b90c7
Revises: ecee6749e5ea
Create Date: 2024-10-11 21:59:53.503642

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3ad7a89b90c7'
down_revision: Union[str, None] = 'ecee6749e5ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column('client_parking', 'time_out',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)



def downgrade() -> None:

    op.alter_column('client_parking', 'time_out',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

