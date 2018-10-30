"""remove billing type

Revision ID: 64cd17bc61dc
Revises: 074a7a57e4f2
Create Date: 2018-10-26 05:50:41.422952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64cd17bc61dc'
down_revision = '074a7a57e4f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('virtual_account_billing_type_key', 'virtual_account', type_='unique')
    op.drop_column('virtual_account', 'billing_type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('virtual_account', sa.Column('billing_type', sa.VARCHAR(length=1), autoincrement=False, nullable=True))
    op.create_unique_constraint('virtual_account_billing_type_key', 'virtual_account', ['billing_type'])
    # ### end Alembic commands ###
