"""Checkout and payment processing service coordinating Purchase Plans with PayPal."""

from collections import defaultdict
from datetime import datetime, timezone
import logging
import threading
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

    _order_locks = defaultdict(threading.Lock)
    _lock_manager_lock = threading.Lock()

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

    @classmethod
    def _get_order_lock(cls, order_id: str) -> threading.Lock:
        with cls._lock_manager_lock:
            return cls._order_locks[order_id]

    def create_paypal_order_for_plan(
        self, purchase_plan_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a PayPal Sandbox order for an approved Purchase Plan.

        Critical Invariants:
        1. Unapproved plans (status != APPROVED) CANNOT initiate a PayPal order.
        2. Plan must belong to authenticated user (user isolation).
        3. Inventory and price must be strictly revalidated; if price changed,
           reverts to AWAITING_APPROVAL and requires renewed user approval.
        4. Real PayPal buyer-approval URL returned for redirecting the buyer.
        """
        plan = self._plan_repo.get_by_id(purchase_plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Plan '{purchase_plan_id}' not found.",
            )

        if user_id and plan.user_id != user_id:
            logger.warning(
                f"Unauthorized checkout attempt: user '{user_id}' requested plan '{plan.id}' owned by '{plan.user_id}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You do not have permission to checkout Purchase Plan '{purchase_plan_id}'.",
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
                "approval_url": plan.approval_url,
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
            plan.status = PurchasePlanStatus.FAILED
            self._plan_repo.update(plan)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is no longer available in stock.",
            )

        # Revalidate price before checkout: if price changed, require renewed user approval!
        if product.price != plan.unit_price:
            old_price = plan.unit_price
            plan.unit_price = product.price
            plan.total_amount = round(product.price * plan.quantity, 2)
            plan.status = PurchasePlanStatus.AWAITING_APPROVAL
            plan.updated_at = datetime.now(timezone.utc)
            self._plan_repo.update(plan)
            logger.warning(
                f"Price changed for plan {plan.id}: was ${old_price:.2f}, now ${product.price:.2f}. Reverting to AWAITING_APPROVAL."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product price has changed from ${old_price:.2f} to ${product.price:.2f}. Renewed user approval is required.",
            )

        # Create authoritative PayPal Order
        try:
            order_response = self._paypal.create_order(plan)
        except RuntimeError as e:
            logger.error(f"PayPal order creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment provider error creating order: {e}",
            )

        paypal_order_id = order_response.get("id")
        if not paypal_order_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="PayPal service did not return an Order ID.",
            )

        # Extract buyer-approval URL from provider links
        approval_url = None
        for link in order_response.get("links", []):
            if link.get("rel") in ("approve", "payer-action"):
                approval_url = link.get("href")
                break

        # Fallback sandbox URL if links missing from response
        if not approval_url:
            approval_url = f"https://www.sandbox.paypal.com/checkoutnow?token={paypal_order_id}"

        # Update Purchase Plan state
        plan.paypal_order_id = paypal_order_id
        plan.approval_url = approval_url
        plan.status = PurchasePlanStatus.PAYPAL_APPROVAL_PENDING
        plan.updated_at = datetime.now(timezone.utc)
        self._plan_repo.update(plan)

        # Record internal payment state
        payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        payment = Payment(
            id=payment_id,
            user_id=plan.user_id,
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
            f"PayPal order created: Plan ID: {plan.id}, PayPal Order: {paypal_order_id}, Approval URL: {approval_url}"
        )

        return {
            "purchase_plan_id": plan.id,
            "paypal_order_id": paypal_order_id,
            "status": plan.status.value,
            "approval_url": approval_url,
        }

    def capture_paypal_payment(
        self, purchase_plan_id: str, paypal_order_id: str, user_id: Optional[str] = None
    ) -> Payment:
        """Capture payment for an approved PayPal Order and verify transaction integrity.

        Critical Invariants:
        1. Authenticated user ownership of purchase plan.
        2. paypal_order_id MUST match purchase_plan.paypal_order_id.
        3. Server-side verification of provider order ID, purchase plan association,
           amount, currency, and buyer approval status.
        4. Idempotent: repeated or concurrent calls do NOT double capture.
        5. Ambiguous timeouts are handled safely without marking unverified transactions COMPLETED.
        """
        plan = self._plan_repo.get_by_id(purchase_plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Plan '{purchase_plan_id}' not found.",
            )

        # User isolation check
        if user_id and plan.user_id != user_id:
            logger.warning(
                f"Unauthorized capture attempt: user '{user_id}' attempted capture on plan '{plan.id}' owned by '{plan.user_id}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You do not have permission to capture payment for Purchase Plan '{purchase_plan_id}'.",
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

        # Thread synchronization per paypal_order_id to prevent concurrent double-capture races
        with self._get_order_lock(paypal_order_id):
            # Double check idempotency after acquiring lock
            existing_payment = self._payment_repo.get_by_provider_order_id(paypal_order_id)
            if existing_payment and existing_payment.status == PaymentStatus.COMPLETED:
                logger.info(f"Idempotent capture request for order {paypal_order_id} caught under lock")
                return existing_payment

            # Step 1: Server-side verification of the provider order
            try:
                order_details = self._paypal.get_order_details(paypal_order_id)
            except TimeoutError as exc:
                logger.error(f"Timeout querying PayPal order details: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"PayPal API timeout while querying order details: {exc}",
                )
            except Exception as exc:
                logger.error(f"Failed to fetch PayPal order details: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid PayPal order ID or error from payment provider: {exc}",
                )

            # Verification A: Provider order ID
            if order_details.get("id") != paypal_order_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provider order ID does not match the requested order.",
                )

            # Verification B: Purchase-plan association
            units = order_details.get("purchase_units", [])
            if not units:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PayPal order contains no purchase units.",
                )

            unit = units[0]
            unit_ref = unit.get("reference_id")
            if unit_ref and unit_ref != plan.id and unit_ref != "PP-DEFAULT":
                logger.warning(
                    f"Plan association mismatch: PayPal order reference_id '{unit_ref}' does not match plan '{plan.id}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PayPal order reference_id '{unit_ref}' does not match Purchase Plan '{plan.id}'.",
                )

            # Verification C: Amount verification
            unit_amt = unit.get("amount", {})
            val_str = str(unit_amt.get("value", ""))
            try:
                provider_amount = float(val_str)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not parse authorized amount from PayPal order.",
                )

            if round(provider_amount, 2) != round(plan.total_amount, 2):
                logger.warning(
                    f"Amount mismatch: Provider order amount ${provider_amount:.2f} != plan total ${plan.total_amount:.2f}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Amount mismatch: PayPal order amount ${provider_amount:.2f} does not match plan amount ${plan.total_amount:.2f}.",
                )

            # Verification D: Currency verification
            provider_currency = unit_amt.get("currency_code", "").upper()
            if provider_currency and provider_currency != plan.currency.upper():
                logger.warning(
                    f"Currency mismatch: Provider currency '{provider_currency}' != plan currency '{plan.currency}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Currency mismatch: PayPal order currency '{provider_currency}' does not match plan currency '{plan.currency}'.",
                )

            # Verification E: Buyer approval status
            provider_status = order_details.get("status")
            if provider_status == "COMPLETED":
                logger.info(f"PayPal order {paypal_order_id} is already completed in PayPal.")
                capture_response = order_details
            elif provider_status != "APPROVED":
                logger.warning(
                    f"PayPal order {paypal_order_id} capture rejected: Provider status is '{provider_status}' (not APPROVED)."
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PayPal order is not approved for capture. Current provider status: '{provider_status}'. Buyer approval required.",
                )
            else:
                # Step 2: Execute PayPal Capture via API with ambiguous timeout safety
                try:
                    capture_response = self._paypal.capture_order(paypal_order_id)
                except TimeoutError as exc:
                    logger.error(f"Ambiguous timeout executing PayPal capture for {paypal_order_id}: {exc}")
                    # Attempt recovery verification without assuming completed
                    try:
                        recovery_details = self._paypal.get_order_details(paypal_order_id)
                        if recovery_details.get("status") == "COMPLETED":
                            capture_response = recovery_details
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                                detail="Payment provider timeout during capture. Transaction status remains unverified; please retry capture.",
                            )
                    except HTTPException:
                        raise
                    except Exception:
                        raise HTTPException(
                            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                            detail="Payment provider timeout during capture. Transaction status remains unverified; please retry capture.",
                        )
                except Exception as exc:
                    logger.error(f"PayPal capture execution failed: {exc}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Payment provider error during capture: {exc}",
                    )

            capture_status = capture_response.get("status")
            if capture_status != "COMPLETED":
                logger.error(f"PayPal capture returned unexpected status: {capture_status}")
                if existing_payment:
                    existing_payment.status = PaymentStatus.FAILED
                    existing_payment.updated_at = datetime.now(timezone.utc)
                    self._payment_repo.update(existing_payment)
                plan.status = PurchasePlanStatus.FAILED
                self._plan_repo.update(plan)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment capture failed with provider status '{capture_status}'.",
                )

            # Extract capture details safely
            capture_id = None
            units_resp = capture_response.get("purchase_units", [])
            if units_resp and "payments" in units_resp[0] and "captures" in units_resp[0]["payments"]:
                captures = units_resp[0]["payments"]["captures"]
                if captures:
                    capture_id = captures[0].get("id")

            payer_info = capture_response.get("payer", {})
            payer_email = payer_info.get("email_address")
            payer_id = payer_info.get("payer_id")

            # Update or create payment record
            if existing_payment:
                payment = existing_payment
                payment.user_id = plan.user_id
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
                    user_id=plan.user_id,
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

    def get_payment(self, payment_id: str, user_id: Optional[str] = None) -> Payment:
        """Fetch payment details by payment ID with user isolation."""
        payment = self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment '{payment_id}' not found.",
            )
        if user_id and payment.user_id and payment.user_id != user_id:
            logger.warning(
                f"Unauthorized payment access: user '{user_id}' requested payment '{payment.id}' owned by '{payment.user_id}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You do not have permission to view payment '{payment_id}'.",
            )
        return payment

    def get_payment_by_plan(self, plan_id: str, user_id: Optional[str] = None) -> Payment:
        """Fetch payment details by purchase plan ID with user isolation."""
        plan = self._plan_repo.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Plan '{plan_id}' not found.",
            )
        if user_id and plan.user_id != user_id:
            logger.warning(
                f"Unauthorized payment access: user '{user_id}' requested payment for plan '{plan.id}' owned by '{plan.user_id}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You do not have permission to view payment for plan '{plan_id}'.",
            )
        payment = self._payment_repo.get_by_plan_id(plan_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No payment record found for Purchase Plan '{plan_id}'.",
            )
        return payment
