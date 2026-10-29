"""FastAPI endpoints for in-app Notifications."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import AuthenticatedUser, get_current_user, verify_user_ownership
from app.schemas.notification import Notification
from app.services.notification_service import NotificationService, get_notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=List[Notification])
def list_notifications(
    user_id: Optional[str] = Query(default=None, description="Identifier of the user"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Retrieve all notifications for the user."""
    verify_user_ownership(current_user, user_id)
    return service.list_user_notifications(user_id=current_user.id)


@router.post("/{notification_id}/read", response_model=Notification)
def mark_read(
    notification_id: str,
    user_id: Optional[str] = Query(default=None, description="Identifier of the user"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as read."""
    verify_user_ownership(current_user, user_id)
    return service.mark_as_read(notification_id=notification_id, user_id=current_user.id)
