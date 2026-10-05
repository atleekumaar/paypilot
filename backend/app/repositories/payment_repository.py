"""In-memory thread-safe repository for Payment transaction records."""

import threading
from typing import Dict, List, Optional
from app.schemas.payment import Payment


class PaymentRepository:
    """Repository storing Payment transactions."""

    def __init__(self):
        self._lock = threading.Lock()
        self._payments: Dict[str, Payment] = {}

    def create(self, payment: Payment) -> Payment:
        with self._lock:
            self._payments[payment.id] = payment
            return payment

    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        with self._lock:
            return self._payments.get(payment_id)

    def get_by_plan_id(self, plan_id: str) -> Optional[Payment]:
        with self._lock:
            for p in self._payments.values():
                if p.purchase_plan_id == plan_id:
                    return p
            return None

    def get_by_provider_order_id(self, order_id: str) -> Optional[Payment]:
        with self._lock:
            for p in self._payments.values():
                if p.provider_order_id == order_id:
                    return p
            return None

    def update(self, payment: Payment) -> Payment:
        with self._lock:
            self._payments[payment.id] = payment
            return payment

    def list_all(self) -> List[Payment]:
        with self._lock:
            return list(self._payments.values())

    def clear(self) -> None:
        """Clear all stored payments (used for test teardown)."""
        with self._lock:
            self._payments.clear()


_payment_repo_instance: Optional[PaymentRepository] = None


def get_payment_repository() -> PaymentRepository:
    """Dependency provider for payment repository."""
    global _payment_repo_instance
    if _payment_repo_instance is None:
        _payment_repo_instance = PaymentRepository()
    return _payment_repo_instance
