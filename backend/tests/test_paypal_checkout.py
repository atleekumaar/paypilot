"""Comprehensive test suite for Phase 3 PayPal Checkout & Purchase Flow."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.payment_repository import get_payment_repository
from app.repositories.product_repository import get_product_repository
from app.repositories.purchase_plan_repository import get_purchase_plan_repository
from app.schemas.payment import PaymentStatus
from app.schemas.purchase_plan import PurchasePlanStatus

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_repositories():
    """Reset repository state before each test."""
    plan_repo = get_purchase_plan_repository()
    payment_repo = get_payment_repository()
    plan_repo.clear()
    payment_repo.clear()


# 1. Test Create Purchase Plan
def test_create_purchase_plan():
    response = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("PP-")
    assert data["product_id"] == "LAP-001"
    assert data["product_name"] == "NovaBook Pro 14"
    assert data["unit_price"] == 1049.0
    assert data["total_amount"] == 1049.0
    assert data["status"] == PurchasePlanStatus.AWAITING_APPROVAL.value


# 2. Test Invalid Product ID
def test_invalid_product():
    response = client.post(
        "/api/purchase-plans",
        json={"product_id": "NON_EXISTENT_SKU", "quantity": 1},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# 3. Test Out of Stock Product
def test_out_of_stock_product():
    # LAP-024 is out of stock in demo catalogue
    response = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-024", "quantity": 1},
    )
    assert response.status_code == 400
    assert "out of stock" in response.json()["detail"].lower()


# 4. Critical Security Test 1: Price Manipulation Protection
def test_price_taken_from_backend():
    """Client attempts to submit price = $1.00; backend MUST ignore and use $1049.00."""
    response = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 2, "unit_price": 1.0, "total_amount": 2.0},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["unit_price"] == 1049.0
    assert data["total_amount"] == 2098.0  # 1049 * 2


# 5. Test Purchase Approval
def test_purchase_approval():
    create_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = create_res.json()["id"]

    approve_res = client.post(f"/api/purchase-plans/{plan_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == PurchasePlanStatus.APPROVED.value


# 6. Test Invalid Purchase State (Double Approval)
def test_invalid_purchase_state():
    create_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = create_res.json()["id"]

    # First approval succeeds
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    # Second approval must be rejected
    second_res = client.post(f"/api/purchase-plans/{plan_id}/approve")
    assert second_res.status_code == 400
    assert "cannot be approved" in second_res.json()["detail"].lower()


# 7. Critical Security Test 4: Unapproved Purchase Cannot Create PayPal Order
def test_unapproved_purchase_rejected():
    create_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = create_res.json()["id"]

    # Attempt to create order without approving first
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 400
    assert "must be explicitly approved" in order_res.json()["detail"].lower()


# 8. Test PayPal Order Creation and ID Saved
def test_paypal_order_creation():
    # 1. Create plan
    plan_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = plan_res.json()["id"]

    # 2. Approve plan
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    # 3. Create PayPal Order
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 201
    order_data = order_res.json()
    assert order_data["purchase_plan_id"] == plan_id
    assert order_data["paypal_order_id"] is not None
    assert order_data["status"] == PurchasePlanStatus.PAYPAL_APPROVAL_PENDING.value

    # Verify ID saved on plan
    get_plan_res = client.get(f"/api/purchase-plans/{plan_id}")
    assert get_plan_res.json()["paypal_order_id"] == order_data["paypal_order_id"]


# 9. Test Capture Success & Verification
def test_capture_success():
    # Setup approved plan with PayPal order
    plan_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    order_id = order_res.json()["paypal_order_id"]

    # Capture payment
    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert capture_res.status_code == 200
    payment_data = capture_res.json()
    assert payment_data["status"] == PaymentStatus.COMPLETED.value
    assert payment_data["amount"] == 1049.0
    assert payment_data["provider_order_id"] == order_id
    assert payment_data["capture_id"] is not None

    # Verify plan status updated to COMPLETED
    updated_plan = client.get(f"/api/purchase-plans/{plan_id}").json()
    assert updated_plan["status"] == PurchasePlanStatus.COMPLETED.value


# 10. Critical Security Test 2: Order ID Mismatch Protection
def test_invalid_paypal_order_mismatch():
    """Attempt capture with mismatched PayPal Order ID; MUST return 400."""
    plan_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )

    # Malicious or mismatched order ID
    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": "FRAUDULENT_ORDER_999"},
    )
    assert capture_res.status_code == 400
    assert "does not match" in capture_res.json()["detail"].lower()


# 11. Critical Security Test 3: Idempotency & Duplicate Capture Protection
def test_duplicate_capture():
    """Calling capture twice on the same completed order must NOT double capture."""
    plan_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    order_id = order_res.json()["paypal_order_id"]

    # First capture
    res1 = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert res1.status_code == 200
    payment1 = res1.json()

    # Second duplicate capture
    res2 = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert res2.status_code == 200
    payment2 = res2.json()

    # Must return existing payment record without error or duplicate billing
    assert payment1["id"] == payment2["id"]
    assert payment1["capture_id"] == payment2["capture_id"]
    assert payment2["status"] == PaymentStatus.COMPLETED.value


# 12. Test Payment Retrieval by Plan ID
def test_get_payment_by_plan():
    plan_res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1},
    )
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    order_id = order_res.json()["paypal_order_id"]
    client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )

    get_pmt = client.get(f"/api/payments/by-plan/{plan_id}")
    assert get_pmt.status_code == 200
    assert get_pmt.json()["purchase_plan_id"] == plan_id
    assert get_pmt.json()["status"] == PaymentStatus.COMPLETED.value
