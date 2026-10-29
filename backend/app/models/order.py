"""SQLAlchemy model for Orders."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from app.db.session import Base


class OrderModel(Base):
    """Persistent representation of completed customer Orders."""

    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    purchase_plan_id = Column(String, unique=True, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    amount = Column(Numeric(10, 2, asdecimal=False), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(String, default="PROCESSING", nullable=False, index=True)
    paypal_order_id = Column(String, nullable=True, index=True)
    payment_id = Column(String, nullable=True, index=True)
    estimated_delivery = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

