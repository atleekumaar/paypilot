"""Agent orchestrator executing controlled, multi-step commerce workflows."""

import logging
from typing import Any, Dict, Optional

from app.agents.planner import AgentPlanner
from app.agents.policies import PolicyDecision, PolicyEngine
from app.agents.registry import ToolRegistry
from app.agents.state import (
    AgentState,
    AgentStatus,
    ConversationMessage,
    SessionStore,
    get_session_store,
)
from app.agents.tools import build_default_tool_registry
from app.services.intent_service import IntentService
from app.services.ranking_service import ProductRankingService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates tool execution, conversational turn-taking, and security boundary enforcement."""

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        policy_engine: Optional[PolicyEngine] = None,
        session_store: Optional[SessionStore] = None,
        intent_service: Optional[IntentService] = None,
        ranking_service: Optional[ProductRankingService] = None,
    ):
        self._registry = tool_registry or build_default_tool_registry()
        self._policy = policy_engine or PolicyEngine(tool_registry=self._registry)
        self._sessions = session_store or get_session_store()
        self._intent_service = intent_service or IntentService()
        self._ranking_service = ranking_service or ProductRankingService()
        self._planner = AgentPlanner()

    def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a conversational commerce turn with the autonomous agent."""
        state = self._sessions.get_or_create(session_id)
        state.user_query = message
        state.messages.append(ConversationMessage(role="user", content=message))
        state.status = AgentStatus.UNDERSTANDING

        # Step 1: Understand request & parse intent
        intent = self._intent_service.extract_intent(message)
        state.log_action("understand_intent", f"Identified category: {intent.category}, budget: ${intent.hard_constraints.max_price}")

        # Step 2: Formulate operational plan
        plan = self._planner.plan_workflow(message, state)
        state.plan = plan
        state.status = AgentStatus.PLANNING

        # Step 3: Execute step-by-step tool actions
        response_text = ""

        for step_tool in plan.steps:
            if state.current_step >= state.max_steps:
                logger.warning(f"Session {state.session_id} exceeded step budget {state.max_steps}")
                state.status = AgentStatus.FAILED
                response_text = "I had to stop because this workflow exceeded the maximum allowed step limit."
                break

            # Build tool arguments based on intent & state
            arguments = self._build_tool_arguments(step_tool, intent, state)

            # Policy Check (Rule & Permission Boundary)
            decision, reason = self._policy.evaluate(step_tool, arguments, state)

            if decision == PolicyDecision.DENY:
                logger.warning(f"Policy denied execution of tool '{step_tool}': {reason}")
                state.log_action(step_tool, f"Denied by policy: {reason}", status="failed")
                response_text = f"Action could not be completed: {reason}"
                state.status = AgentStatus.FAILED
                break

            if decision == PolicyDecision.REQUIRE_APPROVAL:
                # Pause execution and prompt user
                state.status = AgentStatus.WAITING_FOR_APPROVAL
                state.approval_required = True
                state.approval_status = "PENDING"
                plan_obj = state.purchase_plan
                total_str = f"${plan_obj.total_amount:,.2f}" if plan_obj else ""
                prod_name = plan_obj.product_name if plan_obj else "item"
                response_text = (
                    f"I have prepared an authoritative Purchase Plan for {prod_name} ({total_str}). "
                    "Your explicit approval is required before I can initiate PayPal payment. Would you like to approve this purchase?"
                )
                break

            # Allowed: Execute Tool
            result = self._registry.execute(step_tool, arguments, state)
            if not result.success:
                logger.error(f"Tool execution failure: {result.error}")
                response_text = f"Encountered an issue running {step_tool}: {result.error}"
                state.status = AgentStatus.FAILED
                break

        # Generate final conversational synthesis if not waiting for approval or failed
        if state.status not in (AgentStatus.WAITING_FOR_APPROVAL, AgentStatus.FAILED):
            response_text = self._synthesize_response(plan, state)
            state.status = AgentStatus.COMPLETED

        state.messages.append(ConversationMessage(role="assistant", content=response_text))
        self._sessions.save(state)

        return {
            "session_id": state.session_id,
            "status": state.status.value,
            "message": response_text,
            "purchase_plan_id": state.purchase_plan_id,
            "purchase_plan": state.purchase_plan.model_dump() if state.purchase_plan else None,
            "candidate_products": [p.model_dump() for p in state.candidate_products[:3]],
            "actions": [a.model_dump() for a in state.actions],
        }

    def approve_purchase(self, session_id: str) -> Dict[str, Any]:
        """User explicitly approves purchase; resumes agent execution to create PayPal order."""
        state = self._sessions.get(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found.")

        if not state.purchase_plan_id or not state.purchase_plan:
            raise ValueError("No active purchase plan found in session to approve.")

        # Update approval status
        state.approval_status = "APPROVED"
        state.approval_required = False
        state.status = AgentStatus.EXECUTING
        state.log_action("user_approval", f"User explicitly approved purchase of {state.purchase_plan.product_name}.")

        # Execute create_paypal_order tool under approved policy
        order_res = self._registry.execute(
            "create_paypal_order",
            {"purchase_plan_id": state.purchase_plan_id},
            state,
        )

        if not order_res.success:
            state.status = AgentStatus.FAILED
            msg = f"Failed to initialize PayPal order: {order_res.error}"
        else:
            state.status = AgentStatus.COMPLETED
            msg = (
                f"Purchase Plan approved! I've created PayPal Sandbox Order {state.paypal_order_id}. "
                "You can now complete the transaction via PayPal Sandbox."
            )

        state.messages.append(ConversationMessage(role="assistant", content=msg))
        self._sessions.save(state)

        return {
            "session_id": state.session_id,
            "status": state.status.value,
            "message": msg,
            "paypal_order_id": state.paypal_order_id,
            "purchase_plan_id": state.purchase_plan_id,
            "actions": [a.model_dump() for a in state.actions],
        }

    def deny_purchase(self, session_id: str) -> Dict[str, Any]:
        """User denies purchase; halts purchasing workflow gracefully."""
        state = self._sessions.get(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found.")

        state.approval_status = "DENIED"
        state.approval_required = False
        state.status = AgentStatus.IDLE
        state.log_action("user_denial", "User declined purchase plan.", status="completed")

        msg = "Purchase plan cancelled. Let me know if you would like to search for different options or adjust your budget."
        state.messages.append(ConversationMessage(role="assistant", content=msg))
        self._sessions.save(state)

        return {
            "session_id": state.session_id,
            "status": state.status.value,
            "message": msg,
            "actions": [a.model_dump() for a in state.actions],
        }

    def _build_tool_arguments(self, tool_name: str, intent: Any, state: AgentState) -> Dict[str, Any]:
        """Prepare validated arguments for the target tool."""
        if tool_name == "search_products":
            return {
                "category": intent.hard_constraints.category,
                "max_price": intent.hard_constraints.max_price,
                "min_price": intent.hard_constraints.min_price,
                "min_rating": intent.hard_constraints.min_rating,
                "in_stock_only": intent.hard_constraints.in_stock,
                "required_features": intent.requirements,
            }
        elif tool_name == "compare_products":
            return {
                "product_ids": [p.id for p in state.candidate_products[:3]],
            }
        elif tool_name == "create_purchase_plan":
            prod = state.selected_product or (state.candidate_products[0] if state.candidate_products else None)
            return {
                "product_id": prod.id if prod else "",
                "quantity": 1,
                "recommendation_reason": "Top-ranked selection matching user constraints.",
            }
        elif tool_name == "request_purchase_approval":
            return {"purchase_plan_id": state.purchase_plan_id}
        elif tool_name == "create_paypal_order":
            return {"purchase_plan_id": state.purchase_plan_id}
        elif tool_name == "capture_paypal_payment":
            return {
                "purchase_plan_id": state.purchase_plan_id,
                "paypal_order_id": state.paypal_order_id,
            }
        return {}

    def _synthesize_response(self, plan: AgentPlan, state: AgentState) -> str:
        """Construct grounded, concise conversational explanation without hidden chain-of-thought."""
        if plan.goal == "compare_and_explain":
            if state.compared_products:
                lines = ["Here is a side-by-side comparison of the top options:"]
                for p in state.compared_products:
                    lines.append(f"• {p['name']} (${p['price']:,.0f}): {p['battery_hours']}h battery, {p['gpu']}, {p['rating']}★")
                return "\n".join(lines)

        if state.candidate_products:
            # Rank candidates
            top_ranked = self._ranking_service.rank_products(
                state.candidate_products,
                self._intent_service.extract_intent(state.user_query),
                top_k=3,
            )
            if top_ranked:
                top_pick = top_ranked[0]
                state.selected_product = top_pick.product
                state.log_action("recommend_product", f"Recommended {top_pick.product.name} (Score: {top_pick.score}/100)")
                return (
                    f"I found {len(state.candidate_products)} matching options within your criteria. "
                    f"My top recommendation is the **{top_pick.product.name}** (${top_pick.product.price:,.2f}). "
                    f"It offers the strongest combination of specifications and value."
                )

        return "I couldn't find any products matching those constraints. Try adjusting your budget or relaxing some criteria."
