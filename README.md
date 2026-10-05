# PayPilot

> PayPilot is an AI-powered commerce agent that helps users discover, evaluate, and purchase products through PayPal.

Built for the **[PayPal AI Hackathon](https://paypalaihackathon.devpost.com/)**.

---

## Vision

PayPilot empowers everyday consumers to shop using natural conversational language. Instead of browsing dozens of tabs, comparing spec sheets manually, and dealing with tedious multi-step checkouts, a user simply states their intent:

> *"Find me a laptop under $1200 for AI development with good battery life."*

PayPilot autonomously understands the request, searches product offerings, compares benchmarks and user reviews, synthesizes the best recommendations, formulates a precise purchase plan, requests explicit user confirmation, and seamlessly completes the payment with PayPal.

---

## Current Status & Roadmap

- **Phase 1 — Foundation** ✅
  - FastAPI backend & Next.js frontend scaffolded
  - Health and root status endpoints
  - Git repository & clean architecture established

- **Phase 2 — AI Product Discovery** ✅
  - Natural-language intent extraction and normalization
  - Deterministic product search enforcing hard constraints (budget, category, in-stock)
  - Mathematical ranking engine (0–100 composite scoring)
  - Grounded, hallucination-free recommendation explanations
  - Interactive Next.js Shopping Workspace with progressive loading & product modals

- **Phase 3 — PayPal Checkout & Purchase Flow** ✅ *(ACTIVE & IMPLEMENTED)*
  - Authoritative Purchase Plan formulation (zero client price manipulation)
  - Explicit Human-in-the-Loop approval gate
  - PayPal Sandbox OAuth 2.0 authentication and token management
  - PayPal Orders API v2 order creation and authoritative amount binding
  - PayPal Sandbox checkout flow with `● PayPal Sandbox` visual indicator
  - Server-side order capture verification and idempotency protection
  - Verified receipt and payment success screen

- **Phase 4 — Agentic Commerce** ⏳ *(UPCOMING)*
  - Autonomous cart assembly, budget optimization, and dynamic deal ranking

- **Phase 5 — Post-Purchase Agent** ⏳
  - Real-time shipment tracking, delivery notifications, and returns assistance

- **Phase 6 — Production Polish** ⏳
  - Security hardening, telemetry, and hackathon presentation demo

---

## Phase 3 End-to-End Walkthrough

```text
1. Search: "Find me a laptop under $1200 for AI development with good battery life."
      ↓
2. AI Recommendations: PayPilot recommends NovaBook Pro 14 (#1 Pick, $1,049.00).
      ↓
3. Product Selection: User clicks "Select" on the top choice.
      ↓
4. Purchase Plan Formulated:
   - Item: NovaBook Pro 14
   - Authoritative Price: $1,049.00 USD (Derived by backend from verified catalog)
   - Seller: Nova Direct
   - Delivery: 3 days
   - Why: Best balance of GPU performance and battery endurance.
      ↓
5. Explicit User Approval: User reviews the summary and clicks [Approve Purchase].
      ↓
6. PayPal Sandbox Order Created:
   - Backend calls PayPal Orders API v2.
   - Generates authoritative PayPal Order ID.
      ↓
7. PayPal Checkout:
   - User approves in PayPal Sandbox.
      ↓
8. Server-Side Capture:
   - Backend captures the order directly with PayPal API.
   - Verifies capture status is COMPLETED.
      ↓
9. Verified Receipt Screen:
   - Shows green checkmark, Amount Paid ($1,049.00 USD), PayPal Order ID, and Capture ID.
```

---

## PayPal Sandbox Setup Instructions

PayPilot is configured for **PayPal Sandbox Mode** to ensure no real money is processed during testing.

### 1. Obtain PayPal Sandbox Credentials
1. Log in to the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/).
2. Navigate to **Apps & Credentials** and select the **Sandbox** tab.
3. Create a new REST API app or use the Default Application.
4. Copy your **Client ID** and **Secret**.

### 2. Configure Local Environment
Create or edit your local `.env` file in the repository root:
```env
PAYPAL_CLIENT_ID=your_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret_here
PAYPAL_ENVIRONMENT=sandbox
```
*(Note: If no credentials are configured, PayPilot seamlessly activates its local Sandbox emulation mode so judges and automated tests can run without blockers).*

### 3. Sandbox Buyer Accounts
To complete sandbox transactions, use the Sandbox personal buyer account provided in your PayPal Developer dashboard under **Sandbox → Accounts** (e.g. `sb-buyer...@personal.example.com`).

---

## Architecture Flow

```text
                 USER
                   │
                   ▼
              NEXT.JS UI
                   │
                   ▼
          DISCOVERY API (POST /api/discovery/search)
                   │
                   ▼
           PRODUCT SELECTED
                   │
                   ▼
          PURCHASE PLAN (POST /api/purchase-plans)
                   │
                   ▼
        EXPLICIT USER APPROVAL (POST /api/purchase-plans/{id}/approve)
                   │
                   ▼
         PAYPAL ORDER SERVICE (POST /api/payments/paypal/create-order)
                   │
                   ▼
            PAYPAL SANDBOX
                   │
                   ▼
             CAPTURE (POST /api/payments/paypal/capture)
                   │
                   ▼
         PAYMENT VERIFICATION (status == "COMPLETED")
                   │
                   ▼
          SUCCESS CONFIRMATION RECEIPT
```

---

## API Endpoints

### Purchase Plans API
- `POST /api/purchase-plans` — Create purchase plan with backend-derived authoritative price.
- `GET /api/purchase-plans/{id}` — Retrieve purchase plan details.
- `POST /api/purchase-plans/{id}/approve` — Explicitly approve a purchase plan.

### Payments & PayPal API
- `POST /api/payments/paypal/create-order` — Create PayPal Sandbox checkout order for an approved plan.
- `POST /api/payments/paypal/capture` — Capture PayPal payment, verify completion, and issue receipt.
- `GET /api/payments/{id}` — Retrieve payment transaction record.
- `GET /api/payments/by-plan/{plan_id}` — Retrieve payment record by purchase plan ID.

### Discovery & Products API
- `POST /api/discovery/search` — Natural language product search and explainable recommendation.
- `GET /api/products` — Retrieve product catalogue with filters.
- `GET /api/products/{id}` — Single product details by SKU.

### System API
- `GET /health` — Health check endpoint.
- `GET /docs` — Interactive OpenAPI / Swagger UI.

---

## Local Development

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate:
.venv\Scripts\Activate.ps1   # Windows PowerShell
source .venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Run Automated Tests
```bash
cd backend
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
