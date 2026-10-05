"""Configuration settings for PayPilot backend."""

from functools import lru_cache
from typing import Optional
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

    # LLM & AI Agents (Phase 2+)
    LLM_API_KEY: Optional[str] = None

    # PayPal Integration (Phase 3+)
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_ENVIRONMENT: str = "sandbox"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
