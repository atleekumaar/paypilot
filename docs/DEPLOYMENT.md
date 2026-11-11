# PayPilot — Deployment & Production Operations Guide

## 1. System Requirements

- **Python**: 3.11+ (Python 3.12 recommended)
- **Node.js**: 18.x or 20.x
- **Database**: SQLite (SQLAlchemy ORM with Transactional Outbox & ACID Compliance)
- **Payment Gateway**: PayPal Developer Account (Sandbox Credentials)

---

## 2. Environment Configuration

Create a root `.env` or set system environment variables:

```bash
# Core Application
APP_NAME=PayPilot
ENVIRONMENT=production
DEBUG=false

# Persistence (SQL Database)
DATABASE_URL=sqlite:///./paypilot.db

# Production Identity (JWKS)
AUTH_MODE=jwt
AUTH_ISSUER=https://auth.paypilot.internal/
AUTH_AUDIENCE=paypilot-api
AUTH_JWKS_URL=https://auth.paypilot.internal/.well-known/jwks.json
AUTH_ALGORITHMS=["RS256"]

# CORS Whitelist
ALLOWED_ORIGINS=["https://paypilot.internal", "https://app.paypilot.internal"]

# PayPal Gateway
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_MOCK_ENABLED=false

# LLM Agent
LLM_API_KEY=your_gemini_or_openai_api_key
```

---

## 3. Database Migrations

Run database migrations using Alembic:

```bash
cd backend
alembic -c alembic.ini upgrade head
```

To verify database status:
```bash
alembic -c alembic.ini current
```

---

## 4. Running the Services

### Backend Service (FastAPI)
```bash
cd backend
# Local Development (fixed port 8000)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Cloud PaaS / Render (Binds to dynamic $PORT)
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 --app-dir backend
```

### Frontend Service (Next.js)
```bash
cd frontend
npm install
npm run build
npm run start -- -p 3000
```

---

## 5. Health & Observability Endpoints

- **Liveness / Readiness Probe**: `GET /api/health`
- **Application Identification**: `GET /`
- **Reconciliation Audit**: `GET /api/payments/reconciliation/report`
- **OpenAPI Documentation**: `/docs` (Swagger UI) and `/redoc` (ReDoc)

