"""some changes

Revision ID: b6100679d288
Revises: 57c0e9c6da3d
Create Date: 2019-04-10 13:56:50.019356

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6100679d288'
down_revision = '57c0e9c6da3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'bank', ['id'])
    op.create_unique_constraint(None, 'bank_account', ['id'])
    op.create_unique_constraint(None, 'payment', ['id'])
    op.create_unique_constraint(None, 'payment_channel', ['id'])
    op.create_unique_constraint(None, 'payment_plan', ['id'])
    op.create_unique_constraint(None, 'plan', ['id'])
    op.create_unique_constraint(None, 'transaction', ['id'])
    op.create_unique_constraint(None, 'transaction_note', ['id'])
    op.create_unique_constraint(None, 'transaction_type', ['id'])
    op.create_unique_constraint(None, 'user', ['id'])
    op.create_unique_constraint(None, 'virtual_account', ['id'])
    op.create_unique_constraint(None, 'wallet', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='unique')
    op.drop_constraint(None, 'virtual_account', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'transaction_type', type_='unique')
    op.drop_constraint(None, 'transaction_note', type_='unique')
    op.drop_constraint(None, 'transaction', type_='unique')
    op.drop_constraint(None, 'plan', type_='unique')
    op.drop_constraint(None, 'payment_plan', type_='unique')
    op.drop_constraint(None, 'payment_channel', type_='unique')
    op.drop_constraint(None, 'payment', type_='unique')
    op.drop_constraint(None, 'bank_account', type_='unique')
    op.drop_constraint(None, 'bank', type_='unique')
    # ### end Alembic commands ###
