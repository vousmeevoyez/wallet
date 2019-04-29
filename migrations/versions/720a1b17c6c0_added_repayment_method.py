"""added repayment method

Revision ID: 720a1b17c6c0
Revises: 36f929e28d48
Create Date: 2019-04-24 16:29:46.860392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '720a1b17c6c0'
down_revision = '36f929e28d48'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'api_key', ['id'])
    op.create_unique_constraint(None, 'bank', ['id'])
    op.create_unique_constraint(None, 'bank_account', ['id'])
    op.create_unique_constraint(None, 'payment', ['id'])
    op.create_unique_constraint(None, 'payment_channel', ['id'])
    op.add_column('payment_plan', sa.Column('method', sa.Integer(), nullable=True))
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
    op.drop_column('payment_plan', 'method')
    op.drop_constraint(None, 'payment_channel', type_='unique')
    op.drop_constraint(None, 'payment', type_='unique')
    op.drop_constraint(None, 'bank_account', type_='unique')
    op.drop_constraint(None, 'bank', type_='unique')
    op.drop_constraint(None, 'api_key', type_='unique')
    # ### end Alembic commands ###