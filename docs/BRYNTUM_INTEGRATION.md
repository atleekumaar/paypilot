# PayPilot — Bryntum Commerce Timeline Integration

## 1. Overview & Objective

PayPilot integrates **Bryntum** scheduling and timeline visualization principles to deliver an interactive **Commerce Operations Timeline** (`/timeline`).

While traditional e-commerce platforms show static, isolated order lists, PayPilot's Bryntum integration models the dynamic temporal lifecycle of autonomous purchases:
- Customer intent & Agent purchase plan approval.
- PayPal transaction authorization and capture.
- Merchant fulfillment, packing, and carrier dispatch.
- Logistics in-transit tracking across intermediate carrier hubs.
- Guaranteed delivery milestones vs. estimated target dates.
- Partial and full refund adjustments on the payment ledger.

---

## 2. Bryntum Data Architecture

The timeline service (`backend/app/services/timeline_service.py`) formats real-time commerce data into Bryntum Scheduler data stores:

### 2.1 Resources (Schedule Tracks)
Each active or historical order is represented as a resource row:
```json
{
  "id": "res_ORD-001",
  "name": "NovaBook Pro 16",
  "orderId": "ORD-001",
  "brand": "NovaTech",
  "amount": 1499.00,
  "currency": "USD",
  "status": "PROCESSING",
  "carrier": "FastShip Logistics",
  "trackingNumber": "TRK-FAST-884210"
}
```

### 2.2 Events (Lifecycle Milestones)
Each milestone occupies a temporal segment on the order's track:
```json
{
  "id": "evt_trn_ORD-001",
  "resourceId": "res_ORD-001",
  "name": "FastShip Logistics: In Transit",
  "startDate": "2026-10-14T11:45:00Z",
  "endDate": "2026-10-18T18:00:00Z",
  "eventType": "IN_TRANSIT",
  "status": "IN_TRANSIT",
  "isEstimated": false,
  "eventColor": "#8B5CF6",
  "metadata": {
    "carrier": "FastShip Logistics",
    "trackingNumber": "TRK-FAST-884210",
    "lastLocation": "Columbus OH Facility"
  }
}
```

---

## 3. Milestones & Visual State Encoding

| Event Type | Color | Badge | Semantics |
|---|---|---|---|
| **APPROVAL** | `#10B981` (Emerald) | `CONFIRMED` | Purchase plan formulated & approved by user |
| **PAYMENT** | `#3B82F6` (Blue) | `CONFIRMED` | PayPal sandbox payment captured |
| **FULFILLMENT**| `#6366F1` (Indigo) | `CONFIRMED` | Merchant packaging & inventory reserved |
| **IN_TRANSIT** | `#8B5CF6` (Purple) | `CONFIRMED` | Handed over to freight/logistics carrier |
| **DELIVERY** | `#059669` (Green) | `CONFIRMED` / `ESTIMATED` | Actual delivery completed vs. predicted arrival |
| **REFUND** | `#EF4444` (Red) | `CONFIRMED` | Authoritative PayPal capture refund ledger entry |

### Confirmed vs. Estimated Distinction
Bryntum milestone bars explicitly highlight `isEstimated: true` for pending delivery dates calculated from shipping carrier SLAs (`delivery_days`), preventing customer confusion.

---

## 4. Next.js 14 SSR-Safe Architecture

Bryntum scheduling components manipulate DOM canvas and window objects. In Next.js 14 App Router, this requires an SSR-safe dynamic loading pattern:

```tsx
// frontend/components/timeline/BryntumTimelineWrapper.tsx
const DynamicBryntumScheduler = dynamic(
  () => import("./BryntumCommerceScheduler"),
  {
    ssr: false,
    loading: () => <TimelineLoadingSkeleton />,
  }
);
```

This guarantees:
1. Zero server-side hydration mismatches.
2. Clean static code generation (`next build` succeeds with zero errors).
3. Client-side state hydration once window and canvas are available.

---

## 5. Agent Integration: `query_commerce_timeline`

PayPilot's conversational AI agent is equipped with the `query_commerce_timeline` tool (`backend/app/agents/tools.py`):
- Natural language queries such as *"What is my delivery schedule?"*, *"Show my commerce milestones"*, or *"When will my orders arrive?"* automatically invoke the tool.
- The tool queries `TimelineService.get_timeline()` and returns structured schedule metadata.
- The Post-Purchase Agent summarizes active shipments, upcoming dates, and directs the user to the `/timeline` interactive route.

---

## 6. Verification & Test Coverage

- Backend: `backend/tests/test_timeline.py` (9 tests passing).
  - Resource schema validation.
  - Event schema validation.
  - Filtering by event type (`PAYMENT`, `DELIVERY`, etc.).
  - Date boundary checks.
  - User isolation guarantees.
- Frontend: Next.js 14 App Router route `/timeline` verified via production build.

