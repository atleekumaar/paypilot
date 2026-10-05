"""Notification service boundary for proactive user alerts and notification history."""

from datetime import datetime, timezone
import logging
import threading
from typing import Dict, List, Optional
import uuid

from fastapi import HTTPException, status

from app.schemas.notification import Notification, NotificationType

logger = logging.getLogger(__name__)


def _build_default_demo_notifications() -> Dict[str, Notification]:
    """Generates initial realistic demo notifications for the hackathon."""
    return {
        "NOTIF-001": Notification(
            id="NOTIF-001",
            user_id="guest_user",
            order_id="ORD-001",
            type=NotificationType.ORDER_UPDATE,
            title="📦 Your order has shipped",
            message="NovaBook Pro 14 has departed the facility with FastShip Logistics (TRK-FAST-884210).",
            read=True,
            created_at=datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc),
        ),
        "NOTIF-002": Notification(
            id="NOTIF-002",
            user_id="guest_user",
            order_id="ORD-001",
            type=NotificationType.DELIVERY_DELAY,
            title="⚠️ Delivery may be delayed",
            message="Carrier reported a regional logistics delay for order ORD-001. Estimated delivery is Oct 18.",
            read=False,
            created_at=datetime(2026, 10, 16, 9, 30, tzinfo=timezone.utc),
        ),
        "NOTIF-003": Notification(
            id="NOTIF-003",
            user_id="guest_user",
            order_id="ORD-003",
            type=NotificationType.PAYMENT_COMPLETED,
            title="💳 Payment completed",
            message="PayPal payment for VisionBook Studio 16 ($1,150.00 USD) was successfully captured.",
            read=False,
            created_at=datetime(2026, 10, 19, 11, 48, tzinfo=timezone.utc),
        ),
    }


class NotificationService:
    """Thread-safe notification store and dispatcher."""

    def __init__(self, populate_defaults: bool = True):
        self._lock = threading.Lock()
        self._notifications: Dict[str, Notification] = _build_default_demo_notifications() if populate_defaults else {}

    def notify(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        order_id: Optional[str] = None,
    ) -> Notification:
        """Create and dispatch a new in-app notification."""
        notif_id = f"NOTIF-{uuid.uuid4().hex[:6].upper()}"
        notif = Notification(
            id=notif_id,
            user_id=user_id,
            order_id=order_id,
            type=type,
            title=title,
            message=message,
            read=False,
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._notifications[notif.id] = notif
        logger.info(f"Notification created: [{notif.type}] {notif.title} for user {user_id}")
        return notif

    def list_user_notifications(self, user_id: str) -> List[Notification]:
        """Fetch all notifications for the given user ordered newest first."""
        with self._lock:
            return sorted(
                [n for n in self._notifications.values() if n.user_id == user_id],
                key=lambda n: n.created_at,
                reverse=True,
            )

    def mark_as_read(self, notification_id: str, user_id: str) -> Notification:
        """Mark a notification as read with user verification."""
        with self._lock:
            notif = self._notifications.get(notification_id)
            if not notif:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Notification '{notification_id}' not found.",
                )
            if notif.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this notification.",
                )
            notif.read = True
            return notif

    def reset_defaults(self) -> None:
        with self._lock:
            self._notifications = _build_default_demo_notifications()

    def clear(self) -> None:
        with self._lock:
            self._notifications.clear()


_notification_service_instance: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = NotificationService()
    return _notification_service_instance
