"""SQLAlchemy model for Refund Attempts (Idempotent Ledger)."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, JSON, Numeric, String, Text
from app.db.session import Base


class RefundAttemptModel(Base):
    """Persistent audit and idempotency ledger for payment refunds."""

    __tablename__ = "refund_attempts"

    id = Column(String, primary_key=True, default=lambda: f"ref_{uuid.uuid4().hex[:12]}")
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    provider = Column(String, default="PAYPAL", nullable=False)
    provider_capture_id = Column(String, nullable=False, index=True)
    provider_refund_id = Column(String, nullable=True, unique=True, index=True)
    idempotency_key = Column(String, nullable=False, unique=True, index=True)
    requested_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(String, nullable=False, index=True)  # PENDING, COMPLETED, FAILED, RECONCILIATION_REQUIRED
    provider_response = Column(JSON, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)

