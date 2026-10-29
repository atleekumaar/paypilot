"""Strict Pydantic schemas for agent commerce tools with extra='forbid' validation."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StrictBaseToolArgs(BaseModel):
    """Base model forbidding all unknown/extra fields to prevent prompt-injection tampering."""

    model_config = ConfigDict(extra="forbid")


class SearchProductsArgs(StrictBaseToolArgs):
    """Arguments for search_products tool."""

    category: Optional[str] = Field(None, description="e.g. laptop, phone, headphones")
    max_price: Optional[float] = Field(None, ge=0.0, description="Maximum budget ceiling")
    min_price: Optional[float] = Field(None, ge=0.0, description="Minimum price floor")
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Minimum customer star rating")
    in_stock_only: bool = Field(default=True, description="Filter for items currently in stock")
    keywords: Optional[List[str]] = Field(None, description="Keywords to match against product titles and tags")
    required_features: Optional[List[str]] = Field(None, description="Key hardware/software requirements")


class GetProductArgs(StrictBaseToolArgs):
    """Arguments for get_product tool."""

    product_id: str = Field(..., min_length=1, max_length=50, description="Unique product SKU ID")


class CompareProductsArgs(StrictBaseToolArgs):
    """Arguments for compare_products tool."""

    product_ids: Optional[List[str]] = Field(
        default_factory=list,
        description="List of product SKU IDs to compare",
    )


class CreatePurchasePlanArgs(StrictBaseToolArgs):
    """Arguments for create_purchase_plan tool."""

    product_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Product SKU ID")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantity to purchase")
    recommendation_reason: Optional[str] = Field(None, max_length=1000, description="Agent grounding justification")


class RequestPurchaseApprovalArgs(StrictBaseToolArgs):
    """Arguments for request_purchase_approval tool."""

    purchase_plan_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Purchase Plan ID")


class CreatePayPalOrderArgs(StrictBaseToolArgs):
    """Arguments for create_paypal_order tool."""

    purchase_plan_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Purchase Plan ID")


class CapturePayPalPaymentArgs(StrictBaseToolArgs):
    """Arguments for capture_paypal_payment tool."""

    purchase_plan_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Purchase Plan ID")
    paypal_order_id: Optional[str] = Field(None, min_length=1, max_length=100, description="PayPal Provider Order ID")


class GetOrderArgs(StrictBaseToolArgs):
    """Arguments for get_order tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")


class GetUserOrdersArgs(StrictBaseToolArgs):
    """Arguments for get_user_orders tool."""

    user_id: Optional[str] = Field(None, min_length=1, max_length=50, description="User identifier")


class GetPaymentStatusArgs(StrictBaseToolArgs):
    """Arguments for get_payment_status tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")


class GetShipmentStatusArgs(StrictBaseToolArgs):
    """Arguments for get_shipment_status tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")


class GetTrackingDetailsArgs(StrictBaseToolArgs):
    """Arguments for get_tracking_details tool."""

    query: Optional[str] = Field(None, min_length=1, max_length=100, description="Order ID or tracking number")
    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Alternative order ID reference")


class GetDeliveryEstimateArgs(StrictBaseToolArgs):
    """Arguments for get_delivery_estimate tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")


class DetectOrderIssueArgs(StrictBaseToolArgs):
    """Arguments for detect_order_issue tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")
    reference_date: Optional[str] = Field(None, max_length=30, description="Reference ISO date for comparison")


class PrepareSupportRequestArgs(StrictBaseToolArgs):
    """Arguments for prepare_support_request tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")


class SendSupportRequestArgs(StrictBaseToolArgs):
    """Arguments for send_support_request tool."""

    order_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Order identifier")

