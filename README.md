# PayPilot

> PayPilot is an AI-powered commerce agent that helps users discover, evaluate, and eventually purchase products through PayPal.

Built for the **[PayPal AI Hackathon](https://paypalaihackathon.devpost.com/)**.

---

## Vision

PayPilot empowers everyday consumers to shop using natural conversational language. Instead of browsing dozens of tabs, comparing spec sheets manually, and dealing with tedious multi-step checkouts, a user simply states their intent:

> *"Find me a laptop under $1200 for AI development with good battery life."*

PayPilot autonomously understands the request, searches product offerings, compares benchmarks and user reviews, synthesizes the best recommendations, formulates a precise purchase plan, requests explicit user confirmation, and seamlessly completes the payment with PayPal.

---

## Current Status

**Phase 1: Foundation (Active)**
- Core repository structure established
- FastAPI backend scaffolded with health and metadata endpoints
- Next.js + TypeScript + Tailwind CSS frontend initialized with fintech landing page
- Architecture and technical specifications documented
- Continuous integration and Git workflow active

---

## Architecture

```text
User
 ↓
Next.js Frontend (React + TypeScript + Tailwind CSS)
 ↓
FastAPI Backend (Python 3.11+ / Uvicorn / Pydantic / SQLAlchemy)
 ↓
[Phase 2+] AI Agent Layer (Intent Parsing, RAG, Spec Comparison)
 ↓
[Phase 2+] Commerce Services (Product Catalog, Inventory, Search)
 ↓
[Phase 3+] PayPal Integration (Orders API, Vault, Smart Checkout)
```

For in-depth architectural diagrams, component boundaries, and phase boundaries, see [docs/architecture.md](docs/architecture.md).

---

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** — High-performance modern web framework
- **Uvicorn** — Lightning-fast ASGI server
- **Pydantic v2** — Robust data validation and settings management
- **SQLAlchemy** — PostgreSQL-ready ORM
- **pytest** & **httpx** — Automated test suite

### Frontend
- **Next.js 14+** (App Router)
- **React 18+** & **TypeScript**
- **Tailwind CSS** — Modern dark-mode AI/fintech aesthetic
- **Lucide Icons** — Clean iconography

### Development & Security
- Git & GitHub
- Strict environment variable segregation via `.env.example`
- Zero committed secrets policy

---

## Project Structure

```text
paypilot/
├── backend/
│   ├── app/
│   │   ├── api/          # API route definitions
│   │   ├── core/         # Configuration and security settings
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic & agent workflows
│   │   └── main.py       # FastAPI application entrypoint
│   ├── tests/            # Automated test suite (pytest)
│   ├── requirements.txt  # Python backend dependencies
│   └── README.md         # Backend setup documentation
│
├── frontend/
│   ├── app/              # Next.js App Router (pages and layouts)
│   ├── components/       # Reusable React UI components
│   ├── lib/              # Client utilities and helpers
│   ├── public/           # Static assets
│   ├── package.json      # Frontend dependencies and scripts
│   └── README.md         # Frontend setup documentation
│
├── docs/
│   └── architecture.md   # System architecture & sequence diagrams
│
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules
├── LICENSE               # MIT License
└── README.md             # Project documentation
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Verify endpoints:
   - Root: http://127.0.0.1:8000/
   - Health check: http://127.0.0.1:8000/health
   - Interactive OpenAPI docs: http://127.0.0.1:8000/docs

6. Run tests:
   ```bash
   pytest
   ```

---

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

Copy the example environment configuration:

```bash
cp .env.example .env
```

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `APP_NAME` | Name of the application | `PayPilot` |
| `ENVIRONMENT` | Running environment (`development`, `production`) | `development` |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite+aiosqlite:///./paypilot.db` (dev) |
| `LLM_API_KEY` | LLM Provider API Key (Phase 2+) | Placeholder |
| `PAYPAL_CLIENT_ID` | PayPal Developer App Client ID (Phase 3+) | Placeholder |
| `PAYPAL_CLIENT_SECRET` | PayPal Developer App Secret (Phase 3+) | Placeholder |
| `PAYPAL_ENVIRONMENT` | PayPal sandbox or live environment | `sandbox` |

> **IMPORTANT:** Never commit `.env` or real API keys to version control.

---

## Roadmap

- [x] **Phase 1 — Foundation** *(CURRENT)*: Scaffold backend and frontend, establish architecture, setup testing and documentation.
- [ ] **Phase 2 — AI Product Agent**: Conversational intent extraction, mock product catalog, LLM-driven comparison engine.
- [ ] **Phase 3 — PayPal Checkout**: PayPal REST API integration, sandbox order creation, capture workflows, and user approval gate.
- [ ] **Phase 4 — Agentic Commerce**: Autonomous cart assembly, budget constraints enforcement, dynamic deal ranking.
- [ ] **Phase 5 — Post-Purchase Agent**: Order confirmation, real-time shipment tracking, simulated returns and customer support.
- [ ] **Phase 6 — Production Polish**: End-to-end security auditing, telemetry, polished animations, and hackathon presentation demo.

---

## Contributing

1. Fork or branch from `main`.
2. Follow commit message conventions (`feat:`, `chore:`, `docs:`, `test:`).
3. Ensure all tests pass prior to submitting PRs.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
