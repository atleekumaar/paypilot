# PayPilot API Specifications & APIMatic Grounding

This directory houses the machine-readable API contracts and APIMatic metadata configurations that ground coding agents and developers working on PayPilot.

---

## Directory Organization

```
docs/api-specs/
├── paypal/
│   ├── checkout_orders_v2.json     # Official PayPal Orders API v2 OpenAPI 3.0 specification
│   ├── payments_payment_v2.json    # Official PayPal Payments API v2 OpenAPI 3.0 specification
│   └── APIMATIC-META.json          # APIMatic import, export, and code generation settings
├── paypilot/
│   ├── paypilot_openapi.json       # PayPilot backend FastAPI OpenAPI 3.1 specification (27 endpoints)
│   └── APIMATIC-META.json          # APIMatic configuration for PayPilot internal services
└── README.md                       # This reference document
```

---

## Specification Sources & Provenance

### 1. PayPal Orders API v2 (`paypal/checkout_orders_v2.json`)
- **Source**: Official PayPal specification repository ([paypal/paypal-rest-api-specifications](https://github.com/paypal/paypal-rest-api-specifications)).
- **Scope**: Defines operations for `/v2/checkout/orders`:
  - `POST /v2/checkout/orders` (Order Creation)
  - `GET /v2/checkout/orders/{id}` (Order Details)
  - `POST /v2/checkout/orders/{id}/capture` (Order Payment Capture)
  - `POST /v2/checkout/orders/{id}/authorize` (Order Payment Authorization)
  - `PATCH /v2/checkout/orders/{id}` (Order Updates)
- **Use in PayPilot**: Used by `backend/app/services/paypal/orders.py` and `backend/app/api/payments.py` to ensure request payloads (intent, purchase_units, amount formatting) and response schemas match PayPal's authoritative contracts.

### 2. PayPal Payments API v2 (`paypal/payments_payment_v2.json`)
- **Source**: Official PayPal specification repository ([paypal/paypal-rest-api-specifications](https://github.com/paypal/paypal-rest-api-specifications)).
- **Scope**: Defines operations for `/v2/payments`:
  - `GET /v2/payments/captures/{capture_id}` (Capture Details)
  - `POST /v2/payments/captures/{capture_id}/refund` (Capture Refund)
  - `GET /v2/payments/authorizations/{authorization_id}` (Authorization Details)

### 3. PayPilot Application API (`paypilot/paypilot_openapi.json`)
- **Source**: Auto-generated directly from PayPilot's FastAPI application models (`app.openapi()`).
- **Scope**: Covers all 27 PayPilot internal endpoints across:
  - Discovery & Search (`/api/discovery/search`, `/api/products`)
  - Purchase Plans (`/api/purchase-plans`)
  - Payments & Webhooks (`/api/payments/paypal/*`)
  - Autonomous Agent (`/api/agent/*`)
  - Order Tracking & Carrier Milestones (`/api/orders/*`)
  - Notifications (`/api/notifications/*`)

---

## APIMatic Integration (`APIMATIC-META.json`)

Each specification directory is accompanied by an `APIMATIC-META.json` file. This is the official APIMatic metadata format used by the APIMatic platform, APIMatic CLI, and APIMatic Validator to:
1. Control code-generation behaviors without mutating the raw OpenAPI specifications.
2. Specify naming conventions, parameter orders, and type interfaces.
3. Configure authentication bindings and operational overrides.

---

## How Coding Agents Use These Specs

When an AI coding assistant (Antigravity, Cursor, Claude Code, VS Code) works on payment flows:
1. The agent first queries the **APIMatic ContextMatic MCP** tools (`endpoint_search`, `model_search`, `ask`) using `key="paypal"` for idiomatic SDK signatures and patterns.
2. The agent cross-checks parameters against `docs/api-specs/paypal/checkout_orders_v2.json` to verify field formats (e.g. `currency_code`, 2-decimal string format for monetary values, application context).
3. The agent validates that PayPilot's internal endpoints in `docs/api-specs/paypilot/paypilot_openapi.json` remain backwards-compatible with frontend clients.
