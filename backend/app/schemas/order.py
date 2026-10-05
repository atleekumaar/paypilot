"""Pydantic schemas and enums for Orders."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class OrderStatus(str, Enum):
    """Authoritative Order lifecycle states."""

    CREATED = "CREATED"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class Order(BaseModel):
    """Complete Order representation."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique internal order ID (e.g. ORD-001 or PP-001)")
    user_id: str = Field(default="guest_user", description="Owner user ID")
    purchase_plan_id: str = Field(..., description="Associated Purchase Plan ID")
    paypal_order_id: Optional[str] = Field(default=None, description="PayPal Order ID")
    payment_id: Optional[str] = Field(default=None, description="Internal Payment transaction ID")
    product_id: str = Field(..., description="Purchased Product ID")
    product_name: str = Field(..., description="Purchased Product title")
    brand: Optional[str] = Field(default=None, description="Product brand")
    quantity: int = Field(default=1, ge=1, description="Purchased item quantity")
    amount: float = Field(..., description="Total purchase amount")
    currency: str = Field(default="USD", description="Currency ISO code")
    status: OrderStatus = Field(default=OrderStatus.CREATED, description="Current order state")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
