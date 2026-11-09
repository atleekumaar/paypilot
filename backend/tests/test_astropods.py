"""Tests for Astropods Control Plane, Telemetry Tracing, and Blueprint Integration."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.astropods_service import AstropodsService, redact_sensitive_data

client = TestClient(app)


def test_redact_sensitive_data():
    """Verify that sensitive API keys, PayPal secrets, and Bearer tokens are redacted."""
    raw_secret = "paypal_client_secret: mock_secret_key_abcdef1234567890"
    redacted = redact_sensitive_data(raw_secret)
    assert "mock_secret_key_abcdef" not in redacted
    assert "[REDACTED_SECRET]" in redacted

    raw_groq = "Using gsk_mocktestkey1234567890abcdefghijklmnopqrstuvwxyz for inference"
    redacted_groq = redact_sensitive_data(raw_groq)
    assert "mocktestkey" not in redacted_groq
    assert "[REDACTED_GROQ_KEY]" in redacted_groq

    nested = {
        "headers": {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"},
        "details": "api-key=secret1234567890",
    }
    redacted_nested = redact_sensitive_data(nested)
    assert "[REDACTED_TOKEN]" in redacted_nested["headers"]["Authorization"]
    assert "[REDACTED_KEY]" in redacted_nested["details"]


def test_astropods_trace_lifecycle():
    """Test start_trace, start_span, finish_span, and finish_trace behavior."""
    service = AstropodsService()
    session_id = "test-session-astro-1"
    user_id = "test_user_1"

    trace = service.start_trace(session_id, user_id, "Find me a MacBook Pro with secret mock_secret_val_12345")
    assert trace.session_id == session_id
    assert "[REDACTED_SECRET]" in trace.query
    assert trace.status == "executing"

    # Add span
    service.start_span(session_id, "search_products", "tool_call")
    service.finish_span(session_id, "search_products", status="success", metadata={"count": 5})

    # Add error span
    service.start_span(session_id, "invalid_call", "tool_call")
    service.finish_span(session_id, "invalid_call", status="error", error="Tool timeout")

    service.finish_trace(session_id, status="completed")

    traces = service.get_session_traces(session_id)
    assert len(traces) == 1
    t = traces[0]
    assert t["status"] == "completed"
    assert t["metrics"]["total_spans"] == 2
    assert t["metrics"]["failed_spans"] == 1
    assert len(t["spans"]) == 2
    assert t["spans"][0]["name"] == "search_products"
    assert t["spans"][0]["status"] == "success"
    assert t["spans"][1]["name"] == "invalid_call"
    assert t["spans"][1]["status"] == "error"


def test_astropods_overview_metrics():
    """Test aggregated observability metrics across sessions."""
    service = AstropodsService()
    service.start_trace("sess-a", "user-1", "Query A")
    service.finish_trace("sess-a", "completed")

    overview = service.get_overview()
    assert overview["mode"] in ("LOCAL", "CLOUD")
    assert overview["project_id"] == "paypilot-ai-commerce"
    assert overview["total_traces"] >= 1
    assert "guardrails" in overview
    assert overview["guardrails"]["human_in_the_loop"] == "active"


def test_astropods_api_endpoints():
    """Test FastAPI endpoints for Astropods telemetry."""
    # 1. Overview endpoint
    res = client.get("/api/agent/astropods/overview")
    assert res.status_code == 200
    data = res.json()
    assert "mode" in data
    assert "guardrails" in data
    assert data["guardrails"]["secret_redaction"] == "active"

