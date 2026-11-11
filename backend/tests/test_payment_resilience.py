"""Integration tests for payment resilience: webhooks, refunds, reconciliation, outbox, and optimistic locking."""

import concurrent.futures
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db, get_db_context
from app.models.outbox import OutboxEventModel
from app.models.webhook_event import WebhookEventModel
from app.models.agent_session import AgentSessionModel
from app.agents.state import AgentState, SessionStore, SessionConcurrencyError, get_session_store
from app.repositories.payment_repository import get_payment_repository
from app.schemas.payment import Payment, PaymentProvider, PaymentStatus
from app.services.outbox_consumer import OutboxConsumer

client = TestClient(app)

MOCK_HEADERS = {
    "PAYPAL-AUTH-ALGO": "SHA256withRSA",
    "PAYPAL-CERT-URL": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-12345",
    "PAYPAL-TRANSMISSION-ID": "trans-mock-123",
    "PAYPAL-TRANSMISSION-SIG": "MOCK_VALID_SIGNATURE",
    "PAYPAL-TRANSMISSION-TIME": "2026-10-31T20:00:00Z",
}


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    repo = get_payment_repository()
    repo.clear()
    store = get_session_store()
    store.clear()
    with get_db_context() as db:
        db.query(OutboxEventModel).delete()
        db.query(WebhookEventModel).delete()
        db.query(AgentSessionModel).delete()
    yield
    repo.clear()
    store.clear()


# ---------------------------------------------------------------------------
# 1. PayPal Webhook Security & Signatures
# ---------------------------------------------------------------------------

def test_paypal_webhook_forged_signature_rejected():
    webhook_payload = {
        "id": "WH-FORGED-001",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "resource": {"id": "CAP-FORGED-1"},
    }
    forged_headers = {
        **MOCK_HEADERS,
        "PAYPAL-TRANSMISSION-SIG": "INVALID_FORGED_SIGNATURE",
    }
    res = client.post("/api/payments/paypal/webhook", json=webhook_payload, headers=forged_headers)
    assert res.status_code == 400
    assert "Invalid or forged PayPal webhook signature" in res.json()["detail"]


def test_paypal_webhook_valid_signature_and_idempotency():
    webhook_payload = {
        "id": "WH-VALID-001",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "resource": {"id": "CAP-VALID-1"},
    }

    # Initial delivery
    res1 = client.post("/api/payments/paypal/webhook", json=webhook_payload, headers=MOCK_HEADERS)
    assert res1.status_code == 200
    assert res1.json()["status"] == "processed"

    # Replay delivery (duplicate)
    res2 = client.post("/api/payments/paypal/webhook", json=webhook_payload, headers=MOCK_HEADERS)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"


def test_paypal_webhook_concurrent_delivery():
    webhook_payload = {
        "id": "WH-CONCURRENT-001",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "resource": {"id": "CAP-CONCURRENT-1"},
    }

    def send_webhook():
        return client.post("/api/payments/paypal/webhook", json=webhook_payload, headers=MOCK_HEADERS)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(send_webhook) for _ in range(4)]
        responses = [f.result() for f in futures]

    statuses = [r.status_code for r in responses]
    assert all(s == 200 for s in statuses)

    results = [r.json()["status"] for r in responses]
    assert results.count("processed") == 1
    assert results.count("duplicate") == 3


# ---------------------------------------------------------------------------
# 2. Refund Verification & Cumulative Balance
# ---------------------------------------------------------------------------

def test_refund_lifecycle_and_cumulative_balance():
    repo = get_payment_repository()
    payment = Payment(
        id="PAY-REF-CUMULATIVE-1",
        user_id="guest_user",
        purchase_plan_id="PP-CUMULATIVE-1",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="ORD-PP-CUM-1",
        capture_id="MOCK-CAP-1234",
        amount=100.00,
        currency="USD",
        status=PaymentStatus.COMPLETED,
    )
    repo.create(payment)

    # 1. Partial refund #1: $40.00
    res1 = client.post(
        "/api/payments/PAY-REF-CUMULATIVE-1/refund",
        json={"amount": 40.00},
        headers={"X-User-Id": "user_buyer_1"},
    )
    assert res1.status_code == 200
    p1 = res1.json()
    assert p1["status"] == "PARTIALLY_REFUNDED"
    assert p1["refund_amount"] == 40.00
    assert p1["total_refunded"] == 40.00

    # 2. Partial refund #2: $70.00 (exceeds remaining balance $60.00) -> MUST FAIL
    res2 = client.post(
        "/api/payments/PAY-REF-CUMULATIVE-1/refund",
        json={"amount": 70.00},
        headers={"X-User-Id": "user_buyer_1"},
    )
    assert res2.status_code == 400
    assert "exceeds remaining refundable balance" in res2.json()["detail"]

    # 3. Partial refund #3: $60.00 (exactly exhausts remaining balance) -> Marks REFUNDED
    res3 = client.post(
        "/api/payments/PAY-REF-CUMULATIVE-1/refund",
        json={"amount": 60.00},
        headers={"X-User-Id": "user_buyer_1"},
    )
    assert res3.status_code == 200
    p3 = res3.json()
    assert p3["status"] == "REFUNDED"
    assert p3["total_refunded"] == 100.00


