"""Tests for Phase 2: Database architecture, persistence, transactions, and models."""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db_context, reset_db
from app.models.order import OrderModel
from app.models.payment import PaymentModel
from app.models.purchase_plan import PurchasePlanModel
from app.models.user import UserModel
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.purchase_plan_repository import PurchasePlanRepository
from app.schemas.order import Order, OrderStatus
from app.schemas.payment import Payment, PaymentProvider, PaymentStatus
from app.schemas.purchase_plan import PurchasePlan, PurchasePlanStatus


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure a clean database state before each test."""
    reset_db()
    yield


def test_user_model_persistence():
    """Test persistent creation and retrieval of UserModel."""
    with get_db_context() as db:
        user = UserModel(
            id="usr_test_01",
            email="developer@paypilot.internal",
            username="Alice Developer",
            created_at=datetime.now(timezone.utc),
        )
        db.merge(user)

    with get_db_context() as db:
        saved = db.query(UserModel).filter(UserModel.id == "usr_test_01").first()
        assert saved is not None
        assert saved.email == "developer@paypilot.internal"
        assert saved.username == "Alice Developer"


def test_purchase_plan_and_payment_persistence():
    """Test PurchasePlan and Payment persistence across session boundaries."""
    plan_repo = PurchasePlanRepository()
    pay_repo = PaymentRepository()

    plan = PurchasePlan(
        id="PP-DB-TEST-001",
        user_id="test_user_db",
        product_id="LAP-001",
        product_name="NovaBook Pro 14",
        brand="Nova",
        seller="Nova Store",
        delivery_days=2,
        quantity=1,
        unit_price=1049.0,
        currency="USD",
        total_amount=1049.0,
        status=PurchasePlanStatus.AWAITING_APPROVAL,
    )
    plan_repo.create(plan)

    # Verify retrieval
    loaded_plan = plan_repo.get_by_id("PP-DB-TEST-001")
    assert loaded_plan is not None
    assert loaded_plan.total_amount == 1049.0
    assert loaded_plan.status == PurchasePlanStatus.AWAITING_APPROVAL

    # Create associated payment
    payment = Payment(
        id="PAY-DB-TEST-001",
        user_id="test_user_db",
        purchase_plan_id="PP-DB-TEST-001",
        provider=PaymentProvider.PAYPAL,
        provider_order_id="PP-ORD-PROVIDER-99",
        amount=1049.0,
        currency="USD",
        status=PaymentStatus.CREATED,
    )
    pay_repo.create(payment)

    loaded_payment = pay_repo.get_by_provider_order_id("PP-ORD-PROVIDER-99")
    assert loaded_payment is not None
    assert loaded_payment.id == "PAY-DB-TEST-001"
    assert loaded_payment.purchase_plan_id == "PP-DB-TEST-001"


def test_order_purchase_plan_uniqueness_constraint():
    """Test that two orders cannot share the same purchase_plan_id (database uniqueness)."""
    with get_db_context() as db:
        order1 = OrderModel(
            id="ORD-U1",
            user_id="user_1",
            purchase_plan_id="PP-UNIQUE-01",
            product_id="LAP-001",
            product_name="Laptop 1",
            brand="Nova",
            quantity=1,
            amount=999.0,
            currency="USD",
            status="PROCESSING",
        )
        db.add(order1)

    # Attempting to insert second order with same purchase_plan_id must fail IntegrityError
    with pytest.raises(IntegrityError):
        with get_db_context() as db:
            order2 = OrderModel(
                id="ORD-U2",
                user_id="user_1",
                purchase_plan_id="PP-UNIQUE-01",  # Duplicate unique purchase_plan_id
                product_id="LAP-002",
                product_name="Laptop 2",
                brand="Aero",
                quantity=1,
                amount=1199.0,
                currency="USD",
                status="PROCESSING",
            )
            db.add(order2)


def test_transaction_rollback_on_failure():
    """Test that database rollbacks leave no orphaned state on failure."""
    with pytest.raises(RuntimeError):
        with get_db_context() as db:
            user = UserModel(
                id="usr_rollback_test",
                email="fail@test.com",
                username="Fail User",
            )
            db.add(user)
            db.flush()
            # Deliberately raise runtime error before commit
            raise RuntimeError("Simulated failure inside transaction")

    with get_db_context() as db:
        record = db.query(UserModel).filter(UserModel.id == "usr_rollback_test").first()
        assert record is None, "Failed transaction was not rolled back!"


def test_data_persistence_across_repository_reinstantiation():
    """Simulate server restart by re-instantiating repositories."""
    order_repo1 = OrderRepository(populate_defaults=False)
    order = Order(
        id="ORD-RESTART-01",
        user_id="user_restart",
        purchase_plan_id="PP-RESTART-01",
        product_id="LAP-001",
        product_name="NovaBook",
        brand="Nova",
        quantity=1,
        amount=1049.0,
        currency="USD",
        status=OrderStatus.PROCESSING,
    )
    order_repo1.create(order)

    # Simulate fresh process restart
    order_repo2 = OrderRepository(populate_defaults=False)
    loaded = order_repo2.get_by_id("ORD-RESTART-01")
    assert loaded is not None
    assert loaded.product_name == "NovaBook"
    assert loaded.user_id == "user_restart"
