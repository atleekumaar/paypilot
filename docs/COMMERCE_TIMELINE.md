# PayPilot — Commerce Timeline Architecture & Operation Guide

## 1. Executive Summary

PayPilot features an end-to-end **Commerce Timeline** (`/timeline`) powered by **Bryntum** scheduling semantics and observed via **Astropods**.

This system bridges conversational shopping with transparent operational logistics by mapping every transaction lifecycle event from multi-turn agent intent formulation to delivery and refund settlement.

---

## 2. Temporal Commerce Lifecycle

```
[Agent Turn]
  │
  ├── 1. APPROVAL
  │     └─ Purchase plan approved by human buyer ($1,499.00)
  │
  ├── 2. PAYMENT
  │     └─ PayPal Orders v2 Sandbox payment captured
  │
  ├── 3. FULFILLMENT
  │     └─ Merchant inventory reserved & packaging initialized
  │
  ├── 4. IN_TRANSIT
  │     └─ Carrier logistics dispatch (FedEx / FastShip / UPS)
  │
  ├── 5. DELIVERY
  │     ├─ Estimated Milestone (Dashed, predicted via delivery SLA)
  │     └─ Confirmed Delivery (Solid, signed proof of delivery)
  │
  └── 6. REFUND (Optional)
        └─ Official PayPal capture refund processed on ledger
```

---

## 3. Core Features

### 3.1 Interactive Tracks & Lanes
- Orders are mapped as distinct scheduling tracks with product titles, order references, total dollar amounts, and real-time status badges.
- Users can filter tracks by milestone type (`APPROVAL`, `PAYMENT`, `FULFILLMENT`, `IN_TRANSIT`, `DELIVERY`, `REFUND`) or search by order reference and tracking number.

### 3.2 Authoritative Milestone Inspector
- Clicking any milestone populates the side inspector with authoritative metadata:
  - Timestamp ranges (Start and Target/Completion).
  - Provider details (PayPal Order ID, Capture ID).
  - Logistics info (Carrier, Tracking Number, Last Reported Hub Location).

### 3.3 Astropods Control Plane & Safety Panel
- Embedded directly alongside the timeline tracks, showing real-time agent turn counts, tool execution spans, average turn latencies, and active guardrail status (Secret Redaction & Human-in-the-Loop).

### 3.4 Conversational Agent Integration
- Users can ask natural language questions in the chat interface:
  - *"What is my delivery schedule?"*
  - *"Show my upcoming order milestones"*
  - *"When will my NovaBook arrive?"*
- The AI agent invokes `query_commerce_timeline` and summarizes nearest delivery dates and link to `/timeline`.

---

## 4. Verification

- Backend automated test suite: `backend/tests/test_timeline.py` (100% pass).
- Frontend static typing: `tsc --project frontend/tsconfig.json --noEmit` (0 errors).

