"""Zapier Automation API endpoints.

Exposes outbound workflow triggers and inbound webhook integration with Zapier.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.zapier.service import ZapierAutomationService, get_zapier_service

router = APIRouter(prefix="/api/zapier", tags=["Zapier Automation"])


class ZapierTriggerRequest(BaseModel):
    event: str = Field(..., min_length=2, description="Automation event name")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload data")


@router.post("/dispatch", summary="Dispatch automated event to Zapier")
def dispatch_event(
    body: ZapierTriggerRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    zapier_service: ZapierAutomationService = Depends(get_zapier_service),
) -> Dict[str, Any]:
    """Trigger connected multi-app automations (Sheets, Slack, Gmail, QuickBooks)."""
    payload = body.payload.copy()
    payload["triggered_by_user"] = current_user.id
    result = zapier_service.trigger_custom_action(body.event, payload)
    return result.model_dump()


@router.post("/webhook", summary="Inbound Zapier webhook receiver")
def inbound_webhook(
    event_data: Dict[str, Any] = Body(...),
    zapier_service: ZapierAutomationService = Depends(get_zapier_service),
) -> Dict[str, Any]:
    """Receive callbacks and updates from active Zapier Zaps."""
    return {
        "status": "ACCEPTED",
        "received_keys": list(event_data.keys()),
        "message": "Zapier webhook processed successfully by PayPilot.",
    }


@router.get("/health", summary="Check Zapier connection health")
def zapier_health(
    zapier_service: ZapierAutomationService = Depends(get_zapier_service),
) -> Dict[str, Any]:
    return zapier_service.health()
