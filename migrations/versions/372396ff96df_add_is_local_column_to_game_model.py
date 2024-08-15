"""Add is_local column to Game model

Revision ID: 372396ff96df
Revises: c4bc328e3564
Create Date: 2024-08-15 02:21:45.730553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '372396ff96df'
down_revision = 'c4bc328e3564'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game', sa.Column('is_local', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'is_local')
    # ### end Alembic commands ###
