"""SQLAlchemy model for Purchase Plans."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, Numeric, String
from app.db.session import Base


class PurchasePlanModel(Base):
    """Persistent representation of formulated Purchase Plans."""

    __tablename__ = "purchase_plans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    seller = Column(String, nullable=False)
    delivery_days = Column(Integer, default=3, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2, asdecimal=False), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    total_amount = Column(Numeric(10, 2, asdecimal=False), nullable=False)
    status = Column(String, default="AWAITING_APPROVAL", nullable=False, index=True)
    paypal_order_id = Column(String, nullable=True, index=True)
    approval_url = Column(String, nullable=True)
    recommendation_reason = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

