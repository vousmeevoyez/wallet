"""remove bank account unique

Revision ID: e083ddb1ec74
Revises: 554bbfa8bd08
Create Date: 2019-03-12 10:56:56.525630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e083ddb1ec74'
down_revision = '554bbfa8bd08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'bank', ['id'])
    op.drop_constraint('bank_account_account_no_key', 'bank_account', type_='unique')
    op.create_unique_constraint(None, 'bank_account', ['id'])
    op.drop_constraint('payment_ref_number_key', 'payment', type_='unique')
    op.create_unique_constraint(None, 'payment', ['id'])
    op.create_unique_constraint(None, 'payment_channel', ['id'])
    op.create_unique_constraint(None, 'transaction', ['id'])
    op.create_unique_constraint(None, 'user', ['id'])
    op.create_unique_constraint(None, 'virtual_account', ['id'])
    op.create_unique_constraint(None, 'wallet', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='unique')
    op.drop_constraint(None, 'virtual_account', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'transaction', type_='unique')
    op.drop_constraint(None, 'payment_channel', type_='unique')
    op.drop_constraint(None, 'payment', type_='unique')
    op.create_unique_constraint('payment_ref_number_key', 'payment', ['ref_number'])
    op.drop_constraint(None, 'bank_account', type_='unique')
    op.create_unique_constraint('bank_account_account_no_key', 'bank_account', ['account_no'])
    op.drop_constraint(None, 'bank', type_='unique')
    # ### end Alembic commands ###