"""PayPal OAuth 2.0 authentication service."""

import logging
import threading
import time
from typing import Optional
import httpx

from app.services.paypal.config import PayPalConfig, get_paypal_config

logger = logging.getLogger(__name__)


class PayPalAuthService:
    """Manages retrieval and caching of PayPal OAuth 2.0 access tokens."""

    def __init__(self, config: Optional[PayPalConfig] = None):
        self._config = config or get_paypal_config()
        self._lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def get_access_token(self) -> str:
        """Retrieve valid cached access token or fetch new token from PayPal OAuth endpoint."""
        with self._lock:
            current_time = time.time()
            # If token exists and has >60 seconds buffer before expiry, reuse
            if self._access_token and current_time < (self._token_expires_at - 60):
                return self._access_token

            # Otherwise, obtain fresh token
            token, expires_in = self._fetch_token()
            self._access_token = token
            self._token_expires_at = current_time + expires_in
            return self._access_token

    def _fetch_token(self) -> tuple[str, int]:
        """Request OAuth token from PayPal /v1/oauth2/token."""
        if not self._config.is_configured:
            # Safe mock fallback for local testing without credentials
            logger.info("PayPal credentials not configured in environment; issuing local test token.")
            return "MOCK_PAYPAL_ACCESS_TOKEN_FOR_TESTS", 3600

        url = f"{self._config.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        data = {"grant_type": "client_credentials"}

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    url,
                    auth=(self._config.client_id, self._config.client_secret),
                    headers=headers,
                    data=data,
                )
                if response.status_code != 200:
                    logger.error(f"PayPal OAuth error: HTTP {response.status_code}")
                    raise RuntimeError(f"PayPal authentication failed with status {response.status_code}")

                payload = response.json()
                token = payload.get("access_token")
                expires_in = int(payload.get("expires_in", 3600))
                if not token:
                    raise RuntimeError("PayPal OAuth response missing access_token")

                return token, expires_in

        except httpx.RequestError as exc:
            logger.error(f"Network error communicating with PayPal: {exc}")
            raise RuntimeError(f"Network error connecting to PayPal OAuth: {exc}")
