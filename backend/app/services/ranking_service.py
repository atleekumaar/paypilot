"""Deterministic product ranking service applying mathematical scoring formula."""

import json
from typing import List, Optional
from app.schemas.product import Product
from app.schemas.intent import ProductSearchIntent
from app.schemas.recommendation import RankedProduct, ScoreBreakdown


class ProductRankingService:
    """Calculates deterministic 0-100 scores for candidate products based on user intent."""

    # Weights mandated by specification
    WEIGHT_REQUIREMENT = 0.35
    WEIGHT_PRICE_FIT = 0.25
    WEIGHT_RATING = 0.15
    WEIGHT_DELIVERY = 0.10
    WEIGHT_SELLER = 0.10
    WEIGHT_PREFERENCE = 0.05

    def rank_products(
        self,
        products: List[Product],
        intent: ProductSearchIntent,
        top_k: int = 3,
    ) -> List[RankedProduct]:
        """Rank products deterministically and return the top-K highest scoring items."""
        ranked_list: List[RankedProduct] = []

        for product in products:
            breakdown, reasons = self._calculate_scores(product, intent)

            # Compute composite weighted score
            final_score = (
                self.WEIGHT_REQUIREMENT * breakdown.requirement_match
                + self.WEIGHT_PRICE_FIT * breakdown.price_fit
                + self.WEIGHT_RATING * breakdown.rating_score
                + self.WEIGHT_DELIVERY * breakdown.delivery_score
                + self.WEIGHT_SELLER * breakdown.seller_score
                + self.WEIGHT_PREFERENCE * breakdown.preference_score
            )
            final_score = round(final_score, 1)

            ranked_list.append(
                RankedProduct(
                    product=product,
                    product_id=product.id,
                    rank=0,  # Will be assigned after sorting
                    score=final_score,
                    breakdown=breakdown,
                    match_reasons=reasons,
                )
            )

        # Sort descending by final score, tie-breaking deterministically by rating and review count
        ranked_list.sort(
            key=lambda x: (x.score, x.product.rating, x.product.review_count),
            reverse=True,
        )

        # Assign 1-indexed ranks
        for index, item in enumerate(ranked_list):
            item.rank = index + 1

        return ranked_list[:top_k]

    def _calculate_scores(
        self, product: Product, intent: ProductSearchIntent
    ) -> tuple[ScoreBreakdown, List[str]]:
        """Calculate normalized individual component scores (0.0 to 100.0) and grounded match reasons."""
        features = product.features or {}
        match_reasons: List[str] = []

        # 1. Requirement Match (0 - 100)
        req_score = 80.0  # Base match for passing search filters
        norm_feats = intent.normalized_features or {}

        # Battery requirement check
        if "battery_hours_min" in norm_feats:
            bat = features.get("battery_hours", 0.0)
            target = norm_feats["battery_hours_min"]
            if bat >= target:
                req_score += 10.0
                match_reasons.append(f"{bat:.1f}-hour battery (exceeds {target:.0f}h requirement)")
            else:
                req_score -= 15.0

        # GPU / AI requirement check
        if norm_feats.get("gpu_preference") or norm_feats.get("gpu_required"):
            gpu = str(features.get("gpu", "")).lower()
            if "rtx" in gpu or "tensor" in gpu:
                req_score += 10.0
                match_reasons.append(f"Dedicated {features.get('gpu')} for GPU-accelerated AI models")
            elif "arc" in gpu or "radeon 780" in gpu:
                req_score += 2.0
                match_reasons.append(f"Capable integrated {features.get('gpu')} graphics")
            else:
                req_score -= 10.0

        # RAM requirement check
        if "ram_gb_min" in norm_feats:
            ram = features.get("ram_gb", 0)
            target_ram = norm_feats["ram_gb_min"]
            if ram >= target_ram:
                req_score = min(100.0, req_score + 5.0)
                match_reasons.append(f"{ram} GB RAM for multi-tasking and local development")
            else:
                req_score -= 15.0

        req_score = max(0.0, min(100.0, req_score))

        # 2. Price Fit (0 - 100)
        max_budget = intent.hard_constraints.max_price
        if max_budget is not None and max_budget > 0:
            if product.price <= max_budget:
                # Sweet spot: reasonably priced within budget
                # Saving money without sacrificing quality gives higher score
                under_budget_ratio = (max_budget - product.price) / max_budget
                price_fit = 85.0 + (under_budget_ratio * 15.0)
                match_reasons.append(f"${product.price:,.2f} price is within ${max_budget:,.2f} budget")
            else:
                price_fit = 0.0
        else:
            price_fit = 90.0
        price_fit = max(0.0, min(100.0, price_fit))

        # 3. Rating Score (0 - 100)
        rating_score = (product.rating / 5.0) * 100.0
        if product.rating >= 4.5:
            match_reasons.append(f"{product.rating}★ customer rating across {product.review_count:,} reviews")
        rating_score = max(0.0, min(100.0, rating_score))

        # 4. Delivery Score (0 - 100)
        delivery_score = max(40.0, 100.0 - (product.delivery_days - 1) * 10.0)
        if product.delivery_days <= 3:
            match_reasons.append(f"Fast {product.delivery_days}-day delivery via {product.seller}")
        delivery_score = max(0.0, min(100.0, delivery_score))

        # 5. Seller Reliability (0 - 100)
        seller_lower = product.seller.lower()
        if any(term in seller_lower for term in ["direct", "official", "store", "authorized"]):
            seller_score = 98.0
        else:
            seller_score = 82.0

        # 6. Preference Match (0 - 100)
        pref_score = 85.0
        if intent.soft_preferences:
            pref_hits = 0
            prod_blob = f"{product.name} {product.description} {json.dumps(features)}".lower()
            for pref in intent.soft_preferences:
                if any(w in prod_blob for w in pref.lower().split()):
                    pref_hits += 1
            ratio = pref_hits / max(1, len(intent.soft_preferences))
            pref_score = 70.0 + (ratio * 30.0)
        pref_score = max(0.0, min(100.0, pref_score))

        breakdown = ScoreBreakdown(
            requirement_match=round(req_score, 1),
            price_fit=round(price_fit, 1),
            rating_score=round(rating_score, 1),
            delivery_score=round(delivery_score, 1),
            seller_score=round(seller_score, 1),
            preference_score=round(pref_score, 1),
        )

        return breakdown, match_reasons
