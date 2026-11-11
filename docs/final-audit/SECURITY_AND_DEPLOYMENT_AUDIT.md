# PayPilot — Security & Render Cloud Deployment Audit

**Auditor:** Senior DevSecOps & FinTech Architecture Audit  
**Target Commit:** `86bcf85`  
**Date:** 2026-11-10T19:18:00+05:30  
**Scope:** Authentication, CORS, Credential Isolation, Render Blueprint, Database & Redis Settings.

---

## 1. Authentication Security Matrix

| Feature | Audit Finding | Fail-Closed Guardrail |
| :--- | :--- | :--- |
| **Production Auth Mode** | Requires `AUTH_MODE=jwt` | `validate_production_security()` raises `ValueError` if `AUTH_MODE != 'jwt'` in production. |
| **Cryptographic JWT Verification** | Mandatory in production | Verified asymmetric RS256 JWKS tokens using `JWKSTokenVerifier` against `AUTH_JWKS_URL`. Symmetric key confusion is rejected. |
| **Demo Authentication** | Active in `ENVIRONMENT=staging/development` | Allows `x-demo-user-id` header or fallback to `guest_user`. **Must NOT be represented as enterprise production auth.** |
| **User Isolation** | Enforced across all repositories | `order.user_id == current_user.id` and `plan.user_id == current_user.id`. Cross-user access attempts return HTTP 403 Forbidden. |

---

## 2. CORS & Network Boundaries

- **Configured Origins:** Explicitly restricted to `http://localhost:3000`, `http://127.0.0.1:3000`, and `https://paypilot-frontend.onrender.com`.
- **Wildcard Rejection:** `validate_production_security()` explicitly checks `any("*" in o for o in self.ALLOWED_ORIGINS)` and rejects startup if wildcards are detected.
- **Request ID Tracking:** Every request receives a unique UUIDv4 `X-Request-ID` correlation header via `RequestIDMiddleware` for auditability.

---

## 3. Credential & Secret Management

- **Fail-Closed Secrets:** `PAYPAL_CLIENT_SECRET`, `LLM_API_KEY`, and `CHANNEL3_API_KEY` are never committed to git (`.gitignore` protects all `.env*` files).
- **Log Hygiene:** PayPal Orders API v2 logging records only sanitized Order IDs (e.g. `2RR4654859131563D`) and status codes; bearer tokens and client secrets are stripped.
- **Evidence Sanitization:** `docs/final-audit/paypal-live-verification.json` records only public transaction hashes, amounts, and approval URLs.

---

## 4. Render Infrastructure-as-Code (`render.yaml`) Audit

| Service Component | Configuration in `render.yaml` | Validation Result |
| :--- | :--- | :--- |
| **Backend Web Service** | `paypilot-backend` (Python 3.11, Uvicorn, port `$PORT`) | **VALID** — Health check `/health` |
| **Frontend Web Service** | `paypilot-frontend` (Next.js 14, Node 20, standalone build) | **VALID** — Target URL bound |
| **Outbox Background Worker** | `paypilot-outbox-worker` (`python -m backend.app.workers.outbox_worker`) | **VALID** — Background outbox dispatch |
| **Managed PostgreSQL** | `paypilot-db` (Starter plan, PostgreSQL 16) | **VALID** — Bound via `connectionString` |
| **Managed Redis** | `paypilot-redis` (Starter plan, `allkeys-lru`) | **VALID** — Bound via `connectionString` |

---

## 5. Deployment Reality & Distinction

1. **Locally Validated Configuration:** `render.yaml` syntax, environment variable bindings, and database configurations pass strict schema validation.
2. **Staging vs. Production Disclosure:** The Render blueprint is configured with `ENVIRONMENT=staging` and `AUTH_MODE=demo` so hackathon judges can evaluate the app immediately without configuring an enterprise OIDC Auth0 tenant.
3. **Cloud Live Health Check Status:** Live external verification of `https://paypilot-backend.onrender.com/health` requires active deployment credentials on Render; local testing verifies the server runs identically on `http://127.0.0.1:8000/health` (HTTP 200 OK).

