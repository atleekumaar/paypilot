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

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Database (PostgreSQL-ready)
    DATABASE_URL: Optional[str] = None

    # Authentication
    # AUTH_MODE: "demo" (local testing / dev only) or "jwt" (production JWKS / OIDC)
    AUTH_MODE: str = "demo"
    AUTH_ISSUER: Optional[str] = None
    AUTH_AUDIENCE: Optional[str] = None
    AUTH_JWKS_URL: Optional[str] = None
    AUTH_ALGORITHMS: List[str] = ["RS256"]
    AUTH_REQUIRED_CLAIMS: List[str] = ["sub"]
    AUTH_CLOCK_SKEW_SECONDS: int = 60

    # LLM & AI Agents
    LLM_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    @property
    def effective_llm_api_key(self) -> Optional[str]:
        """Return LLM API key with fallback to GROQ_API_KEY."""
        return self.LLM_API_KEY or self.GROQ_API_KEY

    # PayPal Integration (Sandbox)
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_ENVIRONMENT: str = "sandbox"
    PAYPAL_MOCK_ENABLED: Optional[bool] = None  # None: auto (mock allowed in sandbox/dev only if credentials not configured)
    PAYPAL_WEBHOOK_ID: Optional[str] = None

    # Channel3 Integration
    CHANNEL3_API_KEY: Optional[str] = None
    CHANNEL3_BASE_URL: str = "https://api.trychannel3.com"

    # Elasticsearch Integration
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_API_KEY: Optional[str] = None
    ELASTIC_PRODUCT_INDEX: str = "paypilot_products"
    ELASTIC_KNOWLEDGE_INDEX: str = "paypilot_knowledge"

    # Kernel Browser Cloud Infrastructure
    KERNEL_API_KEY: Optional[str] = None
    KERNEL_BASE_URL: str = "https://api.onkernel.com"

    # Zapier Multi-App Workflow Automation
    ZAPIER_WEBHOOK_URL: Optional[str] = None
    ZAPIER_NLA_API_KEY: Optional[str] = None

    # Render Cloud Deployment
    RENDER_EXTERNAL_URL: Optional[str] = None
    DEMO_AUTH_ALLOWED_IN_PROD: bool = False

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Enforce strict production fail-closed security rules."""
        if self.ENVIRONMENT.lower() == "production" and not self.DEMO_AUTH_ALLOWED_IN_PROD:
            if self.AUTH_MODE.lower() != "jwt":
                raise ValueError("AUTH_MODE must be 'jwt' in production environment (set DEMO_AUTH_ALLOWED_IN_PROD=true for hackathon demo)")
            if not self.AUTH_ISSUER:
                raise ValueError("AUTH_ISSUER must be configured when ENVIRONMENT='production'")
            if not self.AUTH_JWKS_URL:
                raise ValueError("AUTH_JWKS_URL must be configured when ENVIRONMENT='production'")
            if not self.PAYPAL_CLIENT_ID or self.PAYPAL_CLIENT_ID.startswith("your_"):
                raise ValueError("PAYPAL_CLIENT_ID must be configured when ENVIRONMENT='production'")
            if not self.PAYPAL_CLIENT_SECRET or self.PAYPAL_CLIENT_SECRET.startswith("your_"):
                raise ValueError("PAYPAL_CLIENT_SECRET must be configured when ENVIRONMENT='production'")
            if not self.PAYPAL_WEBHOOK_ID or self.PAYPAL_WEBHOOK_ID.startswith("your_"):
                raise ValueError("PAYPAL_WEBHOOK_ID must be configured when ENVIRONMENT='production'")
            if not self.DATABASE_URL or self.DATABASE_URL.startswith("sqlite"):
                raise ValueError("Production environment requires a production PostgreSQL DATABASE_URL (SQLite is disallowed)")
            if not self.ALLOWED_ORIGINS or any("*" in o for o in self.ALLOWED_ORIGINS):
                raise ValueError("ALLOWED_ORIGINS must be explicitly configured without wildcards in production")
        return self

    @property
    def paypal_base_url(self) -> str:
        """Return PayPal API Base URL according to configured environment."""
        if self.PAYPAL_ENVIRONMENT.lower() == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )



@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
