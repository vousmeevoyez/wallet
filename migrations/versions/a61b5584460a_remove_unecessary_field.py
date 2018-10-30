"""remove unecessary field

Revision ID: a61b5584460a
Revises: 99f1a0189b62
Create Date: 2018-10-26 13:48:17.294908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a61b5584460a'
down_revision = '99f1a0189b62'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('virtual_account_trx_amount_key', 'virtual_account', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('virtual_account_trx_amount_key', 'virtual_account', ['trx_amount'])
    # ### end Alembic commands ###
