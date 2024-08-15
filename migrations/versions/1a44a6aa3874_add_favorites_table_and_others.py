"""Add favorites table and others

Revision ID: 1a44a6aa3874
Revises: eec6730963d0
Create Date: 2024-08-15 00:31:14.102286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a44a6aa3874'
down_revision = 'eec6730963d0'
branch_labels = None
depends_on = None


def upgrade():
    # Utworzenie tabeli favorites
    op.create_table(
        'favorites',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['game.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'game_id')
    )

def downgrade():
    # Usunięcie tabeli favorites
    op.drop_table('favorites')
