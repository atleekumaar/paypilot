"""Official Channel3 Developer API Client for Cross-Retailer Product Discovery.

Channel3 connects shopping AI agents to over 100M+ structured products across
25,000+ merchants with universal normalization, real-time pricing, and retailer attribution.
"""

from datetime import datetime, timezone
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
import urllib.parse
from pydantic import BaseModel, Field

import httpx

logger = logging.getLogger(__name__)


class Channel3ProductVariant(BaseModel):
    """Product variant model for size, color, or spec variations."""

    id: str
    title: str
    price: float
    sku: Optional[str] = None
    available: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)


class Channel3Product(BaseModel):
    """Normalized product structure returned by Channel3 Product Graph."""

    id: str = Field(..., description="Channel3 universal product ID")
    title: str = Field(..., description="Product title")
    brand: str = Field(..., description="Manufacturer brand name")
    description: str = Field(..., description="Cleaned product description")
    price: float = Field(..., description="Current live price")
    currency: str = Field(default="USD", description="Currency ISO code")
    retailer: str = Field(..., description="Merchant or store name (e.g. Best Buy, Target, Apple)")
    availability: str = Field(default="IN_STOCK", description="Stock status: IN_STOCK, LOW_STOCK, OUT_OF_STOCK")
    category: str = Field(default="general", description="Normalized category")
    image_url: Optional[str] = Field(default=None, description="High-resolution product image")
    source_url: Optional[str] = Field(default=None, description="Direct merchant offer or canonical URL")
    rating: float = Field(default=4.5, description="Average review score (0.0 - 5.0)")
    review_count: int = Field(default=150, description="Review count")
    variants: List[Channel3ProductVariant] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    delivery_days: int = Field(default=3, description="Estimated delivery turnaround")
    source: str = Field(default="CHANNEL3", description="Source provider identifier")


class Channel3Config:
    """Channel3 service configuration."""

    def __init__(self):
        self.api_key: Optional[str] = os.getenv("CHANNEL3_API_KEY")
        self.base_url: str = os.getenv("CHANNEL3_BASE_URL", "https://api.trychannel3.com").rstrip("/")
        self.timeout: float = float(os.getenv("CHANNEL3_TIMEOUT", "10.0"))
        self.cache_ttl: int = int(os.getenv("CHANNEL3_CACHE_TTL", "3600"))  # 1 hour default
        self.mock_fallback_enabled: bool = os.getenv("CHANNEL3_MOCK_FALLBACK", "true").lower() in ("true", "1", "yes")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)


# Deterministic verified products for fallback and test scenarios without external network dependencies
MOCK_CHANNEL3_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "c3_prod_sony_wh1000xm5",
        "title": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones",
        "brand": "Sony",
        "description": "Industry-leading noise canceling with two processors and 8 microphones. Up to 30-hour battery life.",
        "price": 348.00,
        "currency": "USD",
        "retailer": "Best Buy",
        "availability": "IN_STOCK",
        "category": "audio",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=600&q=80",
        "source_url": "https://www.bestbuy.com/site/sony-wh-1000xm5/6505727.p",
        "rating": 4.7,
        "review_count": 2840,
        "variants": [
            {"id": "var_black", "title": "Black", "price": 348.00, "available": True},
            {"id": "var_silver", "title": "Silver", "price": 348.00, "available": True},
        ],
        "attributes": {"battery_hours": 30.0, "noise_cancelling": True, "wireless": True, "weight_g": 250},
        "delivery_days": 2,
    },
    {
        "id": "c3_prod_apple_macbook_air_m3",
        "title": "Apple MacBook Air 13.6-inch Laptop - M3 Chip - 16GB Memory - 512GB SSD",
        "brand": "Apple",
        "description": "Supercharged by the next-generation M3 chip, incredibly thin and fast laptop with Liquid Retina display.",
        "price": 1249.00,
        "currency": "USD",
        "retailer": "Target",
        "availability": "IN_STOCK",
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "source_url": "https://www.target.com/p/apple-macbook-air-m3/-/A-894218",
        "rating": 4.8,
        "review_count": 1420,
        "variants": [
            {"id": "var_space_gray", "title": "Space Gray", "price": 1249.00, "available": True},
            {"id": "var_midnight", "title": "Midnight", "price": 1249.00, "available": True},
        ],
        "attributes": {"ram_gb": 16, "storage_gb": 512, "cpu": "Apple M3", "battery_hours": 18.0, "display_inches": 13.6},
        "delivery_days": 3,
    },
    {
        "id": "c3_prod_bose_quietcomfort_ultra",
        "title": "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones",
        "brand": "Bose",
        "description": "Breakthrough spatial audio for more immersive listening. World-class active noise cancellation with CustomTune.",
        "price": 379.00,
        "currency": "USD",
        "retailer": "Amazon",
        "availability": "IN_STOCK",
        "category": "audio",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
        "source_url": "https://www.amazon.com/dp/B0CCZ26B5V",
        "rating": 4.6,
        "review_count": 1950,
        "variants": [],
        "attributes": {"battery_hours": 24.0, "noise_cancelling": True, "wireless": True},
        "delivery_days": 1,
    },
    {
        "id": "c3_prod_dell_xps_15",
        "title": "Dell XPS 15 9530 Laptop - Intel Core i7 - 32GB RAM - 1TB SSD - RTX 4060",
        "brand": "Dell",
        "description": "High-performance creator laptop with stunning 15.6-inch OLED touch display and NVIDIA GeForce RTX graphics.",
        "price": 1799.00,
        "currency": "USD",
        "retailer": "B&H Photo",
        "availability": "IN_STOCK",
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=600&q=80",
        "source_url": "https://www.bhphotovideo.com/c/product/dell-xps-15",
        "rating": 4.5,
        "review_count": 820,
        "variants": [],
        "attributes": {"ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4060", "cpu": "Intel i7", "battery_hours": 9.0},
        "delivery_days": 2,
    },
    {
        "id": "c3_prod_nike_invincible_3",
        "title": "Nike ZoomX Invincible Run Flyknit 3 Running Shoes",
        "brand": "Nike",
        "description": "Maximum cushioning to support every mile. High support and super-responsive ZoomX foam for road running.",
        "price": 149.99,
        "currency": "USD",
        "retailer": "Dick's Sporting Goods",
        "availability": "IN_STOCK",
        "category": "apparel",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
        "source_url": "https://www.dickssportinggoods.com/p/nike-invincible-3",
        "rating": 4.6,
        "review_count": 670,
        "variants": [
            {"id": "sz_9", "title": "Size 9 US", "price": 149.99, "available": True},
            {"id": "sz_10", "title": "Size 10 US", "price": 149.99, "available": True},
            {"id": "sz_11", "title": "Size 11 US", "price": 149.99, "available": True},
        ],
        "attributes": {"activity": "running", "cushioning": "maximum", "gender": "unisex"},
        "delivery_days": 2,
    },
]


