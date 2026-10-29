"""Purchase Plan API endpoints."""

from fastapi import APIRouter, Depends, status
from app.core.auth import AuthenticatedUser, get_current_user, verify_user_ownership
from app.schemas.purchase_plan import PurchasePlan, PurchasePlanCreateRequest
from app.services.purchase_plan_service import PurchasePlanService

router = APIRouter(prefix="/api/purchase-plans", tags=["Purchase Plans"])


@router.post(
    "",
    response_model=PurchasePlan,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Purchase Plan",
    description="Formulates an authoritative purchase plan derived from catalogue product price. Requires explicit user approval before payment creation.",
)
async def create_purchase_plan(
    request: PurchasePlanCreateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PurchasePlan:
    """Create purchase plan with status AWAITING_APPROVAL."""
    verify_user_ownership(current_user, request.user_id)
    service = PurchasePlanService()
    return service.create_plan(request, user_id=current_user.id)


@router.get(
    "/{plan_id}",
    response_model=PurchasePlan,
    summary="Get Purchase Plan details",
)
async def get_purchase_plan(
    plan_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PurchasePlan:
    """Retrieve purchase plan details by ID."""
    service = PurchasePlanService()
    return service.get_plan(plan_id, user_id=current_user.id)


@router.post(
    "/{plan_id}/approve",
    response_model=PurchasePlan,
    summary="Explicitly approve a Purchase Plan",
    description="Transitions purchase plan to APPROVED status, enabling subsequent PayPal Sandbox checkout order creation.",
)
async def approve_purchase_plan(
    plan_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PurchasePlan:
    """Explicitly approve a purchase plan."""
    service = PurchasePlanService()
    return service.approve_plan(plan_id, user_id=current_user.id)
