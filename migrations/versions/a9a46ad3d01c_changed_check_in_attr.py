"""changed check_in attr

Revision ID: a9a46ad3d01c
Revises: 3ad7a89b90c7
Create Date: 2024-10-11 22:50:05.425893

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a9a46ad3d01c'
down_revision: Union[str, None] = '3ad7a89b90c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('client_parking', 'time_in',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)



def downgrade() -> None:
    op.alter_column('client_parking', 'time_in',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

