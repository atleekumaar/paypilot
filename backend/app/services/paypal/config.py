"""PayPal configuration wrapper enforcing Sandbox safety."""

from dataclasses import dataclass
from typing import Optional
from app.core.config import get_settings


@dataclass
class PayPalConfig:
    """Encapsulates PayPal configuration parameters."""

    client_id: Optional[str]
    client_secret: Optional[str]
    environment: str
    base_url: str
    mock_enabled: Optional[bool] = None

    @property
    def is_configured(self) -> bool:
        """Verify whether valid credentials are provided."""
        return bool(
            self.client_id
            and self.client_secret
            and not self.client_id.startswith("your_")
            and not self.client_secret.startswith("your_")
        )

    @property
    def is_sandbox(self) -> bool:
        return self.environment.lower() == "sandbox"

    @property
    def is_mock_allowed(self) -> bool:
        """Verify whether mock transactions are permitted.

        Rules:
        - In LIVE environment, mock transactions are STRICTLY prohibited.
        - If PAYPAL_MOCK_ENABLED is explicitly configured, obey its value (in sandbox).
        - If not configured, mock is allowed only when credentials are not present in sandbox.
        """
        if not self.is_sandbox:
            return False
        if self.mock_enabled is not None:
            return self.mock_enabled
        return not self.is_configured


def get_paypal_config() -> PayPalConfig:
    """Retrieve active PayPal configuration."""
    settings = get_settings()
    return PayPalConfig(
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET,
        environment=settings.PAYPAL_ENVIRONMENT,
        base_url=settings.paypal_base_url,
        mock_enabled=settings.PAYPAL_MOCK_ENABLED,
    )
