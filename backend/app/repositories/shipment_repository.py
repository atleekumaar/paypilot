"""Database-backed repository for Shipments and Tracking."""

from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional

from app.db.session import get_db_context, init_db
from app.models.shipment import ShipmentModel
from app.schemas.shipment import Shipment, ShipmentStatus, ShipmentTimelineEvent

logger = logging.getLogger(__name__)


def _build_default_demo_shipments() -> Dict[str, Shipment]:
    """Generates initial realistic synthetic shipments matching demo orders."""
    return {
        "SHP-001": Shipment(
            id="SHP-001",
            order_id="ORD-001",
            tracking_number="TRK-FAST-884210",
            carrier="FastShip Logistics",
            status=ShipmentStatus.IN_TRANSIT,
            estimated_delivery="2026-10-18",
            actual_delivery=None,
            last_location="Regional Logistics Facility, Columbus OH",
            last_update="Package arrived at the regional facility. Regional logistics delay reported.",
            timeline=[
                ShipmentTimelineEvent(
                    title="Payment Completed",
                    description="PayPal transaction verified and captured.",
                    timestamp="Oct 12, 2026",
                    completed=True,
                    current=False,
                ),
                ShipmentTimelineEvent(
                    title="Order Confirmed",
                    description="Merchant acknowledged order and reserved inventory.",
                    timestamp="Oct 13, 2026",
                    completed=True,
                    current=False,
                ),
                ShipmentTimelineEvent(
                    title="Shipped",
                    description="Package handed to FastShip Logistics carrier.",
                    timestamp="Oct 15, 2026",
                    completed=True,
                    current=False,
                ),
                ShipmentTimelineEvent(
                    title="In Transit",
                    description="Package arrived at regional facility. Regional logistics delay noted.",
                    timestamp="Oct 16, 2026",
                    completed=True,
                    current=True,
                ),
                ShipmentTimelineEvent(
                    title="Estimated Delivery",
                    description="Expected delivery to buyer address.",
                    timestamp="Oct 18, 2026",
                    completed=False,
                    current=False,
                ),
            ],
            is_demo=True,
            created_at=datetime(2026, 10, 13, 9, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 16, 9, 30, tzinfo=timezone.utc),
        ),
        "SHP-002": Shipment(
            id="SHP-002",
            order_id="ORD-002",
            tracking_number="TRK-FEDX-119420",
            carrier="FedEx Ground",
            status=ShipmentStatus.DELIVERED,
            estimated_delivery="2026-10-04",
            actual_delivery="2026-10-04",
            last_location="Front Porch, Buyer Address",
            last_update="Package delivered. Signed by resident.",
            timeline=[
                ShipmentTimelineEvent(
                    title="Payment Completed",
                    description="Payment received.",
                    timestamp="Sep 28, 2026",
                    completed=True,
                    current=False,
                ),
                ShipmentTimelineEvent(
                    title="Shipped",
                    description="Departed dispatch center.",
                    timestamp="Sep 30, 2026",
                    completed=True,
                    current=False,
                ),
                ShipmentTimelineEvent(
                    title="Delivered",
                    description="Delivered to front porch.",
                    timestamp="Oct 04, 2026",
                    completed=True,
                    current=True,
                ),
            ],
            is_demo=True,
            created_at=datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 4, 16, 25, tzinfo=timezone.utc),
        ),
        "SHP-003": Shipment(
            id="SHP-003",
            order_id="ORD-003",
            tracking_number="TRK-UPS-392811",
            carrier="UPS Next Day Air",
            status=ShipmentStatus.PROCESSING,
            estimated_delivery="2026-10-22",
            actual_delivery=None,
            last_location="Fulfillment Center, Austin TX",
            last_update="Order confirmed. Preparing for shipment.",
            timeline=[
                ShipmentTimelineEvent(
                    title="Payment Completed",
                    description="PayPal Sandbox payment authorized and captured.",
                    timestamp="Oct 19, 2026",
                    completed=True,
                    current=False,
                ),
                ShipmentTimelineEvent(
                    title="Processing",
                    description="Item queued for dispatch packing.",
                    timestamp="Oct 19, 2026",
                    completed=True,
                    current=True,
                ),
                ShipmentTimelineEvent(
                    title="Estimated Delivery",
                    description="Expected arrival.",
                    timestamp="Oct 22, 2026",
                    completed=False,
                    current=False,
                ),
            ],
            is_demo=True,
            created_at=datetime(2026, 10, 19, 11, 48, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 19, 11, 55, tzinfo=timezone.utc),
        ),
        "SHP-099": Shipment(
            id="SHP-099",
            order_id="ORD-099",
            tracking_number="TRK-USPS-990112",
            carrier="USPS Priority",
            status=ShipmentStatus.IN_TRANSIT,
            estimated_delivery="2026-10-20",
            actual_delivery=None,
            last_location="Sorting Center, Chicago IL",
            last_update="Package in transit to destination.",
            timeline=[],
            is_demo=True,
            created_at=datetime(2026, 10, 14, 8, 30, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 15, 12, 10, tzinfo=timezone.utc),
        ),
    }


