"""Unit tests for offline recommendation evaluation metrics (NDCG, Precision, Recall)."""

import pytest
from app.services.recommendation_evaluator import (
    RecommendationEvaluator,
    compute_dcg,
    compute_ndcg_at_k,
    compute_precision_at_k,
    compute_recall_at_k,
)


def test_ndcg_at_k_perfect_ranking():
    ground_truth = {"prod-1": 3.0, "prod-2": 2.0, "prod-3": 1.0}
    retrieved = ["prod-1", "prod-2", "prod-3"]

    score = compute_ndcg_at_k(retrieved, ground_truth, k=3)
    assert score == 1.0


def test_ndcg_at_k_suboptimal_ranking():
    ground_truth = {"prod-1": 3.0, "prod-2": 2.0, "prod-3": 1.0}
    retrieved = ["prod-3", "prod-2", "prod-1"]  # Inverted

    score = compute_ndcg_at_k(retrieved, ground_truth, k=3)
    assert 0.0 < score < 1.0


def test_precision_and_recall_at_k():
    relevant_set = {"prod-1", "prod-2", "prod-4"}
    retrieved = ["prod-1", "prod-3", "prod-2", "prod-5"]

    p_at_2 = compute_precision_at_k(retrieved, relevant_set, k=2)  # prod-1 (yes), prod-3 (no) -> 1/2 = 0.5
    assert p_at_2 == 0.5

    p_at_3 = compute_precision_at_k(retrieved, relevant_set, k=3)  # prod-1, prod-3, prod-2 -> 2/3
    assert round(p_at_3, 2) == 0.67

    r_at_3 = compute_recall_at_k(retrieved, relevant_set, k=3)  # 2 found out of 3 -> 2/3
    assert round(r_at_3, 2) == 0.67


def test_evaluator_suite():
    evaluator = RecommendationEvaluator()
    ground_truth = {"prod-A": 2.0, "prod-B": 1.0, "prod-C": 0.0}
    retrieved = ["prod-A", "prod-B", "prod-X"]

    metrics = evaluator.evaluate_query(retrieved, ground_truth, relevance_threshold=1.0, k=3)
    assert "ndcg@3" in metrics
    assert "precision@3" in metrics
    assert "recall@3" in metrics
    assert metrics["precision@3"] == 0.6667
    assert metrics["recall@3"] == 1.0

