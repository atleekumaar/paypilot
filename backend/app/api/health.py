"""Health check API endpoints."""

from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return backend health status."""
    return HealthResponse(status="ok", service="paypilot-backend")
