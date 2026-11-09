"""Elasticsearch Commerce Service providing intelligent indexing and hybrid retrieval."""

import logging
from typing import Any, Dict, List, Optional

from app.repositories.product_repository import ProductRepository, get_product_repository
from app.schemas.product import Product
from app.services.elastic.client import ElasticConfig, ElasticsearchClient

logger = logging.getLogger(__name__)


class ElasticCommerceService:
    """Unified service for product catalog indexing, vector retrieval, and merchant grounding."""

    def __init__(
        self,
        client: Optional[ElasticsearchClient] = None,
        product_repo: Optional[ProductRepository] = None,
    ):
        self.client = client or ElasticsearchClient()
        self._product_repo = product_repo or get_product_repository()
        self._initialized = False

    def sync_from_repository(self) -> int:
        """Seed Elasticsearch index with all products from database repository."""
        if hasattr(self._product_repo, "list_all"):
            products = self._product_repo.list_all()
        elif hasattr(self._product_repo, "list_products"):
            products = self._product_repo.list_products(limit=10000)
        else:
            products = []
        indexed_count = 0
        for p in products:
            doc = {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "rating": p.rating,
                "review_count": p.review_count,
                "stock": p.stock,
                "seller": p.seller,
                "delivery_days": p.delivery_days,
                "features": p.features,
                "image_url": p.image_url,
                "source": getattr(p, "source", "CATALOG"),
            }
            if self.client.index_document(self.client.config.product_index, p.id, doc):
                indexed_count += 1

        # Also seed merchant policies into knowledge index
        self._seed_merchant_knowledge()
        self._initialized = True
        logger.info(f"Elasticsearch: Synced {indexed_count} products and merchant knowledge.")
        return indexed_count

    def _seed_merchant_knowledge(self) -> None:
        """Index merchant policies, warranties, and shipping standards for Groq context grounding."""
        knowledge_docs = [
            {
                "id": "policy_paypal_purchase_protection",
                "title": "PayPal Buyer Protection Policy",
                "content": "All purchases executed through PayPilot are covered under PayPal Buyer Protection. If an eligible item doesn't arrive or doesn't match the description, PayPal refunds the full purchase price plus original shipping costs.",
                "category": "payment_policy",
            },
            {
                "id": "policy_standard_shipping",
                "title": "Standard Shipping and Logistics SLA",
                "content": "Orders placed with FastShip Logistics arrive within 2-4 business days. Regional distribution centers in Ohio and California dispatch packages within 24 hours of PayPal authorization.",
                "category": "shipping_policy",
            },
            {
                "id": "policy_hardware_warranty",
                "title": "Electronics and Laptop Warranty Terms",
                "content": "NovaTech, Dell, and Apple products include a minimum 1-year manufacturer limited hardware warranty covering manufacturing defects and hardware component failures.",
                "category": "warranty_policy",
            },
        ]
        for doc in knowledge_docs:
            self.client.index_document(self.client.config.knowledge_index, doc["id"], doc)

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.sync_from_repository()

    def index_product(self, product: Product) -> bool:
        """Index a single product into Elasticsearch."""
        doc = product.model_dump()
        return self.client.index_document(self.client.config.product_index, product.id, doc)

    def delete_product(self, product_id: str) -> bool:
        """Remove product from Elasticsearch."""
        return self.client.delete_document(self.client.config.product_index, product_id)

    def keyword_search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Execute BM25 keyword query."""
        self._ensure_initialized()
        filters = {}
        if category and category.lower() != "all":
            filters["category"] = category
        if max_price is not None:
            filters["max_price"] = max_price
        if min_price is not None:
            filters["min_price"] = min_price

        return self.client.search_keyword(self.client.config.product_index, query, filters=filters, limit=limit)

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Execute dense vector semantic similarity search."""
        self._ensure_initialized()
        return self.client.search_vector(self.client.config.product_index, query, top_k=top_k)

    def hybrid_search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search combining BM25 keyword and dense vector semantic similarity."""
        self._ensure_initialized()
        filters = {}
        if category and category.lower() != "all":
            filters["category"] = category
        if max_price is not None:
            filters["max_price"] = max_price
        if min_price is not None:
            filters["min_price"] = min_price

        return self.client.search_hybrid(self.client.config.product_index, query, filters=filters, limit=limit)

    def search_knowledge(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant merchant policies or specs to ground Groq LLM responses."""
        self._ensure_initialized()
        return self.client.search_hybrid(self.client.config.knowledge_index, query, limit=limit)

    def health(self) -> Dict[str, Any]:
        """Health check endpoint for Elasticsearch cluster or local fallback."""
        self._ensure_initialized()
        return self.client.health()


_elastic_service_instance: Optional[ElasticCommerceService] = None


def get_elastic_service() -> ElasticCommerceService:
    global _elastic_service_instance
    if _elastic_service_instance is None:
        _elastic_service_instance = ElasticCommerceService()
    return _elastic_service_instance
