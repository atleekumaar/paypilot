"""Comprehensive test suite for Phase 4 Agentic Commerce, Policy Engine, and Tools."""

import pytest
from fastapi.testclient import TestClient

from app.agents.orchestrator import AgentOrchestrator
from app.agents.policies import AutonomyPolicy, PolicyDecision, PolicyEngine
from app.agents.registry import ToolDefinition, ToolPermission, ToolRegistry
from app.agents.state import AgentAction, AgentPlan, AgentState, AgentStatus, get_session_store
from app.agents.tools import build_default_tool_registry
from app.main import app
from app.repositories.payment_repository import get_payment_repository
from app.repositories.purchase_plan_repository import get_purchase_plan_repository
from app.schemas.payment import PaymentStatus
from app.schemas.purchase_plan import PurchasePlanStatus

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_environment():
    """Reset repositories and sessions before each test."""
    get_purchase_plan_repository().clear()
    get_payment_repository().clear()
    get_session_store().clear()


# 1. Test Agent State Model
def test_agent_state():
    state = AgentState(session_id="test-session")
    assert state.session_id == "test-session"
    assert state.status == AgentStatus.IDLE
    assert state.current_step == 0
    assert state.max_steps == 12

    action = state.log_action("search_products", "Found 10 items")
    assert action.step == 1
    assert action.tool == "search_products"
    assert len(state.actions) == 1


# 2. Test Tool Registry & Permissions
def test_tool_registry():
    registry = build_default_tool_registry()
    tools = registry.list_tools()
    tool_names = [t.name for t in tools]

    assert "search_products" in tool_names
    assert "compare_products" in tool_names
    assert "create_purchase_plan" in tool_names
    assert "create_paypal_order" in tool_names
    assert "capture_paypal_payment" in tool_names

    # Check permission levels
    assert registry.get_tool("search_products").permission == ToolPermission.READ
    assert registry.get_tool("create_purchase_plan").permission == ToolPermission.WRITE
    assert registry.get_tool("create_paypal_order").permission == ToolPermission.APPROVAL_REQUIRED
    assert registry.get_tool("capture_paypal_payment").permission == ToolPermission.PAYMENT


# 3. Test Unknown Tool Rejected
def test_unknown_tool_rejected():
    registry = build_default_tool_registry()
    state = AgentState(session_id="sess-test")
    res = registry.execute("unregistered_malicious_tool", {}, state)
    assert res.success is False
    assert "not registered" in res.error.lower()


# 4. Test Search Tool Execution
def test_search_tool():
    registry = build_default_tool_registry()
    state = AgentState(session_id="sess-search")
    res = registry.execute("search_products", {"category": "laptop", "max_price": 1200}, state)

    assert res.success is True
    assert res.data["total_found"] > 0
    assert len(state.candidate_products) > 0


# 5. Test Compare Products Tool
def test_compare_tool():
    registry = build_default_tool_registry()
    state = AgentState(session_id="sess-compare")
    res = registry.execute("compare_products", {"product_ids": ["LAP-001", "LAP-002"]}, state)

    assert res.success is True
    assert res.data["compared_count"] == 2
    comp = res.data["comparison"]
    assert comp[0]["id"] == "LAP-001"
    assert comp[0]["gpu"] == "RTX 4060"


# 6. Test Purchase Plan Tool (Authoritative Pricing)
def test_purchase_plan_tool():
    registry = build_default_tool_registry()
    state = AgentState(session_id="sess-plan")
    # Even if malicious argument price is passed, backend derives $1049
    res = registry.execute("create_purchase_plan", {"product_id": "LAP-001", "quantity": 1}, state)

    assert res.success is True
    plan_data = res.data
    assert plan_data["product_id"] == "LAP-001"
    assert plan_data["unit_price"] == 1049.0
    assert state.purchase_plan_id == plan_data["id"]
    assert state.approval_required is True
    assert state.status == AgentStatus.WAITING_FOR_APPROVAL


# 7. Critical Policy Test 1: Payment requires user approval
def test_payment_requires_approval():
    registry = build_default_tool_registry()
    policy = PolicyEngine(tool_registry=registry)
    state = AgentState(session_id="sess-policy")

    # Formulate plan
    registry.execute("create_purchase_plan", {"product_id": "LAP-001"}, state)

    # Attempt PayPal order creation while approval_status == NONE
    state.approval_status = "NONE"
    decision, reason = policy.evaluate("create_paypal_order", {"purchase_plan_id": state.purchase_plan_id}, state)

    assert decision == PolicyDecision.REQUIRE_APPROVAL
    assert "require explicit user approval" in reason.lower()


