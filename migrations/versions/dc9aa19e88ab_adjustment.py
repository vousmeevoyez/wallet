"""adjustment

Revision ID: dc9aa19e88ab
Revises: e4a97ca74c79
Create Date: 2018-11-07 06:11:27.505116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc9aa19e88ab'
down_revision = 'e4a97ca74c79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.Integer(), nullable=True))
    op.add_column('virtual_account', sa.Column('bank_id', sa.Integer(), nullable=True))
    op.add_column('virtual_account', sa.Column('va_type', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('virtual_account', 'va_type')
    op.drop_column('virtual_account', 'bank_id')
    op.drop_column('user', 'role')
    # ### end Alembic commands ###
