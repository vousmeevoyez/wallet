"""empty message

Revision ID: da9427af60b9
Revises: 066e7b561320
Create Date: 2019-09-25 15:24:49.910487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da9427af60b9'
down_revision = '066e7b561320'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('virtual_account_wallet_id_fkey', 'virtual_account', type_='foreignkey')
    op.create_foreign_key(None, 'virtual_account', 'wallet', ['wallet_id'], ['id'])
    op.drop_constraint('wallet_user_id_fkey', 'wallet', type_='foreignkey')
    op.create_foreign_key(None, 'wallet', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='foreignkey')
    op.create_foreign_key('wallet_user_id_fkey', 'wallet', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'virtual_account', type_='foreignkey')
    op.create_foreign_key('virtual_account_wallet_id_fkey', 'virtual_account', 'wallet', ['wallet_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###