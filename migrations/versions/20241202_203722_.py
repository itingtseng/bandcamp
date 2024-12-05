from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.models.db import db

# revision identifiers, used by Alembic
revision = 'acd7cf4b29ce'
down_revision = 'ffdc0a98111c'
branch_labels = None
depends_on = None


def upgrade():
    # Create the `cards` table
    op.create_table(
        'cards',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('issuer', sa.String(length=255), nullable=False),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(length=255), nullable=True),
    )

    # Create the `categories` table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_category_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_category_id'], ['categories.id']),
        sa.UniqueConstraint('name'),
    )

    # Create the `reward_points` table
    op.create_table(
        'reward_points',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('bonus_point', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('multiplier_type', sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
    )

    # Create the `spendings` table
    op.create_table(
        'spendings',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )

    # Create the `wallets` table
    op.create_table(
        'wallets',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )

    # Create the `spending_categories` table
    op.create_table(
        'spending_categories',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('spending_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['spending_id'], ['spendings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    )

    # Create the `wallet_cards` table
    op.create_table(
        'wallet_cards',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('nickname', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id']),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id']),
    )

    # Add columns to the `users` table
    op.add_column('users', sa.Column('firstname', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('lastname', sa.String(length=255), nullable=True))


def downgrade():
    # Safely drop columns and tables
    inspector = inspect(db.engine)

    # Drop columns from `users`
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'firstname' in columns:
            op.drop_column('users', 'firstname')
        if 'lastname' in columns:
            op.drop_column('users', 'lastname')

    # Drop tables
    op.drop_table('wallet_cards')
    op.drop_table('spending_categories')
    op.drop_table('wallets')
    op.drop_table('spendings')
    op.drop_table('reward_points')
    op.drop_table('categories')
    op.drop_table('cards')
