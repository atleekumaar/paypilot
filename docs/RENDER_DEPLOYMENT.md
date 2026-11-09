# PayPilot — Render Cloud Deployment & Blueprint Guide

## 1. Overview
[Render](https://paypalaihackathon.devpost.com/details/render) is a modern cloud application platform for hosting web apps, databases, and background workers with automated scaling and zero downtime.

PayPilot includes an official **Infrastructure-as-Code Blueprint** (`render.yaml`) that specifies the full distributed multi-service deployment architecture:

| Component | Render Service Type | Role |
| :--- | :--- | :--- |
| **`paypilot-backend`** | Web Service (Python 3.11) | FastAPI commerce agent, PayPal Orders v2, Channel3, Elastic, Kernel, Zapier |
| **`paypilot-frontend`** | Web Service (Node.js 20) | Next.js 14 interactive UI, Bryntum Timeline (`/timeline`), AG Grid (`/insights`) |
| **`paypilot-outbox-worker`** | Background Worker (Python 3.11) | Transactional outbox event processor, refund reconciler, Zapier dispatch |
| **`paypilot-db`** | Managed PostgreSQL | Relational storage for orders, payments, purchase plans, audit logs |
| **`paypilot-redis`** | Managed Redis Cache | High-speed cache for Channel3 live retailer queries and session states |

---

## 2. Render Blueprint Specification (`render.yaml`)

The root `render.yaml` defines:
- **Environment bindings:** Automatically links `paypilot-backend` and `paypilot-outbox-worker` to `paypilot-db` via `connectionString`.
- **Health check path:** Automatically routes traffic only after `/health` passes.
- **Port mapping:** Binds dynamically to Render's allocated `$PORT`.
- **CORS configuration:** Pre-configures allowed origins between `paypilot-frontend` and `paypilot-backend`.

```yaml
services:
  - type: web
    name: paypilot-backend
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health

  - type: web
    name: paypilot-frontend
    runtime: node
    rootDir: frontend
    buildCommand: npm install && npm run build
    startCommand: npm run start -- -p $PORT

  - type: worker
    name: paypilot-outbox-worker
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: python -m backend.app.workers.outbox_worker
```

---

## 3. Step-by-Step 1-Click Deployment

1. **Fork or Push repository** to GitHub: `https://github.com/atleekumaar/paypilot`.
2. Go to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect the PayPilot GitHub repository.
5. Render reads `render.yaml` and displays the service plan:
   - Web Service: `paypilot-backend`
   - Web Service: `paypilot-frontend`
   - Background Worker: `paypilot-outbox-worker`
   - Database: `paypilot-db`
   - Redis: `paypilot-redis`
6. Fill in the sensitive environment variables when prompted:
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_CLIENT_SECRET`
   - `PAYPAL_WEBHOOK_ID`
   - `GROQ_API_KEY`
   - `CHANNEL3_API_KEY`
   - `KERNEL_API_KEY` (optional)
   - `ZAPIER_WEBHOOK_URL` (optional)
7. Click **Apply**.
8. Render deploys all services simultaneously. Once deployed:
   - Backend URL: `https://paypilot-backend.onrender.com`
   - Frontend URL: `https://paypilot-frontend.onrender.com`

