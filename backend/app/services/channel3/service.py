"""Channel3 Domain Service integrating external product discovery with PayPilot."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from app.schemas.product import Product
from app.services.channel3.client import Channel3Client, Channel3Config, Channel3Product

logger = logging.getLogger(__name__)


def channel3_to_paypilot_product(c3: Channel3Product) -> Product:
    """Map a normalized Channel3Product into PayPilot's authoritative internal Product model."""
    features = dict(c3.attributes or {})
    # Ensure standard hardware attributes exist if present in attributes
    if "ram_gb" in features:
        features["ram_gb"] = int(features["ram_gb"])
    if "storage_gb" in features:
        features["storage_gb"] = int(features["storage_gb"])
    if "battery_hours" in features:
        features["battery_hours"] = float(features["battery_hours"])

    return Product(
        id=c3.id,
        name=c3.title,
        brand=c3.brand,
        category=c3.category,
        description=c3.description,
        price=c3.price,
        currency=c3.currency,
        rating=c3.rating,
        review_count=c3.review_count,
        stock=(c3.availability != "OUT_OF_STOCK"),
        seller=f"{c3.retailer} (via Channel3)",
        delivery_days=c3.delivery_days,
        features=features,
        image_url=c3.image_url,
        source="CHANNEL3",
        source_url=c3.source_url,
    )


class Channel3Service:
    """Service handling Channel3 discovery, cross-merchant comparisons, and source attribution."""

    def __init__(self, client: Optional[Channel3Client] = None):
        self.client = client or Channel3Client()

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        limit: int = 10,
    ) -> List[Product]:
        """Search products and map to PayPilot Product models."""
        c3_products = self.client.search(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            brand=brand,
            limit=limit,
        )
        return [channel3_to_paypilot_product(p) for p in c3_products]

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch individual product by Channel3 ID."""
        c3 = self.client.lookup(product_id)
        if c3:
            return channel3_to_paypilot_product(c3)
        return None

    def compare(self, product_ids: List[str]) -> Dict[str, Any]:
        """Perform cross-retailer comparison with price trade-offs and delivery differences."""
        products: List[Product] = []
        for pid in product_ids:
            p = self.get_product(pid)
            if p:
                products.append(p)

        if not products:
            return {"error": "No matching Channel3 products found for comparison."}

        lowest_price = min(products, key=lambda x: x.price)
        highest_rated = max(products, key=lambda x: x.rating)
        fastest_delivery = min(products, key=lambda x: x.delivery_days)

        comparison_matrix = []
        for p in products:
            comparison_matrix.append({
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "price": p.price,
                "retailer": p.seller,
                "rating": p.rating,
                "delivery_days": p.delivery_days,
                "in_stock": p.stock,
                "source_url": p.source_url,
            })

        return {
            "total_compared": len(products),
            "lowest_price_item": {"id": lowest_price.id, "name": lowest_price.name, "price": lowest_price.price},
            "highest_rated_item": {"id": highest_rated.id, "name": highest_rated.name, "rating": highest_rated.rating},
            "fastest_delivery_item": {"id": fastest_delivery.id, "name": fastest_delivery.name, "days": fastest_delivery.delivery_days},
            "products": comparison_matrix,
            "source": "Channel3 Multi-Merchant Retail Graph",
        }


_channel3_service_instance: Optional[Channel3Service] = None


def get_channel3_service() -> Channel3Service:
    global _channel3_service_instance
    if _channel3_service_instance is None:
        _channel3_service_instance = Channel3Service()
    return _channel3_service_instance

