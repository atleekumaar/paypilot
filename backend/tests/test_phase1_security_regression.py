"""Comprehensive regression test suite for Phase 1 Payment Security and Checkout Reliability."""

import concurrent.futures
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.repositories.payment_repository import get_payment_repository
from app.repositories.product_repository import get_product_repository
from app.repositories.purchase_plan_repository import get_purchase_plan_repository
from app.schemas.payment import PaymentStatus
from app.schemas.purchase_plan import PurchasePlanStatus
from app.services.notification_service import get_notification_service
from app.services.paypal.config import PayPalConfig, get_paypal_config
from app.services.paypal.orders import PayPalOrderService

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_repositories():
    """Reset repository state and mock orders before each test."""
    get_purchase_plan_repository().clear()
    get_payment_repository().clear()
    get_notification_service().reset_defaults()
    PayPalOrderService.clear_mock_orders()

    # Reset any modified catalog price for LAP-001
    prod = get_product_repository().get_by_id("LAP-001")
    if prod:
        prod.price = 1049.0
        prod.stock = True


# =============================================================================
# 1. UNAPPROVED CHECKOUT TESTS
# =============================================================================

def test_unapproved_plan_cannot_create_paypal_order():
    """Create PayPal order must fail if plan is in AWAITING_APPROVAL status."""
    res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = res.json()["id"]

    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 400
    assert "must be explicitly approved" in order_res.json()["detail"].lower()


def test_unapproved_provider_order_cannot_be_captured():
    """If provider PayPal order is still CREATED (buyer has not approved), capture must fail."""
    # 1. Create and approve plan
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    # 2. Create PayPal order
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    order_id = order_res.json()["paypal_order_id"]

    # 3. Simulate buyer NOT yet approving the order in PayPal Sandbox (status remains CREATED)
    PayPalOrderService.register_mock_order(
        order_id,
        {
            "id": order_id,
            "status": "CREATED",
            "purchase_units": [
                {
                    "reference_id": plan_id,
                    "amount": {"currency_code": "USD", "value": "1049.00"},
                }
            ],
        },
    )

    # 4. Attempt capture before buyer approval
    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert capture_res.status_code == 400
    assert "not approved for capture" in capture_res.json()["detail"].lower()
    assert "buyer approval required" in capture_res.json()["detail"].lower()


def test_cancelled_or_failed_plan_cannot_initiate_checkout():
    """A cancelled plan cannot create a PayPal order."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]

    plan = get_purchase_plan_repository().get_by_id(plan_id)
    plan.status = PurchasePlanStatus.CANCELLED
    get_purchase_plan_repository().update(plan)

    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 400


# =============================================================================
# 2. INVALID ORDER IDS TESTS
# =============================================================================

def test_capture_with_mismatched_order_id():
    """Capture request with an order ID differing from plan association must return 400."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})

    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": "WRONG-ORDER-ID-999"},
    )
    assert capture_res.status_code == 400
    assert "does not match" in capture_res.json()["detail"].lower()


def test_capture_with_unknown_provider_order():
    """Capture request with order ID not found at provider must return 400."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    # Manually associate plan with a phantom non-existent order ID
    plan = get_purchase_plan_repository().get_by_id(plan_id)
    plan.paypal_order_id = "NON_EXISTENT_ORDER_XYZ"
    plan.status = PurchasePlanStatus.PAYPAL_APPROVAL_PENDING
    get_purchase_plan_repository().update(plan)

    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": "NON_EXISTENT_ORDER_XYZ"},
    )
    assert capture_res.status_code == 400
    assert "invalid paypal order id" in capture_res.json()["detail"].lower() or "not found" in capture_res.json()["detail"].lower()


# =============================================================================
# 3. AMOUNT AND CURRENCY MISMATCH TESTS
# =============================================================================

def test_capture_amount_mismatch_rejected():
    """If provider order amount does not match purchase plan amount, capture is strictly rejected."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    # Tamper order details at provider (e.g. provider order is for $50.00 instead of $1049.00)
    PayPalOrderService.register_mock_order(
        order_id,
        {
            "id": order_id,
            "status": "APPROVED",
            "purchase_units": [
                {
                    "reference_id": plan_id,
                    "amount": {"currency_code": "USD", "value": "50.00"},
                }
            ],
        },
    )

    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert capture_res.status_code == 400
    assert "amount mismatch" in capture_res.json()["detail"].lower()


