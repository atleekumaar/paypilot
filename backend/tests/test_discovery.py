"""Comprehensive test suite for Phase 2 Product Discovery Agent."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.product_repository import DemoProductRepository
from app.schemas.intent import ProductSearchIntent
from app.schemas.product import Product
from app.services.intent_service import IntentService
from app.services.ranking_service import ProductRankingService
from app.services.recommendation_service import RecommendationService
from app.services.search_service import ProductSearchService

client = TestClient(app)


@pytest.fixture
def repo():
    return DemoProductRepository()


@pytest.fixture
def search_service(repo):
    return ProductSearchService(repository=repo)


@pytest.fixture
def ranking_service():
    return ProductRankingService()


@pytest.fixture
def intent_service():
    return IntentService()


@pytest.fixture
def recommendation_service(intent_service, search_service, ranking_service):
    return RecommendationService(
        intent_service=intent_service,
        search_service=search_service,
        ranking_service=ranking_service,
    )


# 1. Product Model Test
def test_product_model():
    sample = {
        "id": "LAP-999",
        "name": "Test Laptop",
        "brand": "TestBrand",
        "category": "laptop",
        "description": "High performance unit",
        "price": 999.0,
        "currency": "USD",
        "rating": 4.5,
        "review_count": 100,
        "stock": True,
        "seller": "Test Seller",
        "delivery_days": 3,
        "features": {"ram_gb": 16, "gpu": "RTX 4060"},
    }
    prod = Product.model_validate(sample)
    assert prod.id == "LAP-999"
    assert prod.price == 999.0
    assert prod.features["ram_gb"] == 16


# 2. Product Search Test
def test_product_search(search_service):
    results = search_service.search_products(category="laptop", max_price=1200)
    assert len(results) > 0
    for p in results:
        assert p.category == "laptop"
        assert p.price <= 1200


# 3. Budget Filter Test (CRITICAL: Product above budget must NEVER appear)
def test_budget_filter(search_service):
    max_budget = 1100.0
    results = search_service.search_products(max_price=max_budget)
    for p in results:
        assert p.price <= max_budget, f"Product {p.id} with price {p.price} exceeded max budget {max_budget}"


# 4. Category Filter Test
def test_category_filter(search_service):
    results = search_service.search_products(category="headphones")
    assert len(results) > 0
    for p in results:
        assert p.category == "headphones"


# 5. Stock Filter Test (CRITICAL: Out-of-stock product must NEVER be recommended)
def test_stock_filter(search_service):
    results = search_service.search_products(in_stock_only=True)
    for p in results:
        assert p.stock is True, f"Out of stock product {p.id} was returned"


# 6. Ranking Test (CRITICAL: Ranking must be deterministic for identical input)
def test_ranking(ranking_service, search_service, intent_service):
    intent = intent_service.extract_intent("laptop under 1200 for AI development")
    products = search_service.search_products(
        category=intent.hard_constraints.category,
        max_price=intent.hard_constraints.max_price,
    )

    run_1 = ranking_service.rank_products(products, intent)
    run_2 = ranking_service.rank_products(products, intent)

    assert len(run_1) == len(run_2)
    for p1, p2 in zip(run_1, run_2):
        assert p1.product_id == p2.product_id
        assert p1.score == p2.score
        assert p1.rank == p2.rank


# 7. Intent Schema Test
def test_intent_schema(intent_service):
    intent = intent_service.extract_intent(
        "Find me a laptop under 1200 for AI development with good battery life."
    )
    assert isinstance(intent, ProductSearchIntent)
    assert intent.category == "laptop"
    assert intent.hard_constraints.max_price == 1200.0
    assert "good battery life" in intent.requirements
    assert intent.hard_constraints.in_stock is True


# 8. Empty Query Test
def test_empty_query(recommendation_service):
    response = recommendation_service.discover_products("")
    assert response.total_candidates == 0
    assert len(response.recommendations) == 0
    assert "Please describe" in response.explanation


# 9. No Results Test
def test_no_results(recommendation_service):
    # Search for an impossible budget constraint
    response = recommendation_service.discover_products("laptop under 50 dollars")
    assert response.total_candidates == 0
    assert len(response.recommendations) == 0
    assert "couldn't find products" in response.explanation


# 10. Recommendation Endpoint Integration Test
def test_recommendation_endpoint():
    payload = {
        "query": "Find me a laptop under 1200 for AI development with good battery life."
    }
    response = client.post("/api/discovery/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["query"] == payload["query"]
    assert len(data["recommendations"]) <= 3
    assert len(data["recommendations"]) > 0

    top_pick = data["recommendations"][0]
    assert top_pick["rank"] == 1
    assert top_pick["score"] > 0
    assert top_pick["product"]["price"] <= 1200
    assert top_pick["product"]["stock"] is True
    assert "Why it fits:" in data["explanation"]


# 11. Catalogue Products List Endpoint Test
def test_products_list_endpoint():
    response = client.get("/api/products?category=phone&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    for item in data["items"]:
        assert item["category"] == "phone"


# 12. Single Product Detail Endpoint Test
def test_single_product_endpoint():
    response = client.get("/api/products/LAP-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "LAP-001"
    assert data["name"] == "NovaBook Pro 14"

    # Not found case
    not_found = client.get("/api/products/NON-EXISTENT-SKU")
    assert not_found.status_code == 404
