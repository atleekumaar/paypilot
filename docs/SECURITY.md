# PayPilot — Application Security & Threat Model

## 1. Zero-Trust Identity & Authentication Model

### 1.1 Dual Authentication Modes
- **Production Mode (`AUTH_MODE=jwt`)**:
  - Requires cryptographically signed JWT tokens passed via `Authorization: Bearer <token>`.
  - Keys dynamically retrieved and cached from provider JWKS endpoint (`AUTH_JWKS_URL`).
  - Verifies token signature, expiration (`exp`), not-before (`nbf`), issuer (`iss`), audience (`aud`), and clock skew tolerance.
  - Fail-closed: In `ENVIRONMENT=production`, the application refuses to start unless JWKS URL, issuer, and RS256/ES256 algorithms are properly configured.
- **Development/Demo Mode (`AUTH_MODE=demo`)**:
  - Provides fallback for isolated local environments.
  - Rejects cross-user impersonation; strictly binds resources to the authenticated identity.

### 1.2 Resource Ownership Enforcement
- **Session Ownership**: An agent session created by User A cannot be accessed or modified by User B. Attempting to pass another user's session ID returns `HTTP 403 Forbidden`.
- **Purchase Plan Ownership**: Payments can only be created and captured for plans owned by the authenticated caller.
- **Order and Tracking Isolation**: Endpoints `/api/orders`, `/api/orders/{id}`, and `/api/notifications` strictly filter by `current_user.id`. Client-provided `user_id` query parameters are cross-checked against the authenticated identity via `verify_user_ownership()`.

---

## 2. Payment Security & Integrity

- **Never Trust Client Pricing**: The client cannot specify transaction amounts. All order totals, tax, and delivery charges are calculated server-side from authoritative database records.
- **Price Revalidation**: If a product price changes between plan formulation and user checkout, the plan reverts to `AWAITING_APPROVAL` and requires explicit re-approval.
- **Approval Gate**: Checkout initiation strictly rejects any purchase plan whose status is not `APPROVED`.
- **State Machine Integrity**: Transitions from `APPROVAL_PENDING` -> `CAPTURE_PENDING` -> `COMPLETED`. Double-captures are prevented via atomic checks and database constraints.
- **Webhook Replay Protection**: Incoming PayPal webhooks are deduplicated against the `webhook_events` table before processing.

---

## 3. Agent Execution & Tool Safety

- **Strict Tool Schemas**: Every tool exposed to the agent planner validates arguments using Pydantic schemas. Unexpected or malformed arguments cause immediate tool rejection.
- **Execution Budgets**: Max turn count per session prevents runaway recursion or infinite tool loops.
- **Session Expiry**: Sessions inactive for > 24 hours are automatically marked `FAILED`.
- **Prompt Injection Defense**: Multi-pattern regex heuristics screen for prompt injection, system prompt exfiltration, and jailbreak attempts before passing instructions to the planner.
- **Audit Logging**: Every tool execution, its arguments, and its return values are recorded to `tool_audit_logs`.

---

## 4. Network & Transport Security

- **CORS Whitelist**: Explicitly restricts origins to configured domains (e.g., `http://localhost:3000`). Wildcard `*` origins with credentials are expressly prohibited.
- **Traceability**: All requests are assigned a unique `X-Request-ID` via middleware and echoed in responses for audit trails.

