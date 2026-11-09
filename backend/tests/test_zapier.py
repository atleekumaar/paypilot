"""Unit and integration tests for Zapier multi-app automation."""

import pytest
from app.agents.state import AgentState
from app.agents.tools import build_default_tool_registry
from app.services.zapier.client import ZapierClient, ZapierConfig
from app.services.zapier.service import ZapierAutomationService, get_zapier_service


def test_zapier_config():
    conf = ZapierConfig(webhook_url="https://hooks.zapier.com/hooks/catch/12345/abcde")
    assert conf.is_configured is True

    empty = ZapierConfig()
    assert empty.is_configured is False


def test_zapier_order_completed_dispatch():
    service = ZapierAutomationService()
    result = service.dispatch_order_completed(
        order_id="ORD-ZAP-1",
        user_id="user_zap_test",
        amount=299.99,
        currency="USD",
        product_name="Wireless Noise Cancelling Headphones",
        paypal_capture_id="CAP-12345",
    )

    assert result.event == "order_completed"
    assert result.status in ("DISPATCHED", "SUCCESS_SIMULATED")
    assert "Gmail" in result.target_apps or "Connected Zaps" in result.target_apps
    assert result.payload["total_amount"] == 299.99


def test_zapier_refund_alert_dispatch():
    service = ZapierAutomationService()
    result = service.dispatch_refund_alert(
        order_id="ORD-ZAP-1",
        user_id="user_zap_test",
        refund_amount=50.00,
        reason="Defective box latch",
        paypal_refund_id="REF-998877",
    )

    assert result.event == "refund_processed"
    assert result.status in ("DISPATCHED", "SUCCESS_SIMULATED")
    assert result.payload["refund_amount"] == 50.00


def test_zapier_health():
    service = ZapierAutomationService()
    health = service.health()
    assert health["status"] == "healthy"
    assert health["provider"] == "Zapier Automation Platform"
    assert health["connected_apps_supported"] == 9000


def test_agent_zapier_tool_execution():
    registry = build_default_tool_registry()
    tool = registry.get("trigger_zapier_automation")
    assert tool is not None

    state = AgentState(session_id="sess_test_zapier", user_id="agent_user_zapier")
    exec_res = registry.execute(
        tool_name="trigger_zapier_automation",
        arguments={
            "event": "customer_order_alert",
            "payload": {"order_id": "ORD-AGENT-01", "channel": "support-slack"},
        },
        state=state,
    )

    assert exec_res.success is True
    out = exec_res.data
    assert out["event"] == "customer_order_alert"
    assert out["status"] in ("DISPATCHED", "SUCCESS_SIMULATED")
    assert len(state.actions) > 0
    assert "Dispatched Zapier automation" in state.actions[-1].summary

