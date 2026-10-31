"""PayPal Payments and Checkout API endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, Request, status
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


class PaymentRefundRequest(BaseModel):
    """Request payload to initiate a full or partial refund."""

    amount: Optional[float] = Field(
        default=None,
        description="Optional partial refund amount in USD. If omitted, full amount is refunded.",
        json_schema_extra={"example": 50.0},
    )


@router.post(
    "/{payment_id}/refund",
    response_model=Payment,
    summary="Refund Completed Payment",
    description="Processes a full or partial refund for a completed payment with authenticated ownership validation.",
)
async def refund_payment(
    payment_id: str,
    request: Optional[PaymentRefundRequest] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Payment:
    """Refund payment."""
    service = CheckoutService()
    amt = request.amount if request else None
    return service.refund_payment(payment_id, amount=amt, user_id=current_user.id)


@router.get(
    "/reconciliation/report",
    response_model=List[Dict[str, Any]],
    summary="Reconcile In-Flight or Pending Payments",
    description="Scans for payments stuck in CAPTURE_PENDING or RECONCILIATION_REQUIRED and syncs with provider status.",
)
async def reconcile_payments(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Reconcile payments."""
    service = CheckoutService()
    return service.reconcile_payments()


@router.post(
    "/paypal/webhook",
    status_code=status.HTTP_200_OK,
    summary="PayPal Webhook Event Receiver",
    description="Idempotent receiver with replay prevention for incoming asynchronous PayPal notifications.",
)
async def paypal_webhook(
    request: Request,
) -> Dict[str, Any]:
    """Process PayPal webhook event with replay protection."""
    payload = await request.json()
    headers = dict(request.headers)
    service = CheckoutService()
    return service.process_paypal_webhook(headers=headers, payload=payload)
