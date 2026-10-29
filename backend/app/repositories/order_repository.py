"""Database-backed repository for Orders."""

from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional

from app.db.session import get_db_context, init_db
from app.models.order import OrderModel
from app.schemas.order import Order, OrderStatus

logger = logging.getLogger(__name__)


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


def _model_to_schema(m: OrderModel) -> Order:
    return Order(
        id=m.id,
        user_id=m.user_id,
        purchase_plan_id=m.purchase_plan_id,
        paypal_order_id=m.paypal_order_id,
        payment_id=m.payment_id,
        product_id=m.product_id,
        product_name=m.product_name,
        brand=m.brand,
        quantity=m.quantity,
        amount=m.amount,
        currency=m.currency,
        status=OrderStatus(m.status),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class OrderRepository:
    """Database-backed order data store."""

    def __init__(self, populate_defaults: bool = True):
        init_db()
        if populate_defaults:
            with get_db_context() as db:
                if db.query(OrderModel).count() == 0:
                    for order in _build_default_demo_orders().values():
                        db.merge(OrderModel(
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
                            status=order.status.value if hasattr(order.status, "value") else str(order.status),
                            created_at=order.created_at,
                            updated_at=order.updated_at,
                        ))

    def create(self, order: Order) -> Order:
        with get_db_context() as db:
            m = OrderModel(
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
                status=order.status.value if hasattr(order.status, "value") else str(order.status),
                created_at=order.created_at,
                updated_at=order.updated_at,
            )
            db.merge(m)
            return order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        with get_db_context() as db:
            m = db.query(OrderModel).filter(OrderModel.id == order_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def get_by_purchase_plan_id(self, plan_id: str) -> Optional[Order]:
        with get_db_context() as db:
            m = db.query(OrderModel).filter(OrderModel.purchase_plan_id == plan_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def list_by_user(self, user_id: str) -> List[Order]:
        with get_db_context() as db:
            records = (
                db.query(OrderModel)
                .filter(OrderModel.user_id == user_id)
                .order_by(OrderModel.created_at.desc())
                .all()
            )
            return [_model_to_schema(m) for m in records]

    def list_all(self) -> List[Order]:
        with get_db_context() as db:
            records = db.query(OrderModel).order_by(OrderModel.created_at.desc()).all()
            return [_model_to_schema(m) for m in records]

    def update(self, order: Order) -> Order:
        with get_db_context() as db:
            m = db.query(OrderModel).filter(OrderModel.id == order.id).first()
            if m:
                m.status = order.status.value if hasattr(order.status, "value") else str(order.status)
                m.paypal_order_id = order.paypal_order_id
                m.payment_id = order.payment_id
                m.quantity = order.quantity
                m.amount = order.amount
                m.currency = order.currency
                m.updated_at = datetime.now(timezone.utc)
                order.updated_at = m.updated_at
            else:
                self.create(order)
            return order

    def reset_defaults(self) -> None:
        """Reset repository to initial synthetic demo state."""
        with get_db_context() as db:
            db.query(OrderModel).delete()
            for order in _build_default_demo_orders().values():
                db.merge(OrderModel(
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
                    status=order.status.value if hasattr(order.status, "value") else str(order.status),
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                ))

    def clear(self) -> None:
        """Clear all stored orders."""
        with get_db_context() as db:
            db.query(OrderModel).delete()


_order_repo_instance: Optional[OrderRepository] = None


def get_order_repository() -> OrderRepository:
    """Dependency provider singleton for OrderRepository."""
    global _order_repo_instance
    if _order_repo_instance is None:
        _order_repo_instance = OrderRepository()
    return _order_repo_instance
