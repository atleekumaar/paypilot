"""Checkout and payment processing service coordinating Purchase Plans with PayPal."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional
import uuid

from fastapi import HTTPException, status

from app.repositories.payment_repository import PaymentRepository, get_payment_repository
from app.repositories.product_repository import ProductRepository, get_product_repository
from app.repositories.purchase_plan_repository import (
    PurchasePlanRepository,
    get_purchase_plan_repository,
)
from app.schemas.payment import Payment, PaymentProvider, PaymentStatus
from app.schemas.purchase_plan import PurchasePlan, PurchasePlanStatus
from app.services.paypal.orders import PayPalOrderService

logger = logging.getLogger(__name__)


class CheckoutService:
    """Manages secure payment creation and capture workflows with PayPal Sandbox."""

    def __init__(
        self,
        plan_repo: Optional[PurchasePlanRepository] = None,
        payment_repo: Optional[PaymentRepository] = None,
        product_repo: Optional[ProductRepository] = None,
        paypal_order_service: Optional[PayPalOrderService] = None,
    ):
        self._plan_repo = plan_repo or get_purchase_plan_repository()
        self._payment_repo = payment_repo or get_payment_repository()
        self._product_repo = product_repo or get_product_repository()
        self._paypal = paypal_order_service or PayPalOrderService()

    def create_paypal_order_for_plan(self, purchase_plan_id: str) -> Dict[str, Any]:
        """Create a PayPal Sandbox order for an approved Purchase Plan.

        Critical Invariant:
        Unapproved plans (status != APPROVED) CANNOT initiate a PayPal order.
        """
        plan = self._plan_repo.get_by_id(purchase_plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Plan '{purchase_plan_id}' not found.",
            )

        # Idempotent re-use if already created and pending approval
        if (
            plan.status == PurchasePlanStatus.PAYPAL_APPROVAL_PENDING
            and plan.paypal_order_id
        ):
            return {
                "purchase_plan_id": plan.id,
                "paypal_order_id": plan.paypal_order_id,
                "status": plan.status.value,
            }

        # Strictly enforce approval gate
        if plan.status != PurchasePlanStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase Plan must be explicitly APPROVED before checkout. Current status: '{plan.status}'.",
            )

        # Verify inventory before initiating payment
        product = self._product_repo.get_by_id(plan.product_id)
        if not product or not product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is no longer available in stock.",
            )

        # Create authoritative PayPal Order
        order_response = self._paypal.create_order(plan)
        paypal_order_id = order_response.get("id")
        if not paypal_order_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="PayPal service did not return an Order ID.",
            )

        # Update Purchase Plan state
        plan.paypal_order_id = paypal_order_id
        plan.status = PurchasePlanStatus.PAYPAL_APPROVAL_PENDING
        plan.updated_at = datetime.now(timezone.utc)
        self._plan_repo.update(plan)

        # Record internal payment state
        payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        payment = Payment(
            id=payment_id,
            purchase_plan_id=plan.id,
            provider=PaymentProvider.PAYPAL,
            provider_order_id=paypal_order_id,
            amount=plan.total_amount,
            currency=plan.currency,
            status=PaymentStatus.APPROVAL_PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._payment_repo.create(payment)

        logger.info(
            f"PayPal order created: Plan ID: {plan.id}, PayPal Order: {paypal_order_id}"
        )

        return {
            "purchase_plan_id": plan.id,
            "paypal_order_id": paypal_order_id,
            "status": plan.status.value,
        }

    def capture_paypal_payment(
        self, purchase_plan_id: str, paypal_order_id: str
    ) -> Payment:
        """Capture payment for an approved PayPal Order and verify transaction integrity.

        Critical Invariants:
        1. paypal_order_id MUST match purchase_plan.paypal_order_id.
        2. Idempotent: repeated calls do NOT double capture.
        3. Payment status is marked COMPLETED only when verified by PayPal API.
        """
        plan = self._plan_repo.get_by_id(purchase_plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Plan '{purchase_plan_id}' not found.",
            )

        # Security check: Order ownership mismatch protection
        if plan.paypal_order_id != paypal_order_id:
            logger.warning(
                f"Security mismatch: Plan {purchase_plan_id} associated with {plan.paypal_order_id}, but capture requested with {paypal_order_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided PayPal Order ID does not match the associated Purchase Plan.",
            )

        # Idempotency check: avoid double-capturing
        existing_payment = self._payment_repo.get_by_provider_order_id(paypal_order_id)
        if existing_payment and existing_payment.status == PaymentStatus.COMPLETED:
            logger.info(f"Idempotent capture request for already completed order {paypal_order_id}")
            return existing_payment

        # Execute PayPal Capture via API
        capture_response = self._paypal.capture_order(paypal_order_id)
        capture_status = capture_response.get("status")

        if capture_status != "COMPLETED":
            logger.error(f"PayPal capture failed or returned unexpected status: {capture_status}")
            if existing_payment:
                existing_payment.status = PaymentStatus.FAILED
                existing_payment.updated_at = datetime.now(timezone.utc)
                self._payment_repo.update(existing_payment)
            plan.status = PurchasePlanStatus.FAILED
            self._plan_repo.update(plan)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment capture failed with status '{capture_status}'.",
            )

        # Extract capture details safely
        capture_id = None
        units = capture_response.get("purchase_units", [])
        if units and "payments" in units[0] and "captures" in units[0]["payments"]:
            captures = units[0]["payments"]["captures"]
            if captures:
                capture_id = captures[0].get("id")

        payer_info = capture_response.get("payer", {})
        payer_email = payer_info.get("email_address")
        payer_id = payer_info.get("payer_id")

        # Update or create payment record
        if existing_payment:
            payment = existing_payment
            payment.status = PaymentStatus.COMPLETED
            payment.capture_id = capture_id
            payment.payer_email = payer_email
            payment.payer_id = payer_id
            payment.metadata = capture_response
            payment.updated_at = datetime.now(timezone.utc)
            self._payment_repo.update(payment)
        else:
            payment = Payment(
                id=f"PAY-{uuid.uuid4().hex[:8].upper()}",
                purchase_plan_id=plan.id,
                provider=PaymentProvider.PAYPAL,
                provider_order_id=paypal_order_id,
                amount=plan.total_amount,
                currency=plan.currency,
                status=PaymentStatus.COMPLETED,
                capture_id=capture_id,
                payer_email=payer_email,
                payer_id=payer_id,
                metadata=capture_response,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self._payment_repo.create(payment)

        # Update Purchase Plan to COMPLETED
        plan.status = PurchasePlanStatus.COMPLETED
        plan.updated_at = datetime.now(timezone.utc)
        self._plan_repo.update(plan)

        # Seamlessly create Order and Shipment for Post-Purchase Agent
        try:
            from app.services.order_service import OrderService
            order_svc = OrderService()
            order_svc.create_order_from_purchase(
                purchase_plan_id=plan.id,
                user_id=plan.user_id,
                product_id=plan.product_id,
                product_name=plan.product_name,
                brand=plan.brand,
                quantity=plan.quantity,
                amount=plan.total_amount,
                currency=plan.currency,
                paypal_order_id=paypal_order_id,
                payment_id=payment.id,
                delivery_days=plan.delivery_days,
            )
        except Exception as e:
            logger.warning(f"Could not automatically create order on capture: {e}")

        logger.info(
            f"Payment capture completed successfully. Plan: {plan.id}, Amount: {plan.total_amount} {plan.currency}"
        )
        return payment

    def get_payment(self, payment_id: str) -> Payment:
        """Fetch payment details by payment ID."""
        payment = self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment '{payment_id}' not found.",
            )
        return payment

    def get_payment_by_plan(self, plan_id: str) -> Payment:
        """Fetch payment details by purchase plan ID."""
        payment = self._payment_repo.get_by_plan_id(plan_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No payment record found for Purchase Plan '{plan_id}'.",
            )
        return payment
