"""Integration tests for payment resilience: refunds, webhooks, reconciliation, and outbox."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db, get_db_context
from app.models.outbox import OutboxEventModel
from app.models.webhook_event import WebhookEventModel
from app.repositories.payment_repository import get_payment_repository
from app.schemas.payment import Payment, PaymentProvider, PaymentStatus

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    repo = get_payment_repository()
    repo.clear()
    with get_db_context() as db:
        db.query(OutboxEventModel).delete()
        db.query(WebhookEventModel).delete()
    yield
    repo.clear()


def test_payment_refund_lifecycle():
    repo = get_payment_repository()
    # Create completed payment
    payment = Payment(
        id="PAY-REFTEST-1",
        user_id="user_test_1",
        purchase_plan_id="PP-TEST-1",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="ORD-PP-1234",
        amount=150.00,
        currency="USD",
        status=PaymentStatus.COMPLETED,
    )
    repo.create(payment)

    # Partial refund
    res = client.post(
        "/api/payments/PAY-REFTEST-1/refund",
        json={"amount": 50.00},
        headers={"X-User-Id": "user_test_1"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PARTIALLY_REFUNDED"
    assert data["refund_amount"] == 50.00
    assert data["refund_id"] is not None

    # Check outbox event was logged
    with get_db_context() as db:
        evt = db.query(OutboxEventModel).filter(OutboxEventModel.aggregate_id == "PAY-REFTEST-1").first()
        assert evt is not None
        assert evt.event_type == "payment.refunded"


def test_payment_refund_unauthorized_rejected():
    repo = get_payment_repository()
    payment = Payment(
        id="PAY-REFTEST-2",
        user_id="user_owner",
        purchase_plan_id="PP-TEST-2",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="ORD-PP-5678",
        amount=100.00,
        currency="USD",
        status=PaymentStatus.COMPLETED,
    )
    repo.create(payment)

    res = client.post(
        "/api/payments/PAY-REFTEST-2/refund",
        json={"amount": 100.00},
        headers={"X-User-Id": "user_attacker"},
    )
    assert res.status_code == 403


def test_paypal_webhook_idempotency_and_replay_prevention():
    webhook_payload = {
        "id": "WH-TEST-EVENT-001",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "resource": {"id": "CAP-12345"},
    }

    # First event delivery
    res1 = client.post("/api/payments/paypal/webhook", json=webhook_payload)
    assert res1.status_code == 200
    assert res1.json()["status"] == "processed"

    # Duplicate replay attempt
    res2 = client.post("/api/payments/paypal/webhook", json=webhook_payload)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"


def test_payment_reconciliation_endpoint():
    repo = get_payment_repository()
    # Create stuck payment in RECONCILIATION_REQUIRED
    payment = Payment(
        id="PAY-STUCK-1",
        user_id="user_test",
        purchase_plan_id="PP-TEST-3",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="MOCK-STUCK-ORDER",
        amount=200.00,
        currency="USD",
        status=PaymentStatus.RECONCILIATION_REQUIRED,
    )
    repo.create(payment)

    res = client.get("/api/payments/reconciliation/report", headers={"X-User-Id": "user_test"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

