"""Main FastAPI entrypoint for PayPilot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.middleware import RequestIDMiddleware
from app.schemas.health import RootResponse
from app.api.health import router as health_router
from app.api.products import router as products_router
from app.api.discovery import router as discovery_router
from app.api.purchase_plans import router as purchase_plans_router
from app.api.payments import router as payments_router
from app.api.agent import router as agent_router
from app.api.orders import router as orders_router
from app.api.notifications import router as notifications_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered commerce agent backend for PayPal AI Hackathon.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add Request ID correlation middleware
app.add_middleware(RequestIDMiddleware)

# CORS configuration with strictly allowed origins
cors_origins = settings.ALLOWED_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router)
app.include_router(products_router)
app.include_router(discovery_router)
app.include_router(purchase_plans_router)
app.include_router(payments_router)
app.include_router(agent_router)
app.include_router(orders_router)
app.include_router(notifications_router)


@app.get("/", response_model=RootResponse, tags=["General"])
async def root() -> RootResponse:
    """Root endpoint identifying the PayPilot application."""
    return RootResponse(
        name=settings.APP_NAME,
        version=settings.VERSION,
        status="running",
        environment=settings.ENVIRONMENT,
    )
