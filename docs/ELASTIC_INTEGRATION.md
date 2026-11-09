# PayPilot — Elasticsearch Indexing & Hybrid Retrieval Integration

## 1. Overview & Objective

PayPilot integrates **Elasticsearch** (`elastic.co`) as its intelligent search, semantic indexing, and knowledge retrieval infrastructure.

By pairing Elasticsearch with PayPilot's Groq LLM reasoning engine, the platform achieves:
- High-speed BM25 keyword matching for exact catalog queries (e.g. SKU codes, model names).
- Dense vector semantic kNN similarity search for intent-driven conceptual queries (e.g. *"lightweight creator laptop for editing videos on flights"*).
- **Reciprocal Rank Fusion (RRF)** hybrid search combining sparse lexical scores and dense semantic embeddings.
- Merchant policy and warranty retrieval from the Elasticsearch knowledge index (`paypilot_knowledge`).

---

## 2. Architecture & Service Design

Located in `backend/app/services/elastic/`:

```
User Query / Agent Tool
       │
       ▼
ElasticCommerceService
       │
       ├──> BM25 Keyword Search (multi_match on name^3, brand^2, description)
       │         │
       │         └──> Ranked List A
       │
       ├──> Dense Vector Semantic Search (Cosine similarity over embeddings)
       │         │
       │         └──> Ranked List B
       │
       ▼
Reciprocal Rank Fusion (RRF) Engine
  Formula: Score(d) = Σ [ 1 / (60 + Rank(d, r)) ]
       │
       ▼
Ranked Authoritative Candidates
       │
       ▼
Groq LLM Reasoning & Response Grounding
```

---

## 3. Dual-Mode Connection & Graceful Fallback

Elasticsearch service supports both live Elasticsearch clusters and local fallback execution:
- **Cluster Mode**: Connects via `ELASTICSEARCH_URL` (and optional `ELASTICSEARCH_API_KEY` / `ELASTIC_CLOUD_ID`) when an Elasticsearch instance is active.
- **Local Fallback Engine**: If no Elasticsearch server is reachable, PayPilot seamlessly falls back to an in-memory vector & lexical engine with zero exceptions or downtime.
- **Sync & Indexing**: Database products and merchant policies are automatically synchronized into the index via `sync_from_repository()`.

---

## 4. Merchant Knowledge Indexing (`paypilot_knowledge`)

In addition to products, PayPilot indexes key business logic into Elasticsearch to ground AI agent turn responses:
- **PayPal Buyer Protection Policy**: Authoritative terms regarding refunds and unfulfilled items.
- **Standard Logistics SLAs**: Carrier hub dispatch times and transit expectations.
- **Hardware Warranty Policies**: Manufacturer defect and support guarantees.

Tool `get_merchant_policies` retrieves these documents directly during conversational turns.

---

## 5. API Endpoints

1. `POST /api/elastic/search`
   - Input: `{ "query": "laptop", "mode": "hybrid", "max_price": 1500 }`
   - Modes: `"hybrid"`, `"keyword"`, `"semantic"`
   - Returns: Ranked product search results.
2. `POST /api/elastic/knowledge`
   - Input: `{ "query": "buyer protection policy", "limit": 2 }`
   - Returns: Relevant policy and warranty excerpts.
3. `GET /api/elastic/health`
   - Returns: Connection status (`connected` or `active_fallback`), cluster name, active indices, and document counts.
4. `POST /api/elastic/sync`
   - Triggers re-indexing of all products from database repository.

