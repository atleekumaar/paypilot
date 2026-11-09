"""Tests for Elasticsearch Indexing, Dense Vector Semantic Search, and Hybrid Retrieval."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.product import Product
from app.services.elastic.client import ElasticConfig, ElasticsearchClient
from app.services.elastic.service import ElasticCommerceService

client = TestClient(app)


def test_elastic_config():
    """Verify default Elasticsearch configuration."""
    cfg = ElasticConfig()
    assert cfg.product_index == "paypilot_products"
    assert cfg.knowledge_index == "paypilot_knowledge"
    assert cfg.timeout >= 1.0


def test_elastic_health_and_fallback():
    """Verify health check returns active status in both cluster and local fallback modes."""
    service = ElasticCommerceService()
    health = service.health()

    assert "status" in health
    assert "mode" in health
    assert "indices" in health
    assert len(health["indices"]) >= 2


def test_elastic_sync_and_indexing():
    """Verify syncing database products into Elasticsearch product index."""
    service = ElasticCommerceService()
    count = service.sync_from_repository()
    assert count > 0

    # Index custom product
    test_prod = Product(
        id="ELAST-TEST-001",
        name="UltraSpeed AI Accelerator Unit",
        brand="TensorForge",
        category="hardware",
        description="High-speed PCI-e coprocessor for local LLM inference.",
        price=899.00,
        currency="USD",
        rating=4.9,
        review_count=120,
        stock=True,
        seller="TensorForge Direct",
        delivery_days=2,
        source="ELASTIC",
    )
    ok = service.index_product(test_prod)
    assert ok is True

    # Clean up
    deleted = service.delete_product("ELAST-TEST-001")
    assert deleted is True


def test_elastic_keyword_search():
    """Verify BM25 keyword matching with category and price filters."""
    service = ElasticCommerceService()
    service.sync_from_repository()

    # Search for laptop
    hits = service.keyword_search(query="laptop", category="laptop")
    assert len(hits) > 0
    assert any("laptop" in h.get("category", "").lower() for h in hits)

    # Search with budget cap
    budget_hits = service.keyword_search(query="laptop", max_price=1200.0)
    assert all(h.get("price", 0.0) <= 1200.0 for h in budget_hits)


def test_elastic_vector_semantic_search():
    """Verify dense vector kNN semantic similarity search."""
    service = ElasticCommerceService()
    service.sync_from_repository()

    results = service.semantic_search(query="powerful portable workstation for coding", top_k=3)
    assert len(results) > 0
    assert "id" in results[0]
    assert "name" in results[0]


def test_elastic_hybrid_rrf_search():
    """Verify Reciprocal Rank Fusion hybrid retrieval combining keyword and semantic scores."""
    service = ElasticCommerceService()
    service.sync_from_repository()

    hybrid_hits = service.hybrid_search(
        query="gaming high refresh rate display",
        category="laptop",
        limit=3,
    )
    assert len(hybrid_hits) > 0
    assert len(hybrid_hits) <= 3


def test_elastic_merchant_knowledge_retrieval():
    """Verify retrieval of buyer protection, warranty, and shipping policies."""
    service = ElasticCommerceService()
    service.sync_from_repository()

    policies = service.search_knowledge(query="buyer protection refund guarantee", limit=2)
    assert len(policies) > 0
    policy_titles = [p.get("title", "") for p in policies]
    assert any("PayPal Buyer Protection" in t for t in policy_titles)


def test_elastic_api_endpoints():
    """Test FastAPI /api/elastic endpoints."""
    # 1. Health endpoint
    h_res = client.get("/api/elastic/health")
    assert h_res.status_code == 200
    assert "status" in h_res.json()

    # 2. Sync endpoint
    s_res = client.post("/api/elastic/sync")
    assert s_res.status_code == 200
    assert s_res.json()["status"] == "synced"

    # 3. Hybrid search endpoint
    search_res = client.post(
        "/api/elastic/search",
        json={"query": "laptop", "mode": "hybrid", "max_price": 2000.0},
    )
    assert search_res.status_code == 200
    hits = search_res.json()
    assert len(hits) > 0

    # 4. Knowledge endpoint
    k_res = client.post(
        "/api/elastic/knowledge",
        json={"query": "warranty", "limit": 2},
    )
    assert k_res.status_code == 200
    docs = k_res.json()
    assert len(docs) > 0

