"""SQLAlchemy model for Payments."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, JSON, Numeric, String
from app.db.session import Base


class PaymentModel(Base):
    """Persistent representation of Payment transactions."""

    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    purchase_plan_id = Column(String, nullable=False, index=True)
    provider = Column(String, default="PAYPAL", nullable=False)
    provider_order_id = Column(String, unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2, asdecimal=False), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(String, default="CREATED", nullable=False, index=True)
    capture_id = Column(String, nullable=True, index=True)
    payer_email = Column(String, nullable=True)
    payer_id = Column(String, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

