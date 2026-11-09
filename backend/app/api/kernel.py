"""Kernel Browser API endpoints.

Exposes agent cloud browser browsing, anti-bot verification, and live merchant inspection.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.kernel.service import KernelBrowserService, get_kernel_service

router = APIRouter(prefix="/api/kernel", tags=["Kernel Browser"])


class KernelBrowseRequest(BaseModel):
    url: str = Field(..., min_length=4, description="Merchant URL to browse")
    extract_policy: bool = Field(default=True, description="Whether to extract return and shipping terms")
    max_wait_seconds: int = Field(default=15, ge=1, le=60, description="Max dynamic hydration wait")


class KernelDomainVerifyRequest(BaseModel):
    domain: str = Field(..., min_length=3, description="Merchant domain name, e.g. target.com")


@router.post("/browse", summary="Browse merchant page via Kernel Cloud Browser")
def browse_page(
    body: KernelBrowseRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    kernel_service: KernelBrowserService = Depends(get_kernel_service),
) -> Dict[str, Any]:
    """Execute high-speed browser session using Kernel infrastructure."""
    result = kernel_service.inspect_merchant_product(
        url=body.url,
        extract_policy=body.extract_policy,
        max_wait_seconds=body.max_wait_seconds,
    )
    return result.model_dump()


@router.post("/verify-domain", summary="Verify merchant store trust and policies")
def verify_domain(
    body: KernelDomainVerifyRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    kernel_service: KernelBrowserService = Depends(get_kernel_service),
) -> Dict[str, Any]:
    """Verify merchant legitimacy and return policies."""
    return kernel_service.verify_merchant_domain(body.domain)


@router.get("/health", summary="Check Kernel connection health")
def kernel_health(
    kernel_service: KernelBrowserService = Depends(get_kernel_service),
) -> Dict[str, Any]:
    return kernel_service.health()
