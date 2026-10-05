"""PayPal Orders API v2 service for creating and capturing orders."""

import logging
from typing import Any, Dict, Optional
import uuid
import httpx

from app.schemas.purchase_plan import PurchasePlan
from app.services.paypal.auth import PayPalAuthService
from app.services.paypal.config import PayPalConfig, get_paypal_config

logger = logging.getLogger(__name__)


class PayPalOrderService:
    """Handles communication with PayPal Orders API v2."""

    def __init__(
        self,
        config: Optional[PayPalConfig] = None,
        auth_service: Optional[PayPalAuthService] = None,
    ):
        self._config = config or get_paypal_config()
        self._auth_service = auth_service or PayPalAuthService(self._config)

    def create_order(self, plan: PurchasePlan) -> Dict[str, Any]:
        """Create a PayPal Order derived authoritatively from Purchase Plan amounts."""
        logger.info(f"Creating PayPal order for internal plan {plan.id} (${plan.total_amount:.2f} {plan.currency})")

        # Mock fallback for test suites or offline local development
        if not self._config.is_configured:
            mock_order_id = f"MOCK-PAYPAL-{uuid.uuid4().hex[:10].upper()}"
            logger.info(f"Generating mock PayPal Order ID: {mock_order_id}")
            return {
                "id": mock_order_id,
                "status": "CREATED",
                "links": [
                    {
                        "href": f"https://www.sandbox.paypal.com/checkoutnow?token={mock_order_id}",
                        "rel": "approve",
                        "method": "GET",
                    }
                ],
            }

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Prefer": "return=representation",
        }

        order_payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": plan.id,
                    "description": f"PayPilot Purchase: {plan.product_name}",
                    "amount": {
                        "currency_code": plan.currency,
                        "value": f"{plan.total_amount:.2f}",
                    },
                }
            ],
            "application_context": {
                "brand_name": "PayPilot",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
            },
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(url, headers=headers, json=order_payload)
                if response.status_code not in (200, 201):
                    logger.error(f"PayPal Create Order error: HTTP {response.status_code} - {response.text}")
                    raise RuntimeError(f"PayPal Create Order failed: HTTP {response.status_code}")

                data = response.json()
                logger.info(f"PayPal order created successfully. Order ID: {data.get('id')}")
                return data

        except httpx.RequestError as exc:
            logger.error(f"Network error creating PayPal order: {exc}")
            raise RuntimeError(f"Network error contacting PayPal Orders API: {exc}")

    def capture_order(self, paypal_order_id: str) -> Dict[str, Any]:
        """Capture payment for an approved PayPal Order."""
        logger.info(f"Capturing PayPal order {paypal_order_id}")

        # Mock fallback for test suites or offline local development
        if not self._config.is_configured or paypal_order_id.startswith("MOCK-"):
            capture_id = f"CAP-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Mock capture executed for {paypal_order_id}, capture_id: {capture_id}")
            return {
                "id": paypal_order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": capture_id,
                                    "status": "COMPLETED",
                                }
                            ]
                        }
                    }
                ],
                "payer": {
                    "email_address": "sandbox-buyer@paypilot.demo",
                    "payer_id": "MOCK_BUYER_ID",
                },
            }

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v2/checkout/orders/{paypal_order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Prefer": "return=representation",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(url, headers=headers, json={})
                if response.status_code not in (200, 201):
                    logger.error(f"PayPal capture error: HTTP {response.status_code} - {response.text}")
                    raise RuntimeError(f"PayPal capture failed: HTTP {response.status_code}")

                data = response.json()
                logger.info(f"PayPal capture completed. Status: {data.get('status')}")
                return data

        except httpx.RequestError as exc:
            logger.error(f"Network error capturing PayPal order: {exc}")
            raise RuntimeError(f"Network error contacting PayPal Capture API: {exc}")

    def get_order_details(self, paypal_order_id: str) -> Dict[str, Any]:
        """Retrieve details of an existing PayPal Order."""
        if not self._config.is_configured or paypal_order_id.startswith("MOCK-"):
            return {"id": paypal_order_id, "status": "APPROVED"}

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v2/checkout/orders/{paypal_order_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers)
                if response.status_code != 200:
                    raise RuntimeError(f"Failed to fetch PayPal order: HTTP {response.status_code}")
                return response.json()
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error contacting PayPal Order details: {exc}")
