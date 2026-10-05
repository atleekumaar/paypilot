"""Main FastAPI entrypoint for PayPilot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.schemas.health import RootResponse
from app.api.health import router as health_router
from app.api.products import router as products_router
from app.api.discovery import router as discovery_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered commerce agent backend for PayPal AI Hackathon.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration allowing local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router)
app.include_router(products_router)
app.include_router(discovery_router)


@app.get("/", response_model=RootResponse, tags=["General"])
async def root() -> RootResponse:
    """Root endpoint identifying the PayPilot application."""
    return RootResponse(
        name=settings.APP_NAME,
        version=settings.VERSION,
        status="running",
        environment=settings.ENVIRONMENT,
    )
