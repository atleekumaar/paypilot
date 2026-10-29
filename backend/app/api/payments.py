"""PayPal Payments and Checkout API endpoints."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.payment import Payment
from app.services.checkout_service import CheckoutService

router = APIRouter(prefix="/api/payments", tags=["Payments"])


class PayPalCreateOrderRequest(BaseModel):
    """Request payload to initiate a PayPal checkout order."""

    purchase_plan_id: str = Field(
        ...,
        description="ID of the approved Purchase Plan (e.g. PP-8F92A1)",
        json_schema_extra={"example": "PP-8F92A1"},
    )


class PayPalCreateOrderResponse(BaseModel):
    """Response payload containing generated PayPal Order ID and buyer approval URL."""

    purchase_plan_id: str
    paypal_order_id: str
    status: str
    approval_url: Optional[str] = Field(
        default=None,
        description="Real PayPal buyer-approval URL for Sandbox authorization",
    )


class PayPalCaptureRequest(BaseModel):
    """Request payload to capture an approved PayPal Order."""

    purchase_plan_id: str = Field(
        ...,
        description="Associated Purchase Plan ID",
        json_schema_extra={"example": "PP-8F92A1"},
    )
    paypal_order_id: str = Field(
        ...,
        description="PayPal Order ID approved by the buyer",
        json_schema_extra={"example": "7AB12345XYZ"},
    )


@router.post(
    "/paypal/create-order",
    response_model=PayPalCreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create PayPal Checkout Order",
    description="Validates that the Purchase Plan is explicitly APPROVED and creates a PayPal Sandbox order using authoritative backend pricing.",
)
async def create_paypal_order(
    request: PayPalCreateOrderRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PayPalCreateOrderResponse:
    """Create PayPal order for approved purchase plan."""
    service = CheckoutService()
    result = service.create_paypal_order_for_plan(
        purchase_plan_id=request.purchase_plan_id,
        user_id=current_user.id,
    )
    return PayPalCreateOrderResponse(**result)


@router.post(
    "/paypal/capture",
    response_model=Payment,
    status_code=status.HTTP_200_OK,
    summary="Capture PayPal Order Payment",
    description="Verifies the PayPal Order ID matches the internal Purchase Plan, executes capture via PayPal API, and returns verified payment details.",
)
async def capture_paypal_payment(
    request: PayPalCaptureRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Payment:
    """Capture payment and verify completion."""
    service = CheckoutService()
    return service.capture_paypal_payment(
        purchase_plan_id=request.purchase_plan_id,
        paypal_order_id=request.paypal_order_id,
        user_id=current_user.id,
    )


@router.get(
    "/{payment_id}",
    response_model=Payment,
    summary="Get Payment transaction details",
)
async def get_payment(
    payment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Payment:
    """Retrieve payment record by ID."""
    service = CheckoutService()
    return service.get_payment(payment_id, user_id=current_user.id)


@router.get(
    "/by-plan/{plan_id}",
    response_model=Payment,
    summary="Get Payment transaction by Purchase Plan ID",
)
async def get_payment_by_plan(
    plan_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Payment:
    """Retrieve payment record for a given purchase plan."""
    service = CheckoutService()
    return service.get_payment_by_plan(plan_id, user_id=current_user.id)
