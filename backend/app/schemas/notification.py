"""Pydantic schemas and enums for Notifications."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NotificationType(str, Enum):
    """Notification event types."""

    ORDER_UPDATE = "ORDER_UPDATE"
    DELIVERY_DELAY = "DELIVERY_DELAY"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    SUPPORT_UPDATE = "SUPPORT_UPDATE"


class Notification(BaseModel):
    """Complete in-app notification item."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique notification ID (e.g. NOTIF-001)")
    user_id: str = Field(default="guest_user", description="Target recipient user ID")
    order_id: Optional[str] = Field(default=None, description="Related Order ID if applicable")
    type: NotificationType = Field(..., description="Notification event category")
    title: str = Field(..., description="Short notification subject")
    message: str = Field(..., description="Detailed message content")
    read: bool = Field(default=False, description="Whether the user has viewed this notification")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
