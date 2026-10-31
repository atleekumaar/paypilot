"""Reliable background consumer for the Transactional Outbox pattern."""

from datetime import datetime, timedelta, timezone
import logging
import time
from typing import Any, Dict, List, Optional
from sqlalchemy import and_, or_, select, update

from app.db.session import get_db_context
from app.models.outbox import OutboxEventModel
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)


class OutboxConsumer:
    """Worker claiming and processing outbox events with lease-based concurrency and retries."""

    def __init__(self, order_service: Optional[OrderService] = None):
        self._order_service = order_service or OrderService()

    def claim_events(self, batch_size: int = 10, lease_seconds: int = 30) -> List[str]:
        """Claim a batch of pending or expired-lease outbox events atomically."""
        now = datetime.now(timezone.utc)
        leased_until = now + timedelta(seconds=lease_seconds)
        claimed_ids: List[str] = []

        with get_db_context() as db:
            # Query eligible events
            query = (
                db.query(OutboxEventModel.id)
                .filter(
                    or_(
                        OutboxEventModel.status == "PENDING",
                        and_(
                            OutboxEventModel.status == "PROCESSING",
                            OutboxEventModel.leased_until < now,
                        ),
                    ),
                    OutboxEventModel.retry_count < OutboxEventModel.max_retries,
                )
                .order_by(OutboxEventModel.created_at.asc())
                .limit(batch_size)
            )
            candidate_ids = [row[0] for row in query.all()]

            if not candidate_ids:
                return []

            # Atomically claim candidates
            for evt_id in candidate_ids:
                res = db.execute(
                    update(OutboxEventModel)
                    .where(
                        OutboxEventModel.id == evt_id,
                        or_(
                            OutboxEventModel.status == "PENDING",
                            and_(
                                OutboxEventModel.status == "PROCESSING",
                                OutboxEventModel.leased_until < now,
                            ),
                        ),
                    )
                    .values(
                        status="PROCESSING",
                        leased_until=leased_until,
                    )
                )
                if res.rowcount > 0:
                    claimed_ids.append(evt_id)

        return claimed_ids

    def process_event(self, event_id: str) -> bool:
        """Execute the business side effect for a claimed outbox event with idempotency."""
        with get_db_context() as db:
            event = db.query(OutboxEventModel).filter(OutboxEventModel.id == event_id).first()
            if not event or event.status != "PROCESSING":
                return False

            payload: Dict[str, Any] = event.payload or {}
            event_type = event.event_type

            try:
                if event_type == "order.create":
                    self._handle_order_create(payload)
                elif event_type == "payment.refunded":
                    self._handle_payment_refunded(payload)
                else:
                    logger.warning(f"Unknown outbox event type: {event_type}")

                # Mark PROCESSED
                event.status = "PROCESSED"
                event.processed_at = datetime.now(timezone.utc)
                event.error_message = None
                return True

            except Exception as exc:
                logger.error(f"Failed processing outbox event {event.id} ({event_type}): {exc}")
                event.retry_count += 1
                event.error_message = str(exc)

                if event.retry_count >= event.max_retries:
                    event.status = "FAILED"
                    logger.error(f"Outbox event {event.id} reached max retries ({event.max_retries}). Moved to Dead-Letter.")
                else:
                    event.status = "PENDING"
                    # Exponential backoff on lease
                    backoff = 2 ** event.retry_count
                    event.leased_until = datetime.now(timezone.utc) + timedelta(seconds=backoff)
                return False

    def _handle_order_create(self, payload: Dict[str, Any]) -> None:
        """Idempotently fulfill order creation."""
        self._order_service.create_order_from_purchase(
            purchase_plan_id=payload["purchase_plan_id"],
            user_id=payload["user_id"],
            product_id=payload["product_id"],
            product_name=payload["product_name"],
            brand=payload["brand"],
            quantity=payload["quantity"],
            amount=payload["amount"],
            currency=payload["currency"],
            paypal_order_id=payload["paypal_order_id"],
            payment_id=payload["payment_id"],
            delivery_days=payload.get("delivery_days", 3),
        )

    def _handle_payment_refunded(self, payload: Dict[str, Any]) -> None:
        """Idempotently dispatch refund notifications."""
        from app.services.notification_service import get_notification_service
        from app.schemas.notification import NotificationType
        notif_svc = get_notification_service()
        notif_svc.notify(
            user_id=payload.get("user_id", "guest_user"),
            order_id=payload.get("payment_id"),
            type=NotificationType.ORDER_UPDATE,
            title="Refund Processed",
            message=f"Refund of ${payload.get('refund_amount', 0.0):.2f} has been processed for your payment.",
        )

    def process_batch(self, batch_size: int = 10) -> int:
        """Process up to batch_size pending outbox events. Returns count of successful events."""
        claimed = self.claim_events(batch_size=batch_size)
        success_count = 0
        for evt_id in claimed:
            if self.process_event(evt_id):
                success_count += 1
        return success_count


_outbox_consumer_instance: Optional[OutboxConsumer] = None


def get_outbox_consumer() -> OutboxConsumer:
    global _outbox_consumer_instance
    if _outbox_consumer_instance is None:
        _outbox_consumer_instance = OutboxConsumer()
    return _outbox_consumer_instance
