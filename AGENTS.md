# PayPilot Commerce Agent — Agent Card (AGENTS.md)

## 1. Identity & Overview
- **Name:** `paypilot-commerce-agent`
- **Version:** `1.0.0`
- **Framework:** Custom Agentic Monolith (FastAPI + Pydantic + Groq LLM + PayPal Orders API v2)
- **Deployment Platform:** Astropods Agent Operating System
- **Repository:** https://github.com/atleekumaar/paypilot

## 2. Capabilities & Tool Registry
The agent operates under deterministic policy enforcement and executes the following verified tools:

1. **`search_products`** (READ): Discovers catalog products by budget, category, ratings, and keyword filters.
2. **`compare_products`** (READ): Performs multi-factor trade-off analysis across candidate products.
3. **`create_purchase_plan`** (WRITE - SAFE): Formulates an authoritative purchase plan with calculated totals.
4. **`request_purchase_approval`** (WRITE - SAFE): Emits a human-in-the-loop approval gate.
5. **`create_paypal_order`** (WRITE - CONSEQUENTIAL): Initiates a PayPal Orders v2 Sandbox transaction. Requires prior explicit user approval.
6. **`capture_paypal_payment`** (WRITE - CONSEQUENTIAL): Captures funds server-side via PayPal Capture API.
7. **`query_commerce_timeline`** (READ): Queries Bryntum-compatible commerce lifecycle events and delivery milestones.
8. **`get_user_orders`** (READ): Lists persisted user orders with verified user isolation.
9. **`get_shipment_status`** (READ): Tracks real-time carrier tracking numbers and transit status.

## 3. Human-in-the-Loop Safety Boundaries
The agent is governed by strict Astropods guardrails:
- **No autonomous payment capture**: The agent is structurally forbidden from capturing payments without explicit human approval.
- **Authoritative pricing**: Product pricing is derived strictly from backend database/JSON records, not prompt generation.
- **Fail-closed credentials**: Secrets are never injected into LLM context or emitted in agent logs.

## 4. Observability & Telemetry
Astropods telemetry tracks:
- Step count and duration per session.
- Tool invocation latency and outcome (success/failure).
- Model token usage (Groq `openai/gpt-oss-20b`).
- Policy evaluation decisions.

