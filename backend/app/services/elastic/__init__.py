"""Elasticsearch integration package."""

from app.services.elastic.client import ElasticConfig, ElasticsearchClient
from app.services.elastic.service import (
    ElasticCommerceService,
    get_elastic_service,
)

__all__ = [
    "ElasticConfig",
    "ElasticsearchClient",
    "ElasticCommerceService",
    "get_elastic_service",
]

