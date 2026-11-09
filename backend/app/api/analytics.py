"""FastAPI router for Commerce Intelligence and AG Studio Analytics."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.analytics_service import AnalyticsService, get_analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Commerce Intelligence & Analytics"])


class AnalyticsOverviewResponse(BaseModel):
    total_spending: float
    total_orders: int
    average_order_value: float
    completed_payments: int
    failed_payments: int
    pending_orders: int
    currency: str = "USD"


class SpendingAnalyticsResponse(BaseModel):
    spending_over_time: List[Dict[str, Any]]
    spending_by_category: List[Dict[str, Any]]
    payment_status_distribution: List[Dict[str, Any]]


class AnalyticsQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question or query for the dashboard agent", min_length=2)


class AnalyticsQueryResponse(BaseModel):
    intent: str
    suggested_widget: str
    title: str
    summary: str
    data: Any
    insights: List[str]


@router.get("/overview", response_model=AnalyticsOverviewResponse, summary="Get Top-Level Commerce KPIs")
async def get_overview(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsOverviewResponse:
    """Retrieve verified top-level KPI metrics for the current user."""
    return service.get_overview(user_id=current_user.id)


@router.get("/spending", response_model=SpendingAnalyticsResponse, summary="Get Spending & Payment Distribution")
async def get_spending(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> SpendingAnalyticsResponse:
    """Retrieve spending over time, category breakdowns, and payment status distribution."""
    return service.get_spending_analytics(user_id=current_user.id)


@router.get("/orders", response_model=List[Dict[str, Any]], summary="Get Order Intelligence Records")
async def get_orders(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[Dict[str, Any]]:
    """Retrieve enriched order intelligence records for AG Grid."""
    return service.get_order_intelligence(user_id=current_user.id)


@router.get("/payments", response_model=List[Dict[str, Any]], summary="Get Payment Intelligence Records")
async def get_payments(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[Dict[str, Any]]:
    """Retrieve verified payment transaction records for AG Grid."""
    return service.get_payment_intelligence(user_id=current_user.id)


@router.get("/products", response_model=List[Dict[str, Any]], summary="Get Product Intelligence Catalog")
async def get_products(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[Dict[str, Any]]:
    """Retrieve product catalog with specs and scores for Product Intelligence Grid."""
    return service.get_product_intelligence()


@router.post("/query", response_model=AnalyticsQueryResponse, summary="AI Dashboard Agent Query")
async def query_dashboard_agent(
    body: AnalyticsQueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsQueryResponse:
    """Execute a safe, constrained query via the AI Dashboard Agent."""
    res = service.execute_query(user_id=current_user.id, query=body.query)
    return AnalyticsQueryResponse(**res)

