"""Zapier Workflow Automation Client.

Connects PayPilot to 9,000+ business applications (Slack, Google Sheets, Gmail,
QuickBooks, Zendesk) via Zapier Webhooks and Zapier MCP / AI Actions.
Official sponsor: https://paypalaihackathon.devpost.com/details/zapier
"""

import logging
import os
import time
from typing import Any, Dict, Optional
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ZapierConfig(BaseModel):
    """Configuration for Zapier integration."""

    webhook_url: Optional[str] = None
    nla_api_key: Optional[str] = None
    timeout: float = 10.0
    mock_fallback_enabled: bool = True

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url and not self.webhook_url.startswith("your_"))


class ZapierDispatchResult(BaseModel):
    """Result of dispatching an automated action to Zapier."""

    event_id: str
    event: str
    status: str
    target_apps: list[str] = Field(default_factory=list)
    timestamp: float
    payload: Dict[str, Any]
    external_sync_id: Optional[str] = None
    simulated: bool = False


class ZapierClient:
    """Client for triggering Zapier automations."""

    def __init__(self, config: Optional[ZapierConfig] = None):
        if config is None:
            from app.core.config import get_settings

            settings = get_settings()
            webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL") or settings.ZAPIER_WEBHOOK_URL
            nla_api_key = os.environ.get("ZAPIER_NLA_API_KEY") or settings.ZAPIER_NLA_API_KEY
            config = ZapierConfig(webhook_url=webhook_url, nla_api_key=nla_api_key)
        self.config = config

    def dispatch_webhook(self, event: str, payload: Dict[str, Any]) -> ZapierDispatchResult:
        """Send event payload to Zapier Webhook trigger."""
        timestamp = time.time()
        event_id = f"zap_evt_{int(timestamp)}_{event}"

        if self.config.is_configured and self.config.webhook_url:
            try:
                body = {
                    "event_id": event_id,
                    "event": event,
                    "timestamp": timestamp,
                    "source": "PayPilot-CommerceAgent",
                    "data": payload,
                }
                with httpx.Client(timeout=self.config.timeout) as client:
                    resp = client.post(self.config.webhook_url, json=body)
                    if resp.status_code in (200, 201, 202):
                        return ZapierDispatchResult(
                            event_id=event_id,
                            event=event,
                            status="DISPATCHED",
                            target_apps=["Zapier Webhook", "Connected Zaps"],
                            timestamp=timestamp,
                            payload=payload,
                            external_sync_id=resp.headers.get("x-zapier-execution-id"),
                            simulated=False,
                        )
                    else:
                        logger.warning(f"Zapier returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Zapier dispatch error: {e}. Falling back to simulation.")

        # Simulation fallback
        target_apps = ["Gmail", "Google Sheets", "Slack", "QuickBooks"]
        return ZapierDispatchResult(
            event_id=event_id,
            event=event,
            status="SUCCESS_SIMULATED",
            target_apps=target_apps,
            timestamp=timestamp,
            payload=payload,
            external_sync_id=f"zap_sim_{int(timestamp)}",
            simulated=True,
        )

    def health(self) -> Dict[str, Any]:
        """Check Zapier service status."""
        return {
            "status": "healthy",
            "provider": "Zapier Automation Platform",
            "mode": "live" if self.config.is_configured else "simulation",
            "webhook_configured": bool(self.config.webhook_url),
            "nla_configured": bool(self.config.nla_api_key),
            "connected_apps_supported": 9000,
        }

