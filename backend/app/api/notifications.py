"""FastAPI endpoints for in-app Notifications."""

from typing import List

from fastapi import APIRouter, Depends, Query

from app.schemas.notification import Notification
from app.services.notification_service import NotificationService, get_notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=List[Notification])
def list_notifications(
    user_id: str = Query(default="guest_user", description="Identifier of the user"),
    service: NotificationService = Depends(get_notification_service),
):
    """Retrieve all notifications for the user."""
    return service.list_user_notifications(user_id=user_id)


@router.post("/{notification_id}/read", response_model=Notification)
def mark_read(
    notification_id: str,
    user_id: str = Query(default="guest_user", description="Identifier of the user"),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as read."""
    return service.mark_as_read(notification_id=notification_id, user_id=user_id)
