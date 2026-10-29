"""monetary_numeric_precision

Revision ID: 2a10b4f8d99c
Revises: 1d300f03116b
Create Date: 2026-10-29 20:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a10b4f8d99c'
down_revision: Union[str, Sequence[str], None] = '1d300f03116b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade monetary columns to exact NUMERIC(10, 2)."""
    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column(
            'amount',
            type_=sa.Numeric(precision=10, scale=2),
            existing_type=sa.Float(),
            existing_nullable=False,
        )

    with op.batch_alter_table('payments') as batch_op:
        batch_op.alter_column(
            'amount',
            type_=sa.Numeric(precision=10, scale=2),
            existing_type=sa.Float(),
            existing_nullable=False,
        )

    with op.batch_alter_table('purchase_plans') as batch_op:
        batch_op.alter_column(
            'unit_price',
            type_=sa.Numeric(precision=10, scale=2),
            existing_type=sa.Float(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'total_amount',
            type_=sa.Numeric(precision=10, scale=2),
            existing_type=sa.Float(),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade monetary columns back to FLOAT."""
    with op.batch_alter_table('purchase_plans') as batch_op:
        batch_op.alter_column(
            'total_amount',
            type_=sa.Float(),
            existing_type=sa.Numeric(precision=10, scale=2),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'unit_price',
            type_=sa.Float(),
            existing_type=sa.Numeric(precision=10, scale=2),
            existing_nullable=False,
        )

    with op.batch_alter_table('payments') as batch_op:
        batch_op.alter_column(
            'amount',
            type_=sa.Float(),
            existing_type=sa.Numeric(precision=10, scale=2),
            existing_nullable=False,
        )

    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column(
            'amount',
            type_=sa.Float(),
            existing_type=sa.Numeric(precision=10, scale=2),
            existing_nullable=False,
        )

