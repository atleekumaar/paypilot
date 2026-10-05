"""Thread-safe in-memory repository for Shipments and Tracking."""

from datetime import datetime, timezone
import threading
from typing import Dict, List, Optional

from app.schemas.shipment import Shipment, ShipmentStatus, ShipmentTimelineEvent


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


class ShipmentRepository:
    """In-memory thread-safe shipment tracking store."""

    def __init__(self, populate_defaults: bool = True):
        self._lock = threading.Lock()
        self._shipments: Dict[str, Shipment] = _build_default_demo_shipments() if populate_defaults else {}

    def create(self, shipment: Shipment) -> Shipment:
        with self._lock:
            self._shipments[shipment.id] = shipment
            return shipment

    def get_by_id(self, shipment_id: str) -> Optional[Shipment]:
        with self._lock:
            return self._shipments.get(shipment_id)

    def get_by_order_id(self, order_id: str) -> Optional[Shipment]:
        with self._lock:
            for shipment in self._shipments.values():
                if shipment.order_id == order_id:
                    return shipment
            return None

    def list_all(self) -> List[Shipment]:
        with self._lock:
            return list(self._shipments.values())

    def update(self, shipment: Shipment) -> Shipment:
        with self._lock:
            self._shipments[shipment.id] = shipment
            return shipment

    def reset_defaults(self) -> None:
        """Reset repository to initial synthetic demo state."""
        with self._lock:
            self._shipments = _build_default_demo_shipments()

    def clear(self) -> None:
        """Clear all stored shipments."""
        with self._lock:
            self._shipments.clear()


_shipment_repo_instance: Optional[ShipmentRepository] = None


def get_shipment_repository() -> ShipmentRepository:
    """Dependency provider singleton for ShipmentRepository."""
    global _shipment_repo_instance
    if _shipment_repo_instance is None:
        _shipment_repo_instance = ShipmentRepository()
    return _shipment_repo_instance
