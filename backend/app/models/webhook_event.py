"""SQLAlchemy model for Webhook Events (Replay Prevention & Audit)."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, JSON, String
from app.db.session import Base


class WebhookEventModel(Base):
    """Audit and deduplication record for incoming provider webhooks (e.g. PayPal)."""

    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True)  # Provider event ID (e.g. WH-12345)
    provider = Column(String, default="PAYPAL", nullable=False)
    event_type = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True, index=True)
    status = Column(String, default="PROCESSED", nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

