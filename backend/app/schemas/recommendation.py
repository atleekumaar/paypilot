"""Schemas for product ranking and recommendations."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.product import Product
from app.schemas.intent import ProductSearchIntent


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of deterministic score components (all 0-100)."""

    requirement_match: float = Field(..., description="Match against explicit requirements (35% weight)")
    price_fit: float = Field(..., description="Fit within user budget (25% weight)")
    rating_score: float = Field(..., description="Customer satisfaction rating score (15% weight)")
    delivery_score: float = Field(..., description="Speed of delivery (10% weight)")
    seller_score: float = Field(..., description="Seller reputation and reliability (10% weight)")
    preference_score: float = Field(..., description="Match against soft preferences (5% weight)")


class RankedProduct(BaseModel):
    """Product evaluated and scored by the ranking engine."""

    product: Product
    product_id: str
    rank: int
    score: float
    breakdown: ScoreBreakdown
    match_reasons: List[str] = Field(default_factory=list, description="Specific grounded match points")


class RecommendationResponse(BaseModel):
    """Top recommendations returned to user with explanation."""

    query: str
    intent: ProductSearchIntent
    recommendations: List[RankedProduct]
    explanation: str
    total_candidates: int
