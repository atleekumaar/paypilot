"""Database-backed repository for Payment transaction records."""

from datetime import datetime, timezone
import logging
from typing import List, Optional

from app.db.session import get_db_context, init_db
from app.models.payment import PaymentModel
from app.schemas.payment import Payment, PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


def _model_to_schema(m: PaymentModel) -> Payment:
    return Payment(
        id=m.id,
        user_id=m.user_id,
        purchase_plan_id=m.purchase_plan_id,
        provider=PaymentProvider(m.provider),
        provider_order_id=m.provider_order_id,
        amount=m.amount,
        currency=m.currency,
        status=PaymentStatus(m.status),
        capture_id=m.capture_id,
        payer_email=m.payer_email,
        payer_id=m.payer_id,
        metadata=m.metadata_json or {},
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class PaymentRepository:
    """Database-backed repository storing Payment transactions."""

    def __init__(self):
        init_db()

    def create(self, payment: Payment) -> Payment:
        with get_db_context() as db:
            m = PaymentModel(
                id=payment.id,
                user_id=payment.user_id or "guest_user",
                purchase_plan_id=payment.purchase_plan_id,
                provider=payment.provider.value if hasattr(payment.provider, "value") else str(payment.provider),
                provider_order_id=payment.provider_order_id,
                amount=payment.amount,
                currency=payment.currency,
                status=payment.status.value if hasattr(payment.status, "value") else str(payment.status),
                capture_id=payment.capture_id,
                payer_email=payment.payer_email,
                payer_id=payment.payer_id,
                metadata_json=payment.metadata,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
            )
            db.merge(m)
            return payment

    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        with get_db_context() as db:
            m = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def get_by_plan_id(self, plan_id: str) -> Optional[Payment]:
        with get_db_context() as db:
            m = db.query(PaymentModel).filter(PaymentModel.purchase_plan_id == plan_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def get_by_provider_order_id(self, order_id: str) -> Optional[Payment]:
        with get_db_context() as db:
            m = db.query(PaymentModel).filter(PaymentModel.provider_order_id == order_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def update(self, payment: Payment) -> Payment:
        with get_db_context() as db:
            m = db.query(PaymentModel).filter(PaymentModel.id == payment.id).first()
            if m:
                m.status = payment.status.value if hasattr(payment.status, "value") else str(payment.status)
                m.capture_id = payment.capture_id
                m.payer_email = payment.payer_email
                m.payer_id = payment.payer_id
                m.metadata_json = payment.metadata
                m.updated_at = datetime.now(timezone.utc)
                payment.updated_at = m.updated_at
            else:
                self.create(payment)
            return payment

    def list_all(self) -> List[Payment]:
        with get_db_context() as db:
            records = db.query(PaymentModel).all()
            return [_model_to_schema(m) for m in records]

    def clear(self) -> None:
        """Clear all stored payments (used for test teardown)."""
        with get_db_context() as db:
            db.query(PaymentModel).delete()


_payment_repo_instance: Optional[PaymentRepository] = None


def get_payment_repository() -> PaymentRepository:
    """Dependency provider for payment repository."""
    global _payment_repo_instance
    if _payment_repo_instance is None:
        _payment_repo_instance = PaymentRepository()
    return _payment_repo_instance