def test_capture_currency_mismatch_rejected():
    """If provider currency differs from plan currency, capture is rejected."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    # Tamper currency to EUR
    PayPalOrderService.register_mock_order(
        order_id,
        {
            "id": order_id,
            "status": "APPROVED",
            "purchase_units": [
                {
                    "reference_id": plan_id,
                    "amount": {"currency_code": "EUR", "value": "1049.00"},
                }
            ],
        },
    )

    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert capture_res.status_code == 400
    assert "currency mismatch" in capture_res.json()["detail"].lower()


def test_capture_reference_id_mismatch_rejected():
    """If provider reference_id points to a different plan, capture is rejected."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    PayPalOrderService.register_mock_order(
        order_id,
        {
            "id": order_id,
            "status": "APPROVED",
            "purchase_units": [
                {
                    "reference_id": "PP-OTHER-PLAN-999",
                    "amount": {"currency_code": "USD", "value": "1049.00"},
                }
            ],
        },
    )

    capture_res = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert capture_res.status_code == 400
    assert "reference_id" in capture_res.json()["detail"].lower()


# =============================================================================
# 4. CROSS-USER ACCESS & AUTHENTICATION ENFORCEMENT TESTS
# =============================================================================

def test_client_cannot_spoof_user_id_in_query():
    """Client providing ?user_id=target_user without matching credentials must be rejected with 403."""
    # Authenticated as guest_user (default), but attempting to query user_alice's data
    res = client.get("/api/orders?user_id=user_alice")
    assert res.status_code == 403
    assert "does not match" in res.json()["detail"].lower()


def test_client_cannot_spoof_user_id_in_body():
    """Client providing user_id in payload differing from authenticated identity must get 403."""
    res = client.post(
        "/api/purchase-plans",
        json={"product_id": "LAP-001", "quantity": 1, "user_id": "user_victim"},
    )
    assert res.status_code == 403
    assert "does not match" in res.json()["detail"].lower()


def test_cross_user_order_access_forbidden():
    """User B cannot view User A's order."""
    headers_user_b = {"Authorization": "Bearer user_b"}
    # ORD-001 is owned by guest_user
    res = client.get("/api/orders/ORD-001", headers=headers_user_b)
    assert res.status_code == 403
    assert "access denied" in res.json()["detail"].lower()


def test_cross_user_purchase_plan_access_forbidden():
    """User B cannot view, approve, checkout, or capture User A's plan."""
    headers_user_a = {"Authorization": "Bearer user_a"}
    headers_user_b = {"Authorization": "Bearer user_b"}

    # 1. User A creates plan
    plan_res = client.post(
        "/api/purchase-plans",
        headers=headers_user_a,
        json={"product_id": "LAP-001", "quantity": 1},
    )
    assert plan_res.status_code == 201
    plan_id = plan_res.json()["id"]

    # 2. User B tries to view User A's plan -> 403
    get_res = client.get(f"/api/purchase-plans/{plan_id}", headers=headers_user_b)
    assert get_res.status_code == 403

    # 3. User B tries to approve User A's plan -> 403
    approve_res = client.post(f"/api/purchase-plans/{plan_id}/approve", headers=headers_user_b)
    assert approve_res.status_code == 403

    # User A approves their plan
    client.post(f"/api/purchase-plans/{plan_id}/approve", headers=headers_user_a)

    # 4. User B tries to initiate checkout -> 403
    checkout_res = client.post(
        "/api/payments/paypal/create-order",
        headers=headers_user_b,
        json={"purchase_plan_id": plan_id},
    )
    assert checkout_res.status_code == 403

    # User A initiates checkout
    order_res = client.post(
        "/api/payments/paypal/create-order",
        headers=headers_user_a,
        json={"purchase_plan_id": plan_id},
    )
    order_id = order_res.json()["paypal_order_id"]

    # 5. User B tries to capture User A's payment -> 403
    capture_res = client.post(
        "/api/payments/paypal/capture",
        headers=headers_user_b,
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert capture_res.status_code == 403


def test_cross_user_notification_access_forbidden():
    """User B cannot mark User A's notification as read or view User A's notifications."""
    headers_user_b = {"Authorization": "Bearer user_b"}

    # NOTIF-001 belongs to guest_user
    read_res = client.post("/api/notifications/NOTIF-001/read", headers=headers_user_b)
    assert read_res.status_code == 403

    list_res = client.get("/api/notifications", headers=headers_user_b)
    assert list_res.status_code == 200
    notif_ids = [n["id"] for n in list_res.json()]
    assert "NOTIF-001" not in notif_ids


def test_cross_user_agent_session_access_forbidden():
    """User B cannot access or approve User A's agent session."""
    headers_user_a = {"Authorization": "Bearer user_a"}
    headers_user_b = {"Authorization": "Bearer user_b"}
    session_id = "sess-isolated-user-a"

    # User A chats in their session
    chat_res = client.post(
        "/api/agent/chat",
        headers=headers_user_a,
        json={"message": "Find me a laptop under 1200", "session_id": session_id},
    )
    assert chat_res.status_code == 200

    # User B tries to access state -> 403
    state_res = client.get(f"/api/agent/{session_id}/state", headers=headers_user_b)
    assert state_res.status_code == 403

    # User B tries to approve -> 403
    approve_res = client.post(f"/api/agent/{session_id}/approve", headers=headers_user_b)
    assert approve_res.status_code == 403


# =============================================================================
# 5. PRICE AND INVENTORY REVALIDATION TESTS
# =============================================================================

def test_price_change_before_approval_requires_reapproval():
    """If catalog price changes before user approval, approval fails and plan updates to new price."""
    # 1. Create plan when price is $1049.00
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]

    # 2. Price changes in catalog
    prod = get_product_repository().get_by_id("LAP-001")
    prod.price = 1199.0

    # 3. User attempts to approve the stale $1049.00 plan
    approve_res = client.post(f"/api/purchase-plans/{plan_id}/approve")
    assert approve_res.status_code == 400
    assert "price has changed" in approve_res.json()["detail"].lower()
    assert "renewed approval is required" in approve_res.json()["detail"].lower()

    # Plan should now reflect the updated price
    updated_plan = client.get(f"/api/purchase-plans/{plan_id}").json()
    assert updated_plan["unit_price"] == 1199.0
    assert updated_plan["total_amount"] == 1199.0
    assert updated_plan["status"] == PurchasePlanStatus.AWAITING_APPROVAL.value


