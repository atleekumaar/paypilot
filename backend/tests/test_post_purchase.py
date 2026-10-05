"""Comprehensive test suite for Phase 5 Post-Purchase Agent, Order Tracking, and Issue Detection."""

from datetime import date
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.agents.orchestrator import AgentOrchestrator
from app.agents.post_purchase import PostPurchaseAgent, PostPurchaseIntent
from app.agents.state import AgentState, AgentStatus
from app.agents.tools import build_default_tool_registry
from app.repositories.order_repository import get_order_repository
from app.repositories.shipment_repository import get_shipment_repository
from app.schemas.notification import NotificationType
from app.services.notification_service import get_notification_service
from app.services.order_service import OrderService

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_repositories():
    """Ensure repositories have clean demo data before each test."""
    get_order_repository().reset_defaults()
    get_shipment_repository().reset_defaults()
    get_notification_service().reset_defaults()
    yield


# 1. Test Get User Orders
def test_get_user_orders():
    order_svc = OrderService()
    orders = order_svc.get_user_orders(user_id="guest_user")
    assert len(orders) >= 3
    order_ids = [o.id for o in orders]
    assert "ORD-001" in order_ids
    assert "ORD-002" in order_ids
    assert "ORD-003" in order_ids
    assert "ORD-099" not in order_ids  # Belong to other_user_88


# 2. Test Get Single Order Detail
def test_get_order():
    order_svc = OrderService()
    detail = order_svc.get_order("ORD-001", user_id="guest_user")
    assert detail.id == "ORD-001"
    assert detail.product_name == "NovaBook Pro 14"
    assert detail.amount == 1049.0
    assert detail.shipment is not None
    assert detail.shipment.carrier == "FastShip Logistics"
    assert detail.shipment.tracking_number == "TRK-FAST-884210"


# 3. Critical Security: User Isolation & Mismatch Prevention
def test_user_cannot_access_another_users_order():
    order_svc = OrderService()
    # ORD-099 is owned by other_user_88
    with pytest.raises(HTTPException) as exc_info:
        order_svc.get_order("ORD-099", user_id="guest_user")

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail

    # Via REST API
    res = client.get("/api/orders/ORD-099?user_id=guest_user")
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


# 4. Test Payment Status Verification
def test_get_payment_status():
    order_svc = OrderService()
    detail = order_svc.get_order("ORD-001", user_id="guest_user")
    assert detail.status == "IN_TRANSIT"
    assert detail.paypal_order_id == "MOCK-PAYPAL-ORD-001"
    assert detail.payment_id == "PAY-001"


# 5. Test Shipment Status & Tracking Telemetry
def test_get_shipment_status():
    order_svc = OrderService()
    shipment = order_svc.get_shipment("ORD-001", user_id="guest_user")
    assert shipment.status.value == "IN_TRANSIT"
    assert "regional facility" in shipment.last_update.lower()
    assert len(shipment.timeline) >= 4


# 6. Test Delivery Estimate
def test_delivery_estimate():
    registry = build_default_tool_registry()
    state = AgentState(session_id="test-est", user_id="guest_user")
    res = registry.execute("get_delivery_estimate", {"order_id": "ORD-001"}, state)
    assert res.success
    assert res.data["estimated_delivery"] == "2026-10-18"
    assert "scan telemetry" in res.data["confidence"].lower()


# 7. Test Delay Detection Rules (Section 36)
def test_delay_detection():
    order_svc = OrderService()

    # Case A: Current simulated date is Oct 20, 2026 > expected delivery Oct 18, 2026
    issue_delayed = order_svc.detect_order_issue(
        "ORD-001",
        user_id="guest_user",
        reference_date_str="2026-10-20",
    )
    assert issue_delayed["detected"] is True
    assert issue_delayed["issue"] == "DELIVERY_DELAY"
    assert issue_delayed["severity"] == "MEDIUM"

    # Case B: Current simulated date is Oct 17, 2026 < expected delivery Oct 22, 2026 for ORD-003
    issue_ontime = order_svc.detect_order_issue(
        "ORD-003",
        user_id="guest_user",
        reference_date_str="2026-10-17",
    )
    assert issue_ontime["detected"] is False
    assert issue_ontime["issue"] == "NO_ISSUE"


# 8. Test Post-Purchase Intent Classification
def test_post_purchase_intent():
    agent = PostPurchaseAgent()
    state = AgentState(session_id="intent-test", user_id="guest_user")

    assert agent.classify_intent("Where is my order?", state) == PostPurchaseIntent.ORDER_STATUS
    assert agent.classify_intent("Track my package", state) == PostPurchaseIntent.TRACK_ORDER
    assert agent.classify_intent("When should it arrive?", state) == PostPurchaseIntent.DELIVERY_ESTIMATE
    assert agent.classify_intent("Did my payment go through?", state) == PostPurchaseIntent.PAYMENT_STATUS
    assert agent.classify_intent("Show my past orders", state) == PostPurchaseIntent.ORDER_HISTORY
    assert agent.classify_intent("Why hasn't it arrived yet?", state) == PostPurchaseIntent.DELIVERY_DELAY
    assert agent.classify_intent("Prepare a support request", state) == PostPurchaseIntent.SUPPORT_DRAFT


