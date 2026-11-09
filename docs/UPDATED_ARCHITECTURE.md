# PayPilot — Updated System Architecture & Integrations Map

## 1. Unified Architecture Overview

PayPilot is an autonomous agentic commerce platform built for the **PayPal AI Hackathon**, uniting seven core technologies into a cohesive, production-grade commerce stack:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PayPilot Next.js 14 Frontend                          │
│                                                                                 │
│   ┌─────────────────────┐   ┌───────────────────────┐   ┌───────────────────┐   │
│   │ Shopping Workspace  │   │ Commerce Intelligence │   │ Commerce Timeline │   │
│   │ (Catalog/C3/Elastic)│   │ (AG Grid + AG Studio) │   │ (Bryntum Tracks)  │   │
│   └──────────┬──────────┘   └───────────┬───────────┘   └─────────┬─────────┘   │
└──────────────┼──────────────────────────┼─────────────────────────┼─────────────┘
               │                          │                         │
               ▼                          ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FastAPI Backend Engine                             │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        Autonomous Commerce Agent                        │   │
│   │  • Intent Extraction (Groq LLM)                                         │   │
│   │  • Operational Planner                                                  │   │
│   │  • Policy Engine (Strict Human-in-the-Loop Boundaries)                  │   │
│   │  • Observability Traces (Astropods Adapter)                             │   │
│   └───────────────┬─────────────────────────────────────────────────────────┘   │
│                   │                                                             │
│       ┌───────────┴───────────┬───────────────────┬─────────────────┐           │
│       ▼                       ▼                   ▼                 ▼           │
│  ┌───────────┐         ┌───────────────┐     ┌─────────┐      ┌───────────────┐ │
│  │ Channel3  │         │ Elasticsearch │     │ PayPal  │      │ Transactional │ │
│  │ Discovery │         │ Hybrid Search │     │ Sandbox │      │ Outbox & DB   │ │
│  │ (25k+     │         │ (BM25 + RRF)  │     │ Orders  │      │ (SQLAlchemy)  │ │
│  │ Retailers)│         │               │     │ v2      │      │               │ │
│  └───────────┘         └───────────────┘     └─────────┘      └───────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Seven Integrated Technologies Matrix

| Technology | Role & Domain | Integration Artifacts | Status |
|---|---|---|---|
| **PayPal Sandbox** | Consequential payment execution, Orders v2, Captures, Webhooks & Refunds | `services/paypal/`, `api/payments.py` | Verified |
| **Groq LLM** | Intent extraction, conversational synthesis, product ranking reasoning | `services/intent_service.py`, `agents/orchestrator.py` | Verified |
| **Astropods** | Agent control plane, declarative spec, span tracing, secret redaction | `astropods.yml`, `AGENTS.md`, `services/astropods_service.py` | Verified |
| **Bryntum** | Commerce lifecycle timeline, schedule tracks, confirmed vs. estimated dates | `services/timeline_service.py`, `app/timeline/page.tsx` | Verified |
| **AG Grid / AG Studio** | Interactive commerce intelligence, spending grids, product analytics | `components/insights/`, `app/insights/page.tsx` | Verified |
| **Channel3** | Universal cross-retailer product discovery across 25,000+ stores | `services/channel3/`, `api/channel3.py` | Verified |
| **Elasticsearch** | BM25 lexical, dense vector semantic, and RRF hybrid retrieval & knowledge base | `services/elastic/`, `api/elastic.py` | Verified |

---

## 3. Strict Safety & Policy Guarantees

1. **Human-in-the-Loop Non-Negotiable Gate**:
   Neither Groq LLM nor any agent tool can capture payments without explicit buyer confirmation.
2. **Authoritative Pricing**:
   Product prices are frozen from the database or provider responses. Prompts cannot manipulate dollar totals.
3. **Secret Redaction**:
   All telemetry spans and audit logs strip PayPal secrets, Groq keys, Channel3 keys, and Elastic credentials.
4. **Resilient Offline Fallback**:
   When external services (Channel3, Elasticsearch cluster, PostgreSQL) are not running, PayPilot gracefully falls back to deterministic local mock stores without crashing or throwing unhandled errors.

