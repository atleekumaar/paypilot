"""Offline evaluation metrics for recommendation quality (NDCG@K, Precision@K, Recall@K)."""

import math
from typing import Dict, List, Set


def compute_dcg(relevance_scores: List[float], k: int) -> float:
    r"""Compute Discounted Cumulative Gain at rank K.
    
    Formula: \sum_{i=1}^K \frac{2^{rel_i} - 1}{\log_2(i + 1)}
    """
    dcg = 0.0
    for i, rel in enumerate(relevance_scores[:k]):
        gain = (2.0 ** rel) - 1.0
        discount = math.log2(i + 2)  # i=0 -> rank 1 -> log2(2) = 1.0
        dcg += gain / discount
    return dcg


def compute_ndcg_at_k(retrieved_ids: List[str], ground_truth_relevance: Dict[str, float], k: int = 3) -> float:
    """Compute Normalized Discounted Cumulative Gain at rank K.
    
    NDCG@K = DCG@K / IDCG@K
    """
    if k <= 0 or not ground_truth_relevance:
        return 0.0

    # Get relevance of retrieved items
    retrieved_rel = [ground_truth_relevance.get(item_id, 0.0) for item_id in retrieved_ids[:k]]
    actual_dcg = compute_dcg(retrieved_rel, k)

    # Ideal ranking relevance
    ideal_rel = sorted(ground_truth_relevance.values(), reverse=True)[:k]
    ideal_dcg = compute_dcg(ideal_rel, k)

    if ideal_dcg <= 0.0:
        return 0.0

    return round(actual_dcg / ideal_dcg, 4)


def compute_precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = 3) -> float:
    """Compute Precision@K: fraction of retrieved items that are relevant."""
    if k <= 0:
        return 0.0
    retrieved_k = retrieved_ids[:k]
    if not retrieved_k:
        return 0.0
    hits = sum(1 for item in retrieved_k if item in relevant_ids)
    return round(hits / len(retrieved_k), 4)


def compute_recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = 3) -> float:
    """Compute Recall@K: fraction of relevant items that are retrieved."""
    if not relevant_ids or k <= 0:
        return 0.0
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for item in retrieved_k if item in relevant_ids)
    return round(hits / len(relevant_ids), 4)


class RecommendationEvaluator:
    """Offline recommendation evaluator benchmarking retrieval and ranking accuracy."""

    def evaluate_query(
        self,
        retrieved_ids: List[str],
        ground_truth: Dict[str, float],
        relevance_threshold: float = 1.0,
        k: int = 3,
    ) -> Dict[str, float]:
        """Compute all three metrics for a single query."""
        relevant_ids = {item_id for item_id, score in ground_truth.items() if score >= relevance_threshold}
        return {
            f"ndcg@{k}": compute_ndcg_at_k(retrieved_ids, ground_truth, k=k),
            f"precision@{k}": compute_precision_at_k(retrieved_ids, relevant_ids, k=k),
            f"recall@{k}": compute_recall_at_k(retrieved_ids, relevant_ids, k=k),
        }

