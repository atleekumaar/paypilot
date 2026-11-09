"""refund_ledger_and_webhook_lifecycle

Revision ID: 4c32d6f0a11e
Revises: 3b21c5e9f00d
Create Date: 2026-11-01 00:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c32d6f0a11e'
down_revision: Union[str, Sequence[str], None] = '3b21c5e9f00d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create refund_attempts ledger table
    op.create_table(
        'refund_attempts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('payment_id', sa.String(), sa.ForeignKey('payments.id'), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), server_default='PAYPAL', nullable=False),
        sa.Column('provider_capture_id', sa.String(), nullable=False),
        sa.Column('provider_refund_id', sa.String(), nullable=True),
        sa.Column('idempotency_key', sa.String(), nullable=False),
        sa.Column('requested_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(), server_default='USD', nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('error_code', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_refund_attempts_payment_id', 'refund_attempts', ['payment_id'])
    op.create_index('ix_refund_attempts_user_id', 'refund_attempts', ['user_id'])
    op.create_index('ix_refund_attempts_provider_capture_id', 'refund_attempts', ['provider_capture_id'])
    op.create_index('ix_refund_attempts_provider_refund_id', 'refund_attempts', ['provider_refund_id'], unique=True)
    op.create_index('ix_refund_attempts_idempotency_key', 'refund_attempts', ['idempotency_key'], unique=True)
    op.create_index('ix_refund_attempts_status', 'refund_attempts', ['status'])

    # 2. Add lifecycle tracking fields and unique constraint to webhook_events
    with op.batch_alter_table('webhook_events') as batch_op:
        batch_op.add_column(sa.Column('attempt_count', sa.Integer(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('last_error', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('received_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('processed_at', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint('uq_webhook_provider_event_id', ['provider', 'id'])


def downgrade() -> None:
    with op.batch_alter_table('webhook_events') as batch_op:
        batch_op.drop_constraint('uq_webhook_provider_event_id', type_='unique')
        batch_op.drop_column('processed_at')
        batch_op.drop_column('received_at')
        batch_op.drop_column('last_error')
        batch_op.drop_column('attempt_count')

    op.drop_index('ix_refund_attempts_status', table_name='refund_attempts')
    op.drop_index('ix_refund_attempts_idempotency_key', table_name='refund_attempts')
    op.drop_index('ix_refund_attempts_provider_refund_id', table_name='refund_attempts')
    op.drop_index('ix_refund_attempts_provider_capture_id', table_name='refund_attempts')
    op.drop_index('ix_refund_attempts_user_id', table_name='refund_attempts')
    op.drop_index('ix_refund_attempts_payment_id', table_name='refund_attempts')
    op.drop_table('refund_attempts')

