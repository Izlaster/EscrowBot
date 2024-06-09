"""Database creation v1.1

Revision ID: d14b540bb5eb
Revises: 5294746ad66d
Create Date: 2024-06-09 15:25:01.615045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd14b540bb5eb'
down_revision: Union[str, None] = '5294746ad66d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'token_amount',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=10, scale=7),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'token_amount',
               existing_type=sa.Numeric(precision=10, scale=7),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
