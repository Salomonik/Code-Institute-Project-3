from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '123225a82f78'
down_revision = 'fa537963afa3'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the dependent table first
    op.drop_table('game_genre_association')
    
    # Now drop the primary table
    op.drop_table('game_genre')

def downgrade():
    # Create the primary table first
    op.create_table(
        'game_genre',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Now create the dependent table
    op.create_table(
        'game_genre_association',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('genre_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
        sa.ForeignKeyConstraint(['genre_id'], ['game_genre.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