def test_price_change_after_approval_reverts_to_awaiting_approval():
    """If catalog price changes after approval but before PayPal checkout, order creation fails and plan reverts."""
    # 1. Create and approve plan at $1049.00
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    # 2. Price changes in catalog before checkout
    prod = get_product_repository().get_by_id("LAP-001")
    prod.price = 1250.0

    # 3. User initiates PayPal checkout
    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 400
    assert "price has changed" in order_res.json()["detail"].lower()

    # Verify plan reverted to AWAITING_APPROVAL with new price
    reverted_plan = client.get(f"/api/purchase-plans/{plan_id}").json()
    assert reverted_plan["status"] == PurchasePlanStatus.AWAITING_APPROVAL.value
    assert reverted_plan["unit_price"] == 1250.0
    assert reverted_plan["total_amount"] == 1250.0


def test_out_of_stock_before_checkout_rejected():
    """If product goes out of stock after approval, checkout is rejected."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    # Product stock becomes depleted
    prod = get_product_repository().get_by_id("LAP-001")
    prod.stock = False

    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 400
    assert "no longer available" in order_res.json()["detail"].lower()


# =============================================================================
# 6. DUPLICATE CAPTURE & SAFE RETRIES TESTS
# =============================================================================

def test_duplicate_capture_returns_existing_payment_safely():
    """Repeated calls to capture on completed order return existing verified payment safely."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    # First capture
    res1 = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert res1.status_code == 200
    payment1 = res1.json()

    # Second capture call
    res2 = client.post(
        "/api/payments/paypal/capture",
        json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
    )
    assert res2.status_code == 200
    payment2 = res2.json()

    assert payment1["id"] == payment2["id"]
    assert payment1["capture_id"] == payment2["capture_id"]
    assert payment2["status"] == PaymentStatus.COMPLETED.value


def test_concurrent_capture_thread_safety():
    """Multiple concurrent capture requests execute safely without double captures."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    def do_capture():
        return client.post(
            "/api/payments/paypal/capture",
            json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(do_capture) for _ in range(4)]
        responses = [f.result() for f in futures]

    for r in responses:
        assert r.status_code == 200
        assert r.json()["status"] == PaymentStatus.COMPLETED.value

    # All must share the same capture_id
    capture_ids = {r.json()["capture_id"] for r in responses}
    assert len(capture_ids) == 1


def test_create_order_idempotent_retry():
    """Repeated calls to create-order on pending plan return existing order ID and approval URL."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    res1 = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1["approval_url"] is not None

    # Retry create-order
    res2 = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    assert res2.status_code == 201
    data2 = res2.json()

    assert data1["paypal_order_id"] == data2["paypal_order_id"]
    assert data1["approval_url"] == data2["approval_url"]


# =============================================================================
# 7. PROVIDER ERRORS & AMBIGUOUS TIMEOUTS TESTS
# =============================================================================

