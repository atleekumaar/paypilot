"""SQLAlchemy model for Transactional Outbox pattern."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, Integer, JSON, String
from app.db.session import Base


class OutboxEventModel(Base):
    """Transactional outbox event to guarantee reliable messaging/side-effects."""

    __tablename__ = "outbox_events"

    id = Column(String, primary_key=True, default=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type = Column(String, nullable=False, index=True)  # e.g., "order.created", "notification.dispatched"
    aggregate_type = Column(String, nullable=False, index=True)  # e.g., "payment", "order"
    aggregate_id = Column(String, nullable=False, index=True)  # e.g., payment_id
    payload = Column(JSON, nullable=False)
    status = Column(String, default="PENDING", nullable=False, index=True)  # PENDING, PROCESSING, PROCESSED, FAILED
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=5, nullable=False)
    error_message = Column(String, nullable=True)
    leased_until = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime, nullable=True)

