"""Unit and integration tests for Commerce Intelligence & Analytics APIs."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import init_db
from app.core.auth import AuthenticatedUser, get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_analytics_overview_endpoint():
    """Verify GET /api/analytics/overview returns verified KPIs."""
    res = client.get("/api/analytics/overview", headers={"Authorization": "Bearer demo-token"})
    assert res.status_code == 200
    data = res.json()
    assert "total_spending" in data
    assert "total_orders" in data
    assert "average_order_value" in data
    assert "completed_payments" in data
    assert "failed_payments" in data
    assert "pending_orders" in data
    assert data["currency"] == "USD"
    assert isinstance(data["total_spending"], (int, float))


def test_analytics_spending_endpoint():
    """Verify GET /api/analytics/spending returns time and category trends."""
    res = client.get("/api/analytics/spending", headers={"Authorization": "Bearer demo-token"})
    assert res.status_code == 200
    data = res.json()
    assert "spending_over_time" in data
    assert "spending_by_category" in data
    assert "payment_status_distribution" in data
    assert isinstance(data["spending_by_category"], list)


def test_analytics_orders_grid_endpoint():
    """Verify GET /api/analytics/orders returns enriched order records."""
    res = client.get("/api/analytics/orders", headers={"Authorization": "Bearer demo-token"})
    assert res.status_code == 200
    orders = res.json()
    assert isinstance(orders, list)
    if orders:
        first = orders[0]
        assert "order_id" in first
        assert "amount" in first
        assert "order_status" in first


def test_analytics_payments_grid_endpoint():
    """Verify GET /api/analytics/payments returns verified payment records."""
    res = client.get("/api/analytics/payments", headers={"Authorization": "Bearer demo-token"})
    assert res.status_code == 200
    payments = res.json()
    assert isinstance(payments, list)


def test_analytics_products_grid_endpoint():
    """Verify GET /api/analytics/products returns catalog with specs and scores."""
    res = client.get("/api/analytics/products")
    assert res.status_code == 200
    products = res.json()
    assert isinstance(products, list)
    assert len(products) > 0
    assert "recommendation_score" in products[0]
    assert "specs" in products[0]


def test_analytics_ai_dashboard_agent_query():
    """Verify POST /api/analytics/query handles natural language questions."""
    # 1. Laptop recommendation comparison query
    res1 = client.post(
        "/api/analytics/query",
        json={"query": "Compare laptop recommendations and scores"},
        headers={"Authorization": "Bearer demo-token"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["intent"] == "product_comparison"
    assert data1["suggested_widget"] == "scorecard"
    assert len(data1["insights"]) > 0

    # 2. Payment health query
    res2 = client.post(
        "/api/analytics/query",
        json={"query": "Show failed or pending payments health"},
        headers={"Authorization": "Bearer demo-token"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "payment_health"
    assert data2["suggested_widget"] == "health"

    # 3. Category spending query
    res3 = client.post(
        "/api/analytics/query",
        json={"query": "Group spending by category"},
        headers={"Authorization": "Bearer demo-token"},
    )
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["intent"] == "spending_by_category"
    assert data3["suggested_widget"] == "analyzer"

