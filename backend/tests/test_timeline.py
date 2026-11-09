"""Tests for Bryntum Commerce Timeline Service and APIs."""

import pytest
from fastapi.testclient import TestClient

from app.agents.state import AgentState
from app.agents.tools import build_default_tool_registry
from app.main import app
from app.services.timeline_service import TimelineService

client = TestClient(app)


def test_timeline_service_generation():
    """Verify TimelineService builds Bryntum-compatible resources and events."""
    service = TimelineService()
    timeline = service.get_timeline(user_id="demo_user")

    assert "resources" in timeline
    assert "events" in timeline
    assert "timeRange" in timeline
    assert len(timeline["resources"]) > 0
    assert len(timeline["events"]) > 0

    # Verify Resource schema
    res = timeline["resources"][0]
    assert "id" in res
    assert "name" in res
    assert "orderId" in res
    assert "amount" in res

    # Verify Event schema
    event = timeline["events"][0]
    assert "id" in event
    assert "resourceId" in event
    assert "startDate" in event
    assert "endDate" in event
    assert "eventType" in event
    assert "status" in event
    assert "isEstimated" in event
    assert isinstance(event["isEstimated"], bool)


def test_timeline_filtering():
    """Test filtering timeline events by event_type and order_id."""
    service = TimelineService()

    # Filter by event_type = PAYMENT
    pay_timeline = service.get_timeline(user_id="demo_user", event_type="PAYMENT")
    assert all(e["eventType"] == "PAYMENT" for e in pay_timeline["events"])

    # Filter by event_type = DELIVERY
    del_timeline = service.get_timeline(user_id="demo_user", event_type="DELIVERY")
    assert all(e["eventType"] == "DELIVERY" for e in del_timeline["events"])

    # Filter by order_id
    if service.get_timeline(user_id="demo_user")["resources"]:
        target_order = service.get_timeline(user_id="demo_user")["resources"][0]["orderId"]
        filtered = service.get_timeline(user_id="demo_user", order_id=target_order)
        assert all(e["metadata"].get("orderId") == target_order for e in filtered["events"])


def test_timeline_summary():
    """Test timeline summary metrics calculation."""
    service = TimelineService()
    summary = service.get_summary(user_id="demo_user")

    assert "total_orders" in summary
    assert "active_shipments" in summary
    assert "pending_payments" in summary
    assert "verified_at" in summary
    assert summary["total_orders"] >= 1


def test_timeline_api_endpoints():
    """Test FastAPI /api/timeline endpoints."""
    # Test /api/timeline/events
    res = client.get("/api/timeline/events")
    assert res.status_code == 200
    data = res.json()
    assert "resources" in data
    assert "events" in data
    assert "timeRange" in data

    # Test /api/timeline/summary
    res_summary = client.get("/api/timeline/summary")
    assert res_summary.status_code == 200
    sum_data = res_summary.json()
    assert "total_orders" in sum_data
    assert "active_shipments" in sum_data


def test_agent_tool_query_commerce_timeline():
    """Verify that agent can invoke query_commerce_timeline tool."""
    registry = build_default_tool_registry()
    state = AgentState(session_id="test-tool-timeline", user_id="demo_user")

    result = registry.execute("query_commerce_timeline", {}, state)
    assert result.success is True
    assert "summary" in result.data
    assert "events" in result.data
    assert result.data["events_count"] > 0

