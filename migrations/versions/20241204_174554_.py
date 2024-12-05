from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.models.db import db


# revision identifiers, used by Alembic
revision = '51881d7c48cb'
down_revision = 'acd7cf4b29ce'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Alter `cards` table
    with op.batch_alter_table('cards') as batch_op:
        batch_op.alter_column('image_url', nullable=True)
        batch_op.alter_column('url', nullable=True)

    # Alter `reward_points` table
    with op.batch_alter_table('reward_points') as batch_op:
        batch_op.alter_column('bonus_point', type_=sa.Numeric(precision=10, scale=2))

    # Alter `spendings` table
    with op.batch_alter_table('spendings') as batch_op:
        if 'fk_spendings_user_id' in [fk['name'] for fk in inspector.get_foreign_keys('spendings')]:
            batch_op.drop_constraint('fk_spendings_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_spendings_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Alter `wallet_cards` table
    with op.batch_alter_table('wallet_cards') as batch_op:
        if 'network' not in [col['name'] for col in inspector.get_columns('wallet_cards')]:
            batch_op.add_column(sa.Column('network', sa.String(length=255), nullable=True))


def downgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    # Reverse changes to `wallet_cards` table
    with op.batch_alter_table('wallet_cards') as batch_op:
        if 'network' in [col['name'] for col in inspector.get_columns('wallet_cards')]:
            batch_op.drop_column('network')

    # Reverse changes to `spendings` table
    with op.batch_alter_table('spendings') as batch_op:
        if 'fk_spendings_user_id' in [fk['name'] for fk in inspector.get_foreign_keys('spendings')]:
            batch_op.drop_constraint('fk_spendings_user_id', type_='foreignkey')

    # Reverse changes to `reward_points` table
    with op.batch_alter_table('reward_points') as batch_op:
        batch_op.alter_column('bonus_point', type_=sa.FLOAT())

    # Reverse changes to `cards` table
    with op.batch_alter_table('cards') as batch_op:
        batch_op.alter_column('url', nullable=False)
        batch_op.alter_column('image_url', nullable=False)
