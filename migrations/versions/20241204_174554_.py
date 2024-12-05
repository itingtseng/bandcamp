from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '51881d7c48cb'
down_revision = 'acd7cf4b29ce'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Create 'cards' table if it doesn't exist
    if 'cards' not in inspector.get_table_names():
        op.create_table('cards',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('issuer', sa.String(length=255), nullable=False),
            sa.Column('image_url', sa.String(length=255), nullable=False),
            sa.Column('url', sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

    # Create 'wallet_cards' table if it doesn't exist
    if 'wallet_cards' not in inspector.get_table_names():
        op.create_table('wallet_cards',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('wallet_id', sa.Integer(), nullable=False),
            sa.Column('card_id', sa.Integer(), nullable=False),
            sa.Column('nickname', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Add 'network' to 'wallet_cards' table if it doesn't exist
    if 'network' not in [col['name'] for col in inspector.get_columns('wallet_cards')]:
        with op.batch_alter_table('wallet_cards') as batch_op:
            batch_op.add_column(sa.Column('network', sa.String(length=255), nullable=True))

    # Ensure that 'reward_points' and other tables have the correct column types
    with op.batch_alter_table('reward_points') as batch_op:
        batch_op.alter_column('bonus_point', existing_type=sa.FLOAT(), type_=sa.Numeric(precision=10, scale=2))

    # Ensure the foreign key in 'spendings' is set properly
    spendings_constraints = [fk['name'] for fk in inspector.get_foreign_keys('spendings')]
    with op.batch_alter_table('spendings') as batch_op:
        if 'fk_spendings_user_id' in spendings_constraints:
            batch_op.drop_constraint('fk_spendings_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_spendings_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Reverse the changes to 'wallet_cards' table
    with op.batch_alter_table('wallet_cards') as batch_op:
        batch_op.drop_column('network')

    # Drop the 'wallet_cards' table
    if 'wallet_cards' in inspector.get_table_names():
        op.drop_table('wallet_cards')

    # Drop the 'cards' table
    if 'cards' in inspector.get_table_names():
        op.drop_table('cards')

    # Reverse the changes to the 'reward_points' table
    with op.batch_alter_table('reward_points') as batch_op:
        batch_op.alter_column('bonus_point', existing_type=sa.Numeric(precision=10, scale=2), type_=sa.FLOAT())

    # Reverse changes to 'spendings' table foreign key
    spendings_constraints = [fk['name'] for fk in inspector.get_foreign_keys('spendings')]
    with op.batch_alter_table('spendings') as batch_op:
        if 'fk_spendings_user_id' in spendings_constraints:
            batch_op.drop_constraint('fk_spendings_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_spendings_user_id', 'users', ['user_id'], ['id'])
