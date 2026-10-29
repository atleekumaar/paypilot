"""Database-backed repository for Purchase Plans."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import uuid

from app.db.session import get_db_context, init_db
from app.models.purchase_plan import PurchasePlanModel
from app.schemas.purchase_plan import PurchasePlan, PurchasePlanStatus

logger = logging.getLogger(__name__)


def _model_to_schema(m: PurchasePlanModel) -> PurchasePlan:
    return PurchasePlan(
        id=m.id,
        user_id=m.user_id,
        product_id=m.product_id,
        product_name=m.product_name,
        brand=m.brand,
        seller=m.seller,
        delivery_days=m.delivery_days,
        quantity=m.quantity,
        unit_price=m.unit_price,
        currency=m.currency,
        total_amount=m.total_amount,
        status=PurchasePlanStatus(m.status),
        paypal_order_id=m.paypal_order_id,
        approval_url=m.approval_url,
        recommendation_reason=m.recommendation_reason,
        score=m.score,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class PurchasePlanRepository:
    """Database-backed repository storing Purchase Plans."""

    def __init__(self):
        init_db()

    @property
    def _plans(self) -> Dict[str, PurchasePlan]:
        with get_db_context() as db:
            records = db.query(PurchasePlanModel).all()
            return {m.id: _model_to_schema(m) for m in records}

    def create(self, plan: Any) -> Any:
        with get_db_context() as db:
            plan_id = getattr(plan, "id", None)
            if not isinstance(plan_id, str):
                plan_id = f"PP-{uuid.uuid4().hex[:8].upper()}"

            user_id = getattr(plan, "user_id", None)
            if not isinstance(user_id, str):
                user_id = "guest_user"

            product_id = getattr(plan, "product_id", None)
            if not isinstance(product_id, str):
                product_id = "PROD-1"

            product_name = getattr(plan, "product_name", None)
            if not isinstance(product_name, str):
                product_name = "Item"

            brand = getattr(plan, "brand", None)
            if not isinstance(brand, str):
                brand = "Brand"

            seller = getattr(plan, "seller", None)
            if not isinstance(seller, str):
                seller = "Official Store"

            delivery_days = getattr(plan, "delivery_days", 3)
            if not isinstance(delivery_days, int):
                delivery_days = 3

            quantity = getattr(plan, "quantity", 1)
            if not isinstance(quantity, int):
                quantity = 1

            unit_price = getattr(plan, "unit_price", 0.0)
            if not isinstance(unit_price, (int, float)):
                unit_price = 0.0

            currency = getattr(plan, "currency", "USD")
            if not isinstance(currency, str):
                currency = "USD"

            total_amount = getattr(plan, "total_amount", 0.0)
            if not isinstance(total_amount, (int, float)):
                total_amount = 0.0

            raw_status = getattr(plan, "status", "AWAITING_APPROVAL")
            if hasattr(raw_status, "value"):
                status_str = str(raw_status.value)
            elif isinstance(raw_status, str):
                status_str = raw_status
            else:
                status_str = "AWAITING_APPROVAL"

            paypal_order_id = getattr(plan, "paypal_order_id", None)
            if not isinstance(paypal_order_id, str):
                paypal_order_id = None

            approval_url = getattr(plan, "approval_url", None)
            if not isinstance(approval_url, str):
                approval_url = None

            recommendation_reason = getattr(plan, "recommendation_reason", None)
            if not isinstance(recommendation_reason, str):
                recommendation_reason = None

            score = getattr(plan, "score", 1.0)
            if not isinstance(score, (int, float)):
                score = 1.0

            created_at = getattr(plan, "created_at", None)
            if not isinstance(created_at, datetime):
                created_at = datetime.now(timezone.utc)

            updated_at = getattr(plan, "updated_at", None)
            if not isinstance(updated_at, datetime):
                updated_at = datetime.now(timezone.utc)

            m = PurchasePlanModel(
                id=plan_id,
                user_id=user_id,
                product_id=product_id,
                product_name=product_name,
                brand=brand,
                seller=seller,
                delivery_days=delivery_days,
                quantity=quantity,
                unit_price=float(unit_price),
                currency=currency,
                total_amount=float(total_amount),
                status=status_str,
                paypal_order_id=paypal_order_id,
                approval_url=approval_url,
                recommendation_reason=recommendation_reason,
                score=float(score),
                created_at=created_at,
                updated_at=updated_at,
            )
            db.merge(m)
            return plan

    def get_by_id(self, plan_id: str) -> Optional[PurchasePlan]:
        with get_db_context() as db:
            m = db.query(PurchasePlanModel).filter(PurchasePlanModel.id == plan_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def get_by_paypal_order_id(self, order_id: str) -> Optional[PurchasePlan]:
        with get_db_context() as db:
            m = db.query(PurchasePlanModel).filter(PurchasePlanModel.paypal_order_id == order_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def update(self, plan: PurchasePlan) -> PurchasePlan:
        with get_db_context() as db:
            m = db.query(PurchasePlanModel).filter(PurchasePlanModel.id == plan.id).first()
            if m:
                m.status = plan.status.value
                m.unit_price = plan.unit_price
                m.total_amount = plan.total_amount
                m.paypal_order_id = plan.paypal_order_id
                m.approval_url = plan.approval_url
                m.updated_at = datetime.now(timezone.utc)
                plan.updated_at = m.updated_at
            else:
                self.create(plan)
            return plan

    def list_all(self) -> List[PurchasePlan]:
        with get_db_context() as db:
            records = db.query(PurchasePlanModel).all()
            return [_model_to_schema(m) for m in records]

    def clear(self) -> None:
        """Clear all stored plans (used for test teardown)."""
        with get_db_context() as db:
            db.query(PurchasePlanModel).delete()


_plan_repo_instance: Optional[PurchasePlanRepository] = None


def get_purchase_plan_repository() -> PurchasePlanRepository:
    """Dependency provider for purchase plan repository."""
    global _plan_repo_instance
    if _plan_repo_instance is None:
        _plan_repo_instance = PurchasePlanRepository()
    return _plan_repo_instance