def _model_to_schema(m: ShipmentModel) -> Shipment:
    timeline_events = [
        ShipmentTimelineEvent(**item) if isinstance(item, dict) else item
        for item in (m.timeline or [])
    ]
    return Shipment(
        id=m.id,
        order_id=m.order_id,
        tracking_number=m.tracking_number,
        carrier=m.carrier,
        status=ShipmentStatus(m.status),
        estimated_delivery=m.estimated_delivery or "",
        actual_delivery=m.actual_delivery,
        last_location=m.last_location or "",
        last_update=m.last_update or "",
        timeline=timeline_events,
        is_demo=m.is_demo,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class ShipmentRepository:
    """Database-backed shipment tracking store."""

    def __init__(self, populate_defaults: bool = True):
        init_db()
        if populate_defaults:
            with get_db_context() as db:
                if db.query(ShipmentModel).count() == 0:
                    for shp in _build_default_demo_shipments().values():
                        db.merge(ShipmentModel(
                            id=shp.id,
                            order_id=shp.order_id,
                            tracking_number=shp.tracking_number,
                            carrier=shp.carrier,
                            status=shp.status.value if hasattr(shp.status, "value") else str(shp.status),
                            estimated_delivery=shp.estimated_delivery,
                            actual_delivery=shp.actual_delivery,
                            last_location=shp.last_location,
                            last_update=shp.last_update,
                            timeline=[e.model_dump() if hasattr(e, "model_dump") else dict(e) for e in shp.timeline],
                            is_demo=shp.is_demo,
                            created_at=shp.created_at,
                            updated_at=shp.updated_at,
                        ))

    def create(self, shipment: Shipment) -> Shipment:
        with get_db_context() as db:
            m = ShipmentModel(
                id=shipment.id,
                order_id=shipment.order_id,
                tracking_number=shipment.tracking_number,
                carrier=shipment.carrier,
                status=shipment.status.value if hasattr(shipment.status, "value") else str(shipment.status),
                estimated_delivery=shipment.estimated_delivery,
                actual_delivery=shipment.actual_delivery,
                last_location=shipment.last_location,
                last_update=shipment.last_update,
                timeline=[e.model_dump() if hasattr(e, "model_dump") else dict(e) for e in shipment.timeline],
                is_demo=shipment.is_demo,
                created_at=shipment.created_at,
                updated_at=shipment.updated_at,
            )
            db.merge(m)
            return shipment

    def get_by_id(self, shipment_id: str) -> Optional[Shipment]:
        with get_db_context() as db:
            m = db.query(ShipmentModel).filter(ShipmentModel.id == shipment_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def get_by_order_id(self, order_id: str) -> Optional[Shipment]:
        with get_db_context() as db:
            m = db.query(ShipmentModel).filter(ShipmentModel.order_id == order_id).first()
            if m:
                return _model_to_schema(m)
            return None

    def list_all(self) -> List[Shipment]:
        with get_db_context() as db:
            records = db.query(ShipmentModel).all()
            return [_model_to_schema(m) for m in records]

    def update(self, shipment: Shipment) -> Shipment:
        with get_db_context() as db:
            m = db.query(ShipmentModel).filter(ShipmentModel.id == shipment.id).first()
            if m:
                m.status = shipment.status.value if hasattr(shipment.status, "value") else str(shipment.status)
                m.estimated_delivery = shipment.estimated_delivery
                m.actual_delivery = shipment.actual_delivery
                m.last_location = shipment.last_location
                m.last_update = shipment.last_update
                m.timeline = [e.model_dump() if hasattr(e, "model_dump") else dict(e) for e in shipment.timeline]
                m.updated_at = datetime.now(timezone.utc)
                shipment.updated_at = m.updated_at
            else:
                self.create(shipment)
            return shipment

    def reset_defaults(self) -> None:
        """Reset repository to initial synthetic demo state."""
        with get_db_context() as db:
            db.query(ShipmentModel).delete()
            for shp in _build_default_demo_shipments().values():
                db.merge(ShipmentModel(
                    id=shp.id,
                    order_id=shp.order_id,
                    tracking_number=shp.tracking_number,
                    carrier=shp.carrier,
                    status=shp.status.value if hasattr(shp.status, "value") else str(shp.status),
                    estimated_delivery=shp.estimated_delivery,
                    actual_delivery=shp.actual_delivery,
                    last_location=shp.last_location,
                    last_update=shp.last_update,
                    timeline=[e.model_dump() if hasattr(e, "model_dump") else dict(e) for e in shp.timeline],
                    is_demo=shp.is_demo,
                    created_at=shp.created_at,
                    updated_at=shp.updated_at,
                ))

    def clear(self) -> None:
        """Clear all stored shipments."""
        with get_db_context() as db:
            db.query(ShipmentModel).delete()


_shipment_repo_instance: Optional[ShipmentRepository] = None


def get_shipment_repository() -> ShipmentRepository:
    """Dependency provider singleton for ShipmentRepository."""
    global _shipment_repo_instance
    if _shipment_repo_instance is None:
        _shipment_repo_instance = ShipmentRepository()
    return _shipment_repo_instance
