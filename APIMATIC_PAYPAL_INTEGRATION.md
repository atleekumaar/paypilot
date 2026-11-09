# PayPilot — APIMatic PayPal Context Plugin & API Integration Review

## 1. Overview & Award Alignment

PayPilot integrates the **APIMatic PayPal Context Plugin** into the development and agentic architecture to ensure 100% adherence to authoritative PayPal API contracts.

- **Award Category:** APIMatic PayPal Context Plugin Integration
- **Target APIs:** PayPal Orders API v2, Payments Captures API v2, Payments Refund API v2, Webhooks Verification API v1
- **Environment:** PayPal Sandbox (`https://api.sandbox.paypal.com`)
- **Plugin Configuration:** `.apimatic/context.json`

---

## 2. Mandatory Context Plugin Configuration

The APIMatic PayPal Context Plugin was configured to provide AI coding agents and autonomous orchestrators with deterministic schemas and API behavioral contracts:

```json
{
  "$schema": "https://apimatic.io/schemas/context-plugin.json",
  "name": "apimatic-paypal-context-plugin",
  "version": "1.0.0",
  "provider": "PayPal",
  "environment": "sandbox",
  "auth": {
    "type": "oauth2",
    "token_endpoint": "/v1/oauth2/token",
    "grant_type": "client_credentials"
  }
}
```

---

## 3. PayPal Operations Reviewed & Improved with APIMatic Guidance

Using the APIMatic Context Plugin's specifications, the PayPilot development workflow audited and hardened the following critical operations:

### 1. OAuth 2.0 Client Credentials Flow
- **Endpoint:** `POST /v1/oauth2/token`
- **Audit Finding:** Token expiration must be cached and preemptively refreshed 60 seconds prior to expiration to avoid in-flight checkout race conditions.
- **Implementation:** `backend/app/services/paypal/auth.py` with automatic expiration buffer.

### 2. Order Creation with Authoritative Backend Pricing
- **Endpoint:** `POST /v2/checkout/orders`
- **APIMatic Contract Rule:** Amounts must be derived strictly from server-side purchase plans with exact 2-decimal formatting (`val_str = f"{plan.total_amount:.2f}"`) and matching ISO currency (`USD`).
- **Idempotency:** Unique order reference passed in `reference_id` and authoritative `intent: "CAPTURE"`.
- **Implementation:** `backend/app/services/paypal/orders.py:create_order`.

### 3. Server-Side Payment Capture
- **Endpoint:** `POST /v2/checkout/orders/{id}/capture`
- **Security Rule:** Never trust client-side return URLs. Must fetch `GET /v2/checkout/orders/{id}` first to verify buyer approval (`status == "APPROVED"`) and exact amount before executing capture.
- **Transit State:** Pre-persisted as `CAPTURE_PENDING` before external API call to eliminate distributed double-capture risks.
- **Implementation:** `backend/app/services/checkout_service.py:capture_paypal_payment`.

### 4. Official Capture Refund with Persistent Ledger
- **Endpoint:** `POST /v2/payments/captures/{capture_id}/refund`
- **APIMatic Contract Rule:** Requires `PayPal-Request-Id` idempotency header.
- **Financial Correctness:** Replaced simulated refund with official PayPal capture refund endpoint. Persists a durable `RefundAttemptModel` and verifies cumulative balance (`completed + requested <= amount`) with `Decimal` arithmetic.
- **Ambiguous Timeout Safety:** Network timeouts transition attempt to `RECONCILIATION_REQUIRED` without assuming success.
- **Implementation:** `backend/app/services/checkout_service.py:refund_payment`.

### 5. Webhook Signature Cryptographic Verification
- **Endpoint:** `POST /v1/notifications/verify-webhook-signature`
- **Security Rule:** Fail-closed signature verification.
- **Implementation:** Passes 5 normalized headers (`paypal-auth-algo`, `paypal-cert-url`, `paypal-transmission-id`, `paypal-transmission-sig`, `paypal-transmission-time`), target `webhook_id`, and `webhook_event` payload. Rejects any unverified event.
- **Implementation:** `backend/app/services/paypal/orders.py:verify_webhook_signature`.

---

## 4. Architectural Verification Summary

| Operation | Method & Endpoint | APIMatic Validation | Verification Status |
| :--- | :--- | :--- | :--- |
| **OAuth2 Token** | `POST /v1/oauth2/token` | Cached & buffered token renewal | ✅ Tested & Passing |
| **Create Order** | `POST /v2/checkout/orders` | Authoritative pricing & schema | ✅ Tested & Passing |
| **Verify Order** | `GET /v2/checkout/orders/{id}` | Server-side verification | ✅ Tested & Passing |
| **Capture Order** | `POST /v2/checkout/orders/{id}/capture` | Idempotent capture coordination | ✅ Tested & Passing |
| **Capture Refund** | `POST /v2/payments/captures/{id}/refund` | Stable idempotency key & Decimal ledger | ✅ Tested & Passing |
| **Verify Webhook** | `POST /v1/notifications/verify-webhook-signature` | Cryptographic fail-closed validation | ✅ Tested & Passing |

