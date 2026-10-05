"""Pydantic schemas for products in PayPilot."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductFeatures(BaseModel):
    """Common typed product features for hardware and accessories."""

    model_config = ConfigDict(extra="allow")

    ram_gb: Optional[int] = Field(default=None, description="RAM size in gigabytes")
    storage_gb: Optional[int] = Field(default=None, description="Storage capacity in gigabytes")
    gpu: Optional[str] = Field(default=None, description="Graphics processing unit")
    cpu: Optional[str] = Field(default=None, description="Processor model")
    battery_hours: Optional[float] = Field(default=None, description="Battery life in hours")
    display_inches: Optional[float] = Field(default=None, description="Screen size in inches")
    wireless: Optional[bool] = Field(default=None, description="Whether device is wireless")
    noise_cancelling: Optional[bool] = Field(default=None, description="Active noise cancellation")


class ProductBase(BaseModel):
    """Base schema for Product properties."""

    id: str = Field(..., description="Unique product SKU or identifier", json_schema_extra={"example": "LAP-001"})
    name: str = Field(..., description="Full product title", json_schema_extra={"example": "NovaBook Pro 14"})
    brand: str = Field(..., description="Manufacturer brand", json_schema_extra={"example": "Nova"})
    category: str = Field(..., description="Product category", json_schema_extra={"example": "laptop"})
    description: str = Field(..., description="Detailed marketing & technical description")
    price: float = Field(..., ge=0, description="Selling price", json_schema_extra={"example": 1049.00})
    currency: str = Field(default="USD", description="Currency ISO code", json_schema_extra={"example": "USD"})
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Customer review rating (0.0 - 5.0)", json_schema_extra={"example": 4.7})
    review_count: int = Field(default=0, ge=0, description="Number of user reviews", json_schema_extra={"example": 842})
    stock: bool = Field(default=True, description="Inventory availability flag")
    seller: str = Field(..., description="Merchant or vendor name", json_schema_extra={"example": "Nova Direct"})
    delivery_days: int = Field(default=3, ge=1, description="Estimated delivery time in days", json_schema_extra={"example": 3})
    features: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary feature dictionary")
    image_url: Optional[str] = Field(default=None, description="Public image thumbnail URL")


class Product(ProductBase):
    """Complete product schema representing an item in catalogue or database."""

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Response envelope for product listings."""

    total: int
    items: list[Product]
