"""Notification service boundary for proactive user alerts and notification history."""

from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional
import uuid

from fastapi import HTTPException, status

from app.db.session import get_db_context, init_db
from app.models.notification import NotificationModel
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


def _model_to_schema(m: NotificationModel) -> Notification:
    return Notification(
        id=m.id,
        user_id=m.user_id,
        order_id=m.order_id,
        type=NotificationType(m.type),
        title=m.title,
        message=m.message,
        read=m.read,
        created_at=m.created_at,
    )


class NotificationService:
    """Database-backed notification store and dispatcher."""

    def __init__(self, populate_defaults: bool = True):
        init_db()
        if populate_defaults:
            with get_db_context() as db:
                if db.query(NotificationModel).count() == 0:
                    for notif in _build_default_demo_notifications().values():
                        db.merge(NotificationModel(
                            id=notif.id,
                            user_id=notif.user_id,
                            order_id=notif.order_id,
                            type=notif.type.value if hasattr(notif.type, "value") else str(notif.type),
                            title=notif.title,
                            message=notif.message,
                            read=notif.read,
                            created_at=notif.created_at,
                        ))

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
        with get_db_context() as db:
            m = NotificationModel(
                id=notif.id,
                user_id=notif.user_id,
                order_id=notif.order_id,
                type=notif.type.value if hasattr(notif.type, "value") else str(notif.type),
                title=notif.title,
                message=notif.message,
                read=notif.read,
                created_at=notif.created_at,
            )
            db.merge(m)
        logger.info(f"Notification created: [{notif.type}] {notif.title} for user {user_id}")
        return notif

    def list_user_notifications(self, user_id: str) -> List[Notification]:
        """Fetch all notifications for the given user ordered newest first."""
        with get_db_context() as db:
            records = (
                db.query(NotificationModel)
                .filter(NotificationModel.user_id == user_id)
                .order_by(NotificationModel.created_at.desc())
                .all()
            )
            return [_model_to_schema(m) for m in records]

    def mark_as_read(self, notification_id: str, user_id: str) -> Notification:
        """Mark a notification as read with user verification."""
        with get_db_context() as db:
            m = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
            if not m:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Notification '{notification_id}' not found.",
                )
            if m.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this notification.",
                )
            m.read = True
            return _model_to_schema(m)

    def reset_defaults(self) -> None:
        """Reset notifications to default demo set."""
        with get_db_context() as db:
            db.query(NotificationModel).delete()
            for notif in _build_default_demo_notifications().values():
                db.merge(NotificationModel(
                    id=notif.id,
                    user_id=notif.user_id,
                    order_id=notif.order_id,
                    type=notif.type.value if hasattr(notif.type, "value") else str(notif.type),
                    title=notif.title,
                    message=notif.message,
                    read=notif.read,
                    created_at=notif.created_at,
                ))

    def clear(self) -> None:
        with get_db_context() as db:
            db.query(NotificationModel).delete()


_notification_service_instance: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = NotificationService()
    return _notification_service_instance
