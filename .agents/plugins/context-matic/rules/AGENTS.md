# PayPilot Agent Instructions & APIMatic Context Guidelines

## 1. APIMatic Context Integration
When developing, extending, or debugging PayPal or third-party API integrations in PayPilot, ALWAYS leverage APIMatic ContextMatic rather than guessing API contracts or relying on potentially stale training data:
- Use the **ContextMatic MCP server** tools (`fetch_api`, `ask`, `endpoint_search`, `model_search`).
- For PayPal endpoints, the official ContextMatic API key is `paypal` (PayPal Server SDK).
- Language context: Use `python` for backend API implementations and `typescript` for Next.js frontend checkout components.

## 2. Grounding in Official PayPal Specifications
PayPilot maintains offline OpenAPI 3.0 contracts and APIMatic metadata under `docs/api-specs/`:
- `docs/api-specs/paypal/checkout_orders_v2.json`: Authoritative schema for PayPal Orders API v2 (`/v2/checkout/orders` create, get, capture).
- `docs/api-specs/paypal/payments_payment_v2.json`: Authoritative schema for PayPal Payments API v2.
- `docs/api-specs/paypal/APIMATIC-META.json`: APIMatic metadata configuration for PayPal API specs.
- `docs/api-specs/paypilot/paypilot_openapi.json`: Internal PayPilot FastAPI contracts.

Always cross-reference these files to verify field names, required parameters, and response structures.

## 3. PayPilot Payment Architecture Guardrails
Under no circumstances should any coding agent modify the following security and architectural rules:
- **Price Integrity**: All payment amounts are determined authoritatively from the internal `PurchasePlan` on the backend. Client-submitted prices are strictly prohibited.
- **Explicit Approval Gate**: `create_paypal_order` requires explicit human approval (`APPROVAL_REQUIRED`).
- **Idempotent Capture**: Payment captures must verify that the incoming PayPal Order ID matches the approved Purchase Plan before executing capture.
- **Credential Protection**: Never hardcode or log PayPal client credentials or access tokens.
