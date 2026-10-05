# PayPilot

> PayPilot is an AI-powered commerce agent that helps users discover, evaluate, and eventually purchase products through PayPal.

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

- **Phase 2 — Product Discovery** ✅ *(ACTIVE & IMPLEMENTED)*
  - Natural-language intent extraction and normalization
  - Deterministic product search enforcing hard constraints (budget, category, in-stock)
  - Mathematical ranking engine (0–100 composite scoring)
  - Grounded, hallucination-free recommendation explanations
  - Interactive Next.js Shopping Workspace with progressive loading & product modals

- **Phase 3 — PayPal Checkout** ⏳ *(UPCOMING)*
  - Purchase Plan creation & user confirmation gate
  - PayPal Orders API v2 sandbox integration
  - Payment authorization, capture, and instant receipting

- **Phase 4 — Agentic Commerce** ⏳
  - Autonomous cart assembly, budget optimization, and discount ranking

- **Phase 5 — Post-Purchase Agent** ⏳
  - Real-time shipment tracking, delivery notifications, and returns assistance

- **Phase 6 — Production Polish** ⏳
  - Security hardening, telemetry, and hackathon presentation demo

---

## Phase 2 Demo: AI Product Discovery Agent

### Conversational Query Example
```text
User Request:
"Find me a laptop under $1200 for AI development with good battery life."
```

### Pipeline Execution
1. **Intent Extraction**: Identifies category `laptop`, hard budget cap `$1,200.00`, requirement `good battery life`, use case `AI development`.
2. **Filtering**: Deterministically removes laptops over $1200 and out-of-stock items.
3. **Ranking**: Computes composite scores across requirement match (35%), price fit (25%), rating (15%), delivery (10%), seller (10%), and soft preferences (5%).
4. **Top 3 Recommendations**:
   - **Rank #1 (Top Pick)**: **NovaBook Pro 14** (Score: 94.4/100, $1,049.00, RTX 4060, 16GB RAM, 9.5h Battery)
   - **Rank #2**: **ApexBook AI 15** (Score: 92.1/100, $1,149.00, RTX 4050, 16GB RAM, 8.5h Battery)
   - **Rank #3**: **ZenAir Dev 14** (Score: 89.8/100, $899.00, Radeon 780M, 16GB RAM, 13h Battery)
5. **Grounded Explanation**:
   > *"I recommend the NovaBook Pro 14 because it gives you the strongest balance of GPU performance, battery endurance, price-to-value ratio while staying reliably within your specifications.*
   >
   > *Why it fits:*
   > *✓ RTX 4060*
   > *✓ 16 GB RAM*
   > *✓ 9.5-hour battery life*
   > *✓ 512 GB SSD*
   > *✓ $1,049.00 price*
   > *✓ 4.7★ rating (842 reviews)*
   > *✓ Fast 3-day delivery via Nova Direct"*

---

## Architecture Flow

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

See [docs/architecture.md](docs/architecture.md) for full architectural documentation.

---

## API Endpoints

### Discovery API
- `POST /api/discovery/search` — Natural language product search and explainable recommendation.
  ```json
  // Request
  {
    "query": "Find me a laptop under $1200 for AI development with good battery life."
  }
  ```

### Products API
- `GET /api/products` — Retrieve product catalogue with optional category, stock, and pagination query params.
- `GET /api/products/{id}` — Fetch single product details by SKU (e.g. `/api/products/LAP-001`).

### System API
- `GET /health` — Health check endpoint (`{"status": "ok", "service": "paypilot-backend"}`).
- `GET /` — Root service metadata.
- `GET /docs` — Interactive OpenAPI / Swagger UI.

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, pytest
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons
- **Data & Testing**: Deterministic 134-item multi-category catalogue, comprehensive automated test coverage

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
- Swagger Docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- App UI: http://localhost:3000

### 3. Run Backend Tests
```bash
cd backend
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
