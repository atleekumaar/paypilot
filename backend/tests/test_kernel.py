"""Unit and integration tests for Kernel Cloud Browser."""

import pytest
from app.agents.state import AgentState
from app.agents.tools import build_default_tool_registry
from app.services.kernel.client import KernelClient, KernelConfig
from app.services.kernel.service import KernelBrowserService, get_kernel_service


def test_kernel_config_detection():
    config = KernelConfig(api_key="test_key_123")
    assert config.is_configured is True
    assert config.mock_fallback_enabled is True

    empty_config = KernelConfig()
    assert empty_config.is_configured is False


def test_kernel_simulation_browse():
    client = KernelClient()
    result = client.browse("https://www.target.com/p/apple-macbook-air-m3", extract_policy=True)

    assert result.status == "SUCCESS"
    assert result.bot_bypass_success is True
    assert result.latency_ms > 0
    assert "replay" in result.replay_url
    assert result.merchant_policy["return_window_days"] == 30
    assert result.merchant_policy["free_returns"] is True
    assert result.in_stock is True


def test_kernel_domain_verification():
    service = KernelBrowserService()
    res = service.verify_merchant_domain("bestbuy.com")

    assert res["status"] == "VERIFIED_MERCHANT"
    assert res["domain"] == "bestbuy.com"
    assert res["bot_detection_passed"] is True
    assert "return_window_days" in res["policy"]


def test_kernel_health():
    service = KernelBrowserService()
    health = service.health()
    assert health["status"] == "healthy"
    assert health["provider"] == "Kernel Cloud Browser"


def test_agent_kernel_tool_execution():
    registry = build_default_tool_registry()
    tool = registry.get("browse_merchant_page")
    assert tool is not None

    state = AgentState(session_id="sess_test_kernel", user_id="test_user_kernel")
    exec_res = registry.execute(
        tool_name="browse_merchant_page",
        arguments={"url": "https://store.nike.com/air-zoom", "extract_policy": True},
        state=state,
    )

    assert exec_res.success is True
    out = exec_res.data
    assert out["status"] == "SUCCESS"
    assert out["bot_bypass_success"] is True
    assert "Nike" in out["page_title"] or "nike" in out["url"].lower()
    assert len(state.actions) > 0
    assert "Kernel cloud browser inspected" in state.actions[-1].summary

