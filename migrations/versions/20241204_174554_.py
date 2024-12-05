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

    # Create 'cards' table if it does not exist
    if 'cards' not in inspector.get_table_names():
        op.create_table('cards',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('issuer', sa.String(length=255), nullable=False),
            sa.Column('image_url', sa.String(length=255), nullable=False),
            sa.Column('url', sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

    # Create 'reward_points' table if it does not exist
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

    # Add 'firstname' and 'lastname' to 'users' table if they do not exist
    users_columns = [col['name'] for col in inspector.get_columns('users')]
    with op.batch_alter_table('users', schema=None) as batch_op:
        if 'firstname' not in users_columns:
            batch_op.add_column(sa.Column('firstname', sa.String(length=255), nullable=True))
        if 'lastname' not in users_columns:
            batch_op.add_column(sa.Column('lastname', sa.String(length=255), nullable=True))

    # Add 'network' to 'wallet_cards' table if it does not exist
    wallet_cards_columns = [col['name'] for col in inspector.get_columns('wallet_cards')]
    with op.batch_alter_table('wallet_cards', schema=None) as batch_op:
        if 'network' not in wallet_cards_columns:
            batch_op.add_column(sa.Column('network', sa.String(length=255), nullable=True))

    # Adjust the 'cards' table columns if necessary
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.alter_column('image_url', existing_type=sa.VARCHAR(length=255), nullable=True)
        batch_op.alter_column('url', existing_type=sa.VARCHAR(length=255), nullable=True)

    # Adjust the 'reward_points' table column
    with op.batch_alter_table('reward_points', schema=None) as batch_op:
        batch_op.alter_column('bonus_point', existing_type=sa.FLOAT(), type_=sa.Numeric(precision=10, scale=2), existing_nullable=False)

    # Adjust the 'spendings' table foreign key constraints if needed
    spendings_constraints = [fk['name'] for fk in inspector.get_foreign_keys('spendings')]
    with op.batch_alter_table('spendings', schema=None) as batch_op:
        if 'fk_spendings_user_id' in spendings_constraints:
            batch_op.drop_constraint('fk_spendings_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_spendings_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Reverse changes to 'wallet_cards' table
    wallet_cards_constraints = [fk['name'] for fk in inspector.get_foreign_keys('wallet_cards')]
    with op.batch_alter_table('wallet_cards', schema=None) as batch_op:
        if 'fk_wallet_cards_card_id' in wallet_cards_constraints:
            batch_op.drop_constraint('fk_wallet_cards_card_id', type_='foreignkey')
        if 'fk_wallet_cards_wallet_id' in wallet_cards_constraints:
            batch_op.drop_constraint('fk_wallet_cards_wallet_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_wallet_cards_wallet_id', 'wallets', ['wallet_id'], ['id'])
        batch_op.create_foreign_key('fk_wallet_cards_card_id', 'cards', ['card_id'], ['id'])
        if 'network' in [col['name'] for col in inspector.get_columns('wallet_cards')]:
            batch_op.drop_column('network')

    # Reverse changes to 'users' table
    users_columns = [col['name'] for col in inspector.get_columns('users')]
    with op.batch_alter_table('users', schema=None) as batch_op:
        if 'lastname' in users_columns:
            batch_op.drop_column('lastname')
        if 'firstname' in users_columns:
            batch_op.drop_column('firstname')

    # Reverse changes to 'spendings' table
    spendings_constraints = [fk['name'] for fk in inspector.get_foreign_keys('spendings')]
    with op.batch_alter_table('spendings', schema=None) as batch_op:
        if 'fk_spendings_user_id' in spendings_constraints:
            batch_op.drop_constraint('fk_spendings_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_spendings_user_id', 'users', ['user_id'], ['id'])

    # Reverse changes to 'reward_points' table
    with op.batch_alter_table('reward_points', schema=None) as batch_op:
        batch_op.alter_column('bonus_point', existing_type=sa.Numeric(precision=10, scale=2), type_=sa.FLOAT(), existing_nullable=False)

    # Reverse changes to 'cards' table
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.alter_column('url', existing_type=sa.VARCHAR(length=255), nullable=False)
        batch_op.alter_column('image_url', existing_type=sa.VARCHAR(length=255), nullable=False)
