"""Agent planning and multi-turn action determination logic."""

import logging
import re
from typing import Any, Dict, List, Optional

from app.agents.state import AgentPlan, AgentState, AgentStatus
from app.schemas.product import Product

logger = logging.getLogger(__name__)


class AgentPlanner:
    """Analyzes user message and conversational state to formulate structured operational plans."""

    def plan_workflow(self, message: str, state: AgentState) -> AgentPlan:
        """Formulate next sequence of tool actions based on message intent and current state."""
        msg_lower = message.lower().strip()

        # Intent: Explicit intent to purchase or proceed
        if re.search(r"\b(buy|purchase|order|checkout|get it|i'll take it|i like it|proceed)\b", msg_lower):
            target_prod = self._resolve_target_product(msg_lower, state)
            if target_prod:
                state.selected_product = target_prod
                return AgentPlan(
                    goal="create_purchase_plan_and_request_approval",
                    steps=["create_purchase_plan", "request_purchase_approval"],
                )

        # Intent: Follow-up comparison or inquiry on previously discovered products
        if state.candidate_products and re.search(r"\b(compare|which|better|difference|why|worth|specs|battery|gpu|ram)\b", msg_lower):
            return AgentPlan(
                goal="compare_and_explain",
                steps=["compare_products"],
            )

        # Default: New product discovery and recommendation
        return AgentPlan(
            goal="discover_and_recommend",
            steps=["search_products", "compare_products"],
        )

    def _resolve_target_product(self, msg: str, state: AgentState) -> Optional[Product]:
        """Resolve conversational reference (e.g. 'the first one', 'novabook', 'it') from state."""
        candidates = state.candidate_products
        if not candidates:
            return state.selected_product

        if "first" in msg or "1st" in msg or "#1" in msg or "top" in msg:
            return candidates[0]
        if "second" in msg or "2nd" in msg or "#2" in msg and len(candidates) > 1:
            return candidates[1]
        if "third" in msg or "3rd" in msg or "#3" in msg and len(candidates) > 2:
            return candidates[2]

        # Check for matching brand or product name
        for p in candidates:
            if p.name.lower() in msg or p.brand.lower() in msg or p.id.lower() in msg:
                return p

        # Default fallback to top recommended candidate
        return candidates[0]
