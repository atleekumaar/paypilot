# PayPilot — System Architecture

This document outlines the system architecture, service boundaries, data flows, and phased rollout strategy for **PayPilot**, an AI-powered commerce agent developed for the PayPal AI Hackathon.

---

## 1. High-Level Architecture Overview

PayPilot bridges conversational intent with multi-vendor commerce search and PayPal-mediated checkout.

The architecture follows a modular, decoupled design with strict phase separation:

```mermaid
flowchart TD
    User([User])
    
    subgraph Phase1_2 ["Phases 1 & 2: Active Foundation & AI Discovery Agent"]
        Frontend["Next.js Frontend\n(React 18 / TypeScript / Tailwind CSS)"]
        DiscoveryAPI["Discovery & Products API\n(/api/discovery/search, /api/products)"]
        HealthAPI["Health & Root API\n(GET /health, GET /)"]
        IntentService["Intent Service\n(Category, Budget, Use Case, Hard/Soft Constraints)"]
        SearchService["Deterministic Search Service\n(Strict Hard Constraints Filtering)"]
        RankingService["Deterministic Ranking Engine\n(35% Req, 25% Price, 15% Rating, 10% Deliv, 10% Seller, 5% Pref)"]
        ExplanationService["Grounded Explanation Service\n(Verified Specs, Zero Hallucinations)"]
        Repository["Product Repository\n(Demo In-Memory / PostgreSQL Ready)"]
    end

    subgraph FuturePhases ["Phase 3+: Future PayPal & Autonomous Layers"]
        ApprovalGate["[Phase 3+] Explicit User Approval Gate\n(User Confirms Purchase Plan)"]
        PayPalInt["[Phase 3+] PayPal REST Integration\n(v2/checkout/orders, Sandbox Auth, Webhooks)"]
        AgenticCommerce["[Phase 4+] Autonomous Multi-Turn Commerce\n(Dynamic Deal Ranking, Budget Optimizers)"]
        PostPurchase["[Phase 5+] Post-Purchase Agent\n(Order Tracking, Returns, Customer Support)"]
    end

    User <-->|HTTP / REST| Frontend
    Frontend <-->|REST API| DiscoveryAPI
    Frontend <-->|REST API| HealthAPI
    DiscoveryAPI --> IntentService
    IntentService --> SearchService
    SearchService <--> Repository
    SearchService --> RankingService
    RankingService --> ExplanationService
    ExplanationService --> DiscoveryAPI

    Frontend -.->|Purchase Intent Approved| ApprovalGate
    ApprovalGate -.->|Payment Authorization & Capture| PayPalInt
    PayPalInt -.-> AgenticCommerce
    AgenticCommerce -.-> PostPurchase

    classDef active fill:#0e7490,stroke:#06b6d4,stroke-width:2px,color:#fff;
    classDef future fill:#1e293b,stroke:#475569,stroke-width:1px,stroke-dasharray: 5 5,color:#94a3b8;
    class Frontend,DiscoveryAPI,HealthAPI,IntentService,SearchService,RankingService,ExplanationService,Repository active;
    class ApprovalGate,PayPalInt,AgenticCommerce,PostPurchase future;
```

---

## 2. Phase 2: AI Product Discovery Agent Flow

The core intelligence layer implemented in Phase 2 executes as a deterministic, explainable service pipeline:

```text
                    USER
                      │
                      ▼
                 Next.js UI
                      │
                      ▼
              Discovery API (POST /api/discovery/search)
                      │
                      ▼
              Intent Service
                      │
                      ▼
            Structured Intent (ProductSearchIntent)
                      │
                      ▼
          Product Search Service
                      │
                      ▼
            Candidate Products (Enforces budget & stock invariants)
                      │
                      ▼
          Ranking Service (0-100 Mathematical Weighting)
                      │
                      ▼
             Top 3 Products
                      │
                      ▼
       Grounded Explanation Service (Verified product specs)
                      │
                      ▼
                 Frontend (3 Best Matches + Grounded Analysis)
```

---

## 3. Component Details & Safety Invariants

### 1. Intent Extraction & Normalization (`IntentService`)
- Parses natural language into strongly-typed `ProductSearchIntent` Pydantic models.
- Categorizes user constraints into **hard constraints** (category, budget ceiling, in-stock requirement) and **soft preferences** (battery life, GPU acceleration, quiet switches).
- Normalizes natural expressions (e.g., *"under one grand"* → `$1,000.00`, *"laptop below $1200"* → `$1,200.00`).
- Provides deterministic extraction guarantee with optional LLM reasoning.

### 2. Deterministic Search (`ProductSearchService`)
- Enforces non-negotiable safety rules:
  - **Rule 1**: Products with `price > max_budget` are strictly excluded.
  - **Rule 2**: Products with `stock == False` are strictly excluded.
  - **Rule 3**: Product category mismatches are excluded.
- The LLM is never allowed to override hard search constraints.

### 3. Mathematical Ranking Engine (`ProductRankingService`)
Applies a deterministic, normalized scoring formula (0.0 to 100.0):

$$\text{Score} = 0.35 \times \text{Req} + 0.25 \times \text{Price} + 0.15 \times \text{Rating} + 0.10 \times \text{Delivery} + 0.10 \times \text{Seller} + 0.05 \times \text{Pref}$$

- **Requirement Match (35%)**: Evaluates satisfaction of explicit feature thresholds (GPU, RAM, battery hours).
- **Price Fit (25%)**: Calculates optimal budget utilization.
- **Customer Rating (15%)**: Normalized score from verified customer ratings.
- **Delivery Speed (10%)**: Delivery days penalty factor.
- **Seller Reliability (10%)**: Verified merchant tier.
- **Preference Match (5%)**: Match against contextual soft preferences.

### 4. Grounded Explanation Engine (`RecommendationService`)
- Generates natural language justifications strictly from real product attributes.
- Hallucinations are structurally impossible: the engine only references validated fields (`gpu`, `ram_gb`, `battery_hours`, `price`, `rating`, `delivery_days`).

---

## 4. Phase Boundary: Future PayPal Integration (Phase 3+)

> [!IMPORTANT]
> Payment processing, PayPal REST API order creation, token capture, autonomous payment agents, and webhooks are strictly designated for **Phase 3+**.
> 
> The selection of a product in Phase 2 hands off the chosen SKU and agreed price to the upcoming Phase 3 **Purchase Plan & PayPal Sandbox Checkout** pipeline.