def test_refund_forged_unauthorized_access():
    repo = get_payment_repository()
    payment = Payment(
        id="PAY-REF-AUTH-1",
        user_id="user_legit_owner",
        purchase_plan_id="PP-AUTH-1",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="ORD-PP-AUTH-1",
        capture_id="MOCK-CAP-AUTH",
        amount=50.00,
        currency="USD",
        status=PaymentStatus.COMPLETED,
    )
    repo.create(payment)

    # Impersonator attempting refund
    res = client.post(
        "/api/payments/PAY-REF-AUTH-1/refund",
        json={"amount": 50.00},
        headers={"X-User-Id": "user_hacker"},
    )
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# 3. Role-Based Reconciliation Access
# ---------------------------------------------------------------------------

def test_reconciliation_role_authorization():
    # Regular/demo user attempting admin endpoint
    res_user = client.get("/api/payments/reconciliation/report")
    assert res_user.status_code == 403

    # Client attempting privilege escalation via X-User-Role header MUST FAIL (Priority 1 fix)
    res_spoof = client.get(
        "/api/payments/reconciliation/report",
        headers={"X-User-Id": "admin_user", "X-User-Role": "admin"},
    )
    assert res_spoof.status_code == 403

    # Legitimate admin access succeeds (via dependency override or verified token)
    from app.main import app
    from app.core.auth import get_current_user, AuthenticatedUser
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id="admin_user", role="admin", is_authenticated=True
    )
    try:
        res_admin = client.get("/api/payments/reconciliation/report")
        assert res_admin.status_code == 200
        assert isinstance(res_admin.json(), list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# 4. True Optimistic Session Concurrency Locking
# ---------------------------------------------------------------------------

def test_true_optimistic_locking_concurrency():
    store = get_session_store()
    state = store.get_or_create("sess-optimistic-test", user_id="user_optimistic")
    assert state.version == 1

    # Simulate worker 1 and worker 2 holding version 1
    state_worker1 = store.get("sess-optimistic-test", user_id="user_optimistic")
    state_worker2 = store.get("sess-optimistic-test", user_id="user_optimistic")

    # Worker 1 succeeds in updating: version goes 1 -> 2
    state_worker1.user_query = "Query from Worker 1"
    store.save(state_worker1)
    assert state_worker1.version == 2

    # Worker 2 attempts to save with stale version 1 -> Concurrency conflict
    state_worker2.user_query = "Query from Worker 2"
    with pytest.raises(SessionConcurrencyError):
        store.save(state_worker2)

    # Worker 2 uses save_with_retry: successfully reloads version 2 and persists as version 3
    saved = store.save_with_retry(state_worker2, max_retries=3)
    assert saved.version == 3


def test_session_immutable_ownership():
    store = get_session_store()
    state = store.get_or_create("sess-immutable-test", user_id="original_owner")
    state.user_query = "Original query"
    store.save(state)

    # Attacker attempting to claim session
    attacker_state = AgentState(
        session_id="sess-immutable-test",
        user_id="attacker_user",
        version=state.version,
    )
    with pytest.raises(PermissionError):
        store.save(attacker_state)


# ---------------------------------------------------------------------------
# 5. Transactional Outbox Worker & Recovery
# ---------------------------------------------------------------------------

def test_outbox_consumer_lease_and_worker_recovery():
    with get_db_context() as db:
        evt = OutboxEventModel(
            id="evt_test_outbox_1",
            event_type="order.create",
            aggregate_type="payment",
            aggregate_id="PAY-TEST-OUTBOX",
            payload={
                "purchase_plan_id": "PP-OUTBOX-1",
                "user_id": "user_outbox_test",
                "product_id": "prod-1",
                "product_name": "NovaBook Pro 14",
                "brand": "NovaTech",
                "quantity": 1,
                "amount": 999.00,
                "currency": "USD",
                "paypal_order_id": "ORD-OUTBOX-1",
                "payment_id": "PAY-TEST-OUTBOX",
                "delivery_days": 2,
            },
            status="PENDING",
            retry_count=0,
            max_retries=3,
        )
        db.add(evt)

    consumer = OutboxConsumer()

    # Step 1: Claim and process event
    claimed = consumer.claim_events(batch_size=5, lease_seconds=10)
    assert "evt_test_outbox_1" in claimed

    with get_db_context() as db:
        e = db.query(OutboxEventModel).filter(OutboxEventModel.id == "evt_test_outbox_1").first()
        assert e.status == "PROCESSING"
        assert e.leased_until is not None

    # Step 2: Process event to completion
    success = consumer.process_event("evt_test_outbox_1")
    assert success is True

    with get_db_context() as db:
        e = db.query(OutboxEventModel).filter(OutboxEventModel.id == "evt_test_outbox_1").first()
        assert e.status == "PROCESSED"
        assert e.processed_at is not None

    # Step 3: Simulate worker crash on a second event with expired lease
    with get_db_context() as db:
        expired_evt = OutboxEventModel(
            id="evt_crashed_worker",
            event_type="payment.refunded",
            aggregate_type="payment",
            aggregate_id="PAY-CRASHED",
            payload={"user_id": "user_outbox_test", "refund_amount": 25.00, "payment_id": "PAY-CRASHED"},
            status="PROCESSING",
            leased_until=datetime.now(timezone.utc) - timedelta(minutes=5),  # Expired lease
            retry_count=1,
            max_retries=3,
        )
        db.add(expired_evt)

    # Re-claim should recover the crashed event
    reclaimed = consumer.claim_events(batch_size=5, lease_seconds=15)
    assert "evt_crashed_worker" in reclaimed

    recovered_success = consumer.process_event("evt_crashed_worker")
    assert recovered_success is True
