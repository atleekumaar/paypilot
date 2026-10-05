"""Concrete commerce tool implementations wrapping backend services."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import uuid

from app.agents.registry import ToolPermission, ToolRegistry
from app.agents.state import AgentState, AgentStatus
from app.repositories.product_repository import get_product_repository
from app.schemas.purchase_plan import PurchasePlanCreateRequest
from app.services.checkout_service import CheckoutService
from app.services.order_service import OrderService
from app.services.purchase_plan_service import PurchasePlanService
from app.services.ranking_service import ProductRankingService
from app.services.search_service import ProductSearchService

logger = logging.getLogger(__name__)


def build_default_tool_registry() -> ToolRegistry:
    """Instantiate and populate the tool registry with all approved commerce tools."""
    registry = ToolRegistry()

    # Repositories & Services
    product_repo = get_product_repository()
    search_service = ProductSearchService(repository=product_repo)
    ranking_service = ProductRankingService()
    plan_service = PurchasePlanService()
    checkout_service = CheckoutService()

    # 1. TOOL: search_products (READ)
    def _search_products_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        category = arguments.get("category")
        max_price = arguments.get("max_price")
        min_price = arguments.get("min_price")
        min_rating = arguments.get("min_rating")
        in_stock_only = arguments.get("in_stock_only", True)
        keywords = arguments.get("keywords")
        required_features = arguments.get("required_features")

        candidates = search_service.search_products(
            category=category,
            max_price=max_price,
            min_price=min_price,
            min_rating=min_rating,
            in_stock_only=in_stock_only,
            keywords=keywords,
            required_features=required_features,
        )

        state.candidate_products = candidates
        summary = f"Found {len(candidates)} matching candidate products in catalogue."
        state.log_action("search_products", summary)
        logger.info(f"Agent tool [search_products]: {summary}")

        return {
            "total_found": len(candidates),
            "products": [p.model_dump() for p in candidates[:6]],
        }

    registry.register(
        name="search_products",
        description="Search PayPilot product catalogue with strict budget, category, and inventory filters.",
        permission=ToolPermission.READ,
        handler=_search_products_handler,
        parameters={
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "e.g. laptop, phone, headphones"},
                "max_price": {"type": "number", "description": "Maximum budget ceiling"},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "required_features": {"type": "array", "items": {"type": "string"}},
            },
        },
    )

    # 2. TOOL: get_product (READ)
    def _get_product_handler(arguments: Dict[str, Any], state: AgentState) -> Optional[Dict[str, Any]]:
        product_id = arguments.get("product_id", "").strip().upper()
        prod = product_repo.get_by_id(product_id)
        if prod:
            state.log_action("get_product", f"Retrieved verified specs for {prod.name} ({prod.id})")
            return prod.model_dump()
        return None

    registry.register(
        name="get_product",
        description="Retrieve comprehensive details and specifications for a single product SKU.",
        permission=ToolPermission.READ,
        handler=_get_product_handler,
        parameters={
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
        },
    )

    # 3. TOOL: compare_products (READ)
    def _compare_products_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        product_ids = arguments.get("product_ids", [])
        if not product_ids and state.candidate_products:
            # Default to top candidates already in state
            product_ids = [p.id for p in state.candidate_products[:3]]

        items = []
        for pid in product_ids:
            p = product_repo.get_by_id(pid)
            if p:
                feats = p.features or {}
                items.append({
                    "id": p.id,
                    "name": p.name,
                    "brand": p.brand,
                    "price": p.price,
                    "rating": p.rating,
                    "stock": p.stock,
                    "delivery_days": p.delivery_days,
                    "gpu": feats.get("gpu", "N/A"),
                    "ram_gb": feats.get("ram_gb", "N/A"),
                    "battery_hours": feats.get("battery_hours", "N/A"),
                })

        state.compared_products = items
        summary = f"Compared specifications for {len(items)} products."
        state.log_action("compare_products", summary)
        return {"compared_count": len(items), "comparison": items}

    registry.register(
        name="compare_products",
        description="Compare specifications, price-to-performance, and ratings across candidate products.",
        permission=ToolPermission.READ,
        handler=_compare_products_handler,
        parameters={
            "type": "object",
            "properties": {
                "product_ids": {"type": "array", "items": {"type": "string"}}
            },
        },
    )

    # 4. TOOL: create_purchase_plan (WRITE)
    def _create_purchase_plan_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        product_id = arguments.get("product_id")
        if not product_id and state.selected_product:
            product_id = state.selected_product.id

        if not product_id and state.candidate_products:
            product_id = state.candidate_products[0].id

        if not product_id:
            raise ValueError("No product_id provided for purchase plan formulation.")

        # Create authoritative plan
        plan = plan_service.create_plan(
            PurchasePlanCreateRequest(
                product_id=product_id,
                quantity=arguments.get("quantity", 1),
                recommendation_reason=arguments.get("recommendation_reason"),
            )
        )

        state.purchase_plan_id = plan.id
        state.purchase_plan = plan
        state.selected_product = product_repo.get_by_id(product_id)
        state.approval_required = True
        state.approval_status = "PENDING"
        state.status = AgentStatus.WAITING_FOR_APPROVAL

        summary = f"Created Purchase Plan {plan.id} for {plan.product_name} (${plan.total_amount:.2f})"
        state.log_action("create_purchase_plan", summary)
        return plan.model_dump()

    registry.register(
        name="create_purchase_plan",
        description="Formulate an authoritative purchase plan derived strictly from catalog pricing. Requires user approval.",
        permission=ToolPermission.WRITE,
        handler=_create_purchase_plan_handler,
        parameters={
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "quantity": {"type": "integer", "default": 1},
                "recommendation_reason": {"type": "string"},
            },
            "required": ["product_id"],
        },
    )

    # 5. TOOL: request_purchase_approval (APPROVAL_REQUIRED)
    def _request_purchase_approval_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        plan_id = arguments.get("purchase_plan_id") or state.purchase_plan_id
        if not plan_id:
            raise ValueError("No purchase plan available to request approval for.")

        plan = plan_service.get_plan(plan_id)
        state.status = AgentStatus.WAITING_FOR_APPROVAL
        state.approval_required = True
        state.approval_status = "PENDING"

        summary = f"Paused execution: Waiting for explicit user approval to purchase {plan.product_name} (${plan.total_amount:.2f})."
        state.log_action("request_purchase_approval", summary, status="waiting")
        return {
            "status": "WAITING_FOR_APPROVAL",
            "purchase_plan_id": plan.id,
            "product_name": plan.product_name,
            "total_amount": plan.total_amount,
            "currency": plan.currency,
        }

    registry.register(
        name="request_purchase_approval",
        description="Pause agent execution to prompt user for explicit purchase approval.",
        permission=ToolPermission.APPROVAL_REQUIRED,
        handler=_request_purchase_approval_handler,
        parameters={
            "type": "object",
            "properties": {"purchase_plan_id": {"type": "string"}},
        },
    )

    # 6. TOOL: create_paypal_order (APPROVAL_REQUIRED)
    def _create_paypal_order_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        plan_id = arguments.get("purchase_plan_id") or state.purchase_plan_id
        if not plan_id:
            raise ValueError("Cannot create PayPal order: Missing purchase plan ID.")

        order_data = checkout_service.create_paypal_order_for_plan(plan_id)
        state.paypal_order_id = order_data["paypal_order_id"]
        state.log_action("create_paypal_order", f"Created PayPal Sandbox order {state.paypal_order_id}")
        return order_data

    registry.register(
        name="create_paypal_order",
        description="Initialize PayPal Sandbox order for an approved purchase plan.",
        permission=ToolPermission.APPROVAL_REQUIRED,
        handler=_create_paypal_order_handler,
        parameters={
            "type": "object",
            "properties": {"purchase_plan_id": {"type": "string"}},
            "required": ["purchase_plan_id"],
        },
    )

    # 7. TOOL: capture_paypal_payment (PAYMENT)
    def _capture_paypal_payment_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        plan_id = arguments.get("purchase_plan_id") or state.purchase_plan_id
        order_id = arguments.get("paypal_order_id") or state.paypal_order_id

        if not plan_id or not order_id:
            raise ValueError("Missing purchase plan ID or PayPal Order ID.")

        payment = checkout_service.capture_paypal_payment(plan_id, order_id)
        state.payment_status = payment.status.value
        state.status = AgentStatus.COMPLETED

        summary = f"Verified payment capture {payment.capture_id} (${payment.amount:.2f} {payment.currency})"
        state.log_action("capture_paypal_payment", summary)
        return payment.model_dump()

    registry.register(
        name="capture_paypal_payment",
        description="Execute authoritative server-side capture of approved PayPal order.",
        permission=ToolPermission.PAYMENT,
        handler=_capture_paypal_payment_handler,
        parameters={
            "type": "object",
            "properties": {
                "purchase_plan_id": {"type": "string"},
                "paypal_order_id": {"type": "string"},
            },
            "required": ["purchase_plan_id", "paypal_order_id"],
        },
    )

    # =========================================================================
    # PHASE 5: POST-PURCHASE TOOLS
    # =========================================================================
    order_service = OrderService()

    # 8. TOOL: get_order (READ)
    def _get_order_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        if not order_id:
            raise ValueError("Missing required order_id.")
        detail = order_service.get_order(order_id, user_id=state.user_id)
        state.active_order_id = detail.id
        state.active_order = detail.model_dump()
        state.active_shipment = detail.shipment.model_dump() if detail.shipment else None
        state.log_action("get_order", f"Retrieved order {detail.id} ({detail.product_name})")
        return detail.model_dump()

    registry.register(
        name="get_order",
        description="Retrieve complete order detail with product, payment, and shipment status.",
        permission=ToolPermission.READ,
        handler=_get_order_handler,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    )

    # 9. TOOL: get_user_orders (READ)
    def _get_user_orders_handler(arguments: Dict[str, Any], state: AgentState) -> List[Dict[str, Any]]:
        user_id = arguments.get("user_id") or state.user_id
        orders = order_service.get_user_orders(user_id=user_id)
        state.log_action("get_user_orders", f"Retrieved {len(orders)} order(s) for user '{user_id}'")
        return [o.model_dump() for o in orders]

    registry.register(
        name="get_user_orders",
        description="Retrieve recent order history for the authenticated user.",
        permission=ToolPermission.READ,
        handler=_get_user_orders_handler,
        parameters={
            "type": "object",
            "properties": {"user_id": {"type": "string"}},
        },
    )

    # 10. TOOL: get_payment_status (READ)
    def _get_payment_status_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        if not order_id:
            raise ValueError("Missing required order_id.")
        detail = order_service.get_order(order_id, user_id=state.user_id)
        result = {
            "order_id": detail.id,
            "product_name": detail.product_name,
            "amount": detail.amount,
            "currency": detail.currency,
            "payment_status": detail.status,
            "paypal_order_id": detail.paypal_order_id,
            "payment_id": detail.payment_id,
            "provider": "PayPal",
        }
        state.log_action("get_payment_status", f"Verified payment status for {detail.id}: {detail.status}")
        return result

    registry.register(
        name="get_payment_status",
        description="Verify authoritative payment and PayPal capture state for an order.",
        permission=ToolPermission.READ,
        handler=_get_payment_status_handler,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    )

    # 11. TOOL: get_shipment_status (READ)
    def _get_shipment_status_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        if not order_id:
            raise ValueError("Missing required order_id.")
        shipment = order_service.get_shipment(order_id, user_id=state.user_id)
        state.active_shipment = shipment.model_dump()
        state.log_action("get_shipment_status", f"Retrieved shipment for {order_id}: {shipment.status.value}")
        return shipment.model_dump()

    registry.register(
        name="get_shipment_status",
        description="Fetch current shipment state, carrier, and latest scan update.",
        permission=ToolPermission.READ,
        handler=_get_shipment_status_handler,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    )

    # 12. TOOL: get_tracking_details (READ)
    def _get_tracking_details_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        query = arguments.get("query") or arguments.get("order_id") or state.active_order_id
        if not query:
            raise ValueError("Missing tracking query or order_id.")
        tracking = order_service.get_tracking(query, user_id=state.user_id)
        state.log_action("get_tracking_details", f"Retrieved tracking updates for {query}")
        return tracking

    registry.register(
        name="get_tracking_details",
        description="Lookup carrier tracking milestones and facility scan history.",
        permission=ToolPermission.READ,
        handler=_get_tracking_details_handler,
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    )

    # 13. TOOL: get_delivery_estimate (READ)
    def _get_delivery_estimate_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        if not order_id:
            raise ValueError("Missing required order_id.")
        detail = order_service.get_order(order_id, user_id=state.user_id)
        shipment = detail.shipment
        est = {
            "order_id": detail.id,
            "product_name": detail.product_name,
            "estimated_delivery": shipment.estimated_delivery if shipment else "Pending scheduling",
            "current_status": shipment.status.value if shipment else detail.status,
            "confidence": "Based on latest carrier scan telemetry",
            "is_demo": shipment.is_demo if shipment else True,
        }
        state.log_action("get_delivery_estimate", f"Delivery estimate for {detail.id}: {est['estimated_delivery']}")
        return est

    registry.register(
        name="get_delivery_estimate",
        description="Retrieve estimated delivery date and carrier delivery window.",
        permission=ToolPermission.READ,
        handler=_get_delivery_estimate_handler,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    )

    # 14. TOOL: detect_order_issue (READ)
    def _detect_order_issue_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        ref_date = arguments.get("reference_date")
        if not order_id:
            raise ValueError("Missing required order_id.")
        issue = order_service.detect_order_issue(order_id, user_id=state.user_id, reference_date_str=ref_date)
        state.log_action("detect_order_issue", f"Evaluated shipment issues for {order_id}: {issue['issue']}")
        return issue

    registry.register(
        name="detect_order_issue",
        description="Deterministic issue detector evaluating delivery delays, carrier notes, and milestones.",
        permission=ToolPermission.READ,
        handler=_detect_order_issue_handler,
        parameters={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "reference_date": {"type": "string"},
            },
            "required": ["order_id"],
        },
    )

    # 15. TOOL: prepare_support_request (WRITE)
    def _prepare_support_request_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        if not order_id:
            raise ValueError("Missing required order_id.")
        detail = order_service.get_order(order_id, user_id=state.user_id)
        shipment = detail.shipment
        est_date = shipment.estimated_delivery if shipment else "the scheduled date"

        draft = {
            "order_id": detail.id,
            "product_name": detail.product_name,
            "subject": f"Delivery delay inquiry for order {detail.id}",
            "recipient": "Merchant Support",
            "message": (
                f"Hello,\n\n"
                f"I'm contacting you regarding order {detail.id} ({detail.product_name}). "
                f"The estimated delivery date was {est_date}, but the shipment has not yet arrived.\n\n"
                f"Could you please provide an updated delivery estimate?\n\n"
                f"Thank you."
            ),
            "status": "DRAFT_READY",
        }
        state.support_request_draft = draft
        state.log_action("prepare_support_request", f"Prepared draft support inquiry for order {detail.id}")
        return draft

    registry.register(
        name="prepare_support_request",
        description="Draft a merchant support inquiry without sending it.",
        permission=ToolPermission.WRITE,
        handler=_prepare_support_request_handler,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    )

    # 16. TOOL: send_support_request (APPROVAL_REQUIRED)
    def _send_support_request_handler(arguments: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        order_id = arguments.get("order_id") or state.active_order_id
        if not order_id:
            raise ValueError("Missing required order_id.")
        ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"
        result = {
            "status": "SENT",
            "ticket_id": ticket_id,
            "order_id": order_id,
            "message": f"Support request {ticket_id} has been submitted to merchant support.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        state.support_request_approved = True
        state.log_action("send_support_request", f"Dispatched merchant support ticket {ticket_id}")
        return result

    registry.register(
        name="send_support_request",
        description="Dispatch prepared support inquiry to merchant after explicit user approval.",
        permission=ToolPermission.APPROVAL_REQUIRED,
        handler=_send_support_request_handler,
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    )

    return registry
