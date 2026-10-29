"""SQLAlchemy model for Shipments and logistics tracking."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, JSON, String
from app.db.session import Base


class ShipmentModel(Base):
    """Persistent representation of shipment carrier tracking."""

    __tablename__ = "shipments"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, unique=True, nullable=False, index=True)
    tracking_number = Column(String, nullable=False, index=True)
    carrier = Column(String, nullable=False)
    status = Column(String, default="LABEL_CREATED", nullable=False, index=True)
    estimated_delivery = Column(String, nullable=True)
    actual_delivery = Column(String, nullable=True)
    last_location = Column(String, nullable=True)
    last_update = Column(String, nullable=True)
    timeline = Column(JSON, default=list)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

