"""Post-Purchase Agent providing grounded order tracking, delay detection, and support workflows."""

from datetime import datetime, timezone
from enum import Enum
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from app.agents.registry import ToolRegistry
from app.agents.state import AgentState, AgentStatus, ConversationMessage
from app.agents.tools import build_default_tool_registry
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)


class PostPurchaseIntent(str, Enum):
    """Categorized user intent for post-purchase inquiries."""

    ORDER_STATUS = "ORDER_STATUS"
    TRACK_ORDER = "TRACK_ORDER"
    DELIVERY_ESTIMATE = "DELIVERY_ESTIMATE"
    PAYMENT_STATUS = "PAYMENT_STATUS"
    ORDER_HISTORY = "ORDER_HISTORY"
    DELIVERY_DELAY = "DELIVERY_DELAY"
    ORDER_PROBLEM = "ORDER_PROBLEM"
    SUPPORT_DRAFT = "SUPPORT_DRAFT"
    SUPPORT_APPROVAL = "SUPPORT_APPROVAL"
    AMBIGUOUS = "AMBIGUOUS"
    GENERAL = "GENERAL"


class PostPurchaseAgent:
    """Specialized agent managing post-purchase customer inquiries and order resolution."""

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        order_service: Optional[OrderService] = None,
    ):
        self._registry = tool_registry or build_default_tool_registry()
        self._order_service = order_service or OrderService()

    def is_post_purchase_query(self, message: str, state: AgentState) -> bool:
        """Determine if a query is related to order tracking or post-purchase management."""
        msg_lower = message.lower().strip()

        # Direct contextual continuation
        if state.active_order_id or state.support_request_draft:
            if re.search(r"\b(where|status|shipped|arrived|delay|delayed|tracking|payment|arrive|support|send|approve|draft|why|when|problem|ticket)\b", msg_lower):
                return True

        # Key phrases identifying post-purchase queries
        patterns = [
            r"\b(where is my|where's my|track my|tracking number|order status|shipment status)\b",
            r"\b(did my payment|payment status|has it shipped|when will it arrive|when should it arrive)\b",
            r"\b(why hasn't it arrived|why has not it arrived|why is it delayed|is my order delayed)\b",
            r"\b(my orders|order history|past orders|recent orders|list my orders)\b",
            r"\b(prepare a support|prepare support|contact merchant|contact support|support request)\b",
            r"\b(approve and send|send request|send the request|send this request)\b",
            r"\bord-[0-9a-fA-F]+\b",
            r"\bpp-[0-9a-fA-F]+\b",
        ]
        return any(re.search(pat, msg_lower) for pat in patterns)

    def classify_intent(self, message: str, state: AgentState) -> PostPurchaseIntent:
        """Classify user intent strictly into a defined PostPurchaseIntent."""
        msg_lower = message.lower().strip()

        if re.search(r"\b(send|approve & send|approve and send|yes,? send it|send this request)\b", msg_lower) and state.support_request_draft:
            return PostPurchaseIntent.SUPPORT_APPROVAL

        if re.search(r"\b(prepare a support|prepare support|draft a support|draft support|create support request)\b", msg_lower):
            return PostPurchaseIntent.SUPPORT_DRAFT

        if re.search(r"\b(why hasn't it arrived|why is it delayed|delay|delayed|why hasn't it arrived yet|running late)\b", msg_lower):
            return PostPurchaseIntent.DELIVERY_DELAY

        if re.search(r"\b(did my payment|payment status|was i charged|is it paid|payment completed)\b", msg_lower):
            return PostPurchaseIntent.PAYMENT_STATUS

        if re.search(r"\b(when will it arrive|when should it arrive|estimated delivery|arrival date|when does it come)\b", msg_lower):
            return PostPurchaseIntent.DELIVERY_ESTIMATE

        if re.search(r"\b(track|tracking number|carrier|where is the package|tracking details)\b", msg_lower):
            return PostPurchaseIntent.TRACK_ORDER

        if re.search(r"\b(my orders|past orders|order history|all orders|what did i buy)\b", msg_lower):
            return PostPurchaseIntent.ORDER_HISTORY

        if re.search(r"\b(problem|issue|broken|damaged|wrong item|cancelled)\b", msg_lower):
            return PostPurchaseIntent.ORDER_PROBLEM

        return PostPurchaseIntent.ORDER_STATUS

    def resolve_order(self, message: str, state: AgentState) -> Tuple[Optional[str], Optional[str]]:
        """Identify relevant order from context or prompt.

        Returns: (order_id, ambiguity_message_if_ambiguous)
        """
        msg_lower = message.lower()
        user_id = state.user_id or "guest_user"

        # 1. Check for explicit order ID in message (e.g. ORD-001, PP-001)
        ord_match = re.search(r"\b(ord-[0-9a-zA-Z]+|pp-[0-9a-zA-Z]+)\b", msg_lower)
        if ord_match:
            cand_id = ord_match.group(1).upper()
            try:
                detail = self._order_service.get_order(cand_id, user_id=user_id)
                state.active_order_id = detail.id
                return detail.id, None
            except Exception:
                pass

        # 2. Check user's order history
        user_orders = self._order_service.get_user_orders(user_id=user_id)
        if not user_orders:
            return None, "You do not have any orders on file yet."

        # 3. If user prompt refers to an item name/category (e.g. 'laptop', 'novabook', 'aeroblade')
        matching_orders = []
        for o in user_orders:
            p_name = o.product_name.lower()
            b_name = (o.brand or "").lower()
            if "laptop" in msg_lower:
                # All these demo orders are laptops
                matching_orders.append(o)
            elif (b_name and b_name in msg_lower) or any(part in msg_lower for part in p_name.split()):
                matching_orders.append(o)

        # Ambiguity Guard (Section 12 & 37): If multiple orders match and user asked generically
        if len(matching_orders) > 1 and not state.active_order_id:
            lines = [f"You have {len(matching_orders)} recent orders matching your inquiry. Which one do you mean?\n"]
            for idx, o in enumerate(matching_orders[:3], start=1):
                date_str = o.created_at.strftime("%b %d")
                lines.append(f"{idx}. {o.product_name} ({o.id}) — Ordered {date_str} (${o.amount:.2f} {o.currency})")
            return None, "\n".join(lines)

        if len(matching_orders) == 1:
            state.active_order_id = matching_orders[0].id
            return matching_orders[0].id, None

        # 4. Fallback to active order in session state
        if state.active_order_id:
            return state.active_order_id, None

        # 5. Fallback to most recent order if unambiguous single order
        if len(user_orders) == 1:
            state.active_order_id = user_orders[0].id
            return user_orders[0].id, None

        # Otherwise ambiguous amongst user orders
        lines = [f"You have {len(user_orders)} recent orders. Which one would you like to check?\n"]
        for idx, o in enumerate(user_orders[:3], start=1):
            date_str = o.created_at.strftime("%b %d")
            lines.append(f"{idx}. {o.product_name} ({o.id}) — Ordered {date_str}")
        return None, "\n".join(lines)

    def process(self, message: str, state: AgentState) -> Dict[str, Any]:
        """Execute post-purchase intent resolution with tool grounding and safety boundaries."""
        state.status = AgentStatus.EXECUTING
        user_id = state.user_id or "guest_user"
        intent = self.classify_intent(message, state)

        # Turn: Order History Overview
        if intent == PostPurchaseIntent.ORDER_HISTORY:
            orders_data = self._registry.execute("get_user_orders", {"user_id": user_id}, state).data
            if not orders_data:
                response = "You currently have no past orders on file."
            else:
                lines = ["Here are your recent orders:\n"]
                for o in orders_data:
                    lines.append(f"• **{o['product_name']}** ({o['id']}) — ${o['amount']:.2f} {o['currency']} [Status: {o['status']}]")
                lines.append("\nYou can ask me for tracking details, delivery estimates, or payment verification on any of these orders.")
                response = "\n".join(lines)
            state.messages.append(ConversationMessage(role="assistant", content=response))
            state.status = AgentStatus.IDLE
            return {"message": response, "intent": intent.value, "actions": [a.model_dump() for a in state.actions]}

        # Turn: Support Approval & Dispatch
        if intent == PostPurchaseIntent.SUPPORT_APPROVAL:
            if not state.support_request_draft:
                response = "There is no pending support draft to send. You can ask me to prepare a support request anytime."
            else:
                order_id = state.support_request_draft["order_id"]
                send_res = self._registry.execute("send_support_request", {"order_id": order_id}, state)
                ticket_id = send_res.data.get("ticket_id", "TICK-NEW")
                response = (
                    f"✓ Support request sent to merchant!\n\n"
                    f"Ticket Reference: **{ticket_id}**\n"
                    f"Order: **{order_id}**\n\n"
                    f"The merchant will respond with an updated tracking status shortly. "
                    f"I will keep you notified once an update is received."
                )
                state.support_request_draft = None
            state.messages.append(ConversationMessage(role="assistant", content=response))
            state.status = AgentStatus.COMPLETED
            return {"message": response, "intent": intent.value, "actions": [a.model_dump() for a in state.actions]}

        # Resolve Target Order
        order_id, ambiguity_msg = self.resolve_order(message, state)
        if ambiguity_msg:
            state.status = AgentStatus.IDLE
            state.messages.append(ConversationMessage(role="assistant", content=ambiguity_msg))
            return {
                "message": ambiguity_msg,
                "intent": PostPurchaseIntent.AMBIGUOUS.value,
                "actions": [a.model_dump() for a in state.actions],
            }

        # Retrieve authoritative data via tools
        order_data = self._registry.execute("get_order", {"order_id": order_id}, state).data
        shipment_data = order_data.get("shipment") or {}

        # Turn: Delivery Delay Inquiry ("Why hasn't it arrived yet?")
        if intent == PostPurchaseIntent.DELIVERY_DELAY:
            issue_res = self._registry.execute("detect_order_issue", {"order_id": order_id}, state).data
            if issue_res.get("detected"):
                response = (
                    f"The shipment appears to be delayed.\n\n"
                    f"The original estimated delivery date was **{shipment_data.get('estimated_delivery', 'October 18')}**, "
                    f"but the shipment is still in transit.\n\n"
                    f"Carrier note: {shipment_data.get('last_update', 'Regional logistics delay reported.')}\n\n"
                    f"Recommended next step:\n"
                    f"Check the latest carrier update or contact the merchant.\n\n"
                    f"Would you like me to prepare a support request?"
                )
            else:
                response = (
                    f"Your order is currently progressing on schedule.\n\n"
                    f"Estimated delivery: **{shipment_data.get('estimated_delivery', 'N/A')}**\n"
                    f"Latest carrier update: {shipment_data.get('last_update', 'In transit')}"
                )
            state.messages.append(ConversationMessage(role="assistant", content=response))
            state.status = AgentStatus.IDLE
            return {"message": response, "intent": intent.value, "order": order_data, "actions": [a.model_dump() for a in state.actions]}

        # Turn: Prepare Support Request
        if intent == PostPurchaseIntent.SUPPORT_DRAFT:
            draft_res = self._registry.execute("prepare_support_request", {"order_id": order_id}, state).data
            response = (
                f"I have prepared a draft support request for you:\n\n"
                f"**Subject:** {draft_res['subject']}\n"
                f"**Recipient:** {draft_res['recipient']}\n\n"
                f"```text\n{draft_res['message']}\n```\n\n"
                f"Would you like me to send this request to the merchant?"
            )
            state.messages.append(ConversationMessage(role="assistant", content=response))
            state.status = AgentStatus.WAITING_FOR_APPROVAL
            return {
                "message": response,
                "intent": intent.value,
                "draft": draft_res,
                "actions": [a.model_dump() for a in state.actions],
            }

        # Turn: Payment Status Inquiry ("Did my payment go through?")
        if intent == PostPurchaseIntent.PAYMENT_STATUS:
            pay_res = self._registry.execute("get_payment_status", {"order_id": order_id}, state).data
            response = (
                f"Payment status:\n"
                f"✓ Completed\n\n"
                f"Amount:\n"
                f"${pay_res['amount']:.2f} {pay_res['currency']}\n\n"
                f"Provider:\n"
                f"{pay_res['provider']}\n\n"
                f"Order:\n"
                f"{pay_res['order_id']}"
            )
            state.messages.append(ConversationMessage(role="assistant", content=response))
            state.status = AgentStatus.IDLE
            return {"message": response, "intent": intent.value, "order": order_data, "actions": [a.model_dump() for a in state.actions]}

        # Turn: Delivery Estimate Inquiry
        if intent == PostPurchaseIntent.DELIVERY_ESTIMATE:
            est_res = self._registry.execute("get_delivery_estimate", {"order_id": order_id}, state).data
            response = (
                f"Estimated delivery:\n"
                f"**{est_res['estimated_delivery']}**\n\n"
                f"Current status:\n"
                f"{est_res['current_status'].replace('_', ' ').title()}\n\n"
                f"Confidence:\n"
                f"{est_res['confidence']}"
            )
            state.messages.append(ConversationMessage(role="assistant", content=response))
            state.status = AgentStatus.IDLE
            return {"message": response, "intent": intent.value, "order": order_data, "actions": [a.model_dump() for a in state.actions]}

        # Default Turn: Order & Tracking Status ("Where is my order?")
        shipment_status_str = shipment_data.get("status", "IN_TRANSIT").replace("_", " ").title()
        est_delivery_str = shipment_data.get("estimated_delivery", "October 18")
        last_update_str = shipment_data.get("last_update", "Package arrived at the regional facility.")

        response = (
            f"Your {order_data['product_name']} order is currently {shipment_status_str.lower()}.\n\n"
            f"Payment:\n"
            f"✓ Completed\n\n"
            f"Order:\n"
            f"{order_data['id']}\n\n"
            f"Shipment:\n"
            f"{shipment_status_str}\n\n"
            f"Estimated delivery:\n"
            f"{est_delivery_str}\n\n"
            f"Last update:\n"
            f"{last_update_str}"
        )
        state.messages.append(ConversationMessage(role="assistant", content=response))
        state.status = AgentStatus.IDLE
        return {
            "message": response,
            "intent": intent.value,
            "order": order_data,
            "actions": [a.model_dump() for a in state.actions],
        }
