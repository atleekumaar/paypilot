"""Thread-safe in-memory repository for Orders."""

from datetime import datetime, timezone
import threading
from typing import Dict, List, Optional

from app.schemas.order import Order, OrderStatus


def _build_default_demo_orders() -> Dict[str, Order]:
    """Generates initial realistic synthetic orders for demo and evaluation."""
    return {
        "ORD-001": Order(
            id="ORD-001",
            user_id="guest_user",
            purchase_plan_id="PP-001",
            paypal_order_id="MOCK-PAYPAL-ORD-001",
            payment_id="PAY-001",
            product_id="LAP-001",
            product_name="NovaBook Pro 14",
            brand="Nova",
            quantity=1,
            amount=1049.0,
            currency="USD",
            status=OrderStatus.IN_TRANSIT,
            created_at=datetime(2026, 10, 12, 14, 30, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 16, 9, 15, tzinfo=timezone.utc),
        ),
        "ORD-002": Order(
            id="ORD-002",
            user_id="guest_user",
            purchase_plan_id="PP-002",
            paypal_order_id="MOCK-PAYPAL-ORD-002",
            payment_id="PAY-002",
            product_id="LAP-002",
            product_name="AeroBlade Slim 15",
            brand="Aero",
            quantity=1,
            amount=1199.0,
            currency="USD",
            status=OrderStatus.DELIVERED,
            created_at=datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 4, 16, 20, tzinfo=timezone.utc),
        ),
        "ORD-003": Order(
            id="ORD-003",
            user_id="guest_user",
            purchase_plan_id="PP-003",
            paypal_order_id="MOCK-PAYPAL-ORD-003",
            payment_id="PAY-003",
            product_id="LAP-003",
            product_name="VisionBook Studio 16",
            brand="Vision",
            quantity=1,
            amount=1150.0,
            currency="USD",
            status=OrderStatus.PROCESSING,
            created_at=datetime(2026, 10, 19, 11, 45, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 19, 11, 50, tzinfo=timezone.utc),
        ),
        "ORD-099": Order(
            id="ORD-099",
            user_id="other_user_88",
            purchase_plan_id="PP-099",
            paypal_order_id="MOCK-PAYPAL-ORD-099",
            payment_id="PAY-099",
            product_id="LAP-004",
            product_name="Zenith UltraBook 13",
            brand="Zenith",
            quantity=1,
            amount=899.0,
            currency="USD",
            status=OrderStatus.IN_TRANSIT,
            created_at=datetime(2026, 10, 14, 8, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc),
        ),
    }


class OrderRepository:
    """In-memory thread-safe order data store."""

    def __init__(self, populate_defaults: bool = True):
        self._lock = threading.Lock()
        self._orders: Dict[str, Order] = _build_default_demo_orders() if populate_defaults else {}

    def create(self, order: Order) -> Order:
        with self._lock:
            self._orders[order.id] = order
            return order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        with self._lock:
            return self._orders.get(order_id)

    def get_by_purchase_plan_id(self, plan_id: str) -> Optional[Order]:
        with self._lock:
            for order in self._orders.values():
                if order.purchase_plan_id == plan_id:
                    return order
            return None

    def list_by_user(self, user_id: str) -> List[Order]:
        with self._lock:
            return [
                order for order in sorted(
                    self._orders.values(),
                    key=lambda o: o.created_at,
                    reverse=True
                )
                if order.user_id == user_id
            ]

    def list_all(self) -> List[Order]:
        with self._lock:
            return list(self._orders.values())

    def update(self, order: Order) -> Order:
        with self._lock:
            self._orders[order.id] = order
            return order

    def reset_defaults(self) -> None:
        """Reset repository to initial synthetic demo state."""
        with self._lock:
            self._orders = _build_default_demo_orders()

    def clear(self) -> None:
        """Clear all stored orders."""
        with self._lock:
            self._orders.clear()


_order_repo_instance: Optional[OrderRepository] = None


def get_order_repository() -> OrderRepository:
    """Dependency provider singleton for OrderRepository."""
    global _order_repo_instance
    if _order_repo_instance is None:
        _order_repo_instance = OrderRepository()
    return _order_repo_instance
