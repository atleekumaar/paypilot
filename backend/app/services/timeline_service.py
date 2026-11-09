"""Bryntum-compatible Commerce Timeline Service.

Constructs unified scheduling and milestone datasets representing the full commerce
lifecycle: agent purchase plans, PayPal payment authorizations and captures, merchant
fulfillment, carrier in-transit logistics, and refund events.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
from typing import Any, Dict, List, Optional

from app.repositories.order_repository import OrderRepository, get_order_repository
from app.repositories.payment_repository import PaymentRepository, get_payment_repository
from app.repositories.purchase_plan_repository import PurchasePlanRepository, get_purchase_plan_repository
from app.repositories.shipment_repository import ShipmentRepository, get_shipment_repository

logger = logging.getLogger(__name__)


def _to_iso(dt: Optional[datetime]) -> str:
    """Format datetime as ISO 8601 string with UTC timezone."""
    if not dt:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse common date strings into a timezone-aware datetime."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(date_str.split(".")[0], fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue
    return None


class TimelineService:
    """Aggregates commerce lifecycle data into Bryntum Scheduler / Timeline format."""

    def __init__(
        self,
        order_repo: Optional[OrderRepository] = None,
        payment_repo: Optional[PaymentRepository] = None,
        shipment_repo: Optional[ShipmentRepository] = None,
        plan_repo: Optional[PurchasePlanRepository] = None,
    ):
        self._order_repo = order_repo or get_order_repository()
        self._payment_repo = payment_repo or get_payment_repository()
        self._shipment_repo = shipment_repo or get_shipment_repository()
        self._plan_repo = plan_repo or get_purchase_plan_repository()

    def _get_user_orders(self, user_id: str):
        orders = self._order_repo.list_by_user(user_id)
        if not orders and user_id in ("guest_user", "demo_user", "admin"):
            orders = self._order_repo.list_all()
        return orders

    def _get_user_payments(self, user_id: str):
        payments = self._payment_repo.list_by_user(user_id)
        if not payments and user_id in ("guest_user", "demo_user", "admin"):
            payments = self._payment_repo.list_all()
        return payments

    def get_timeline(
        self,
        user_id: str,
        order_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate Bryntum-compatible resources and event store for the commerce timeline."""
        orders = self._get_user_orders(user_id)
        if order_id:
            orders = [o for o in orders if o.id == order_id]

        all_payments = self._get_user_payments(user_id)
        payment_by_order = {p.purchase_plan_id: p for p in all_payments}
        payment_by_id = {p.id: p for p in all_payments}

        shipments = self._shipment_repo.list_all()
        shipment_by_order = {s.order_id: s for s in shipments}

        resources: List[Dict[str, Any]] = []
        events: List[Dict[str, Any]] = []

        filter_start = _parse_date(start_date)
        filter_end = _parse_date(end_date)

        for order in orders:
            shipment = shipment_by_order.get(order.id)
            payment = payment_by_order.get(order.purchase_plan_id) or payment_by_id.get(order.payment_id or "")

            # Create Resource Row
            resource_id = f"res_{order.id}"
            resources.append({
                "id": resource_id,
                "name": order.product_name,
                "orderId": order.id,
                "brand": order.brand,
                "amount": float(order.amount),
                "currency": order.currency,
                "status": order.status,
                "carrier": shipment.carrier if shipment else None,
                "trackingNumber": shipment.tracking_number if shipment else None,
            })

            base_time = order.created_at or datetime.now(timezone.utc)
            if base_time.tzinfo is None:
                base_time = base_time.replace(tzinfo=timezone.utc)

            # 1. Approval / Order Created Event
            events.append({
                "id": f"evt_order_{order.id}",
                "resourceId": resource_id,
                "name": f"Order Created: {order.product_name}",
                "startDate": _to_iso(base_time),
                "endDate": _to_iso(base_time + timedelta(hours=2)),
                "eventType": "APPROVAL",
                "status": "COMPLETED",
                "isEstimated": False,
                "eventColor": "#10B981",  # emerald
                "iconCls": "b-fa b-fa-check-circle",
                "metadata": {
                    "orderId": order.id,
                    "productName": order.product_name,
                    "brand": order.brand,
                    "quantity": order.quantity,
                    "amount": float(order.amount),
                },
            })

            # 2. Payment Captured / Authorized Event
            pay_time = (payment.created_at if payment and payment.created_at else base_time)
            if pay_time.tzinfo is None:
                pay_time = pay_time.replace(tzinfo=timezone.utc)
            pay_status = payment.status if payment else "CAPTURED"
            is_captured = pay_status in ("CAPTURED", "COMPLETED")
            events.append({
                "id": f"evt_pay_{order.id}",
                "resourceId": resource_id,
                "name": f"PayPal Payment: {pay_status}",
                "startDate": _to_iso(pay_time),
                "endDate": _to_iso(pay_time + timedelta(hours=1)),
                "eventType": "PAYMENT",
                "status": "COMPLETED" if is_captured else "PENDING",
                "isEstimated": False,
                "eventColor": "#3B82F6" if is_captured else "#F59E0B",  # blue or amber
                "iconCls": "b-fa b-fa-credit-card",
                "metadata": {
                    "orderId": order.id,
                    "provider": "PAYPAL",
                    "paypalOrderId": order.paypal_order_id or (payment.provider_order_id if payment else None),
                    "captureId": payment.capture_id if payment else None,
                    "amount": float(order.amount),
                    "currency": order.currency,
                    "status": pay_status,
                },
            })

            # 3. Merchant Fulfillment & Packing
            fulfill_start = base_time + timedelta(hours=3)
            fulfill_end = base_time + timedelta(days=1)
            fulfill_status = "COMPLETED" if shipment or order.status in ("CONFIRMED", "SHIPPED", "DELIVERED") else "IN_PROGRESS"
            events.append({
                "id": f"evt_flf_{order.id}",
                "resourceId": resource_id,
                "name": f"Merchant Fulfillment: {order.brand}",
                "startDate": _to_iso(fulfill_start),
                "endDate": _to_iso(fulfill_end),
                "eventType": "FULFILLMENT",
                "status": fulfill_status,
                "isEstimated": False,
                "eventColor": "#6366F1",  # indigo
                "iconCls": "b-fa b-fa-box",
                "metadata": {
                    "orderId": order.id,
                    "merchant": order.brand,
                    "status": fulfill_status,
                },
            })

            # 4. Carrier Logistics & In-Transit
            transit_start = fulfill_end
            raw_est = getattr(order, "estimated_delivery", None) or (shipment.estimated_delivery if shipment else None)
            est_del_dt = _parse_date(raw_est) or (base_time + timedelta(days=4))
            act_del_dt = _parse_date(shipment.actual_delivery) if shipment else None

            transit_end = act_del_dt or est_del_dt
            carrier_name = shipment.carrier if shipment else "Standard Shipping"
            carrier_status = shipment.status.value if shipment and hasattr(shipment.status, "value") else (str(shipment.status) if shipment else "IN_TRANSIT")

            events.append({
                "id": f"evt_trn_{order.id}",
                "resourceId": resource_id,
                "name": f"{carrier_name}: In Transit",
                "startDate": _to_iso(transit_start),
                "endDate": _to_iso(transit_end),
                "eventType": "IN_TRANSIT",
                "status": carrier_status,
                "isEstimated": False if shipment else True,
                "eventColor": "#8B5CF6",  # purple
                "iconCls": "b-fa b-fa-truck",
                "metadata": {
                    "orderId": order.id,
                    "carrier": carrier_name,
                    "trackingNumber": shipment.tracking_number if shipment else None,
                    "lastLocation": shipment.last_location if shipment else "Origin Logistics Hub",
                    "lastUpdate": shipment.last_update if shipment else "Manifest received",
                },
            })

            # 5. Delivery Event (Milestone / Destination)
            is_delivered = order.status == "DELIVERED" or (shipment and shipment.status.value == "DELIVERED" if hasattr(shipment.status, "value") else str(getattr(shipment, "status", "")) == "DELIVERED")
            del_time = act_del_dt or est_del_dt
            events.append({
                "id": f"evt_del_{order.id}",
                "resourceId": resource_id,
                "name": f"Delivered: {order.product_name}" if is_delivered else f"Estimated Delivery ({del_time.strftime('%b %d')})",
                "startDate": _to_iso(del_time),
                "endDate": _to_iso(del_time + timedelta(hours=2)),
                "eventType": "DELIVERY",
                "status": "COMPLETED" if is_delivered else "ESTIMATED",
                "isEstimated": not is_delivered,
                "eventColor": "#059669" if is_delivered else "#D97706",  # emerald vs amber
                "iconCls": "b-fa b-fa-home" if is_delivered else "b-fa b-fa-clock",
                "metadata": {
                    "orderId": order.id,
                    "isDelivered": is_delivered,
                    "deliveryDate": _to_iso(del_time),
                },
            })

            # 6. Refund Event (if applicable)
            if payment and (payment.refund_id or payment.refund_status or (payment.total_refunded and float(payment.total_refunded) > 0)):
                refund_time = payment.updated_at or (base_time + timedelta(days=2))
                if refund_time.tzinfo is None:
                    refund_time = refund_time.replace(tzinfo=timezone.utc)
                events.append({
                    "id": f"evt_ref_{order.id}",
                    "resourceId": resource_id,
                    "name": f"PayPal Refund: ${float(payment.total_refunded or 0):.2f}",
                    "startDate": _to_iso(refund_time),
                    "endDate": _to_iso(refund_time + timedelta(hours=1)),
                    "eventType": "REFUND",
                    "status": payment.refund_status or "COMPLETED",
                    "isEstimated": False,
                    "eventColor": "#EF4444",  # red
                    "iconCls": "b-fa b-fa-undo",
                    "metadata": {
                        "orderId": order.id,
                        "refundId": payment.refund_id,
                        "refundAmount": float(payment.total_refunded or 0),
                        "refundStatus": payment.refund_status,
                    },
                })

        # Apply filtering by event_type if specified
        if event_type:
            events = [e for e in events if e["eventType"].upper() == event_type.upper()]

        # Apply filtering by date range if specified
        if filter_start or filter_end:
            filtered_events = []
            for ev in events:
                ev_start = _parse_date(ev["startDate"])
                if filter_start and ev_start and ev_start < filter_start:
                    continue
                if filter_end and ev_start and ev_start > filter_end:
                    continue
                filtered_events.append(ev)
            events = filtered_events

        # Determine overall timeline bounds
        all_dates = []
        for e in events:
            s = _parse_date(e["startDate"])
            ed = _parse_date(e["endDate"])
            if s:
                all_dates.append(s)
            if ed:
                all_dates.append(ed)

        if all_dates:
            min_dt = min(all_dates) - timedelta(days=1)
            max_dt = max(all_dates) + timedelta(days=2)
        else:
            min_dt = datetime.now(timezone.utc) - timedelta(days=3)
            max_dt = datetime.now(timezone.utc) + timedelta(days=7)

        return {
            "resources": resources,
            "events": events,
            "timeRange": {
                "startDate": _to_iso(min_dt),
                "endDate": _to_iso(max_dt),
            },
            "meta": {
                "totalResources": len(resources),
                "totalEvents": len(events),
                "generatedAt": _to_iso(datetime.now(timezone.utc)),
            },
        }

    def get_summary(self, user_id: str) -> Dict[str, Any]:
        """Summary indicators for dashboard metric cards and agent tools."""
        orders = self._get_user_orders(user_id)
        payments = self._get_user_payments(user_id)
        shipments = self._shipment_repo.list_all()

        active_shipments = [
            s for s in shipments
            if (s.status.value != "DELIVERED" if hasattr(s.status, "value") else str(s.status) != "DELIVERED")
        ]

        pending_payments = [
            p for p in payments
            if p.status not in ("CAPTURED", "COMPLETED", "VOIDED")
        ]

        # Find next upcoming delivery
        upcoming_deliveries = []
        now = datetime.now(timezone.utc)
        for s in shipments:
            if s.estimated_delivery:
                del_dt = _parse_date(s.estimated_delivery)
                if del_dt and del_dt >= now:
                    upcoming_deliveries.append({
                        "order_id": s.order_id,
                        "carrier": s.carrier,
                        "tracking_number": s.tracking_number,
                        "estimated_delivery": s.estimated_delivery,
                        "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                    })

        upcoming_deliveries.sort(key=lambda x: x["estimated_delivery"])

        return {
            "total_orders": len(orders),
            "active_shipments": len(active_shipments),
            "pending_payments": len(pending_payments),
            "next_delivery": upcoming_deliveries[0] if upcoming_deliveries else None,
            "upcoming_deliveries_count": len(upcoming_deliveries),
            "verified_at": _to_iso(now),
        }


_timeline_instance: Optional[TimelineService] = None


def get_timeline_service() -> TimelineService:
    global _timeline_instance
    if _timeline_instance is None:
        _timeline_instance = TimelineService()
    return _timeline_instance
