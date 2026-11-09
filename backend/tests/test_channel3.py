"""Tests for Channel3 Live Multi-Merchant Product Discovery and Comparison."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.channel3.client import Channel3Client, Channel3Config, Channel3Product
from app.services.channel3.service import Channel3Service

client = TestClient(app)


def test_channel3_config():
    """Verify default Channel3 configuration and environment loading."""
    cfg = Channel3Config()
    assert cfg.base_url == "https://api.trychannel3.com"
    assert cfg.timeout == 10.0
    assert cfg.cache_ttl >= 60
    assert cfg.mock_fallback_enabled is True


def test_channel3_normalization_and_variants():
    """Verify Channel3Client correctly normalizes raw JSON payloads and variant lists."""
    c3_client = Channel3Client()
    raw_payload = {
        "id": "c3_item_999",
        "title": "Bose QuietComfort 45",
        "brand": "Bose",
        "price": 279.00,
        "retailer": "Best Buy",
        "availability": "IN_STOCK",
        "category": "audio",
        "image_url": "https://example.com/bose.jpg",
        "source_url": "https://bestbuy.com/p/bose-qc45",
        "variants": [
            {"id": "v1", "title": "Triple Black", "price": 279.00, "available": True},
            {"id": "v2", "title": "White Smoke", "price": 299.00, "available": False},
        ],
        "attributes": {"battery_hours": 24.0, "noise_cancelling": True},
    }

    product = c3_client.normalize(raw_payload)
    assert isinstance(product, Channel3Product)
    assert product.id == "c3_item_999"
    assert product.title == "Bose QuietComfort 45"
    assert product.brand == "Bose"
    assert product.price == 279.00
    assert product.retailer == "Best Buy"
    assert len(product.variants) == 2
    assert product.variants[0].title == "Triple Black"
    assert product.variants[1].available is False
    assert product.attributes["noise_cancelling"] is True


def test_channel3_search_with_constraints():
    """Verify Channel3 search filters by price, category, and keyword."""
    service = Channel3Service()

    # Search laptops under $1500
    laptops = service.search(query="laptop", category="laptop", max_price=1500.0)
    assert len(laptops) > 0
    assert all(p.category == "laptop" for p in laptops)
    assert all(p.price <= 1500.0 for p in laptops)
    assert all(p.source == "CHANNEL3" for p in laptops)

    # Search audio headphones under $400
    headphones = service.search(query="headphones", category="audio", max_price=400.0)
    assert len(headphones) > 0
    assert any("sony" in p.name.lower() or "bose" in p.name.lower() for p in headphones)


def test_channel3_caching():
    """Verify in-memory caching prevents redundant external API invocations."""
    c3_client = Channel3Client()
    q = "sony headphones"

    # First invocation seeds cache
    res1 = c3_client.search(query=q)
    # Second invocation should retrieve from cache
    res2 = c3_client.search(query=q)

    assert len(res1) == len(res2)
    assert [p.id for p in res1] == [p.id for p in res2]


def test_channel3_multi_product_comparison():
    """Verify multi-factor trade-off comparison matrix across candidate products."""
    service = Channel3Service()
    comparison = service.compare([
        "c3_prod_sony_wh1000xm5",
        "c3_prod_bose_quietcomfort_ultra",
    ])

    assert "total_compared" in comparison
    assert comparison["total_compared"] == 2
    assert "lowest_price_item" in comparison
    assert "highest_rated_item" in comparison
    assert "fastest_delivery_item" in comparison
    assert len(comparison["products"]) == 2
    # Sony WH-1000XM5 ($348) is cheaper than Bose Ultra ($379)
    assert comparison["lowest_price_item"]["price"] == 348.00


def test_channel3_api_endpoints():
    """Test FastAPI /api/channel3 endpoints."""
    # 1. Search endpoint
    search_res = client.post(
        "/api/channel3/search",
        json={"query": "macbook", "category": "laptop", "max_price": 1300.0},
    )
    assert search_res.status_code == 200
    items = search_res.json()
    assert len(items) > 0
    assert items[0]["brand"] == "Apple"
    assert items[0]["source"] == "CHANNEL3"

    # 2. Product lookup endpoint
    prod_res = client.get("/api/channel3/product/c3_prod_sony_wh1000xm5")
    assert prod_res.status_code == 200
    assert prod_res.json()["name"].startswith("Sony")

    # 3. Compare endpoint
    compare_res = client.post(
        "/api/channel3/compare",
        json={"product_ids": ["c3_prod_sony_wh1000xm5", "c3_prod_bose_quietcomfort_ultra"]},
    )
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert comp_data["total_compared"] == 2

