"""temporary remove msisdn

Revision ID: 745cf032bd89
Revises: 1b180b9e0751
Create Date: 2018-10-26 10:07:55.047035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '745cf032bd89'
down_revision = '1b180b9e0751'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('virtual_account_msisdn_key', 'virtual_account', type_='unique')
    op.drop_column('virtual_account', 'msisdn')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('virtual_account', sa.Column('msisdn', sa.VARCHAR(length=12), autoincrement=False, nullable=True))
    op.create_unique_constraint('virtual_account_msisdn_key', 'virtual_account', ['msisdn'])
    # ### end Alembic commands ###
