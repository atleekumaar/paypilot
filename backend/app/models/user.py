"""SQLAlchemy model for Users / Identity references."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from app.db.session import Base


class UserModel(Base):
    """Persistent user identity representation."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

