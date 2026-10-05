"""Pydantic schemas and enums for Shipments and Tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ShipmentStatus(str, Enum):
    """Controlled shipment and logistics states."""

    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class ShipmentTimelineEvent(BaseModel):
    """Discrete milestone in the shipment journey."""

    title: str = Field(..., description="Short milestone name (e.g. 'Order Confirmed', 'In Transit')")
    description: str = Field(..., description="Contextual logistics update")
    timestamp: str = Field(..., description="Timestamp or human-readable date (e.g. 'Oct 16, 2026')")
    completed: bool = Field(default=False, description="Whether this stage has been passed")
    current: bool = Field(default=False, description="Whether this is the current active stage")


class Shipment(BaseModel):
    """Complete Shipment representation."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique shipment ID (e.g. SHP-001)")
    order_id: str = Field(..., description="Associated Order ID")
    tracking_number: str = Field(..., description="Carrier tracking identifier (e.g. TRK-USPS-8842)")
    carrier: str = Field(default="FastShip Logistics", description="Carrier name (e.g. FedEx, UPS, USPS)")
    status: ShipmentStatus = Field(default=ShipmentStatus.PROCESSING, description="Current logistics status")
    estimated_delivery: str = Field(..., description="Promised or estimated arrival date (e.g. '2026-10-18')")
    actual_delivery: Optional[str] = Field(default=None, description="Actual delivered date if reached")
    last_location: str = Field(default="Regional Logistics Hub", description="Most recent facility or town")
    last_update: str = Field(..., description="Last verified status message from carrier")
    timeline: List[ShipmentTimelineEvent] = Field(default_factory=list, description="Milestone progression")
    is_demo: bool = Field(default=True, description="Indicates synthetic demo data for the hackathon")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderDetailResponse(BaseModel):
    """Rich order representation including shipment details and payment summary."""

    id: str
    user_id: str
    purchase_plan_id: str
    paypal_order_id: Optional[str] = None
    payment_id: Optional[str] = None
    product_id: str
    product_name: str
    brand: Optional[str] = None
    quantity: int
    amount: float
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    shipment: Optional[Shipment] = None
