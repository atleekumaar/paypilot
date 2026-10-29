"""SQLAlchemy model for in-app Notifications."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, String
from app.db.session import Base


class NotificationModel(Base):
    """Persistent representation of user alerts and notifications."""

    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    order_id = Column(String, nullable=True, index=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

