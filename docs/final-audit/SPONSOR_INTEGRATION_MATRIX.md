# PayPilot — Sponsor Integration Honesty Matrix

**Auditor:** Senior FinTech Architect & Hackathon Compliance Auditor  
**Date:** 2026-11-10T19:28:00+05:30  
**Target:** PayPal AI Hackathon Sponsor Tools Transparency Review  

---

## 1. Summary Matrix

| Sponsor Technology | Code Implementation | Verified Mode | External Evidence | Accurate Devpost Disclosure |
| :--- | :--- | :--- | :--- | :--- |
| **PayPal Sandbox** | `backend/app/services/paypal/` | **LIVE EXTERNAL (Stages 1 & 2)** | OAuth2 Token + Live Order `2RR4654859131563D` created on `api-m.sandbox.paypal.com` | *PayPal Orders API v2 Sandbox OAuth & Order Formulation; Server-Side Capture with Human-in-the-Loop Approval* |
| **Channel3** | `backend/app/services/channel3/` | **LIVE EXTERNAL** | HTTP 200 from `api.trychannel3.com` returning Samsung, Newegg, Lenovo products | *Live cross-retailer product discovery across 25,000+ merchants via official Channel3 API* |
| **Groq LLM** | `backend/app/services/intent_service.py` | **LIVE EXTERNAL** | HTTP 200 from `api.groq.com` using `openai/gpt-oss-20b` | *Conversational intent parsing with Groq LLM and deterministic rule-based fallback* |
| **Elasticsearch** | `backend/app/services/elastic/` | **HYBRID / LOCAL FALLBACK** | Cluster kNN query syntax implemented; embeddings derived from **MD5 hash vectors** | *Elasticsearch REST Client supporting BM25 and kNN queries with deterministic normalized vectors and local hybrid engine* |
| **Kernel Browser** | `backend/app/services/kernel/` | **HIGH-FIDELITY SIMULATION** | Returns `is_simulated: True` and replay templates (`https://app.onkernel.com`) | *Kernel Cloud Browser integration architecture with anti-bot bypass simulation and session replay schema* |
| **Zapier** | `backend/app/services/zapier/` | **SIMULATION & MCP SPEC** | Returns `simulated: True`; `.zapier/mcp_config.json` defines MCP schema | *Zapier workflow automation adapter with transactional outbox dispatcher and Model Context Protocol (MCP) server specification* |
| **Bryntum** | `frontend/components/timeline/` | **SCHEMA-COMPATIBLE ONLY** | Custom React scheduler; **no licensed Bryntum package in `package.json`** | *Bryntum-compatible Commerce Timeline implementing Bryntum's ResourceStore & EventStore JSON models* |

---

## 2. Technical Findings per Sponsor Technology

### 2.1 PayPal Developer Platform Sandbox
- **Verified Working:**
  - OAuth 2.0 bearer token exchange with `https://api-m.sandbox.paypal.com/v1/oauth2/token`.
  - Authoritative Order creation with `intent: CAPTURE` and exact `$1,049.00 USD` amount.
  - Active enforcement of buyer approval: server capture before approval is rejected with HTTP 422 `ORDER_NOT_APPROVED`.
- **Honest Boundary:** Full payment capture on live PayPal rails requires an interactive human login on the returned Sandbox approval URL.

### 2.2 Channel3 Cross-Retailer Graph
- **Verified Working:** Active connection to `https://api.trychannel3.com` with API key `8v20TV...`. Fetches live normalized catalog records, real-time pricing, and merchant attribution from real retailers.

### 2.3 Groq High-Speed LLM Inference
- **Verified Working:** Natural language queries (e.g. *"laptop under $1200 for AI development"*) are converted to JSON intents via Groq's `openai/gpt-oss-20b` model. Fails closed to regex extractor if credentials are unavailable.

### 2.4 Elasticsearch Hybrid & Knowledge Retrieval
- **Verified Working:** BM25 keyword search, REST health checks, and kNN query formatting against Elasticsearch clusters.
- **Important Technical Distinction:** The dense vector embeddings are generated using `_compute_mock_embedding()`, which uses **deterministic MD5 token hashing normalized to unit length, NOT neural semantic transformer embeddings** (such as BERT or Ada).

### 2.5 Kernel Agent Browser Cloud
- **Verified Working:** Clean HTTP client and data models for browser automation.
- **Important Technical Distinction:** Because no paid `KERNEL_API_KEY` is present in the local `.env`, the client executes its high-fidelity simulation path (`is_simulated: True`), producing pre-formatted return policy extractions and session replay URL formats.

### 2.6 Zapier Automation Platform & MCP
- **Verified Working:** Transactional outbox event dispatcher and Model Context Protocol (MCP) tool configuration in `.zapier/mcp_config.json`.
- **Important Technical Distinction:** Without an active live webhook URL in `ZAPIER_WEBHOOK_URL`, dispatch returns `SUCCESS_SIMULATED`. Downstream actions in QuickBooks or Google Sheets are simulated.

### 2.7 Bryntum Scheduler Pro Interoperability
- **Verified Working:** Rich interactive timeline component ([`BryntumCommerceScheduler.tsx`](../../frontend/components/timeline/BryntumCommerceScheduler.tsx)) displaying Gantt milestone progress (Approval -> Capture -> Transit -> Delivery).
- **Important Technical Distinction:** **No `@bryntum/scheduler` package is installed in `frontend/package.json`**. The component is a custom React implementation built strictly against Bryntum's `ResourceStore` and `EventStore` JSON schema, providing data-level interoperability without token-gated open-source build friction.

