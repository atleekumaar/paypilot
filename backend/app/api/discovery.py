"""AI Product Discovery API endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/discovery", tags=["Discovery"])


class DiscoverySearchRequest(BaseModel):
    """Payload for natural language product discovery request."""

    query: str = Field(
        ...,
        json_schema_extra={
            "example": "Find me a laptop under $1200 for AI development with good battery life."
        },
        description="Natural language user request for product search",
    )


@router.post(
    "/search",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Natural Language AI Product Discovery",
    description="Processes user intent, searches and filters catalogue, ranks candidates, and returns top explainable recommendations.",
)
async def discovery_search(request: DiscoverySearchRequest) -> RecommendationResponse:
    """Execute AI product discovery pipeline."""
    service = RecommendationService()
    return service.discover_products(query=request.query)
