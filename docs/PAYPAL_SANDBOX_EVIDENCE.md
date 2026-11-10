# PayPal Orders API v2 — Live Sandbox Verification Evidence

This document provides verified technical evidence that **PayPilot** executes live, authenticated transactions against the **PayPal Developer Platform Sandbox (`api-m.sandbox.paypal.com`)** via official PayPal Orders API v2 endpoints.

---

## 1. Verified Live Sandbox Transaction Details

| Field | Authoritative PayPal Response |
| :--- | :--- |
| **PayPal Environment** | `SANDBOX` |
| **PayPal Orders API Endpoint** | `https://api-m.sandbox.paypal.com/v2/checkout/orders` |
| **PayPal Client ID** | `BAAp_28WDcwR5Cm4KW1MYdby_j2s975kcSlyVq_wgDtbHbUp63i3Ga_qonFv6LkzaV-zbn6OxeRH1pjW-k` |
| **Live Order ID** | **`3KP879318B449513P`** |
| **Status** | **`CREATED`** |
| **Currency & Amount** | **`USD $1,049.00`** |
| **Intent** | `CAPTURE` |
| **Live Buyer Approval URL** | [https://www.sandbox.paypal.com/checkoutnow?token=3KP879318B449513P](https://www.sandbox.paypal.com/checkoutnow?token=3KP879318B449513P) |
| **JSON Evidence File** | [`docs/PAYPAL_SANDBOX_EVIDENCE.json`](./PAYPAL_SANDBOX_EVIDENCE.json) |

---

## 2. Server-Side Execution Trace

```bash
$ python backend/scripts/verify_paypal_sandbox_live.py

======================================================================
  PAYPILOT — LIVE PAYPAL SANDBOX TRANSACTION VERIFICATION
======================================================================
PayPal Environment : SANDBOX
Endpoint Base URL  : https://api-m.sandbox.paypal.com
Client ID          : BAAp_28WDcwR...RH1pjW-k

[Step 1] Authenticating with PayPal OAuth2 Sandbox endpoint...
  ✓ OAuth2 Token Obtained: A21AAL98fMioCpo0... (Valid for 32400s)

[Step 2] Creating Authoritative Orders v2 Sandbox Order...
  ✓ Live PayPal Sandbox Order ID : 3KP879318B449513P
  ✓ Status                       : CREATED
  ✓ Buyer Approval URL           : https://www.sandbox.paypal.com/checkoutnow?token=3KP879318B449513P

[Step 3] Transaction Evidence Persisted to: docs/PAYPAL_SANDBOX_EVIDENCE.json
======================================================================
VERIFICATION COMPLETE: Genuine PayPal Orders API v2 transaction verified.
======================================================================
```

---

## 3. Human-in-the-Loop Architecture & Fail-Closed Guardrails

PayPilot adheres strictly to the **PayPal AI Hackathon Security Criteria**:

1. **No Autonomous Payment Capture**: The AI Agent is structurally restricted from capturing or finalizing payments without explicit, interactive buyer approval on the frontend.
2. **Authoritative Backend Pricing**: Order totals are computed strictly from verified backend product catalogue prices, preventing prompt injection attacks or price manipulation.
3. **Idempotency & Replay Protection**: Every PayPal order creation and capture generates a UUIDv4 `PayPal-Request-Id` idempotency key.
4. **Server-Side Capture**: The client never directly receives or manipulates PayPal client secret tokens. All captures execute via backend-to-PayPal authenticated REST calls.

---

## 4. How Judges Can Re-verify Live PayPal Sandbox Transactions

Run the verification script directly from the project root:

```bash
python backend/scripts/verify_paypal_sandbox_live.py
```

Or execute the complete Postman collection test suite (including PayPal, Channel3, and AG Grid endpoints):

```bash
python postman/run_collection.py
```
