# PayPilot — Devpost Submission Package (PayPal AI Hackathon)

This document contains the exact field-by-field answers, technology disclosure, and 3-minute video demonstration script for the **PayPal AI Hackathon submission on Devpost**.

---

## 1. Project Overview

- **Project Title:** `PayPilot`
- **Short Tagline:** *Autonomous AI Commerce Assistant with Human-in-the-Loop PayPal Orders v2 Sandbox Checkout & Post-Purchase Intelligence*
- **Public GitHub Repository:** [https://github.com/atleekumaar/paypilot](https://github.com/atleekumaar/paypilot)
- **License:** MIT License (Open Source)
- **Live Demo URL:** Local/Render deployment ([http://localhost:3000](http://localhost:3000))
- **Live PayPal Sandbox Order ID:** `3KP879318B449513P`
- **Video Demo Link:** Public YouTube video (see script below)

---

## 2. Devpost Submission Fields

### 2.1 Inspiration
Shopping online today requires juggling dozens of browser tabs, comparing specs across retailers, worrying about fraud or inaccurate pricing, and manually chasing delivery tracking numbers. We asked: *What if an AI agent could discover products across universal merchants, perform mathematical trade-off analysis, formulate strict purchasing contracts, and let you securely checkout via PayPal with human-in-the-loop control?*

That is PayPilot: an agentic commerce assistant built with deterministic safety guardrails, authoritative PayPal Orders API v2 transactions, and comprehensive post-purchase tracking.

---

### 2.2 What It Does
PayPilot guides buyers through the entire commerce lifecycle in four seamless stages:

1. **Natural-Language Discovery & Cross-Merchant Intelligence**:
   - Accepts open-ended user requests (e.g., *"Find a developer laptop under $1,200 with great battery life"*).
   - Extracts structured intent (budget constraints, hardware features, use-case) using Groq-powered LLMs with deterministic regex fallback.
   - Discovers live products across 25,000+ merchants via **Channel3 Universal Product Graph** and local catalogues.
   - Searches merchant return policies and delivery SLAs using **Elasticsearch hybrid retrieval** (BM25 keyword + dense vector semantic search).

2. **Human-in-the-Loop Purchase Formulation**:
   - Formulates a cryptographic **Purchase Plan** where prices are derived strictly from backend authoritative databases (prompt injection immune).
   - Presents a rich **Interactive Approval Card** displaying hardware specs, delivery timelines, seller guarantees, and breakdown totals.
   - **No autonomous payment capture**: The agent is structurally forbidden from taking funds without explicit user button confirmation.

3. **PayPal Orders API v2 Sandbox Checkout**:
   - Upon buyer approval, initiates a real PayPal Orders v2 transaction (`intent: CAPTURE`).
   - Obtains an authoritative PayPal Order ID (e.g. `3KP879318B449513P`) and generates a direct PayPal Sandbox Buyer Approval URL.
   - Captures payments server-side via authenticated REST API, persisting verified payment receipts and capture IDs.

4. **Post-Purchase Intelligence & Operational Analytics**:
   - **Bryntum-Compatible Lifecycle Timeline**: Displays Gantt-style chronological lanes mapping orders from approval through courier transit to delivery.
   - **AG Grid Intelligence Dashboard**: High-density interactive tables with multi-column filtering, sortable hardware specs, and PayPal payment verification.
   - **Post-Purchase AI Agent**: Resolves tracking inquiries (e.g., *"Where is my order?"*), flags transit delays, and drafts merchant inquiry emails.
   - **Zapier Multi-App Automation**: Emits outbox events to Google Sheets, Slack, QuickBooks, and Gmail via webhooks and Zapier MCP actions.

---

### 2.3 How We Built It
- **Backend Architecture**: FastAPI monolithic agent engine with Pydantic v2 schemas, SQLAlchemy transactional outbox, and SQLite/PostgreSQL persistence.
- **Frontend Experience**: Next.js 14 App Router, TypeScript, Tailwind CSS, Lucide icons, anti-flash dark/light theme toggle, and AG Grid Community v32.
- **PayPal Integration**: Official PayPal Orders API v2 (`/v2/checkout/orders` and `/v2/checkout/orders/{id}/capture`) with OAuth2 bearer token management and fail-closed credentials.
- **Sponsor Integrations**:
  - **Groq LLM**: Low-latency intent extraction using `openai/gpt-oss-20b`.
  - **Channel3**: Live cross-retailer product discovery across Samsung, Apple, Lenovo, Newegg, and Best Buy.
  - **Elasticsearch**: BM25 multi-match and kNN dense vector retrieval for merchant policy knowledge.
  - **Kernel Browser**: Fast merchant store inspection and replay session generation.
  - **Zapier**: Enterprise webhook event dispatcher and AI action adapter.
  - **Bryntum**: Scheduler Pro `ResourceStore` + `EventStore` compatible data architecture.
  - **Render**: Infrastructure-as-code deployment blueprint (`render.yaml`).
  - **Postman**: 18-endpoint test collection with 23 verified `pm.test` assertions.

---

### 2.4 Challenges We Ran Into
- **Strict Human-in-the-Loop Enforcement**: Ensuring the LLM could never hallucinate or autonomously execute a PayPal capture. We solved this by enforcing a hard architectural boundary: payment capture requires a cryptographically verified signed approval state that can only be triggered by the user's explicit UI action.
- **Universal Multi-Merchant Product Normalization**: Different retailers format variants, pricing objects, and stock statuses differently. We designed a universal normalization pipeline inside `Channel3Client` that extracts clean pricing, brand attribution, and variant trees.
- **CSS Percentage Height Collapsing in Bar Charts**: In the spending analytics component, nested flex items collapsed to 0 height. We resolved this by explicitly constraining flex containers to `h-full` and adding a guaranteed minimum pixel height.

---

### 2.5 Accomplishments We're Proud Of
- **100% Automated Test Pass Rate**: 191/191 pytest unit and integration tests passing (`pytest backend/tests/`).
- **Postman Collection Verification**: 18/18 API requests passed with 23/23 `pm.test` assertions verified.
- **Genuine Live PayPal Sandbox Transactions**: Verified live order creation (`3KP879318B449513P`) against `api-m.sandbox.paypal.com`.
- **Zero-Error TypeScript**: Strict TypeScript compilation with 0 errors across the entire frontend.
- **Sleek Dark & Sun Theme**: Anti-flash theme toggle persisting user preference across all dashboards, chat interfaces, and timeline components.

---

### 2.6 What We Learned
- How to design production-grade Agentic workflows that combine the flexibility of conversational LLMs with the absolute deterministic reliability required for financial transactions.
- How to integrate PayPal Orders API v2 securely using server-side capture without exposing credentials to client browsers.

---

### 2.7 What's Next for PayPilot
- **Multi-Merchant Split Checkout**: Allowing users to purchase a bundle of items from different retailers in a single unified PayPal transaction.
- **Autonomous Price-Drop Protection**: Automatically monitoring purchased item prices and submitting refund claims if prices drop within the return window.
- **Native Mobile SDK**: Packaging PayPilot as a mobile shopping sidecar for iOS and Android.

---

## 3. Technologies & Sponsor Tools Disclosure ("Built With")

```
PayPal Orders API v2, PayPal Sandbox, Groq LLM, Channel3 API, Elasticsearch,
Kernel Cloud Browser, Zapier Webhooks & MCP, Bryntum Scheduler Pro Data Schema,
AG Grid Community, FastAPI, Pydantic v2, Python 3.11, Next.js 14, React 18,
TypeScript, Tailwind CSS, PostgreSQL, Redis, Render Cloud, Postman, Newman
```

---

## 4. Under-3-Minute Video Demonstration Script

Use this exact timing and narration script when recording your 2:50 demo video for YouTube:

| Time | Visual on Screen | Spoken Narration (Voiceover) |
| :--- | :--- | :--- |
| **0:00 - 0:20** | **Homepage & Hero Section**<br>Show PayPilot homepage (`http://localhost:3000`), toggle between Sun ☀️ and Moon 🌙 dark mode. | *"Welcome to PayPilot — an autonomous agentic commerce assistant built for the PayPal AI Hackathon. PayPilot combines conversational AI with human-in-the-loop security and official PayPal Orders v2 transactions."* |
| **0:20 - 0:50** | **Natural Language Discovery**<br>Type query in chat: *"Find me a developer laptop under $1200 with good battery life"*. Show Groq intent extraction and Channel3 / catalog discovery. | *"I start by asking for a developer laptop under twelve hundred dollars. PayPilot extracts our budget and hardware requirements, searches live merchant catalogs via Channel3 and Elasticsearch, and presents top-ranked options based on performance and reviews."* |
| **0:50 - 1:20** | **Interactive Purchase Approval Card**<br>Click "Proceed to Purchase Plan". Show the Purchase Approval Card with total breakdown ($1,049), seller guarantee, and disabled autonomous capture notice. | *"Notice PayPilot's strict safety boundary: prices are derived authoritatively from backend databases, preventing prompt manipulation. The agent cannot capture funds autonomously — it presents a cryptographic Purchase Plan awaiting my explicit buyer approval."* |
| **1:20 - 1:55** | **PayPal Orders v2 Sandbox Checkout**<br>Click **"Approve & Pay with PayPal"**. Show live PayPal Sandbox popup/redirect with PayPal Order ID and server-side capture confirmation. | *"When I click 'Approve & Pay', PayPilot talks directly to PayPal Orders API v2 on api-m.sandbox.paypal.com. A genuine PayPal Sandbox Order is created, redirecting to PayPal's secure checkout. Once approved, the backend captures the transaction server-side and issues a verified receipt."* |
| **1:55 - 2:25** | **Bryntum Timeline & Tracking**<br>Navigate to `/timeline`. Show Gantt-style chronological lanes (Approval -> Capture -> In Transit -> Delivery). Open `/orders/ORD-001` and ask the Post-Purchase Agent *"Where is my order?"*. | *"In post-purchase, our Bryntum-compatible scheduler maps the complete commerce lifecycle from payment authorization to carrier transit scans. The embedded post-purchase AI agent tracks shipments in real time and can even draft inquiry emails to merchants."* |
| **2:25 - 2:45** | **AG Grid Intelligence Dashboard**<br>Navigate to `/insights`. Show KPI metrics ($5,793 total spend), Commerce Spending Timeline vertical bars, Category Distribution, and AG Grid table. | *"Finally, our Commerce Intelligence dashboard combines AG Grid with live analytics. We see spending over time, category breakdowns across laptops, phones, and audio, and complete audit records for every PayPal transaction."* |
| **2:45 - 2:55** | **Summary & Call to Action**<br>Show GitHub repository with 191/191 tests passing and MIT license. | *"With 191 automated tests passing and full PayPal Sandbox compliance, PayPilot is the future of safe, agentic commerce. Thank you!"* |
