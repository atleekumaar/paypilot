"""PayPal Payments and Checkout API endpoints."""

from typing import Any, Dict
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

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
    """Response payload containing generated PayPal Order ID."""

    purchase_plan_id: str
    paypal_order_id: str
    status: str


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
async def create_paypal_order(request: PayPalCreateOrderRequest) -> PayPalCreateOrderResponse:
    """Create PayPal order for approved purchase plan."""
    service = CheckoutService()
    result = service.create_paypal_order_for_plan(request.purchase_plan_id)
    return PayPalCreateOrderResponse(**result)


@router.post(
    "/paypal/capture",
    response_model=Payment,
    status_code=status.HTTP_200_OK,
    summary="Capture PayPal Order Payment",
    description="Verifies the PayPal Order ID matches the internal Purchase Plan, executes capture via PayPal API, and returns verified payment details.",
)
async def capture_paypal_payment(request: PayPalCaptureRequest) -> Payment:
    """Capture payment and verify completion."""
    service = CheckoutService()
    return service.capture_paypal_payment(
        purchase_plan_id=request.purchase_plan_id,
        paypal_order_id=request.paypal_order_id,
    )


@router.get(
    "/{payment_id}",
    response_model=Payment,
    summary="Get Payment transaction details",
)
async def get_payment(payment_id: str) -> Payment:
    """Retrieve payment record by ID."""
    service = CheckoutService()
    return service.get_payment(payment_id)


@router.get(
    "/by-plan/{plan_id}",
    response_model=Payment,
    summary="Get Payment transaction by Purchase Plan ID",
)
async def get_payment_by_plan(plan_id: str) -> Payment:
    """Retrieve payment record for a given purchase plan."""
    service = CheckoutService()
    return service.get_payment_by_plan(plan_id)
