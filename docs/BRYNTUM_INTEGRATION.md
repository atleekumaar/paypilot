# Bryntum-Compatible Commerce Lifecycle Scheduler

PayPilot implements an authoritative, event-driven **Commerce Lifecycle Scheduler** architected directly against the **Bryntum Scheduler Pro Data Model** (`ResourceStore` + `EventStore` JSON schema).

---

## 1. Architectural Design & Philosophy

Bryntum Scheduler Pro is the industry standard for complex interactive scheduling, Gantt milestones, and chronological event orchestration.

In open-source and hackathon CI/CD environments, installing commercial `@bryntum/*` packages requires private authentication tokens (`@bryntum:registry https://npm.bryntum.com`). To allow **zero-friction cloning, continuous integration in GitHub Actions, and one-click cloud deployment on Render/Vercel**, PayPilot implements:

1. **Bryntum Store Schema Compatibility**: Full 1:1 mapping of commerce resources (`TimelineResource`) and chronological events (`TimelineEvent`) matching Bryntum Scheduler Pro's data stores.
2. **Server-Side Milestone Generation**: Backend `TimelineService` computes dependency chains:
   $$\text{User Intent} \longrightarrow \text{Purchase Approval} \longrightarrow \text{PayPal Capture} \longrightarrow \text{Merchant Dispatch} \longrightarrow \text{Carrier Transit} \longrightarrow \text{Delivery}$$
3. **Interactive Gantt Lanes**: The frontend scheduler ([`BryntumCommerceScheduler.tsx`](../frontend/components/timeline/BryntumCommerceScheduler.tsx)) renders Gantt milestone progress, carrier tracking scans, delay flags, and time intervals.
4. **Bryntum Export/Import Interoperability**: Generates JSON exports directly consumable by any Bryntum Scheduler Pro or Bryntum Gantt enterprise instance.

---

## 2. Bryntum Data Schema Mapping

```typescript
// Matches Bryntum ResourceModel
interface TimelineResource {
  id: string;               // Unique order/item ID
  name: string;             // Product Title (e.g. "NovaBook Pro 14")
  orderId: string;          // Authoritative order identifier
  brand?: string;           // Merchant / Brand
  amount: number;           // Settlement value
  currency: string;         // Currency code (e.g. "USD")
  status: string;           // IN_TRANSIT, DELIVERED, PROCESSING
  carrier?: string;         // Logistics provider (FedEx, UPS, DHL)
  trackingNumber?: string;  // Carrier tracking code
}

// Matches Bryntum EventModel
interface TimelineEvent {
  id: string;               // Unique milestone event ID
  resourceId: string;       // Foreign key referencing TimelineResource.id
  name: string;             // Event title ("PayPal Capture Completed", "Carrier In-Transit")
  startDate: string;        // ISO 8601 start timestamp
  endDate: string;          // ISO 8601 completion timestamp
  eventType: "APPROVAL" | "PAYMENT" | "FULFILLMENT" | "IN_TRANSIT" | "DELIVERY" | "REFUND";
  status: string;           // COMPLETED, IN_PROGRESS, DELAYED, SCHEDULED
  isEstimated: boolean;     // Whether the milestone is predictive or authoritative
  eventColor: string;       // Hex / Tailwind color matching milestone type
  iconCls?: string;         // Icon descriptor
  metadata?: Record<string, any>;
}
```

---

## 3. Endpoints & Verification

The scheduler is backed by:
- `GET /api/timeline/events`: Fetches live Bryntum-compatible `resources` and `events` JSON data stores.
- `GET /api/timeline/summary`: Returns milestone telemetry, active carrier tracking, and countdowns to next delivery.

Both endpoints are validated continuously in PayPilot's automated test suite:
```bash
pytest backend/tests/test_timeline.py -v
```
And verified via Postman test runner:
```bash
python postman/run_collection.py
```
