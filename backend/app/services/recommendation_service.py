"""Recommendation service coordinating the AI product discovery pipeline."""

import logging
from typing import List, Optional

from app.schemas.intent import ProductSearchIntent
from app.schemas.product import Product
from app.schemas.recommendation import RankedProduct, RecommendationResponse
from app.services.intent_service import IntentService
from app.services.ranking_service import ProductRankingService
from app.services.search_service import ProductSearchService

logger = logging.getLogger(__name__)


class RecommendationService:
    """Orchestrates the entire discovery pipeline from natural query to explainable recommendation."""

    def __init__(
        self,
        intent_service: Optional[IntentService] = None,
        search_service: Optional[ProductSearchService] = None,
        ranking_service: Optional[ProductRankingService] = None,
    ):
        self._intent_service = intent_service or IntentService()
        self._search_service = search_service or ProductSearchService()
        self._ranking_service = ranking_service or ProductRankingService()

    def discover_products(self, query: str) -> RecommendationResponse:
        """Execute the end-to-end product discovery agent flow."""
        cleaned_query = (query or "").strip()

        # Handle empty query gracefully
        if not cleaned_query:
            empty_intent = self._intent_service.extract_intent("")
            return RecommendationResponse(
                query="",
                intent=empty_intent,
                recommendations=[],
                explanation="Please describe what you're looking for.",
                total_candidates=0,
            )

        # Step 1: Extract and normalize structured intent
        intent = self._intent_service.extract_intent(cleaned_query)

        # Step 2: Search and filter candidates enforcing hard constraints
        candidates = self._search_service.search_products(
            category=intent.hard_constraints.category,
            max_price=intent.hard_constraints.max_price,
            min_price=intent.hard_constraints.min_price,
            min_rating=intent.hard_constraints.min_rating,
            in_stock_only=intent.hard_constraints.in_stock,
            required_features=intent.requirements,
        )

        total_candidates = len(candidates)

        # Handle no results gracefully
        if not candidates:
            explanation = (
                "I couldn't find products matching those constraints. "
                "Try increasing your budget or relaxing a requirement."
            )
            return RecommendationResponse(
                query=cleaned_query,
                intent=intent,
                recommendations=[],
                explanation=explanation,
                total_candidates=0,
            )

        # Step 3: Deterministic ranking
        ranked_products = self._ranking_service.rank_products(
            products=candidates,
            intent=intent,
            top_k=3,
        )

        # Step 4: Generate grounded explanation (No hallucinations permitted)
        top_pick = ranked_products[0]
        explanation = self._generate_grounded_explanation(top_pick, intent)

        return RecommendationResponse(
            query=cleaned_query,
            intent=intent,
            recommendations=ranked_products,
            explanation=explanation,
            total_candidates=total_candidates,
        )

    def _generate_grounded_explanation(
        self, top_pick: RankedProduct, intent: ProductSearchIntent
    ) -> str:
        """Construct grounded natural language explanation strictly from verified product specs."""
        prod = top_pick.product
        feats = prod.features or {}

        # Opening synthesis
        lead_aspects: List[str] = []
        if feats.get("gpu") and "integrated" not in str(feats.get("gpu", "")).lower():
            lead_aspects.append("GPU performance")
        if feats.get("battery_hours") and feats["battery_hours"] >= 8.0:
            lead_aspects.append("battery endurance")
        if intent.hard_constraints.max_price and prod.price <= intent.hard_constraints.max_price:
            lead_aspects.append("price-to-value ratio")

        if lead_aspects:
            aspects_phrase = ", ".join(lead_aspects)
            summary_sentence = (
                f"I recommend the {prod.name} because it gives you the strongest balance of "
                f"{aspects_phrase} while staying reliably within your specifications."
            )
        else:
            summary_sentence = (
                f"I recommend the {prod.name} as the top overall match for your search criteria."
            )

        # Structured bullet proof points
        bullet_points: List[str] = []
        if feats.get("gpu"):
            bullet_points.append(f"✓ {feats['gpu']}")
        if feats.get("ram_gb"):
            bullet_points.append(f"✓ {feats['ram_gb']} GB RAM")
        if feats.get("battery_hours"):
            bullet_points.append(f"✓ {feats['battery_hours']:.1f}-hour battery life")
        if feats.get("storage_gb"):
            bullet_points.append(f"✓ {feats['storage_gb']} GB SSD")
        bullet_points.append(f"✓ ${prod.price:,.2f} price")
        bullet_points.append(f"✓ {prod.rating}★ rating ({prod.review_count:,} reviews)")
        if prod.delivery_days <= 3:
            bullet_points.append(f"✓ Fast {prod.delivery_days}-day delivery via {prod.seller}")

        bullets_formatted = "\n".join(bullet_points[:5])

        return f"{summary_sentence}\n\nWhy it fits:\n{bullets_formatted}"
