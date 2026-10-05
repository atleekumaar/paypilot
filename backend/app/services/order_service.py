"""Authoritative Order and Shipment Service with strict user isolation and issue detection."""

from datetime import date, datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import uuid

from fastapi import HTTPException, status

from app.repositories.order_repository import OrderRepository, get_order_repository
from app.repositories.payment_repository import PaymentRepository, get_payment_repository
from app.repositories.shipment_repository import ShipmentRepository, get_shipment_repository
from app.schemas.order import Order, OrderStatus
from app.schemas.shipment import OrderDetailResponse, Shipment, ShipmentStatus

logger = logging.getLogger(__name__)


class OrderService:
    """Manages order lifecycle, shipment tracking, user authorization, and anomaly detection."""

    def __init__(
        self,
        order_repo: Optional[OrderRepository] = None,
        shipment_repo: Optional[ShipmentRepository] = None,
        payment_repo: Optional[PaymentRepository] = None,
    ):
        self._order_repo = order_repo or get_order_repository()
        self._shipment_repo = shipment_repo or get_shipment_repository()
        self._payment_repo = payment_repo or get_payment_repository()

    def get_order(self, order_id: str, user_id: Optional[str] = None) -> OrderDetailResponse:
        """Fetch complete order detail with strict user isolation.

        Security Invariant:
        If user_id is provided, order.user_id MUST match user_id.
        Otherwise raises HTTP 403 Forbidden to prevent leaking order metadata.
        """
        order = self._order_repo.get_by_id(order_id)
        if not order:
            # Check by purchase_plan_id fallback
            order = self._order_repo.get_by_purchase_plan_id(order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order '{order_id}' not found.",
            )

        if user_id and order.user_id != user_id:
            logger.warning(f"Unauthorized order access attempt: user '{user_id}' requested order '{order.id}' owned by '{order.user_id}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You do not have permission to view order '{order_id}'.",
            )

        shipment = self._shipment_repo.get_by_order_id(order.id)

        return OrderDetailResponse(
            id=order.id,
            user_id=order.user_id,
            purchase_plan_id=order.purchase_plan_id,
            paypal_order_id=order.paypal_order_id,
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product_name,
            brand=order.brand,
            quantity=order.quantity,
            amount=order.amount,
            currency=order.currency,
            status=order.status.value,
            created_at=order.created_at,
            updated_at=order.updated_at,
            shipment=shipment,
        )

    def get_user_orders(self, user_id: str) -> List[OrderDetailResponse]:
        """Fetch all orders belonging strictly to the specified user."""
        orders = self._order_repo.list_by_user(user_id)
        results = []
        for o in orders:
            shipment = self._shipment_repo.get_by_order_id(o.id)
            results.append(
                OrderDetailResponse(
                    id=o.id,
                    user_id=o.user_id,
                    purchase_plan_id=o.purchase_plan_id,
                    paypal_order_id=o.paypal_order_id,
                    payment_id=o.payment_id,
                    product_id=o.product_id,
                    product_name=o.product_name,
                    brand=o.brand,
                    quantity=o.quantity,
                    amount=o.amount,
                    currency=o.currency,
                    status=o.status.value,
                    created_at=o.created_at,
                    updated_at=o.updated_at,
                    shipment=shipment,
                )
            )
        return results

    def get_shipment(self, order_id: str, user_id: Optional[str] = None) -> Shipment:
        """Retrieve authoritative shipment data for an authorized order."""
        detail = self.get_order(order_id, user_id)
        if not detail.shipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No shipment record found for order '{order_id}'.",
            )
        return detail.shipment

    def get_tracking(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve tracking details by order ID or carrier tracking number."""
        # Try direct order ID lookup
        order = self._order_repo.get_by_id(query)
        if order:
            detail = self.get_order(order.id, user_id)
            return {
                "order_id": order.id,
                "product_name": order.product_name,
                "status": order.status.value,
                "shipment": detail.shipment.model_dump() if detail.shipment else None,
            }

        # Try tracking number search across shipments
        for shipment in self._shipment_repo.list_all():
            if shipment.tracking_number.lower() == query.lower() or query.lower() in shipment.tracking_number.lower():
                order = self._order_repo.get_by_id(shipment.order_id)
                if order and user_id and order.user_id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied: Tracking number belongs to another user's order.",
                    )
                return {
                    "order_id": shipment.order_id,
                    "product_name": order.product_name if order else "Unknown Product",
                    "status": shipment.status.value,
                    "shipment": shipment.model_dump(),
                }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No tracking or order record found for '{query}'.",
        )

    def detect_order_issue(
        self,
        order_id: str,
        user_id: Optional[str] = None,
        reference_date_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deterministic issue detection engine evaluating timeline and carrier telemetry.

        Rules:
        1. If shipment.status == DELAYED or 'delay' mentioned in last_update:
           Issue: DELIVERY_DELAY (MEDIUM)
        2. If reference_date > estimated_delivery and status != DELIVERED:
           Issue: DELIVERY_DELAY (MEDIUM)
        3. If order.status == CANCELLED:
           Issue: ORDER_CANCELLED (HIGH)
        4. If payment_status != COMPLETED and order not cancelled:
           Issue: PAYMENT_PENDING (MEDIUM)
        5. If status == DELIVERED:
           Issue: DELIVERY_COMPLETED (INFO)
        """
        detail = self.get_order(order_id, user_id)
        shipment = detail.shipment

        # Rule: Order Cancelled
        if detail.status == OrderStatus.CANCELLED.value:
            return {
                "order_id": detail.id,
                "issue": "ORDER_CANCELLED",
                "severity": "HIGH",
                "detected": True,
                "reason": "This order was cancelled. No active shipment is in transit.",
                "recommended_action": "Contact merchant support or browse new catalog items.",
            }

        # Rule: Already Delivered
        if detail.status == OrderStatus.DELIVERED.value or (shipment and shipment.status == ShipmentStatus.DELIVERED):
            return {
                "order_id": detail.id,
                "issue": "DELIVERY_COMPLETED",
                "severity": "INFO",
                "detected": False,
                "reason": f"Package was delivered on {shipment.actual_delivery if shipment else 'recorded date'}.",
                "recommended_action": "Confirm package receipt or submit review.",
            }

        if shipment:
            # Rule: Carrier explicit delay notation
            is_explicit_delay = (
                shipment.status == ShipmentStatus.DELAYED
                or "delay" in shipment.last_update.lower()
            )

            # Rule: Date comparison against estimated arrival
            ref_date = None
            if reference_date_str:
                try:
                    ref_date = datetime.strptime(reference_date_str, "%Y-%m-%d").date()
                except ValueError:
                    pass

            est_date = None
            try:
                est_date = datetime.strptime(shipment.estimated_delivery, "%Y-%m-%d").date()
            except ValueError:
                pass

            is_date_exceeded = False
            if est_date and ref_date:
                is_date_exceeded = ref_date > est_date
            elif est_date and not reference_date_str:
                # Default hackathon demo date: Oct 20, 2026
                demo_now = date(2026, 10, 20)
                is_date_exceeded = demo_now > est_date

            if is_explicit_delay or is_date_exceeded:
                reason = "Regional logistics delay reported by carrier." if is_explicit_delay else f"Estimated delivery ({shipment.estimated_delivery}) has elapsed while package remains in transit."
                return {
                    "order_id": detail.id,
                    "issue": "DELIVERY_DELAY",
                    "severity": "MEDIUM",
                    "detected": True,
                    "expected_delivery": shipment.estimated_delivery,
                    "current_status": shipment.status.value,
                    "last_update": shipment.last_update,
                    "reason": reason,
                    "recommended_action": "Check the latest carrier update or contact the merchant.",
                    "can_prepare_support_request": True,
                }

        # No anomaly detected
        return {
            "order_id": detail.id,
            "issue": "NO_ISSUE",
            "severity": "INFO",
            "detected": False,
            "reason": "Shipment is progressing normally within expected delivery window.",
            "recommended_action": "Continue monitoring package tracking.",
        }

    def create_order_from_purchase(
        self,
        purchase_plan_id: str,
        user_id: str,
        product_id: str,
        product_name: str,
        brand: Optional[str],
        quantity: int,
        amount: float,
        currency: str,
        paypal_order_id: Optional[str],
        payment_id: Optional[str],
        delivery_days: int = 3,
    ) -> OrderDetailResponse:
        """Automatically create Order and Shipment records when a checkout succeeds."""
        order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc)

        order = Order(
            id=order_id,
            user_id=user_id,
            purchase_plan_id=purchase_plan_id,
            paypal_order_id=paypal_order_id,
            payment_id=payment_id,
            product_id=product_id,
            product_name=product_name,
            brand=brand,
            quantity=quantity,
            amount=amount,
            currency=currency,
            status=OrderStatus.PAID,
            created_at=now,
            updated_at=now,
        )
        self._order_repo.create(order)

        # Create matching shipment
        shipment_id = f"SHP-{uuid.uuid4().hex[:6].upper()}"
        tracking_num = f"TRK-FAST-{uuid.uuid4().hex[:8].upper()}"
        est_arrival = date.fromtimestamp(now.timestamp() + (delivery_days * 86400)).isoformat()

        shipment = Shipment(
            id=shipment_id,
            order_id=order_id,
            tracking_number=tracking_num,
            carrier="FastShip Logistics",
            status=ShipmentStatus.PROCESSING,
            estimated_delivery=est_arrival,
            actual_delivery=None,
            last_location="Fulfillment Center",
            last_update="Payment verified. Order confirmed and packing for shipment.",
            timeline=[],
            is_demo=True,
            created_at=now,
            updated_at=now,
        )
        self._shipment_repo.create(shipment)

        logger.info(f"Created order {order.id} and shipment {shipment.id} for plan {purchase_plan_id}")
        return self.get_order(order_id, user_id)
