"""Kernel Browser Service.

High-level business service orchestrating Kernel agent browser sessions,
live merchant term verification, and session replay generation.
"""

import logging
from typing import Any, Dict, Optional
from app.services.kernel.client import KernelBrowseResult, KernelClient

logger = logging.getLogger(__name__)


class KernelBrowserService:
    """Service orchestrating agent browser actions via Kernel."""

    def __init__(self, client: Optional[KernelClient] = None):
        self.client = client or KernelClient()

    def inspect_merchant_product(
        self,
        url: str,
        extract_policy: bool = True,
        max_wait_seconds: int = 15,
    ) -> KernelBrowseResult:
        """Inspect a live product page URL to verify availability, stock, and return policies."""
        logger.info(f"Kernel: Initiating cloud browser session for URL: {url}")
        return self.client.browse(
            url=url,
            extract_policy=extract_policy,
            max_wait_seconds=max_wait_seconds,
        )

    def verify_merchant_domain(self, domain: str) -> Dict[str, Any]:
        """Verify trust, SSL, and return terms for a given merchant domain."""
        url = f"https://{domain}" if not domain.startswith("http") else domain
        result = self.inspect_merchant_product(url, extract_policy=True)
        return {
            "domain": domain,
            "session_id": result.session_id,
            "replay_url": result.replay_url,
            "status": "VERIFIED_MERCHANT",
            "bot_detection_passed": result.bot_bypass_success,
            "latency_ms": result.latency_ms,
            "policy": result.merchant_policy,
        }

    def health(self) -> Dict[str, Any]:
        return self.client.health()


_kernel_service_instance: Optional[KernelBrowserService] = None


def get_kernel_service() -> KernelBrowserService:
    global _kernel_service_instance
    if _kernel_service_instance is None:
        _kernel_service_instance = KernelBrowserService()
    return _kernel_service_instance

