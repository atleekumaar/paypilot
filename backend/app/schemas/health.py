"""Schemas for health and root endpoints."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="ok", description="Current status of the backend service")
    service: str = Field(default="paypilot-backend", description="Service identifier")


class RootResponse(BaseModel):
    """Root endpoint response schema."""

    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    status: str = Field(default="running", description="Application status")
    environment: str = Field(..., description="Running environment")
