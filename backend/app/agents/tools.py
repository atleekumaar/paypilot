"""Concrete commerce tool implementations wrapping backend services."""

import logging
from typing import Any, Dict, List, Optional

from app.agents.registry import ToolPermission, ToolRegistry
from app.agents.state import AgentState, AgentStatus
from app.repositories.product_repository import get_product_repository
from app.schemas.purchase_plan import PurchasePlanCreateRequest
from app.services.checkout_service import CheckoutService
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

    return registry
