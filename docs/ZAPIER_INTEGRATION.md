# PayPilot — Zapier Multi-App Workflow Integration

## 1. Overview
[Zapier](https://paypalaihackathon.devpost.com/details/zapier) enables AI agents and commerce systems to trigger automated workflows across **9,000+ connected business applications**.

In PayPilot, Zapier powers the **Post-Purchase Operations & Multi-App Automation Pipeline**:
- **Accounting & Invoicing:** Dispatches transaction details to QuickBooks/Xero upon successful PayPal payment capture.
- **Ledger Recording:** Automatically appends an immutable transaction row to Google Sheets.
- **Customer Communications:** Sends formatted order confirmations and receipts via Gmail.
- **Merchant Incident Response:** Emits real-time Slack notifications to the support channel when refunds or delivery delays occur.
- **Agentic Automation Tool:** The Groq Commerce Agent can execute `trigger_zapier_automation` to coordinate external workflows.
- **Zapier MCP / AI Actions:** Provides `.zapier/mcp_config.json` enabling Zapier Central and AI agents to orchestrate PayPilot.

---

## 2. Architecture & Trigger Flow

```
                      +---------------------------------------+
                      |   PayPal Sandbox Capture (Order v2)  |
                      +---------------------------------------+
                                          |
                      +---------------------------------------+
                      |      CheckoutService.capture()        |
                      +---------------------------------------+
                                          |
                      +---------------------------------------+
                      |   ZapierAutomationService.dispatch()  |
                      +---------------------------------------+
                                          |
                      +---------------------------------------+
                      |       Zapier Webhook Endpoint         |
                      +---------------------------------------+
                           /              |              \
                          v               v               v
                   +------------+  +-------------+  +------------+
                   | QuickBooks |  |Google Sheets|  |   Gmail    |
                   | (Invoice)  |  |  (Ledger)   |  | (Receipt)  |
                   +------------+  +-------------+  +------------+
```

### Key Modules:
- `backend/app/services/zapier/client.py`: Webhook dispatcher and Natural Language Actions client.
- `backend/app/services/zapier/service.py`: Domain methods `dispatch_order_completed()`, `dispatch_refund_alert()`, `trigger_custom_action()`.
- `backend/app/api/zapier.py`: API routes `POST /api/zapier/dispatch`, `POST /api/zapier/webhook`, `GET /api/zapier/health`.
- `.zapier/mcp_config.json`: Specification describing PayPilot endpoints for Zapier AI Actions and MCP.
- `backend/app/agents/tools.py`: Agent tool `trigger_zapier_automation` (`ToolPermission.WRITE`).

---

## 3. Environment Configuration

Add the following to `.env`:
```ini
# Zapier Automation
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/your_webhook_id/
ZAPIER_NLA_API_KEY=your_zapier_nla_key_here
```

*Note: If `ZAPIER_WEBHOOK_URL` is omitted, PayPilot automatically operates in simulation mode (`SUCCESS_SIMULATED`), logging multi-app target dispatches with zero runtime failures.*

---

## 4. Verification & Testing

Run unit and agent execution tests:
```powershell
python -m pytest backend/tests/test_zapier.py -v
```
All 5 Zapier tests verify:
1. Webhook configuration detection.
2. Post-capture dispatch with multi-app targets (Gmail, Sheets, QuickBooks).
3. Post-refund alert dispatch to Slack support.
4. Health endpoint check.
5. Autonomous agent tool execution.

