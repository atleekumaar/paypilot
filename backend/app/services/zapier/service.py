"""Zapier Workflow Service.

Orchestrates post-purchase automated operations across connected business apps:
- Auto-invoice generation in accounting (QuickBooks/Xero)
- Customer order receipt dispatch via Gmail
- Transaction recording into Google Sheets
- Merchant support alert notification via Slack
"""

import logging
from typing import Any, Dict, Optional
from app.services.zapier.client import ZapierClient, ZapierDispatchResult

logger = logging.getLogger(__name__)


class ZapierAutomationService:
    """Service orchestrating business automations through Zapier."""

    def __init__(self, client: Optional[ZapierClient] = None):
        self.client = client or ZapierClient()

    def dispatch_order_completed(
        self,
        order_id: str,
        user_id: str,
        amount: float,
        currency: str,
        product_name: str,
        paypal_capture_id: str,
    ) -> ZapierDispatchResult:
        """Trigger post-capture automations across QuickBooks, Gmail, and Google Sheets."""
        payload = {
            "order_id": order_id,
            "user_id": user_id,
            "product_name": product_name,
            "total_amount": amount,
            "currency": currency,
            "paypal_capture_id": paypal_capture_id,
            "status": "COMPLETED",
            "action_targets": [
                "accounting_invoice_created",
                "google_sheets_row_appended",
                "customer_receipt_emailed",
            ],
        }
        logger.info(f"Zapier: Dispatching order_completed event for order {order_id}")
        return self.client.dispatch_webhook("order_completed", payload)

    def dispatch_refund_alert(
        self,
        order_id: str,
        user_id: str,
        refund_amount: float,
        reason: str,
        paypal_refund_id: str,
    ) -> ZapierDispatchResult:
        """Trigger refund alert to Slack and update ledger."""
        payload = {
            "order_id": order_id,
            "user_id": user_id,
            "refund_amount": refund_amount,
            "reason": reason,
            "paypal_refund_id": paypal_refund_id,
            "status": "REFUNDED",
            "action_targets": [
                "slack_support_alert_sent",
                "crm_status_updated",
            ],
        }
        logger.info(f"Zapier: Dispatching refund_alert event for order {order_id}")
        return self.client.dispatch_webhook("refund_processed", payload)

    def trigger_custom_action(self, event: str, payload: Dict[str, Any]) -> ZapierDispatchResult:
        """Allow AI agent to trigger user-specified automations."""
        return self.client.dispatch_webhook(event, payload)

    def health(self) -> Dict[str, Any]:
        return self.client.health()


_zapier_service_instance: Optional[ZapierAutomationService] = None


def get_zapier_service() -> ZapierAutomationService:
    global _zapier_service_instance
    if _zapier_service_instance is None:
        _zapier_service_instance = ZapierAutomationService()
    return _zapier_service_instance

