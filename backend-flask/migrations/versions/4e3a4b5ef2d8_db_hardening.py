"""DB hardening: money precision, statuses, audit fields, indexes

Revision ID: 4e3a4b5ef2d8
Revises: f59a071650ff
Create Date: 2025-12-09
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '4e3a4b5ef2d8'
down_revision = 'f59a071650ff'
branch_labels = None
depends_on = None


def upgrade():
    # Users: add is_active and indexes
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.create_index('ix_user_created_at', ['created_at'])

    # Transactions: precision, status enum, audit fields, indexes, constraints
    status_enum = sa.Enum('pending', 'approved', 'rejected', name='transaction_status', native_enum=False)
    status_enum.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table('transaction') as batch_op:
        batch_op.alter_column('amount', type_=sa.Numeric(12, 2))
        batch_op.alter_column('status', type_=status_enum, existing_nullable=False, server_default='pending')
        batch_op.add_column(sa.Column('reviewed_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('reviewed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.create_index('ix_transaction_user_id', ['user_id'])
        batch_op.create_index('ix_transaction_status', ['status'])
        batch_op.create_index('ix_transaction_created_at', ['created_at'])
        batch_op.create_unique_constraint('uq_transaction_user_ref', ['user_id', 'transaction_ref'])
        batch_op.create_foreign_key('fk_transaction_reviewed_by_user', 'user', ['reviewed_by'], ['id'])


def downgrade():
    # Transactions rollback
    status_enum = sa.Enum('pending', 'approved', 'rejected', name='transaction_status', native_enum=False)

    with op.batch_alter_table('transaction') as batch_op:
        batch_op.drop_constraint('fk_transaction_reviewed_by_user', type_='foreignkey')
        batch_op.drop_constraint('uq_transaction_user_ref', type_='unique')
        batch_op.drop_index('ix_transaction_created_at')
        batch_op.drop_index('ix_transaction_status')
        batch_op.drop_index('ix_transaction_user_id')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('reviewed_at')
        batch_op.drop_column('reviewed_by')
        batch_op.alter_column('status', type_=sa.String(length=20), existing_nullable=False)
        batch_op.alter_column('amount', type_=sa.Float(), existing_nullable=False)

    status_enum.drop(op.get_bind(), checkfirst=True)

    # Users rollback
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_index('ix_user_created_at')
        batch_op.drop_column('is_active')

