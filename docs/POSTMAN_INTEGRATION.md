# PayPilot — Postman API Integration & Automated Testing

## 1. Overview
[Postman](https://paypalaihackathon.devpost.com/details/postman) is the industry standard for API design, contract validation, and automated integration testing.

PayPilot includes a complete, production-ready **Postman Collection v2.1.0** and **Postman Environment** covering all 8 major architectural domains of the platform:
1. **01 - Health & Infrastructure:** API Root, `/health`, Kernel health, Zapier health, Elastic health.
2. **02 - Product Discovery & Catalog:** Product listing, SKU lookup.
3. **03 - Channel3 Universal Retailers:** Cross-retailer search, live offer comparison.
4. **04 - Elasticsearch Hybrid & Knowledge:** BM25 + dense vector hybrid search, merchant policy grounding.
5. **05 - Kernel Cloud Browser:** Live URL inspection, stealth anti-bot verification, store trust.
6. **06 - Zapier Workflow Automation:** Outbound webhook dispatch, inbound webhook callbacks.
7. **07 - Bryntum Commerce Timeline:** Milestones, tracking telemetry, SLA delivery events.
8. **08 - AG Grid Commerce Analytics:** KPI overview, spending series over time.

---

## 2. File Artifacts

- `postman/PayPilot.postman_collection.json`: Official Postman Collection with pre-request scripts, test assertions, and environment variables.
- `postman/PayPilot.postman_environment.json`: Postman Environment configured for `baseUrl` (`http://localhost:8000`) and Render deployment (`https://paypilot-backend.onrender.com`).
- `postman/run_collection.py`: Automated collection runner executing all collection requests and assertions via FastAPI TestClient without requiring external Node/Newman dependencies.
- `backend/tests/test_postman_spec.py`: Pytest suite verifying collection schema, environment variables, and execution status.

---

## 3. How to Use in Postman App

1. Open the Postman Desktop App.
2. Click **Import** in the upper-left corner.
3. Select `postman/PayPilot.postman_collection.json` and `postman/PayPilot.postman_environment.json`.
4. Select the **PayPilot Local & Render Environment** active environment.
5. Click **Run collection** to run all 18 test requests sequentially.

---

## 4. Automated CLI Test Execution

Run the collection runner directly via Python:
```powershell
python postman/run_collection.py
```

Expected output:
```text
📂 Folder: 01 - Health & Infrastructure
  ✓ [200] API Root Info (GET /)
  ✓ [200] System Health Check (GET /health)
  ✓ [200] Kernel Browser Health (GET /api/kernel/health)
  ✓ [200] Zapier Automation Health (GET /api/zapier/health)
  ✓ [200] Elasticsearch Health (GET /api/elastic/health)

📂 Folder: 02 - Product Discovery & Catalog
  ✓ [200] List Products (GET /api/products/?limit=5)
  ✓ [200] Get Product Details (GET /api/products/LAP-001)

📂 Folder: 03 - Channel3 Universal Retailers
  ✓ [200] Channel3 Live Product Search (POST /api/channel3/search)
  ✓ [200] Channel3 Multi-Retailer Comparison (POST /api/channel3/compare)

📂 Folder: 04 - Elasticsearch Hybrid & Knowledge
  ✓ [200] Elastic Hybrid Search (BM25 + Dense Vector) (POST /api/elastic/search)
  ✓ [200] Elastic Knowledge Retrieval (Merchant Policies) (POST /api/elastic/knowledge)

📂 Folder: 05 - Kernel Cloud Browser
  ✓ [200] Browse & Verify Merchant Page (POST /api/kernel/browse)
  ✓ [200] Verify Merchant Domain Trust (POST /api/kernel/verify-domain)

📂 Folder: 06 - Zapier Workflow Automation
  ✓ [200] Dispatch Event to Zapier (Sheets, Slack, Gmail) (POST /api/zapier/dispatch)
  ✓ [200] Inbound Zapier Webhook Callback (POST /api/zapier/webhook)

📂 Folder: 07 - Bryntum Commerce Timeline
  ✓ [200] Query Commerce Timeline Events (GET /api/timeline/events)

📂 Folder: 08 - AG Grid Commerce Analytics
  ✓ [200] KPI Analytics Summary (GET /api/analytics/overview)
  ✓ [200] Spending Trends Over Time (GET /api/analytics/spending)

============================================================
Postman Collection Execution: 18/18 Passed.
============================================================
```

