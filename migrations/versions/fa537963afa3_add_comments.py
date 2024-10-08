"""add comments

Revision ID: fa537963afa3
Revises: c9818907d334
Create Date: 2024-07-11 17:12:39.704068

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fa537963afa3'
down_revision = 'c9818907d334'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('favorite')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('favorite',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('game_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], name='favorite_game_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='favorite_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='favorite_pkey')
    )
    # ### end Alembic commands ###
