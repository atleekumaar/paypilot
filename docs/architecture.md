# PayPilot — System Architecture

This document outlines the system architecture, service boundaries, data flows, state machines, and security invariants for **PayPilot**, an AI-powered commerce agent developed for the PayPal AI Hackathon.

---

## 1. High-Level Architecture Overview

PayPilot connects natural-language product discovery with human-in-the-loop purchase approvals and verified PayPal Sandbox checkouts.

```mermaid
flowchart TD
    User([User])
    
    subgraph Client ["Frontend Canvas (Next.js 14 / React 18 / Tailwind)"]
        UI_Search["Conversational Search Bar & Suggestion Chips"]
        UI_Results["AI Recommendations & Grounded 'Why This?'"]
        UI_Plan["Purchase Plan Confirmation Modal"]
        UI_PayPal["PayPal Sandbox Checkout & Smart Buttons"]
        UI_Receipt["Verified Payment Receipt & Status"]
    end

    subgraph BackendCore ["FastAPI Backend Architecture"]
        API_Discovery["/api/discovery/search"]
        API_Plans["/api/purchase-plans"]
        API_Payments["/api/payments/paypal/*"]
        
        IntentSvc["IntentService\n(Rule + Semantic Normalizer)"]
        SearchSvc["ProductSearchService\n(Strict Constraint Filters)"]
        RankSvc["ProductRankingService\n(0-100 Composite Formula)"]
        PlanSvc["PurchasePlanService\n(Price Integrity & Approval Gate)"]
        CheckoutSvc["CheckoutService\n(State Machine & Verification)"]
        
        Repo_Catalog[(Product Repository)]
        Repo_Plans[(Purchase Plan Repository)]
        Repo_Payments[(Payment Repository)]
    end

    subgraph ExternalServices ["External Commerce & Payment Providers"]
        PayPal_Auth["PayPal OAuth 2.0\n(/v1/oauth2/token)"]
        PayPal_Orders["PayPal Orders API v2\n(/v2/checkout/orders)"]
        PayPal_Capture["PayPal Order Capture\n(/v2/checkout/orders/{id}/capture)"]
    end

    User <--> UI_Search
    UI_Search --> API_Discovery
    API_Discovery --> IntentSvc --> SearchSvc <--> Repo_Catalog
    SearchSvc --> RankSvc --> UI_Results
    
    UI_Results --> UI_Plan
    UI_Plan --> API_Plans --> PlanSvc <--> Repo_Plans
    
    UI_Plan --> UI_PayPal
    UI_PayPal --> API_Payments --> CheckoutSvc
    CheckoutSvc <--> Repo_Payments
    CheckoutSvc --> PayPal_Auth
    CheckoutSvc --> PayPal_Orders
    CheckoutSvc --> PayPal_Capture
    CheckoutSvc --> UI_Receipt
```

---

## 2. Phase 3: PayPal Sandbox Checkout Flow

The complete end-to-end purchasing pipeline follows a strict multi-step sequence:

```text
                 USER
                   │
                   ▼
              NEXT.JS UI
                   │
                   ▼
          DISCOVERY API
                   │
                   ▼
           PRODUCT SELECTED
                   │
                   ▼
          PURCHASE PLAN
                   │
                   ▼
        EXPLICIT USER APPROVAL
                   │
                   ▼
         PAYPAL ORDER SERVICE
                   │
                   ▼
            PAYPAL SANDBOX
                   │
                   ▼
             CAPTURE
                   │
                   ▼
         PAYMENT VERIFICATION
                   │
                   ▼
          SUCCESS CONFIRMATION
```

---

## 3. Payment & Purchase Plan State Machine

State transitions are strictly validated. Invalid transitions are rejected by the backend:

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> AWAITING_APPROVAL : Plan Formulated
    AWAITING_APPROVAL --> APPROVED : User Explicit Approval
    AWAITING_APPROVAL --> CANCELLED : User Dismisses
    
    APPROVED --> PAYPAL_APPROVAL_PENDING : PayPal Order Created
    PAYPAL_APPROVAL_PENDING --> PAYPAL_APPROVED : Buyer Authorizes
    PAYPAL_APPROVAL_PENDING --> FAILED : Payment Aborted
    
    PAYPAL_APPROVED --> CAPTURED : Server-side API Capture
    CAPTURED --> COMPLETED : Payment Verified
    
    COMPLETED --> [*]
    FAILED --> [*]
```

---

## 4. Critical Security & Integrity Invariants

1. **Backend Authoritative Pricing (No Client Price Trust)**:
   - When creating a `PurchasePlan`, the client sends only `product_id` and `quantity`.
   - The backend looks up the authoritative price directly from the verified product catalog.
   - Any price submitted by the frontend is strictly ignored.

2. **Explicit User Approval Gate**:
   - Selecting a product **never** initiates payment or order creation automatically.
   - The purchase plan requires explicit user confirmation via `POST /api/purchase-plans/{id}/approve` before a PayPal order can be initialized.
   - Calling `/api/payments/paypal/create-order` on an unapproved plan is rejected with `HTTP 400 Bad Request`.

3. **Order Ownership Verification (Mismatch Protection)**:
   - When `/api/payments/paypal/capture` is invoked, the backend verifies that `paypal_order_id` belongs strictly to the designated `purchase_plan_id`.
   - Attempting to capture with a mismatched or stolen order ID fails immediately with `HTTP 400 Bad Request`.

4. **Idempotency & Double-Capture Guard**:
   - Calling capture multiple times on an already completed order returns the existing payment record safely without triggering duplicate capture calls or double-billing.

5. **Server-Side PayPal Verification**:
   - The application never marks a purchase as paid simply because a client requests it.
   - The PayPal API response (`status == "COMPLETED"`) is the sole authoritative proof of payment.

6. **Credentials Security**:
   - `PAYPAL_CLIENT_SECRET` is kept exclusively on the backend and is never sent to the client, logged, or exposed in error messages.
