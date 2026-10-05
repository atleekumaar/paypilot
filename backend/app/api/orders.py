"""FastAPI endpoints for Order history, shipment tracking, and issue detection."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.shipment import OrderDetailResponse
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["Orders & Tracking"])


def get_order_service() -> OrderService:
    return OrderService()


@router.get("", response_model=List[OrderDetailResponse])
def list_orders(
    user_id: str = Query(default="guest_user", description="Identifier of the current user"),
    order_service: OrderService = Depends(get_order_service),
):
    """Retrieve complete order history for the authenticated user with strict user isolation."""
    return order_service.get_user_orders(user_id=user_id)


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_detail(
    order_id: str,
    user_id: Optional[str] = Query(default="guest_user", description="Identifier of the current user"),
    order_service: OrderService = Depends(get_order_service),
):
    """Retrieve single order detail with strict user isolation and shipment milestones."""
    return order_service.get_order(order_id=order_id, user_id=user_id)


@router.get("/{order_id}/tracking")
def get_order_tracking(
    order_id: str,
    user_id: Optional[str] = Query(default="guest_user", description="Identifier of the current user"),
    order_service: OrderService = Depends(get_order_service),
):
    """Fetch real-time tracking status, carrier information, and shipment timeline."""
    return order_service.get_tracking(query=order_id, user_id=user_id)


@router.get("/{order_id}/issues")
def check_order_issues(
    order_id: str,
    user_id: Optional[str] = Query(default="guest_user", description="Identifier of the current user"),
    reference_date: Optional[str] = Query(default=None, description="Optional reference date (YYYY-MM-DD) for simulation"),
    order_service: OrderService = Depends(get_order_service),
):
    """Deterministic issue detector evaluating delivery delays, carrier notes, and milestones."""
    return order_service.detect_order_issue(
        order_id=order_id,
        user_id=user_id,
        reference_date_str=reference_date,
    )
