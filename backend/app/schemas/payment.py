"""Pydantic schemas and enums for Payments."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class PaymentStatus(str, Enum):
    """Payment transaction states."""

    CREATED = "CREATED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    CAPTURED = "CAPTURED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentProvider(str, Enum):
    """Supported payment providers."""

    PAYPAL = "PAYPAL"


class Payment(BaseModel):
    """Authoritative Payment transaction record."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique internal payment ID (e.g. PAY-...)")
    purchase_plan_id: str = Field(..., description="Associated Purchase Plan ID")
    provider: PaymentProvider = Field(default=PaymentProvider.PAYPAL, description="Payment processor")
    provider_order_id: str = Field(..., description="PayPal Order ID (e.g. 7AB12345XYZ)")
    amount: float = Field(..., description="Authorized/captured transaction amount")
    currency: str = Field(default="USD", description="Currency ISO code")
    status: PaymentStatus = Field(default=PaymentStatus.CREATED, description="Payment lifecycle status")
    capture_id: Optional[str] = Field(default=None, description="PayPal Capture transaction ID")
    payer_email: Optional[str] = Field(default=None, description="Buyer PayPal account email")
    payer_id: Optional[str] = Field(default=None, description="Buyer PayPal account ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw provider metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