# 8. Critical Policy Test 2: Unknown tool denied by policy
def test_policy_engine_unknown_tool():
    registry = build_default_tool_registry()
    policy = PolicyEngine(tool_registry=registry)
    state = AgentState(session_id="sess-unknown")

    decision, reason = policy.evaluate("random_untrusted_tool", {}, state)
    assert decision == PolicyDecision.DENY
    assert "not registered" in reason.lower()


# 9. Critical Policy Test 3: Out-of-stock product purchase denied
def test_policy_denies_out_of_stock_purchase():
    registry = build_default_tool_registry()
    policy = PolicyEngine(tool_registry=registry)
    state = AgentState(session_id="sess-stock")

    decision, reason = policy.evaluate("create_purchase_plan", {"product_id": "LAP-024"}, state)
    assert decision == PolicyDecision.DENY
    assert "out-of-stock" in reason.lower()


# 10. Critical Policy Test 4: Max agent step budget enforcement
def test_max_agent_steps():
    registry = build_default_tool_registry()
    policy = PolicyEngine(tool_registry=registry)
    state = AgentState(session_id="sess-steps", max_steps=5, current_step=5)

    decision, reason = policy.evaluate("search_products", {}, state)
    assert decision == PolicyDecision.DENY
    assert "exceeded maximum allowed step count" in reason.lower()


# 11. Test Multi-turn Conversational Context and Pronoun Resolution
def test_session_context_and_reference_resolution():
    orchestrator = AgentOrchestrator()
    session_id = "sess-multiturn-1"

    # Turn 1: Search query
    res1 = orchestrator.process_message("Find me a laptop under 1200 for AI development.", session_id=session_id)
    assert res1["status"] == AgentStatus.COMPLETED.value
    assert len(res1["candidate_products"]) > 0

    # Turn 2: Follow-up question referencing previous results
    res2 = orchestrator.process_message("Why do you recommend this laptop?", session_id=session_id)
    assert res2["status"] == AgentStatus.COMPLETED.value
    assert "optimal balance" in res2["message"].lower()

    # Turn 3: "Buy it" - should resolve reference to the previously recommended product!
    res3 = orchestrator.process_message("Buy it.", session_id=session_id)
    assert res3["status"] == AgentStatus.WAITING_FOR_APPROVAL.value
    assert res3["purchase_plan_id"] is not None
    assert "approval is required" in res3["message"].lower()


# 12. Test Approval Resumes Agent to PayPal Order Creation
def test_approval_resumes_agent():
    orchestrator = AgentOrchestrator()
    session_id = "sess-approval-1"

    # Trigger purchase workflow
    orchestrator.process_message("Find me a laptop under 1200 and buy it.", session_id=session_id)

    # Approve purchase
    approve_res = orchestrator.approve_purchase(session_id)
    assert approve_res["status"] == AgentStatus.COMPLETED.value
    assert approve_res["paypal_order_id"] is not None
    assert "Purchase Plan approved!" in approve_res["message"]


# 13. Test Denial Stops Agent Workflow
def test_denial_stops_agent():
    orchestrator = AgentOrchestrator()
    session_id = "sess-denial-1"

    orchestrator.process_message("Find me a laptop under 1200 and buy it.", session_id=session_id)

    # Deny purchase
    deny_res = orchestrator.deny_purchase(session_id)
    assert deny_res["status"] == AgentStatus.IDLE.value
    assert "cancelled" in deny_res["message"].lower()


# 14. Test Agent Chat API Endpoint
def test_agent_chat_api():
    payload = {"message": "Find me the best laptop for AI development under 1200.", "session_id": "sess-api-1"}
    response = client.post("/api/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "sess-api-1"
    assert len(data["actions"]) > 0
    assert "recommend" in data["message"].lower() or "found" in data["message"].lower()


# 15. Test Agent Summary & Telemetry API
def test_agent_summary_api():
    session_id = "sess-telemetry-1"
    client.post("/api/agent/chat", json={"message": "Find me a keyboard under 150.", "session_id": session_id})

    summary_res = client.get(f"/api/agent/{session_id}/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["session_id"] == session_id
    assert summary["step_count"] > 0
    assert len(summary["tools_used"]) > 0