# 9. Test Order Ambiguity Resolution (Section 37)
def test_ambiguous_order_resolution():
    agent = PostPurchaseAgent()
    state = AgentState(session_id="ambig-test", user_id="guest_user")

    # User has multiple laptop orders (ORD-001, ORD-002, ORD-003)
    order_id, ambiguity_msg = agent.resolve_order("Where is my laptop?", state)

    # Must NOT arbitrarily choose one
    assert order_id is None
    assert ambiguity_msg is not None
    assert "Which one do you mean?" in ambiguity_msg
    assert "NovaBook Pro 14" in ambiguity_msg
    assert "AeroBlade Slim 15" in ambiguity_msg


# 10. Test Single Unambiguous Order Resolution
def test_order_reference_resolution():
    agent = PostPurchaseAgent()
    state = AgentState(session_id="ref-test", user_id="guest_user")

    # Specific brand mentioned
    order_id, ambiguity_msg = agent.resolve_order("Where is my NovaBook?", state)
    assert order_id == "ORD-001"
    assert ambiguity_msg is None

    # Specific order ID mentioned
    order_id2, _ = agent.resolve_order("Can you track ORD-002?", state)
    assert order_id2 == "ORD-002"


# 11. Test Support Request Draft (No Automatic Sending)
def test_support_request_draft():
    agent = PostPurchaseAgent()
    state = AgentState(session_id="draft-test", user_id="guest_user", active_order_id="ORD-001")

    res = agent.process("Prepare a support request", state)
    assert res["intent"] == PostPurchaseIntent.SUPPORT_DRAFT.value
    assert "draft" in res
    assert res["draft"]["status"] == "DRAFT_READY"
    assert res["draft"]["order_id"] == "ORD-001"
    assert state.status == AgentStatus.WAITING_FOR_APPROVAL
    assert state.support_request_draft is not None
    assert state.support_request_approved is False


# 12. Test Support Action Approval Execution
def test_support_action_requires_approval():
    orchestrator = AgentOrchestrator()
    session_id = "sess-support-approval"

    # Step 1: User asks to prepare support request
    r1 = orchestrator.process_message("Where is my NovaBook? Why hasn't it arrived yet?", session_id=session_id)
    assert "delayed" in r1["message"].lower()

    r2 = orchestrator.process_message("Prepare a support request", session_id=session_id)
    assert "Subject:" in r2["message"]

    # Step 2: User explicitly approves sending the draft
    r3 = orchestrator.approve_purchase(session_id=session_id)
    assert r3["status"] == AgentStatus.COMPLETED.value
    assert "Support request sent to merchant" in r3["message"]
    assert "Ticket Reference:" in r3["message"]


# 13. Test Notification Creation & Listing
def test_notification_creation():
    notif_svc = get_notification_service()
    notif = notif_svc.notify(
        user_id="guest_user",
        type=NotificationType.ORDER_UPDATE,
        title="Delivery update",
        message="Package scanned at destination facility.",
        order_id="ORD-001",
    )
    assert notif.id is not None
    assert notif.read is False

    user_notifs = notif_svc.list_user_notifications("guest_user")
    assert any(n.id == notif.id for n in user_notifs)


# 14. Test Notification Read State
def test_notification_read_state():
    notif_svc = get_notification_service()
    user_notifs = notif_svc.list_user_notifications("guest_user")
    target_id = user_notifs[0].id

    updated = notif_svc.mark_as_read(target_id, user_id="guest_user")
    assert updated.read is True


# 15. End-to-End Demo Scenario Test (Section 40 & 46)
def test_demo_scenario_end_to_end():
    orchestrator = AgentOrchestrator()
    session_id = "sess-demo-scenario"

    # Turn 1: User asks: "Where is my NovaBook?"
    t1 = orchestrator.process_message("Where is my NovaBook?", session_id=session_id)
    assert "in transit" in t1["message"].lower()
    assert "ORD-001" in t1["message"]
    assert "October 18" in t1["message"]
    assert "Package arrived at the regional facility" in t1["message"]

    # Turn 2: User asks: "Why hasn't it arrived yet?"
    t2 = orchestrator.process_message("Why hasn't it arrived yet?", session_id=session_id)
    assert "delayed" in t2["message"].lower()
    assert "Regional logistics delay" in t2["message"]
    assert "Would you like me to prepare a support request?" in t2["message"]

    # Turn 3: User says: "Prepare a support request."
    t3 = orchestrator.process_message("Prepare a support request.", session_id=session_id)
    assert "draft support request" in t3["message"].lower()
    assert "Delivery delay inquiry" in t3["message"]
    assert "Would you like me to send this request" in t3["message"]

    # Turn 4: User approves action
    t4 = orchestrator.approve_purchase(session_id=session_id)
    assert "Support request sent to merchant" in t4["message"]
    assert "Ticket Reference:" in t4["message"]
