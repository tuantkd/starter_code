"""Update migration.

Revision ID: d5c58e769715
Revises: 6052b5138ecd
Create Date: 2023-02-26 17:28:16.115418

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd5c58e769715'
down_revision = '6052b5138ecd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.drop_column('shows', 'created_on')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('shows', 'start_time')
    # ### end Alembic commands ###
