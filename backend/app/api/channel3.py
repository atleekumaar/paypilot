"""Channel3 Live Multi-Merchant Product Discovery API endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.schemas.product import Product
from app.services.channel3.service import Channel3Service, get_channel3_service

router = APIRouter(prefix="/api/channel3", tags=["Channel3"])


class Channel3SearchRequest(BaseModel):
    """Payload for Channel3 cross-retailer product discovery."""

    query: str = Field(..., min_length=1, description="Natural language search query")
    category: Optional[str] = Field(None, description="Category filter (e.g. laptop, audio, apparel)")
    min_price: Optional[float] = Field(None, ge=0.0, description="Minimum price boundary")
    max_price: Optional[float] = Field(None, ge=0.0, description="Maximum price ceiling")
    brand: Optional[str] = Field(None, description="Brand name filter")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum items to return")


class Channel3CompareRequest(BaseModel):
    """Payload to compare multiple Channel3 retailer products."""

    product_ids: List[str] = Field(..., min_length=2, description="List of Channel3 product IDs to compare")


@router.post(
    "/search",
    response_model=List[Product],
    summary="Search Channel3 Product Graph",
    description="Query 100M+ products across 25,000+ retailers with universal normalization and live pricing.",
    status_code=status.HTTP_200_OK,
)
async def channel3_search(
    req: Channel3SearchRequest,
    channel3_service: Channel3Service = Depends(get_channel3_service),
) -> List[Product]:
    """Execute live product discovery across retailers."""
    return channel3_service.search(
        query=req.query,
        category=req.category,
        min_price=req.min_price,
        max_price=req.max_price,
        brand=req.brand,
        limit=req.limit,
    )


@router.get(
    "/product/{product_id}",
    response_model=Product,
    summary="Get Channel3 Product Details",
    description="Retrieve normalized product details with merchant offers and pricing.",
    status_code=status.HTTP_200_OK,
)
async def get_channel3_product(
    product_id: str,
    channel3_service: Channel3Service = Depends(get_channel3_service),
) -> Product:
    """Lookup product details by Channel3 ID."""
    prod = channel3_service.get_product(product_id)
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel3 product '{product_id}' not found.",
        )
    return prod


@router.post(
    "/compare",
    summary="Compare Channel3 Retailer Products",
    description="Performs multi-factor trade-off matrix across prices, ratings, and shipping speed.",
    status_code=status.HTTP_200_OK,
)
async def channel3_compare(
    req: Channel3CompareRequest,
    channel3_service: Channel3Service = Depends(get_channel3_service),
) -> Dict[str, Any]:
    """Compare trade-offs between candidate products."""
    return channel3_service.compare(req.product_ids)

