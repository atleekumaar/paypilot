"""Commerce Timeline API endpoints powered by Bryntum data specifications."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query, status

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/api/timeline", tags=["Timeline"])


@router.get(
    "/events",
    summary="Get Commerce Timeline Events & Resources",
    description="Returns Bryntum-compatible resources and events representing order approvals, PayPal captures, merchant fulfillment, carrier logistics, and refund milestones.",
    status_code=status.HTTP_200_OK,
)
async def get_timeline_events(
    order_id: Optional[str] = Query(default=None, description="Filter timeline events for a specific order"),
    event_type: Optional[str] = Query(default=None, description="Filter by event type (APPROVAL, PAYMENT, FULFILLMENT, IN_TRANSIT, DELIVERY, REFUND)"),
    start_date: Optional[str] = Query(default=None, description="Earliest event start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Latest event end date filter (YYYY-MM-DD)"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
) -> Dict[str, Any]:
    """Retrieve full Bryntum-ready commerce timeline store."""
    return timeline_service.get_timeline(
        user_id=current_user.id,
        order_id=order_id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/summary",
    summary="Get Commerce Timeline Summary & Upcoming Milestones",
    description="Returns aggregate counts of active shipments, pending payments, and nearest upcoming delivery date.",
    status_code=status.HTTP_200_OK,
)
async def get_timeline_summary(
    current_user: AuthenticatedUser = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
) -> Dict[str, Any]:
    """Retrieve high-level schedule and logistics KPI summary."""
    return timeline_service.get_summary(user_id=current_user.id)

