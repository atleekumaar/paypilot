"""Deterministic product search and filtering service."""

from typing import Any, Dict, List, Optional
from app.schemas.product import Product
from app.repositories.product_repository import ProductRepository, get_product_repository


class ProductSearchService:
    """Service responsible for deterministic product search and hard-constraint filtering."""

    def __init__(self, repository: Optional[ProductRepository] = None):
        self._repository = repository or get_product_repository()

    def search_products(
        self,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = True,
        required_features: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        feature_thresholds: Optional[Dict[str, Any]] = None,
    ) -> List[Product]:
        """Perform deterministic search enforcing hard constraints.

        Critical Safety Invariants:
        1. Products with price > max_price are strictly EXCLUDED.
        2. Products with stock == False are strictly EXCLUDED if in_stock_only is True.
        3. Hard category constraints are strictly enforced.
        """
        # Step 1: Base search via repository
        candidates = self._repository.search(
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            in_stock_only=in_stock_only,
            keywords=keywords,
        )

        # Step 2: Strict invariant filter (double check to guarantee safety against repository bugs)
        filtered: List[Product] = []
        for p in candidates:
            # Rule 1: Price constraint
            if max_price is not None and p.price > max_price:
                continue
            if min_price is not None and p.price < min_price:
                continue

            # Rule 2: Stock constraint
            if in_stock_only and not p.stock:
                continue

            # Rule 3: Rating constraint
            if min_rating is not None and p.rating < min_rating:
                continue

            # Rule 4: Required features validation
            if required_features:
                if not self._matches_required_features(p, required_features):
                    continue

            # Rule 5: Specific numerical feature thresholds
            if feature_thresholds:
                if not self._matches_feature_thresholds(p, feature_thresholds):
                    continue

            filtered.append(p)

        return filtered

    def _matches_required_features(self, product: Product, required_features: List[str]) -> bool:
        """Verify whether product meets all required feature tags."""
        features = product.features or {}
        text_context = f"{product.name} {product.description}".lower()

        for req in required_features:
            norm_req = req.lower().strip()

            # Dedicated GPU check
            if norm_req in ("gpu", "dedicated_gpu", "nvidia", "rtx"):
                gpu_spec = str(features.get("gpu", "")).lower()
                if not gpu_spec or "integrated" in gpu_spec:
                    if "rtx" not in text_context and "gpu" not in text_context:
                        return False

            # RAM checks (e.g. 16gb_ram, 32gb_ram)
            elif "ram" in norm_req:
                ram_val = features.get("ram_gb")
                if "16" in norm_req:
                    if ram_val is not None and ram_val < 16:
                        return False
                elif "32" in norm_req:
                    if ram_val is not None and ram_val < 32:
                        return False

            # Battery check
            elif "battery" in norm_req:
                battery_val = features.get("battery_hours")
                if battery_val is not None and battery_val < 7.0:
                    return False

            # Noise cancelling
            elif "noise_cancelling" in norm_req or "anc" in norm_req:
                if not features.get("noise_cancelling", False):
                    return False

            # Wireless
            elif "wireless" in norm_req:
                if not features.get("wireless", False):
                    return False

        return True

    def _matches_feature_thresholds(
        self, product: Product, thresholds: Dict[str, Any]
    ) -> bool:
        """Verify numerical or boolean thresholds on product features."""
        features = product.features or {}

        for key, expected in thresholds.items():
            if key == "ram_gb_min":
                val = features.get("ram_gb", 0)
                if val < expected:
                    return False
            elif key == "battery_hours_min":
                val = features.get("battery_hours", 0)
                if val < expected:
                    return False
            elif key == "storage_gb_min":
                val = features.get("storage_gb", 0)
                if val < expected:
                    return False
            elif key == "gpu_required" and expected:
                gpu_spec = str(features.get("gpu", "")).lower()
                if not gpu_spec or "integrated" in gpu_spec:
                    return False

        return True
