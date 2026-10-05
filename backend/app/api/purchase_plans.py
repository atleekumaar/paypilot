"""Purchase Plan API endpoints."""

from fastapi import APIRouter, status
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
async def create_purchase_plan(request: PurchasePlanCreateRequest) -> PurchasePlan:
    """Create purchase plan with status AWAITING_APPROVAL."""
    service = PurchasePlanService()
    return service.create_plan(request)


@router.get(
    "/{plan_id}",
    response_model=PurchasePlan,
    summary="Get Purchase Plan details",
)
async def get_purchase_plan(plan_id: str) -> PurchasePlan:
    """Retrieve purchase plan details by ID."""
    service = PurchasePlanService()
    return service.get_plan(plan_id)


@router.post(
    "/{plan_id}/approve",
    response_model=PurchasePlan,
    summary="Explicitly approve a Purchase Plan",
    description="Transitions purchase plan to APPROVED status, enabling subsequent PayPal Sandbox checkout order creation.",
)
async def approve_purchase_plan(plan_id: str) -> PurchasePlan:
    """Explicitly approve a purchase plan."""
    service = PurchasePlanService()
    return service.approve_plan(plan_id)