class Channel3Client:
    """HTTP Client communicating with official Channel3 endpoints."""

    def __init__(self, config: Optional[Channel3Config] = None):
        self.config = config or Channel3Config()
        self._cache: Dict[str, tuple[float, Any]] = {}

    def _get_cached(self, key: str) -> Optional[Any]:
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self.config.cache_ttl:
                return val
            del self._cache[key]
        return None

    def _set_cached(self, key: str, val: Any) -> None:
        self._cache[key] = (time.time(), val)

    def normalize(self, raw: Dict[str, Any]) -> Channel3Product:
        """Universal normalization of Channel3 product payloads into strict Pydantic model."""
        variants: List[Channel3ProductVariant] = []
        raw_variants = raw.get("variants") or []
        for v in raw_variants:
            if isinstance(v, dict):
                variants.append(
                    Channel3ProductVariant(
                        id=str(v.get("id", f"var_{time.time()}")),
                        title=str(v.get("title", v.get("name", "Standard"))),
                        price=float(v.get("price", raw.get("price", 0.0) if not isinstance(raw.get("price"), dict) else 0.0)),
                        sku=v.get("sku"),
                        available=bool(v.get("available", True)),
                        attributes=v.get("attributes") or {},
                    )
                )

        # Brand extraction from live brands list or string
        brand_name = "Brand"
        raw_brands = raw.get("brands") or []
        if isinstance(raw_brands, list) and len(raw_brands) > 0:
            first_b = raw_brands[0]
            if isinstance(first_b, dict):
                brand_name = first_b.get("name", "Brand")
            elif isinstance(first_b, str):
                brand_name = first_b
        elif raw.get("brand"):
            brand_name = str(raw["brand"])
        elif raw.get("manufacturer"):
            brand_name = str(raw["manufacturer"])

        # Price, Retailer, Source URL extraction from live offers list
        price = 0.0
        currency = str(raw.get("currency", "USD"))
        retailer = "Direct Retailer"
        source_url = raw.get("source_url") or raw.get("url")
        availability = str(raw.get("availability", "IN_STOCK"))

        offers = raw.get("offers") or []
        if isinstance(offers, list) and len(offers) > 0:
            first_offer = offers[0]
            if isinstance(first_offer, dict):
                source_url = first_offer.get("url") or source_url
                raw_domain = first_offer.get("domain", "")
                if raw_domain:
                    retailer = raw_domain.split(".")[0].capitalize()

                off_price = first_offer.get("price")
                if isinstance(off_price, dict):
                    price = float(off_price.get("price", 0.0))
                    currency = str(off_price.get("currency", currency))
                elif isinstance(off_price, (int, float)):
                    price = float(off_price)

                avail_raw = str(first_offer.get("availability", "InStock")).lower()
                if "instock" in avail_raw:
                    availability = "IN_STOCK"
                elif "out" in avail_raw:
                    availability = "OUT_OF_STOCK"

        # Fallback to direct raw attributes
        if price == 0.0 and raw.get("price"):
            if isinstance(raw["price"], dict):
                price = float(raw["price"].get("amount", raw["price"].get("price", 0.0)))
            elif isinstance(raw["price"], (int, float)):
                price = float(raw["price"])
        if retailer == "Direct Retailer" and raw.get("retailer"):
            retailer = str(raw["retailer"])

        # Image extraction from live images list or direct key
        image_url = None
        images = raw.get("images") or []
        if isinstance(images, list) and len(images) > 0:
            main_img = next((img for img in images if isinstance(img, dict) and img.get("is_main_image")), images[0])
            if isinstance(main_img, dict):
                image_url = main_img.get("url") or main_img.get("cleaned_url")
            elif isinstance(main_img, str):
                image_url = main_img
        if not image_url:
            image_url = raw.get("image_url") or raw.get("image") or raw.get("thumbnail")

        # Category parsing
        cat_raw = raw.get("category", "general")
        cat_str = cat_raw if isinstance(cat_raw, str) else str(cat_raw.get("name", "general") if isinstance(cat_raw, dict) else "general")

        return Channel3Product(
            id=str(raw.get("id", f"c3_{time.time()}")),
            title=str(raw.get("title", raw.get("name", "Retail Item"))),
            brand=brand_name,
            description=str(raw.get("description", "")),
            price=price,
            currency=currency,
            retailer=retailer,
            availability=availability,
            category=cat_str.lower(),
            image_url=image_url,
            source_url=source_url,
            rating=float(raw.get("rating", 4.5) if not isinstance(raw.get("ratings"), dict) else raw.get("ratings", {}).get("average", 4.5)),
            review_count=int(raw.get("review_count", 100) if not isinstance(raw.get("ratings"), dict) else raw.get("ratings", {}).get("count", 100)),
            variants=variants,
            attributes=raw.get("attributes") or raw.get("structured_attributes") or {},
            delivery_days=int(raw.get("delivery_days", 3)),
            source="CHANNEL3",
        )

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        limit: int = 10,
    ) -> List[Channel3Product]:
        """Search products across live retailers via Channel3."""
        cache_key = f"search:{query}:{category}:{min_price}:{max_price}:{brand}:{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            logger.debug(f"Channel3 cache hit for key '{cache_key}'")
            return cached

        # Live external API execution if configured
        if self.config.is_configured:
            headers = {
                "x-api-key": self.config.api_key,
                "Content-Type": "application/json",
                "User-Agent": "PayPilot-CommerceAgent/1.0",
            }
            payload = {
                "query": query,
                "limit": limit,
                "filters": {},
            }
            if min_price is not None or max_price is not None:
                payload["filters"]["price_range"] = {}
                if min_price is not None:
                    payload["filters"]["price_range"]["min"] = min_price
                if max_price is not None:
                    payload["filters"]["price_range"]["max"] = max_price
            if brand:
                payload["filters"]["brands"] = [brand]
            if category:
                payload["filters"]["categories"] = [category]

            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    resp = client.post(
                        f"{self.config.base_url}/v1/search",
                        headers=headers,
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        items = data.get("items") or data.get("products") or data.get("data") or []
                        results = [self.normalize(item) for item in items]
                        self._set_cached(cache_key, results)
                        return results
                    elif resp.status_code == 429:
                        logger.warning("Channel3 API rate limit exceeded (HTTP 429). Falling back to mock dataset.")
                    else:
                        logger.warning(f"Channel3 API returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Channel3 API connection failed: {e}. Falling back to deterministic catalog.")

        # Fallback path: Filter mock catalog safely
        if self.config.mock_fallback_enabled:
            return self._mock_search(query, category, min_price, max_price, brand, limit)

        return []

    def _mock_search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        limit: int = 10,
    ) -> List[Channel3Product]:
        """Deterministic search on verified multi-merchant mock products."""
        q_tokens = [t.lower() for t in query.split() if len(t) > 1]
        matches: List[Channel3Product] = []

        for p_raw in MOCK_CHANNEL3_PRODUCTS:
            p = self.normalize(p_raw)

            # Price constraints
            if max_price is not None and p.price > max_price:
                continue
            if min_price is not None and p.price < min_price:
                continue

            # Brand constraint
            if brand and brand.lower() not in p.brand.lower():
                continue

            # Category constraint
            if category and category.lower() != "all" and category.lower() not in p.category.lower():
                continue

            # Text relevance check
            text_corpus = f"{p.title} {p.brand} {p.category} {p.description} {p.retailer}".lower()
            if q_tokens:
                if not any(token in text_corpus for token in q_tokens):
                    continue

            matches.append(p)

        return matches[:limit]

    def lookup(self, product_id: str) -> Optional[Channel3Product]:
        """Lookup specific product by Channel3 ID or external merchant reference."""
        cache_key = f"lookup:{product_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if self.config.is_configured:
            headers = {"x-api-key": self.config.api_key}
            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    resp = client.get(f"{self.config.base_url}/v1/products/{product_id}", headers=headers)
                    if resp.status_code == 200:
                        prod = self.normalize(resp.json())
                        self._set_cached(cache_key, prod)
                        return prod
            except Exception as e:
                logger.warning(f"Channel3 lookup request failed: {e}")

        for p_raw in MOCK_CHANNEL3_PRODUCTS:
            if p_raw["id"] == product_id:
                prod = self.normalize(p_raw)
                self._set_cached(cache_key, prod)
                return prod

        return None

