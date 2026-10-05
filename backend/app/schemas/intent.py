"""Pydantic schemas for intent extraction and normalized search criteria."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BudgetConstraint(BaseModel):
    """Budget constraints extracted from user query."""

    max: Optional[float] = Field(default=None, description="Maximum budget amount")
    min: Optional[float] = Field(default=None, description="Minimum budget amount")
    currency: str = Field(default="USD", description="Currency code")


class HardConstraints(BaseModel):
    """Hard constraints that must strictly be satisfied."""

    max_price: Optional[float] = Field(default=None, description="Hard upper bound on price")
    min_price: Optional[float] = Field(default=None, description="Hard lower bound on price")
    category: Optional[str] = Field(default=None, description="Strict category filter")
    in_stock: bool = Field(default=True, description="Strict inventory requirement")
    min_rating: Optional[float] = Field(default=None, description="Minimum rating required")


class ProductSearchIntent(BaseModel):
    """Structured representation of a natural language product search request."""

    intent: str = Field(default="product_search", description="Action intent type")
    category: Optional[str] = Field(default=None, description="Identified product category")
    budget: Optional[BudgetConstraint] = Field(default=None, description="Extracted budget limits")
    use_case: Optional[str] = Field(default=None, description="Identified intended use case")
    requirements: List[str] = Field(default_factory=list, description="Explicit stated requirements")
    preferences: List[str] = Field(default_factory=list, description="User soft preferences")
    hard_constraints: HardConstraints = Field(
        default_factory=HardConstraints,
        description="Strict deterministic filters",
    )
    soft_preferences: List[str] = Field(
        default_factory=list,
        description="Features to rank or prioritize",
    )
    normalized_features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Normalized feature thresholds (e.g. battery_hours_min, gpu_required)",
    )
