"""added response time

Revision ID: 129505a613ae
Revises: 26529f84fa9c
Create Date: 2019-01-09 19:30:45.711011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '129505a613ae'
down_revision = '26529f84fa9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('external_log', sa.Column('response_time', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('external_log', 'response_time')
    # ### end Alembic commands ###