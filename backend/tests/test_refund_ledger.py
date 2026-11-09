"""Comprehensive tests for the Refund Ledger, Webhook Lifecycle, and Outbox Worker."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import init_db, get_db_context
from app.models.outbox import OutboxEventModel
from app.models.webhook_event import WebhookEventModel
from app.models.refund_attempt import RefundAttemptModel
from app.models.payment import PaymentModel
from app.models.agent_session import AgentSessionModel
from app.agents.state import AgentAction, AgentState, ConversationMessage, get_session_store
from app.repositories.payment_repository import get_payment_repository
from app.schemas.payment import Payment, PaymentProvider, PaymentStatus
from app.services.checkout_service import CheckoutService
from app.workers.outbox_worker import OutboxWorkerRunner
from app.services.outbox_consumer import OutboxConsumer
from app.services.paypal.config import PayPalConfig
from app.services.paypal.orders import PayPalOrderService

client = TestClient(app)

MOCK_HEADERS = {
    "PAYPAL-AUTH-ALGO": "SHA256withRSA",
    "PAYPAL-CERT-URL": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-12345",
    "PAYPAL-TRANSMISSION-ID": "trans-mock-ledger-123",
    "PAYPAL-TRANSMISSION-SIG": "MOCK_VALID_SIGNATURE",
    "PAYPAL-TRANSMISSION-TIME": "2026-11-01T00:00:00Z",
}


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    repo = get_payment_repository()
    repo.clear()
    store = get_session_store()
    store.clear()
    with get_db_context() as db:
        db.query(RefundAttemptModel).delete()
        db.query(OutboxEventModel).delete()
        db.query(WebhookEventModel).delete()
        db.query(AgentSessionModel).delete()
    yield
    repo.clear()
    store.clear()


def test_refund_ledger_cumulative_balance_and_idempotency(monkeypatch):
    """Verify refund ledger records attempts with Decimal precision and strictly blocks over-refunding."""
    repo = get_payment_repository()
    payment = Payment(
        id="PAY-LEDGER-001",
        user_id="user_test_ledger",
        purchase_plan_id="PP-LEDGER-001",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="ORD-LEDGER-001",
        amount=100.0,
        currency="USD",
        status=PaymentStatus.COMPLETED,
        capture_id="CAP-LEDGER-001",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    repo.create(payment)

    mock_paypal = MagicMock()
    mock_paypal.refund_capture.side_effect = lambda capture_id, amount, currency, idempotency_key: {
        "status": "COMPLETED",
        "id": f"REF-MOCK-{amount}",
    }
    svc = CheckoutService(paypal_order_service=mock_paypal)

    # Step 1: Partial refund $40.00
    res1 = svc.refund_payment("PAY-LEDGER-001", amount=40.0, user_id="user_test_ledger")
    assert res1.status == PaymentStatus.PARTIALLY_REFUNDED
    assert res1.total_refunded == 40.0

    # Verify attempt in DB ledger
    with get_db_context() as db:
        attempts = db.query(RefundAttemptModel).filter(RefundAttemptModel.payment_id == "PAY-LEDGER-001").all()
        assert len(attempts) == 1
        assert attempts[0].status == "COMPLETED"
        assert Decimal(str(attempts[0].requested_amount)) == Decimal("40.00")
        assert attempts[0].idempotency_key.startswith("ref-idem-PAY-LEDGER-001")

    # Step 2: Partial refund $50.00
    res2 = svc.refund_payment("PAY-LEDGER-001", amount=50.0, user_id="user_test_ledger")
    assert res2.status == PaymentStatus.PARTIALLY_REFUNDED
    assert res2.total_refunded == 90.0

    with get_db_context() as db:
        attempts = db.query(RefundAttemptModel).filter(RefundAttemptModel.payment_id == "PAY-LEDGER-001").all()
        assert len(attempts) == 2

    # Step 3: Attempt refund $20.00 (only $10.00 left) -> Should be rejected
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        svc.refund_payment("PAY-LEDGER-001", amount=20.0, user_id="user_test_ledger")
    assert exc.value.status_code == 400
    assert "exceeds remaining refundable balance" in exc.value.detail

    # Step 4: Final refund $10.00 -> Should fully refund
    res3 = svc.refund_payment("PAY-LEDGER-001", amount=10.0, user_id="user_test_ledger")
    assert res3.status == PaymentStatus.REFUNDED
    assert res3.total_refunded == 100.0

    with get_db_context() as db:
        attempts = db.query(RefundAttemptModel).filter(RefundAttemptModel.payment_id == "PAY-LEDGER-001").all()
        assert len(attempts) == 3
        completed_sum = sum(Decimal(str(a.requested_amount)) for a in attempts if a.status == "COMPLETED")
        assert completed_sum == Decimal("100.00")


def test_refund_timeout_records_reconciliation_required():
    """Verify provider timeout durably marks both attempt and payment as RECONCILIATION_REQUIRED."""
    repo = get_payment_repository()
    payment = Payment(
        id="PAY-LEDGER-TIMEOUT",
        user_id="user_test_timeout",
        purchase_plan_id="PP-LEDGER-TIMEOUT",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="ORD-LEDGER-TIMEOUT",
        amount=50.0,
        currency="USD",
        status=PaymentStatus.COMPLETED,
        capture_id="CAP-LEDGER-TIMEOUT",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    repo.create(payment)

    mock_paypal = MagicMock()
    mock_paypal.refund_capture.side_effect = TimeoutError("Gateway timeout from PayPal")
    svc = CheckoutService(paypal_order_service=mock_paypal)

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        svc.refund_payment("PAY-LEDGER-TIMEOUT", amount=50.0, user_id="user_test_timeout")
    assert exc.value.status_code == 504

    # Verify attempt and payment status in DB
    with get_db_context() as db:
        attempts = db.query(RefundAttemptModel).filter(RefundAttemptModel.payment_id == "PAY-LEDGER-TIMEOUT").all()
        assert len(attempts) == 1
        assert attempts[0].status == "RECONCILIATION_REQUIRED"

    updated_payment = repo.get_by_id("PAY-LEDGER-TIMEOUT")
    assert updated_payment.refund_status == "RECONCILIATION_REQUIRED"


def test_outbox_worker_processes_and_dead_letters():
    """Verify the outbox worker consumes pending events and safely dead-letters events exceeding max retries."""
    with get_db_context() as db:
        # Create an event that will fail
        bad_evt = OutboxEventModel(
            id="evt_bad_test_01",
            event_type="order.create",
            aggregate_type="payment",
            aggregate_id="PAY-BAD",
            payload={"invalid": "no_plan_id"},
            status="PENDING",
            retry_count=4,
            max_retries=5,
        )
        db.add(bad_evt)

    consumer = OutboxConsumer()
    runner = OutboxWorkerRunner(consumer=consumer, poll_interval=0.1, batch_size=5)

    # Process batch
    processed = consumer.process_batch(batch_size=5)
    assert processed == 0

    with get_db_context() as db:
        rec = db.query(OutboxEventModel).filter(OutboxEventModel.id == "evt_bad_test_01").first()
        assert rec is not None
        assert rec.status == "FAILED"
        assert rec.retry_count == 5


def test_webhook_lifecycle_received_to_processed():
    """Verify incoming webhooks track lifecycle from processing to processed."""
    webhook_payload = {
        "id": "WH-LIFECYCLE-001",
        "event_type": "CHECKOUT.ORDER.APPROVED",
        "resource_type": "checkout-order",
        "resource": {"id": "ORD-LIFE-001"},
    }

    with patch.object(PayPalOrderService, "verify_webhook_signature", return_value=True):
        res = client.post("/api/payments/paypal/webhook", json=webhook_payload, headers=MOCK_HEADERS)
        assert res.status_code == 200
        assert res.json()["status"] == "processed"

    with get_db_context() as db:
        rec = db.query(WebhookEventModel).filter(WebhookEventModel.id == "WH-LIFECYCLE-001").first()
        assert rec is not None
        assert rec.status == "PROCESSED"
        assert rec.processed_at is not None
        assert rec.received_at is not None


def test_optimistic_concurrency_intelligent_merge():
    """Verify intelligent merge combines concurrent state changes rather than blindly overwriting."""
    store = get_session_store()
    init_state = AgentState(
        session_id="sess_merge_test",
        user_id="user_alice",
        user_query="buy headphones",
        current_step=1,
    )
    store.save(init_state)

    # Remote worker adds message and action
    remote_state = store.get("sess_merge_test")
    remote_state.messages.append(ConversationMessage(role="assistant", content="Found products"))
    remote_state.actions.append(AgentAction(session_id="sess_merge_test", step=2, tool="search", summary="Searched audio"))
    remote_state.current_step = 2
    store.save(remote_state)

    # Local worker was modifying in-memory state concurrently
    local_state = init_state.model_copy(deep=True)
    local_state.messages.append(ConversationMessage(role="user", content="under $100"))
    local_state.actions.append(AgentAction(session_id="sess_merge_test", step=2, tool="filter", summary="Filtered by price"))

    # Save local with retry, which triggers _merge_states
    saved = store.save_with_retry(local_state)
    assert saved.version == 3
    assert len(saved.messages) == 2  # Both messages preserved
    assert len(saved.actions) == 2   # Both actions preserved
    assert saved.current_step == 2


def test_fail_closed_production_webhook_verification():
    """Verify PayPalOrderService strictly fails closed when mock is disallowed."""
    config = PayPalConfig(
        client_id="dummy_id",
        client_secret="dummy_secret",
        environment="live",
        base_url="https://api.paypal.com",
        mock_enabled=False,
        webhook_id=None,
    )
    service = PayPalOrderService(config=config)

    headers = {
        "paypal-auth-algo": "SHA256withRSA",
        "paypal-cert-url": "https://api.sandbox.paypal.com/cert",
        "paypal-transmission-id": "123",
        "paypal-transmission-sig": "MOCK_VALID_SIGNATURE",
        "paypal-transmission-time": "2026-11-01T00:00:00Z",
    }
    # In live environment, mock signature must immediately return False
    is_valid = service.verify_webhook_signature(headers=headers, body_json={})
    assert is_valid is False

