"""Deterministic recommendation benchmark suite testing multi-attribute ranking scenarios."""

import pytest
from app.schemas.intent import HardConstraints, ProductSearchIntent
from app.schemas.product import Product
from app.services.ranking_service import ProductRankingService


@pytest.fixture
def ranking_service():
    return ProductRankingService()


def _make_sample_product(
    id: str,
    name: str = "Test Laptop",
    price: float = 999.0,
    rating: float = 4.5,
    review_count: int = 100,
    delivery_days: int = 3,
    seller: str = "Official Store",
    features: dict = None,
    stock: bool = True,
) -> Product:
    return Product(
        id=id,
        name=name,
        category="laptop",
        brand="TechCorp",
        price=price,
        rating=rating,
        review_count=review_count,
        stock=stock,
        delivery_days=delivery_days,
        seller=seller,
        features=features or {},
        tags=["laptop"],
        description="Benchmark test product description",
    )


def test_scenario_1_exact_requirement_match(ranking_service):
    """Scenario 1: Exact hardware requirement match (RTX GPU + 32GB RAM) receives highest score."""
    p_exact = _make_sample_product(
        id="P-EXACT",
        name="NovaBook RTX Pro",
        price=1200.0,
        features={"gpu": "NVIDIA RTX 4080", "ram_gb": 32, "battery_hours": 12.0},
    )
    p_baseline = _make_sample_product(
        id="P-BASE",
        name="Standard Office Laptop",
        price=1200.0,
        features={"gpu": "Integrated Intel UHD", "ram_gb": 8, "battery_hours": 6.0},
    )

    intent = ProductSearchIntent(
        raw_query="laptop with RTX GPU and 32GB RAM for local AI",
        category="laptop",
        hard_constraints=HardConstraints(max_price=1500.0),
        normalized_features={"gpu_required": True, "ram_gb_min": 32, "battery_hours_min": 10.0},
    )

    ranked = ranking_service.rank_products([p_baseline, p_exact], intent)
    assert ranked[0].product_id == "P-EXACT"
    assert ranked[0].breakdown.requirement_match > ranked[1].breakdown.requirement_match
    assert any("RTX" in r for r in ranked[0].match_reasons)


def test_scenario_2_budget_constraint(ranking_service):
    """Scenario 2: Hard budget ceiling strictly penalizes products over budget."""
    p_within_budget = _make_sample_product(id="P-UNDER", price=899.0)
    p_over_budget = _make_sample_product(id="P-OVER", price=1150.0)

    intent = ProductSearchIntent(
        raw_query="budget laptop under 1000",
        category="laptop",
        hard_constraints=HardConstraints(max_price=1000.0),
    )

    ranked = ranking_service.rank_products([p_over_budget, p_within_budget], intent)
    assert ranked[0].product_id == "P-UNDER"
    assert ranked[0].breakdown.price_fit >= 85.0
    assert ranked[1].breakdown.price_fit == 0.0


def test_scenario_3_seller_reputation_vs_price(ranking_service):
    """Scenario 3: Authorized/Official store receives higher seller reliability score."""
    p_official = _make_sample_product(id="P-OFFICIAL", seller="Nova Official Store", price=1000.0)
    p_third_party = _make_sample_product(id="P-UNVERIFIED", seller="RandomReseller_99", price=1000.0)

    intent = ProductSearchIntent(raw_query="laptop", category="laptop")

    ranked = ranking_service.rank_products([p_third_party, p_official], intent)
    assert ranked[0].product_id == "P-OFFICIAL"
    assert ranked[0].breakdown.seller_score == 98.0
    assert ranked[1].breakdown.seller_score == 82.0


def test_scenario_4_fast_delivery_preference(ranking_service):
    """Scenario 4: Fast delivery (1-2 days) scores higher than prolonged delivery (7 days)."""
    p_fast = _make_sample_product(id="P-FAST", delivery_days=1)
    p_slow = _make_sample_product(id="P-SLOW", delivery_days=7)

    intent = ProductSearchIntent(raw_query="laptop urgent", category="laptop")

    ranked = ranking_service.rank_products([p_slow, p_fast], intent)
    assert ranked[0].product_id == "P-FAST"
    assert ranked[0].breakdown.delivery_score == 100.0
    assert ranked[1].breakdown.delivery_score == 40.0


def test_scenario_5_missing_attribute_handling(ranking_service):
    """Scenario 5: Products with empty or missing features dictionary score gracefully without crash."""
    p_empty_features = _make_sample_product(id="P-EMPTY", features={})
    p_partial_features = _make_sample_product(
        id="P-PARTIAL",
        features={"gpu": None, "ram_gb": None, "battery_hours": None},
    )

    intent = ProductSearchIntent(
        raw_query="laptop",
        category="laptop",
        normalized_features={"ram_gb_min": 16, "gpu_required": True},
    )

    ranked = ranking_service.rank_products([p_empty_features, p_partial_features], intent)
    assert len(ranked) == 2
    assert ranked[0].score >= 0.0
    assert ranked[1].score >= 0.0


def test_scenario_6_deterministic_tie_breaking(ranking_service):
    """Scenario 6: Identical scores tie-break deterministically by rating then review count."""
    p1 = _make_sample_product(id="P-1", rating=4.8, review_count=500)
    p2 = _make_sample_product(id="P-2", rating=4.8, review_count=200)
    p3 = _make_sample_product(id="P-3", rating=4.5, review_count=1000)

    intent = ProductSearchIntent(raw_query="laptop", category="laptop")

    ranked = ranking_service.rank_products([p3, p2, p1], intent)
    # p1 and p2 have higher rating (4.8 > 4.5). Between p1 and p2, p1 has 500 reviews > 200.
    assert ranked[0].product_id == "P-1"
    assert ranked[1].product_id == "P-2"
    assert ranked[2].product_id == "P-3"
