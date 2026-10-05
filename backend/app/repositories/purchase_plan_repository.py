"""In-memory thread-safe repository for Purchase Plans."""

import threading
from typing import Dict, List, Optional
from app.schemas.purchase_plan import PurchasePlan


class PurchasePlanRepository:
    """Repository storing Purchase Plans."""

    def __init__(self):
        self._lock = threading.Lock()
        self._plans: Dict[str, PurchasePlan] = {}

    def create(self, plan: PurchasePlan) -> PurchasePlan:
        with self._lock:
            self._plans[plan.id] = plan
            return plan

    def get_by_id(self, plan_id: str) -> Optional[PurchasePlan]:
        with self._lock:
            return self._plans.get(plan_id)

    def get_by_paypal_order_id(self, order_id: str) -> Optional[PurchasePlan]:
        with self._lock:
            for plan in self._plans.values():
                if plan.paypal_order_id == order_id:
                    return plan
            return None

    def update(self, plan: PurchasePlan) -> PurchasePlan:
        with self._lock:
            self._plans[plan.id] = plan
            return plan

    def list_all(self) -> List[PurchasePlan]:
        with self._lock:
            return list(self._plans.values())

    def clear(self) -> None:
        """Clear all stored plans (used for test teardown)."""
        with self._lock:
            self._plans.clear()


_plan_repo_instance: Optional[PurchasePlanRepository] = None


def get_purchase_plan_repository() -> PurchasePlanRepository:
    """Dependency provider for purchase plan repository."""
    global _plan_repo_instance
    if _plan_repo_instance is None:
        _plan_repo_instance = PurchasePlanRepository()
    return _plan_repo_instance
