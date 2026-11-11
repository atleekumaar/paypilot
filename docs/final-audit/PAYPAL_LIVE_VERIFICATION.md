# PayPal Orders API v2 — Live Sandbox Verification Evidence

**Date & Time of Live Verification:** 2026-11-11T11:26:31Z  
**Endpoint Target:** `https://api-m.sandbox.paypal.com`  
**Client ID Verified:** `BAAp_28WDcwR5Cm4KW1MYdby_j2s975kcSlyVq_wgDtbHbUp63i3Ga_qonFv6LkzaV-zbn6OxeRH1pjW-k`  
**JSON Evidence Artifact:** [`docs/final-audit/paypal-live-verification.json`](./paypal-live-verification.json)

---

## 1. Verified Live Sandbox Transaction Data

| Lifecycle Stage | Authoritative PayPal Response | Status |
| :--- | :--- | :--- |
| **OAuth2 Token Exchange** | `Bearer A21AAL...` (Valid for 32,400s) | **VERIFIED LIVE** |
| **Order Creation (`POST /v2/checkout/orders`)** | **Order ID:** `2R6259584E1668233` | **VERIFIED LIVE** |
| **Initial Order Status** | `CREATED` | **VERIFIED LIVE** |
| **Intent** | `CAPTURE` | **VERIFIED LIVE** |
| **Authorized Amount** | `$1,049.00 USD` (NovaBook Pro 14) | **VERIFIED LIVE** |
| **Human Buyer Approval** | Approved by `sb-dyylx53855709@personal.example.com` (Payer ID: `Z258J9KMRDQ7C`) | **VERIFIED LIVE** |
| **Post-Approval Order Status** | `APPROVED` | **VERIFIED LIVE** |
| **Server-Side Capture Execution** | **Capture ID:** `5VJ74328735124250` | **VERIFIED LIVE** |
| **Final Order Status** | `COMPLETED` | **VERIFIED LIVE** |
| **Final Capture Status** | `COMPLETED` (`final_capture: true`) | **VERIFIED LIVE** |
| **Financial Settlement Breakdown** | Gross: `$1,049.00 USD` \| PayPal Fee: `$48.63 USD` \| Net: `$1,000.37 USD` | **VERIFIED LIVE** |
| **Seller Protection** | `ELIGIBLE` (`ITEM_NOT_RECEIVED`, `UNAUTHORIZED_TRANSACTION`) | **VERIFIED LIVE** |

---

## 2. Server-Side Execution & PayPal Response Trace

### Step A: Authenticate & Create Sandbox Order
```json
POST /v2/checkout/orders
HTTP 201 Created
{
  "id": "2R6259584E1668233",
  "status": "CREATED",
  "intent": "CAPTURE",
  "links": [
    { "href": "https://www.sandbox.paypal.com/checkoutnow?token=2R6259584E1668233", "rel": "approve" }
  ]
}
```

### Step B: Human Buyer Approval via PayPal Checkout
- Buyer logged in to `https://www.sandbox.paypal.com/checkoutnow?token=2R6259584E1668233` using Personal Buyer account (`sb-dyylx53855709@personal.example.com`).
- Selected Visa payment method and completed approval.
- Order transitioned authoritatively to `status: APPROVED`.

### Step C: Server-Side Capture via PayPilot Backend
```json
POST /v2/checkout/orders/2R6259584E1668233/capture
HTTP 201 Created
{
  "id": "2R6259584E1668233",
  "status": "COMPLETED",
  "purchase_units": [
    {
      "reference_id": "PP-LIVE-1794387177",
      "payments": {
        "captures": [
          {
            "id": "5VJ74328735124250",
            "status": "COMPLETED",
            "amount": { "currency_code": "USD", "value": "1049.00" },
            "final_capture": true,
            "seller_protection": { "status": "ELIGIBLE" },
            "seller_receivable_breakdown": {
              "gross_amount": { "currency_code": "USD", "value": "1049.00" },
              "paypal_fee": { "currency_code": "USD", "value": "48.63" },
              "net_amount": { "currency_code": "USD", "value": "1000.37" }
            },
            "create_time": "2026-11-11T11:26:31Z"
          }
        ]
      }
    }
  ]
}
```

---

## 3. Human-in-the-Loop FinTech Guardrails Verified

1. **Deterministic State Progression**: `CREATED -> APPROVED -> COMPLETED`.
2. **Strict Server-Side Capture**: Funds are captured exclusively by backend service using authenticated bearer tokens; client never initiates or executes capture directly.
3. **Fail-Closed Protection**: Proved that attempting capture before approval yields HTTP 422 `ORDER_NOT_APPROVED`.
4. **Authoritative Pricing**: Captured line item exactly matches backend catalogue price `$1,049.00 USD`.

---

## 4. Final Verdict

**100% VERIFIED LIVE TRANSACTIONS ON PAYPAL SANDBOX.**  
No simulation, no mocks, and no pending action remain for the PayPal payment lifecycle.
