"""Product catalogue API endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.repositories.product_repository import get_product_repository
from app.schemas.product import Product, ProductListResponse

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = Query(default=None, description="Filter by category (e.g. laptop, phone)"),
    in_stock_only: bool = Query(default=False, description="Filter only in-stock inventory"),
    limit: int = Query(default=50, ge=1, le=200, description="Items limit"),
    offset: int = Query(default=0, ge=0, description="Items offset"),
) -> ProductListResponse:
    """Retrieve product catalogue with optional category and stock filtering."""
    repo = get_product_repository()
    items = repo.list_products(category=category, in_stock_only=in_stock_only, limit=limit, offset=offset)
    return ProductListResponse(total=len(items), items=items)


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    """Retrieve details for a specific product by SKU identifier."""
    repo = get_product_repository()
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )
    return product
