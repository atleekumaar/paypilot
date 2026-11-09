# PayPilot — Integration & Environment Setup Guide

## 1. Prerequisites

- Python 3.12+ (tested through 3.14.5)
- Node.js 18+ / 20+ and npm
- PayPal Developer Sandbox Account (free)
- Groq API Key (free tier supported)
- *(Optional)* Channel3 API Key (`trychannel3.com`)
- *(Optional)* Elasticsearch Instance (`localhost:9200` or Elastic Cloud)
- *(Optional)* Astropods Cloud Project

---

## 2. Environment Variables (`.env`)

Create `.env` in repository root from `.env.example`:

```env
# Application Core
APP_NAME=PayPilot
ENVIRONMENT=development
DEBUG=false
AUTH_MODE=demo
DATABASE_URL=sqlite:///./paypilot.db

# 1. Groq LLM (Required for Conversational Intelligence)
LLM_API_KEY=gsk_your_groq_api_key_here
LLM_MODEL=openai/gpt-oss-20b

# 2. PayPal Sandbox (Required for Live Sandbox Checkout)
PAYPAL_CLIENT_ID=BAAp_your_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=EFzCAN_your_sandbox_secret_here
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_MOCK_ENABLED=false

# 3. Astropods Control Plane (Optional - Defaults to LOCAL in-memory mode)
ASTROPODS_API_KEY=
ASTROPODS_PROJECT_ID=paypilot-ai-commerce
ASTROPODS_ENVIRONMENT=development

# 4. Channel3 Discovery (Optional - Defaults to Verified Multi-Retailer Mock)
CHANNEL3_API_KEY=
CHANNEL3_BASE_URL=https://api.trychannel3.com

# 5. Elasticsearch (Optional - Defaults to Local Hybrid Engine)
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=
ELASTIC_PRODUCT_INDEX=paypilot_products
ELASTIC_KNOWLEDGE_INDEX=paypilot_knowledge
```

---

## 3. Installation & Startup

### Step 1: Backend
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server on port 8000
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Frontend
```bash
# Install node dependencies
npm --prefix frontend install

# Start Next.js development server on port 3000
npm --prefix frontend run dev
```

Visit `http://localhost:3000` to interact with PayPilot.

