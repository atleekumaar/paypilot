"""Configuration settings for PayPilot backend."""

from functools import lru_cache
from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "PayPilot"
    SERVICE_NAME: str = "paypilot-backend"
    ENVIRONMENT: str = "development"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database (PostgreSQL-ready)
    DATABASE_URL: Optional[str] = None

    # Authentication (Phase 4A)
    # AUTH_MODE: "demo" (local testing / dev only) or "jwt" (production JWKS / OIDC)
    AUTH_MODE: str = "demo"
    AUTH_ISSUER: Optional[str] = None
    AUTH_AUDIENCE: Optional[str] = None
    AUTH_JWKS_URL: Optional[str] = None
    AUTH_ALGORITHMS: List[str] = ["RS256"]
    AUTH_REQUIRED_CLAIMS: List[str] = ["sub"]
    AUTH_CLOCK_SKEW_SECONDS: int = 60

    # LLM & AI Agents (Phase 2+)
    LLM_API_KEY: Optional[str] = None

    # PayPal Integration (Sandbox)
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_ENVIRONMENT: str = "sandbox"
    PAYPAL_MOCK_ENABLED: Optional[bool] = None  # None: auto (mock allowed in sandbox/dev only if credentials not configured)

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Enforce strict production fail-closed security rules."""
        if self.ENVIRONMENT.lower() == "production":
            if self.AUTH_MODE.lower() != "jwt":
                raise ValueError("AUTH_MODE must be 'jwt' in production environment")
            if not self.AUTH_ISSUER:
                raise ValueError("AUTH_ISSUER must be configured when ENVIRONMENT='production'")
            if not self.AUTH_JWKS_URL:
                raise ValueError("AUTH_JWKS_URL must be configured when ENVIRONMENT='production'")
        return self

    @property
    def paypal_base_url(self) -> str:
        """Return PayPal API Base URL according to configured environment."""
        if self.PAYPAL_ENVIRONMENT.lower() == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )



@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
