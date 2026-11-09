"""Elasticsearch Indexing & Hybrid Retrieval API endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.product import Product
from app.services.elastic.service import ElasticCommerceService, get_elastic_service

router = APIRouter(prefix="/api/elastic", tags=["Elastic"])


class ElasticSearchRequest(BaseModel):
    """Payload for Elasticsearch queries."""

    query: str = Field(..., min_length=1, description="Natural language search term")
    mode: str = Field(default="hybrid", description="Retrieval mode: 'hybrid', 'keyword', or 'semantic'")
    category: Optional[str] = Field(None, description="Category filter")
    min_price: Optional[float] = Field(None, ge=0.0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0.0, description="Maximum price")
    limit: int = Field(default=10, ge=1, le=50, description="Max results to return")


class KnowledgeSearchRequest(BaseModel):
    """Payload for merchant policy and knowledge retrieval."""

    query: str = Field(..., min_length=1, description="Query on policies, shipping, or warranty")
    limit: int = Field(default=3, ge=1, le=10, description="Max docs to return")


@router.post(
    "/search",
    summary="Elasticsearch Product Retrieval",
    description="Query product index using BM25 keyword matching, dense vector semantic search, or Reciprocal Rank Fusion hybrid retrieval.",
    status_code=status.HTTP_200_OK,
)
async def elastic_search(
    req: ElasticSearchRequest,
    elastic_service: ElasticCommerceService = Depends(get_elastic_service),
) -> List[Dict[str, Any]]:
    """Execute search across Elasticsearch product index."""
    mode = req.mode.lower()
    if mode == "keyword":
        return elastic_service.keyword_search(
            query=req.query,
            category=req.category,
            min_price=req.min_price,
            max_price=req.max_price,
            limit=req.limit,
        )
    elif mode == "semantic":
        return elastic_service.semantic_search(query=req.query, top_k=req.limit)
    else:
        # Default: Hybrid Search (RRF)
        return elastic_service.hybrid_search(
            query=req.query,
            category=req.category,
            min_price=req.min_price,
            max_price=req.max_price,
            limit=req.limit,
        )


@router.post(
    "/knowledge",
    summary="Elasticsearch Merchant Knowledge Retrieval",
    description="Retrieve merchant policies, warranty terms, and shipping guarantees to ground AI responses.",
    status_code=status.HTTP_200_OK,
)
async def elastic_knowledge(
    req: KnowledgeSearchRequest,
    elastic_service: ElasticCommerceService = Depends(get_elastic_service),
) -> List[Dict[str, Any]]:
    """Retrieve grounded merchant and warranty policies."""
    return elastic_service.search_knowledge(query=req.query, limit=req.limit)


@router.get(
    "/health",
    summary="Elasticsearch Cluster & Local Engine Health",
    description="Returns cluster connection state, active indices, and document counts.",
    status_code=status.HTTP_200_OK,
)
async def elastic_health(
    elastic_service: ElasticCommerceService = Depends(get_elastic_service),
) -> Dict[str, Any]:
    """Retrieve Elasticsearch cluster status and statistics."""
    return elastic_service.health()


@router.post(
    "/sync",
    summary="Sync Products to Elasticsearch",
    description="Triggers re-indexing of all products from database repository into Elasticsearch.",
    status_code=status.HTTP_200_OK,
)
async def elastic_sync(
    elastic_service: ElasticCommerceService = Depends(get_elastic_service),
) -> Dict[str, Any]:
    """Re-sync catalog into Elasticsearch."""
    count = elastic_service.sync_from_repository()
    return {"status": "synced", "total_indexed": count}