def test_provider_error_on_capture_handled():
    """When provider returns an error, payment is not marked as completed."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    with patch.object(PayPalOrderService, "capture_order", side_effect=RuntimeError("PayPal 500 Internal Error")):
        capture_res = client.post(
            "/api/payments/paypal/capture",
            json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
        )
        assert capture_res.status_code == 502
        assert "provider error" in capture_res.json()["detail"].lower()

    # Payment must NOT be marked COMPLETED
    pmt = get_payment_repository().get_by_provider_order_id(order_id)
    assert pmt.status != PaymentStatus.COMPLETED


def test_provider_timeout_handled_without_marking_completed():
    """When capture times out and recovery shows order not completed, returns 504 without marking COMPLETED."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    with patch.object(PayPalOrderService, "capture_order", side_effect=TimeoutError("Connection timed out")):
        # Mock get_order_details during recovery to show still APPROVED (not completed)
        with patch.object(
            PayPalOrderService,
            "get_order_details",
            return_value={
                "id": order_id,
                "status": "APPROVED",
                "purchase_units": [
                    {
                        "reference_id": plan_id,
                        "amount": {"currency_code": "USD", "value": "1049.00"},
                    }
                ],
            },
        ):
            capture_res = client.post(
                "/api/payments/paypal/capture",
                json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
            )
            assert capture_res.status_code == 504
            assert "timeout" in capture_res.json()["detail"].lower()

    # Must NOT be marked COMPLETED
    pmt = get_payment_repository().get_by_provider_order_id(order_id)
    assert pmt.status != PaymentStatus.COMPLETED


def test_provider_timeout_recovery_when_order_actually_completed():
    """When capture times out, but recovery check reveals PayPal DID complete the order, succeed safely."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")
    order_res = client.post("/api/payments/paypal/create-order", json={"purchase_plan_id": plan_id})
    order_id = order_res.json()["paypal_order_id"]

    # First get_order_details succeeds for initial verification (status APPROVED)
    # capture_order raises TimeoutError
    # Second get_order_details (recovery) returns COMPLETED with capture details
    orig_get_details = PayPalOrderService.get_order_details
    calls = []

    def mocked_get_details(self, oid):
        calls.append(oid)
        if len(calls) == 1:
            return {
                "id": oid,
                "status": "APPROVED",
                "purchase_units": [
                    {
                        "reference_id": plan_id,
                        "amount": {"currency_code": "USD", "value": "1049.00"},
                    }
                ],
            }
        else:
            return {
                "id": oid,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "reference_id": plan_id,
                        "payments": {
                            "captures": [{"id": "CAP-RECOVERED-001", "status": "COMPLETED"}]
                        },
                    }
                ],
            }

    with patch.object(PayPalOrderService, "get_order_details", mocked_get_details):
        with patch.object(PayPalOrderService, "capture_order", side_effect=TimeoutError("Ambiguous timeout")):
            capture_res = client.post(
                "/api/payments/paypal/capture",
                json={"purchase_plan_id": plan_id, "paypal_order_id": order_id},
            )
            assert capture_res.status_code == 200
            payment = capture_res.json()
            assert payment["status"] == PaymentStatus.COMPLETED.value
            assert payment["capture_id"] == "CAP-RECOVERED-001"


# =============================================================================
# 8. REAL SANDBOX BUYER-APPROVAL URL & MOCK ISOLATION TESTS
# =============================================================================

def test_buyer_approval_url_returned_on_create_order():
    """Create order must return a valid buyer-approval URL for PayPal Sandbox redirect."""
    plan_res = client.post("/api/purchase-plans", json={"product_id": "LAP-001", "quantity": 1})
    plan_id = plan_res.json()["id"]
    client.post(f"/api/purchase-plans/{plan_id}/approve")

    order_res = client.post(
        "/api/payments/paypal/create-order",
        json={"purchase_plan_id": plan_id},
    )
    assert order_res.status_code == 201
    data = order_res.json()
    assert "approval_url" in data
    assert "sandbox.paypal.com" in data["approval_url"]
    assert data["paypal_order_id"] in data["approval_url"]


def test_mock_disabled_when_live_or_explicitly_forbidden():
    """In live environment or when mock is disabled, mock transactions are strictly rejected."""
    live_config = PayPalConfig(
        client_id=None,
        client_secret=None,
        environment="live",
        base_url="https://api-m.paypal.com",
    )
    assert live_config.is_mock_allowed is False

    svc = PayPalOrderService(config=live_config)
    plan = get_purchase_plan_repository().create(
        get_purchase_plan_repository()._plans.get("NONEXISTENT", None) or MagicMock(id="PP-1", total_amount=100, currency="USD", product_name="Test")
    )
    with pytest.raises(RuntimeError) as exc_info:
        svc.create_order(plan)
    assert "mock transactions are disabled" in str(exc_info.value).lower()

