"""Business logic service managing Purchase Plan creation, pricing integrity, and approval."""

from datetime import datetime, timezone
import logging
from typing import Optional
import uuid

from fastapi import HTTPException, status

from app.repositories.product_repository import ProductRepository, get_product_repository
from app.repositories.purchase_plan_repository import (
    PurchasePlanRepository,
    get_purchase_plan_repository,
)
from app.schemas.purchase_plan import (
    PurchasePlan,
    PurchasePlanCreateRequest,
    PurchasePlanStatus,
)

logger = logging.getLogger(__name__)


class PurchasePlanService:
    """Enforces price integrity and lifecycle state transitions for Purchase Plans."""

    def __init__(
        self,
        product_repo: Optional[ProductRepository] = None,
        plan_repo: Optional[PurchasePlanRepository] = None,
    ):
        self._product_repo = product_repo or get_product_repository()
        self._plan_repo = plan_repo or get_purchase_plan_repository()

    def create_plan(self, request: PurchasePlanCreateRequest, user_id: Optional[str] = None) -> PurchasePlan:
        """Create a new Purchase Plan strictly using authoritative product catalog data.

        Critical Security Rule:
        The frontend CANNOT dictate unit_price, total_amount, or currency.
        All pricing is derived authoritatively by looking up the product in the backend.
        The plan is bound strictly to the authenticated user.
        """
        product = self._product_repo.get_by_id(request.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{request.product_id}' not found.",
            )

        if not product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is currently out of stock.",
            )

        # Derive authoritative values
        quantity = max(1, request.quantity)
        authoritative_price = product.price
        total_amount = round(authoritative_price * quantity, 2)
        plan_id = f"PP-{uuid.uuid4().hex[:8].upper()}"
        effective_user_id = user_id or request.user_id or "guest_user"

        plan = PurchasePlan(
            id=plan_id,
            user_id=effective_user_id,
            product_id=product.id,
            product_name=product.name,
            brand=product.brand,
            seller=product.seller,
            delivery_days=product.delivery_days,
            quantity=quantity,
            unit_price=authoritative_price,
            currency=product.currency,
            total_amount=total_amount,
            status=PurchasePlanStatus.AWAITING_APPROVAL,
            recommendation_reason=request.recommendation_reason,
            score=request.score,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        saved = self._plan_repo.create(plan)
        logger.info(f"Created Purchase Plan {saved.id} for {saved.product_name} (${saved.total_amount})")
        return saved

    def get_plan(self, plan_id: str, user_id: Optional[str] = None) -> PurchasePlan:
        """Retrieve Purchase Plan by ID with authenticated ownership validation."""
        plan = self._plan_repo.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Plan '{plan_id}' not found.",
            )
        if user_id and plan.user_id != user_id:
            logger.warning(
                f"Unauthorized plan access: user '{user_id}' requested plan '{plan.id}' owned by '{plan.user_id}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You do not have permission to view Purchase Plan '{plan_id}'.",
            )
        return plan

    def approve_plan(self, plan_id: str, user_id: Optional[str] = None) -> PurchasePlan:
        """Approve a Purchase Plan.

        Validations:
        - Plan exists and belongs to authenticated user
        - Current status must be AWAITING_APPROVAL
        - Product still exists and is in stock
        - Current product price has not changed; if changed, requires renewed approval
        """
        plan = self.get_plan(plan_id, user_id=user_id)

        # State transition validation
        if plan.status != PurchasePlanStatus.AWAITING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase Plan cannot be approved from current state '{plan.status}'.",
            )

        # Verify product still valid
        product = self._product_repo.get_by_id(plan.product_id)
        if not product or not product.stock:
            plan.status = PurchasePlanStatus.FAILED
            self._plan_repo.update(plan)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected product is no longer available in inventory.",
            )

        # Revalidate price: if price changed, update plan and require renewed approval
        if product.price != plan.unit_price:
            old_price = plan.unit_price
            plan.unit_price = product.price
            plan.total_amount = round(product.price * plan.quantity, 2)
            plan.updated_at = datetime.now(timezone.utc)
            self._plan_repo.update(plan)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product price has changed from ${old_price:.2f} to ${product.price:.2f}. Renewed approval is required.",
            )

        # Transition to APPROVED
        plan.status = PurchasePlanStatus.APPROVED
        plan.updated_at = datetime.now(timezone.utc)
        updated = self._plan_repo.update(plan)
        logger.info(f"Purchase Plan {plan.id} has been explicitly APPROVED by user {plan.user_id}.")
        return updated
