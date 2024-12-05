from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'acd7cf4b29ce'
down_revision = 'ffdc0a98111c'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Check if 'cards' table exists before creating it
    if 'cards' not in inspector.get_table_names():
        op.create_table('cards',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('issuer', sa.String(length=255), nullable=False),
            sa.Column('image_url', sa.String(length=255), nullable=False),
            sa.Column('url', sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

    # Check if 'categories' table exists before creating it
    if 'categories' not in inspector.get_table_names():
        op.create_table('categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('parent_category_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['parent_category_id'], ['categories.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    # Check if 'reward_points' table exists before creating it
    if 'reward_points' not in inspector.get_table_names():
        op.create_table('reward_points',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('card_id', sa.Integer(), nullable=False),
            sa.Column('category_id', sa.Integer(), nullable=False),
            sa.Column('bonus_point', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('multiplier_type', sa.String(length=10), nullable=False),
            sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
            sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Check if 'spendings' table exists before creating it
    if 'spendings' not in inspector.get_table_names():
        op.create_table('spendings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Check if 'wallets' table exists before creating it
    if 'wallets' not in inspector.get_table_names():
        op.create_table('wallets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Check if 'spending_categories' table exists before creating it
    if 'spending_categories' not in inspector.get_table_names():
        op.create_table('spending_categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('spending_id', sa.Integer(), nullable=False),
            sa.Column('category_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['spending_id'], ['spendings.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Check if 'wallet_cards' table exists before creating it
    if 'wallet_cards' not in inspector.get_table_names():
        op.create_table('wallet_cards',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('wallet_id', sa.Integer(), nullable=False),
            sa.Column('card_id', sa.Integer(), nullable=False),
            sa.Column('nickname', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
            sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Add 'firstname' and 'lastname' columns to 'users' table if not exists
    if 'firstname' not in [col['name'] for col in inspector.get_columns('users')]:
        op.add_column('users', sa.Column('firstname', sa.String(length=255), nullable=True))

    if 'lastname' not in [col['name'] for col in inspector.get_columns('users')]:
        op.add_column('users', sa.Column('lastname', sa.String(length=255), nullable=True))


def downgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Drop 'firstname' and 'lastname' columns if they exist
    if 'firstname' in [col['name'] for col in inspector.get_columns('users')]:
        op.drop_column('users', 'firstname')

    if 'lastname' in [col['name'] for col in inspector.get_columns('users')]:
        op.drop_column('users', 'lastname')

    # Drop 'wallet_cards' table if it exists
    if 'wallet_cards' in inspector.get_table_names():
        op.drop_table('wallet_cards')

    # Drop 'spending_categories' table if it exists
    if 'spending_categories' in inspector.get_table_names():
        op.drop_table('spending_categories')

    # Drop 'wallets' table if it exists
    if 'wallets' in inspector.get_table_names():
        op.drop_table('wallets')

    # Drop 'spendings' table if it exists
    if 'spendings' in inspector.get_table_names():
        op.drop_table('spendings')

    # Drop 'reward_points' table if it exists
    if 'reward_points' in inspector.get_table_names():
        op.drop_table('reward_points')

    # Drop 'categories' table if it exists
    if 'categories' in inspector.get_table_names():
        op.drop_table('categories')

    # Drop 'cards' table if it exists
    if 'cards' in inspector.get_table_names():
        op.drop_table('cards')
