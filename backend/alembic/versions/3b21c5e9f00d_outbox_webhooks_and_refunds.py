"""outbox_webhooks_and_refunds

Revision ID: 3b21c5e9f00d
Revises: 2a10b4f8d99c
Create Date: 2026-10-31 23:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b21c5e9f00d'
down_revision: Union[str, Sequence[str], None] = '2a10b4f8d99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create outbox_events table
    op.create_table(
        'outbox_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('aggregate_type', sa.String(), nullable=False),
        sa.Column('aggregate_id', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(), server_default='PENDING', nullable=False),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_outbox_events_event_type', 'outbox_events', ['event_type'])
    op.create_index('ix_outbox_events_aggregate_type', 'outbox_events', ['aggregate_type'])
    op.create_index('ix_outbox_events_aggregate_id', 'outbox_events', ['aggregate_id'])
    op.create_index('ix_outbox_events_status', 'outbox_events', ['status'])

    # 2. Create webhook_events table
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('provider', sa.String(), server_default='PAYPAL', nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='PROCESSED', nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_webhook_events_event_type', 'webhook_events', ['event_type'])
    op.create_index('ix_webhook_events_resource_id', 'webhook_events', ['resource_id'])

    # 3. Add refund columns to payments
    with op.batch_alter_table('payments') as batch_op:
        batch_op.add_column(sa.Column('refund_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('refund_status', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('refund_amount', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.create_index('ix_payments_refund_id', ['refund_id'])

    # 4. Add version column to agent_sessions
    with op.batch_alter_table('agent_sessions') as batch_op:
        batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('agent_sessions') as batch_op:
        batch_op.drop_column('version')

    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_index('ix_payments_refund_id')
        batch_op.drop_column('refund_amount')
        batch_op.drop_column('refund_status')
        batch_op.drop_column('refund_id')

    op.drop_index('ix_webhook_events_resource_id', table_name='webhook_events')
    op.drop_index('ix_webhook_events_event_type', table_name='webhook_events')
    op.drop_table('webhook_events')

    op.drop_index('ix_outbox_events_status', table_name='outbox_events')
    op.drop_index('ix_outbox_events_aggregate_id', table_name='outbox_events')
    op.drop_index('ix_outbox_events_aggregate_type', table_name='outbox_events')
    op.drop_index('ix_outbox_events_event_type', table_name='outbox_events')
    op.drop_table('outbox_events')

