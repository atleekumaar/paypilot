"""Pydantic schemas and enums for Purchase Plans."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PurchasePlanStatus(str, Enum):
    """Controlled lifecycle statuses for a Purchase Plan."""

    DRAFT = "DRAFT"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    PAYPAL_ORDER_CREATED = "PAYPAL_ORDER_CREATED"
    PAYPAL_APPROVAL_PENDING = "PAYPAL_APPROVAL_PENDING"
    PAYPAL_APPROVED = "PAYPAL_APPROVED"
    CAPTURED = "CAPTURED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PurchasePlanCreateRequest(BaseModel):
    """Client request to formulate a Purchase Plan.

    Note: The client CANNOT specify unit_price or total_amount.
    The backend looks up the authoritative price from the product catalogue.
    """

    model_config = ConfigDict(extra="ignore")

    product_id: str = Field(..., description="Unique product identifier (e.g. LAP-001)")
    quantity: int = Field(default=1, ge=1, le=10, description="Quantity to purchase")
    user_id: Optional[str] = Field(default="guest_user", description="Identifier of the buyer")
    recommendation_reason: Optional[str] = Field(
        default=None, description="Contextual explanation for why this product was chosen"
    )
    score: Optional[float] = Field(default=None, description="PayPilot discovery score")


class PurchasePlan(BaseModel):
    """Complete Purchase Plan representation."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique purchase plan ID (e.g. PP-8F92A1)")
    user_id: str = Field(..., description="User ID")
    product_id: str = Field(..., description="Selected product ID")
    product_name: str = Field(..., description="Product title")
    brand: str = Field(..., description="Product manufacturer")
    seller: str = Field(..., description="Authoritative seller name")
    delivery_days: int = Field(..., description="Estimated delivery window in days")
    quantity: int = Field(..., description="Purchased quantity")
    unit_price: float = Field(..., description="Authoritative unit price derived by backend")
    currency: str = Field(default="USD", description="Currency ISO code")
    total_amount: float = Field(..., description="Total amount calculated as unit_price * quantity")
    status: PurchasePlanStatus = Field(
        default=PurchasePlanStatus.AWAITING_APPROVAL,
        description="Current lifecycle status",
    )
    paypal_order_id: Optional[str] = Field(
        default=None, description="Associated PayPal Order ID once created"
    )
    recommendation_reason: Optional[str] = Field(
        default=None, description="AI grounded reason for this item"
    )
    score: Optional[float] = Field(default=None, description="Discovery match score")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
