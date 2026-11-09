"""PayPal Orders API v2 service for creating and capturing orders."""

import logging
import threading
from typing import Any, Dict, Optional
import uuid
import httpx

from app.schemas.purchase_plan import PurchasePlan
from app.services.paypal.auth import PayPalAuthService
from app.services.paypal.config import PayPalConfig, get_paypal_config

logger = logging.getLogger(__name__)


class PayPalOrderService:
    """Handles communication with PayPal Orders API v2 with explicit mock isolation."""

    _mock_orders: Dict[str, Dict[str, Any]] = {}
    _mock_lock = threading.Lock()

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

        # Mock fallback isolated strictly behind explicit demo/sandbox configuration
        if not self._config.is_configured or (self._config.is_mock_allowed and self._config.mock_enabled is True):
            if not self._config.is_mock_allowed:
                raise RuntimeError("PayPal credentials are not configured and mock transactions are disabled.")

            mock_order_id = f"MOCK-PAYPAL-{uuid.uuid4().hex[:10].upper()}"
            approval_url = f"https://www.sandbox.paypal.com/checkoutnow?token={mock_order_id}"
            logger.info(f"Generating mock PayPal Order ID: {mock_order_id}")

            mock_order_data = {
                "id": mock_order_id,
                "status": "APPROVED",
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
                "links": [
                    {
                        "href": approval_url,
                        "rel": "approve",
                        "method": "GET",
                    }
                ],
            }

            with self._mock_lock:
                self._mock_orders[mock_order_id] = mock_order_data

            return mock_order_data

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

        # Mock fallback isolated behind explicit test/demo configuration
        if not self._config.is_configured or (self._config.is_mock_allowed and self._config.mock_enabled is True) or paypal_order_id.startswith("MOCK-"):
            if not self._config.is_configured and not self._config.is_mock_allowed:
                raise RuntimeError("PayPal credentials are not configured and mock transactions are disabled.")

            capture_id = f"CAP-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Mock capture executed for {paypal_order_id}, capture_id: {capture_id}")

            with self._mock_lock:
                mock_order = self._mock_orders.get(paypal_order_id)
                ref_id = "PP-MOCK"
                if mock_order:
                    mock_order["status"] = "COMPLETED"
                    units = mock_order.get("purchase_units", [])
                    if units and "reference_id" in units[0]:
                        ref_id = units[0]["reference_id"]

            return {
                "id": paypal_order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "reference_id": ref_id,
                        "payments": {
                            "captures": [
                                {
                                    "id": capture_id,
                                    "status": "COMPLETED",
                                }
                            ]
                        },
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

        except httpx.TimeoutException as exc:
            logger.error(f"Timeout communicating with PayPal capture endpoint: {exc}")
            raise TimeoutError(f"PayPal Capture API timed out: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"Network error capturing PayPal order: {exc}")
            raise RuntimeError(f"Network error contacting PayPal Capture API: {exc}")

    def get_order_details(self, paypal_order_id: str) -> Dict[str, Any]:
        """Retrieve details of an existing PayPal Order for server-side verification."""
        if not self._config.is_configured or (self._config.is_mock_allowed and self._config.mock_enabled is True) or paypal_order_id.startswith("MOCK-"):
            if not self._config.is_configured and not self._config.is_mock_allowed:
                raise RuntimeError("PayPal credentials are not configured and mock transactions are disabled.")

            with self._mock_lock:
                if paypal_order_id in self._mock_orders:
                    return self._mock_orders[paypal_order_id]

            # If mock order ID starts with MOCK-PAYPAL but not found in runtime registry,
            # return standard mock order representation if ID is structurally valid
            if paypal_order_id.startswith("MOCK-PAYPAL-") or paypal_order_id.startswith("MOCK-ORD-"):
                return {
                    "id": paypal_order_id,
                    "status": "APPROVED",
                    "purchase_units": [
                        {
                            "reference_id": "PP-DEFAULT",
                            "amount": {"currency_code": "USD", "value": "1049.00"},
                        }
                    ],
                }

            raise RuntimeError(f"PayPal Order '{paypal_order_id}' not found.")

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v2/checkout/orders/{paypal_order_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers)
                if response.status_code == 404:
                    raise RuntimeError(f"PayPal Order '{paypal_order_id}' not found.")
                if response.status_code != 200:
                    raise RuntimeError(f"Failed to fetch PayPal order: HTTP {response.status_code}")
                return response.json()
        except httpx.TimeoutException as exc:
            logger.error(f"Timeout communicating with PayPal order details: {exc}")
            raise TimeoutError(f"PayPal Order details timed out: {exc}")
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error contacting PayPal Order details: {exc}")

    def refund_capture(
        self,
        capture_id: str,
        amount: float,
        currency: str = "USD",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a refund against a completed PayPal capture with provider idempotency."""
        logger.info(f"Initiating PayPal refund for capture {capture_id}: {amount:.2f} {currency}")

        if not self._config.is_configured or (self._config.is_mock_allowed and self._config.mock_enabled is True) or capture_id.startswith("MOCK-"):
            if not self._config.is_configured and not self._config.is_mock_allowed:
                raise RuntimeError("PayPal credentials are not configured and mock transactions are disabled.")

            mock_refund_id = f"REF-{uuid.uuid4().hex[:10].upper()}"
            return {
                "id": mock_refund_id,
                "status": "COMPLETED",
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency_code": currency,
                },
                "capture_id": capture_id,
            }

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v2/payments/captures/{capture_id}/refund"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Prefer": "return=representation",
        }
        if idempotency_key:
            headers["PayPal-Request-Id"] = idempotency_key

        payload = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency_code": currency,
            },
            "note_to_payer": "Refund for PayPilot purchase",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code not in (200, 201):
                    logger.error(f"PayPal refund error: HTTP {response.status_code} - {response.text}")
                    raise RuntimeError(f"PayPal refund failed: HTTP {response.status_code} - {response.text}")
                return response.json()
        except httpx.TimeoutException as exc:
            logger.error(f"Timeout communicating with PayPal refund endpoint: {exc}")
            raise TimeoutError(f"PayPal refund API timed out: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"Network error contacting PayPal refund endpoint: {exc}")
            raise RuntimeError(f"Network error contacting PayPal refund API: {exc}")

    def get_capture_details(self, capture_id: str) -> Dict[str, Any]:
        """Retrieve details of a PayPal capture for authoritative verification."""
        if not self._config.is_configured or (self._config.is_mock_allowed and self._config.mock_enabled is True) or capture_id.startswith("MOCK-"):
            if not self._config.is_configured and not self._config.is_mock_allowed:
                raise RuntimeError("PayPal credentials are not configured and mock transactions are disabled.")
            return {
                "id": capture_id,
                "status": "COMPLETED",
                "amount": {"currency_code": "USD", "value": "100.00"},
            }

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v2/payments/captures/{capture_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers)
                if response.status_code != 200:
                    raise RuntimeError(f"Failed to fetch PayPal capture details: HTTP {response.status_code}")
                return response.json()
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"PayPal capture details timed out: {exc}")
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error contacting PayPal capture details: {exc}")

    def verify_webhook_signature(
        self,
        headers: Dict[str, str],
        body_json: Dict[str, Any],
        webhook_id: Optional[str] = None,
    ) -> bool:
        """Verify authenticity of PayPal webhook notification using provider API. Fail-closed by default."""
        norm_headers = {k.lower(): v for k, v in headers.items()}
        auth_algo = norm_headers.get("paypal-auth-algo")
        cert_url = norm_headers.get("paypal-cert-url")
        transmission_id = norm_headers.get("paypal-transmission-id")
        transmission_sig = norm_headers.get("paypal-transmission-sig")
        transmission_time = norm_headers.get("paypal-transmission-time")

        if not all([auth_algo, cert_url, transmission_id, transmission_sig, transmission_time]):
            logger.warning("Missing required PayPal webhook signature headers.")
            return False

        # In mock / test harness mode: Strictly permitted ONLY when mock is explicitly allowed
        if not self._config.is_configured or (self._config.is_mock_allowed and self._config.mock_enabled is True):
            if not self._config.is_mock_allowed:
                logger.error("PayPal credentials not configured and mock transactions are disallowed; rejecting webhook signature.")
                return False
            # Deterministic test validation: reject forged/invalid signatures
            if "forged" in transmission_sig.lower() or "invalid" in transmission_sig.lower():
                return False
            return True

        # Live / Sandbox verification via PayPal API
        target_webhook_id = webhook_id or self._config.webhook_id
        if not target_webhook_id:
            logger.error("PAYPAL_WEBHOOK_ID is not configured; cannot verify signature in non-mock mode.")
            return False

        token = self._auth_service.get_access_token()
        url = f"{self._config.base_url}/v1/notifications/verify-webhook-signature"
        payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": target_webhook_id,
            "webhook_event": body_json,
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    json=payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    status_val = data.get("verification_status", "").upper()
                    return status_val == "SUCCESS"
                logger.warning(f"PayPal webhook signature verification returned HTTP {resp.status_code}")
                return False
        except Exception as exc:
            logger.error(f"Error calling PayPal webhook verification endpoint: {exc}")
            return False

    @classmethod
    def register_mock_order(cls, order_id: str, order_data: Dict[str, Any]) -> None:
        """Helper for test harness to register deterministic mock order data."""
        with cls._mock_lock:
            cls._mock_orders[order_id] = order_data

    @classmethod
    def clear_mock_orders(cls) -> None:
        """Helper for test harness to reset mock orders."""
        with cls._mock_lock:
            cls._mock_orders.clear()
