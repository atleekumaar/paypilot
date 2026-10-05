"""Policy engine enforcing security boundaries, spending limits, and human approval gates."""

from enum import Enum
import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.agents.registry import ToolPermission, ToolRegistry
from app.agents.state import AgentState
from app.repositories.product_repository import get_product_repository
from app.repositories.purchase_plan_repository import get_purchase_plan_repository
from app.schemas.purchase_plan import PurchasePlanStatus

logger = logging.getLogger(__name__)


class PolicyDecision(str, Enum):
    """Outcomes from policy engine evaluation."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class AutonomyPolicy(BaseModel):
    """User-level or platform-level spending and approval rules."""

    max_auto_purchase_amount: float = Field(
        default=0.0,
        description="Maximum dollar amount permitted for zero-approval autonomous purchase (Default $0: require approval for all)",
    )
    require_approval_all_purchases: bool = Field(
        default=True,
        description="Non-negotiable human-in-the-loop approval requirement",
    )


class PolicyEngine:
    """Evaluates proposed agent tool invocations against security and commercial constraints."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        autonomy_policy: Optional[AutonomyPolicy] = None,
    ):
        self._registry = tool_registry
        self._policy = autonomy_policy or AutonomyPolicy()
        self._product_repo = get_product_repository()
        self._plan_repo = get_purchase_plan_repository()

    def evaluate(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        state: AgentState,
    ) -> tuple[PolicyDecision, Optional[str]]:
        """Determine whether a tool request may execute, must be denied, or requires human approval."""
        # Rule 1: Unknown tool -> DENY
        tool_defn = self._registry.get_tool(tool_name)
        if not tool_defn:
            logger.warning(f"Policy DENY: Unknown tool '{tool_name}'")
            return PolicyDecision.DENY, f"Unknown tool '{tool_name}' is not registered."

        # Rule 2: Runaway step budget guard
        if state.current_step >= state.max_steps:
            logger.warning(f"Policy DENY: Agent exceeded max step budget ({state.max_steps})")
            return PolicyDecision.DENY, "Agent execution halted: Exceeded maximum allowed step count."

        # Rule 3: Read-only tools always allowed
        if tool_defn.permission == ToolPermission.READ:
            return PolicyDecision.ALLOW, None

        # Rule 4: Create Purchase Plan (Plan != Payment)
        if tool_name == "create_purchase_plan":
            prod_id = arguments.get("product_id") or (state.selected_product.id if state.selected_product else None)
            if prod_id:
                product = self._product_repo.get_by_id(prod_id)
                if not product or not product.stock:
                    return PolicyDecision.DENY, f"Cannot formulate purchase plan for unavailable or out-of-stock product."
            return PolicyDecision.ALLOW, None

        # Rule 5: Approval-required or Payment tools
        if tool_defn.permission in (ToolPermission.APPROVAL_REQUIRED, ToolPermission.PAYMENT):
            plan_id = arguments.get("purchase_plan_id") or state.purchase_plan_id

            if not plan_id:
                return PolicyDecision.DENY, "Missing required Purchase Plan reference."

            plan = self._plan_repo.get_by_id(plan_id)
            if not plan:
                return PolicyDecision.DENY, f"Referenced Purchase Plan '{plan_id}' does not exist."

            # Verify product inventory
            prod = self._product_repo.get_by_id(plan.product_id)
            if not prod or not prod.stock:
                return PolicyDecision.DENY, f"Payment denied: Product '{plan.product_name}' is out of stock."

            # Verify plan not already completed or cancelled
            if plan.status in (PurchasePlanStatus.COMPLETED, PurchasePlanStatus.CANCELLED, PurchasePlanStatus.FAILED):
                return PolicyDecision.DENY, f"Payment denied: Plan is already {plan.status.value}."

            # Strict Human-in-the-Loop check
            if state.approval_status != "APPROVED" or plan.status == PurchasePlanStatus.AWAITING_APPROVAL:
                logger.info(f"Policy REQUIRE_APPROVAL: Sensitive tool '{tool_name}' requires explicit user confirmation.")
                return PolicyDecision.REQUIRE_APPROVAL, "Payment and order creation require explicit user approval."

            # If user explicitly approved, allow execution through secure backend services
            return PolicyDecision.ALLOW, None

        # Default fallback
        return PolicyDecision.ALLOW, None
