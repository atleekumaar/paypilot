# PayPilot — Full Project Regression Test Report

## 1. Executive Summary
- **Execution Timestamp:** 2026-11-10T14:05:05Z
- **Baseline Git Commit:** `86bcf855` (`main`)
- **Backend Test Status:** 191 Passed, 5 Skipped, 0 Failed (Pytest)
- **Newman API Assertion Status:** 18 Requests, 23 Assertions Passed, 0 Failed (Newman CLI 6.2.3)
- **Frontend Typecheck Status:** 0 Errors (`tsc --noEmit`)
- **Frontend Build Status:** Next.js 14.2.35 Production Build Succeeded (8/8 routes generated)
- **GitHub Actions Remote CI:** Run ID `42812406951` Passed (`completed / success`)

---

## 2. Backend Pytest Suite Verification

### Command Executed
```bash
pytest backend/tests/ -q
```

### Pytest Execution Summary
```
........................................................................ [ 36%]
........................................................................ [ 73%]
........................sssss.......................                     [100%]
============================== warnings summary ===============================
backend/tests/test_jwt_auth.py::test_scenario_13_rejection_of_disallowed_symmetric_alg
  InsecureKeyLengthWarning: The HMAC key is 20 bytes long...
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
191 passed, 5 skipped, 1 warning in 406.27s (0:06:46)
```

### Test Category Breakdown
| Test Category | Test File | Passed | Skipped | Failed | Coverage Focus |
|---|---|---|---|---|---|
| JWT & Security Policies | `test_jwt_auth.py` | 13 | 0 | 0 | Algorithm confusion, signature verification, expiry, issuer check |
| User Isolation & RBAC | `test_security_audit.py`, `test_auth_isolation.py` | 18 | 0 | 0 | Cross-tenant rejection, admin boundaries, SQL injection prevention |
| PayPal Checkout & Capture | `test_paypal_checkout.py` | 16 | 0 | 0 | Orders v2 flow, server-side capture, mock fallbacks, token caching |
| Agent Workflows & HITL | `test_agent_workflow.py`, `test_orchestrator.py` | 24 | 0 | 0 | Deterministic planning, HITL approval gate, prompt guardrails |
| Post-Purchase Operations | `test_post_purchase.py`, `test_post_purchase_e2e.py` | 22 | 0 | 0 | Tracking, returns, replacement order generation, shipment status |
| Catalog & Channel3 | `test_channel3.py`, `test_products.py` | 21 | 0 | 0 | Filter validation, live product sync, algorithmic scoring |
| Elastic Vector Search | `test_elastic_search.py`, `test_hybrid_search.py` | 19 | 0 | 0 | BM25 lexical score, vector cosine ranking, schema fallback |
| Analytics & AG Studio | `test_analytics.py`, `test_ag_studio.py` | 20 | 0 | 0 | AG Grid payload generation, metric aggregation, query safety |
| Timeline & Bryntum Schemas | `test_bryntum_timeline.py` | 14 | 0 | 0 | ResourceStore & EventStore schema compliance, date ranges |
| Kernel & Zapier Integrations | `test_kernel_agent.py`, `test_zapier_mcp.py` | 12 | 0 | 0 | Execution protocol, simulation contracts, payload validation |
| Real Database Migrations | `test_database_postgres.py` | 12 | 5 (Docker-gated) | 0 | SQLite fallback verified; direct Postgres integration skipped when offline |
| **Total** | | **191** | **5** | **0** | **100% Pass Rate of Active Tests** |

---

## 3. Postman / Newman CLI Collection Verification

### Command Executed
```bash
.\node_modules\.bin\newman.cmd run postman/PayPilot.postman_collection.json \
  --environment postman/PayPilot.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export docs/final-audit/newman-report.json
```

### Newman Execution Summary
- **Total Requests:** 18
- **Failed Requests:** 0
- **Total `pm.test` Assertions:** 23
- **Passed Assertions:** 23
- **Failed Assertions:** 0
- **Pass Rate:** 100.0%
- **Artifact:** `docs/final-audit/newman-report.json`

### Endpoints Verified in Sequence:
1. `GET /health` → HTTP 200 (asserted `status: healthy`)
2. `GET /api/v1/products` → HTTP 200 (asserted array + saved dynamic `test_product_id`)
3. `GET /api/v1/products/{id}` → HTTP 200 (asserted target product schema)
4. `POST /api/v1/agent/chat` → HTTP 200 (asserted Groq assistant response)
5. `POST /api/v1/orders/create` → HTTP 200 (asserted order initialization)
6. `POST /api/v1/orders/{id}/approve` → HTTP 200 (asserted HITL user approval transition)
7. `POST /api/v1/orders/{id}/capture` → HTTP 200 (asserted server-side capture)
8. `GET /api/v1/orders/user` → HTTP 200 (asserted user isolation)
9. `GET /api/v1/channel3/search` → HTTP 200 (asserted real-time external products array)
10. `POST /api/v1/channel3/compare` → HTTP 200 (asserted multi-factor comparison payload)
11. `POST /api/v1/elastic/hybrid-search` → HTTP 200 (asserted BM25 + dense vector ranking)
12. `POST /api/v1/elastic/knowledge-search` → HTTP 200 (asserted policy knowledge retrieval)
13. `GET /api/v1/timeline/bryntum-feed` → HTTP 200 (asserted resource & event store schemas)
14. `POST /api/v1/kernel/execute` → HTTP 200 (asserted simulated cloud sandboxed run)
15. `POST /api/v1/zapier/trigger` → HTTP 200 (asserted webhook trigger structure)
16. `POST /api/v1/ag-studio/query` → HTTP 200 (asserted AI natural language query analytics)
17. `GET /api/v1/analytics/spending-trends` → HTTP 200 (asserted `spending_over_time` data)
18. `GET /api/v1/post-purchase/tracking/{id}` → HTTP 200 (asserted carrier transit milestones)

---

## 4. Frontend TypeScript Validation

### Command Executed
```bash
cd frontend ; .\node_modules\.bin\tsc.cmd --noEmit
```

### Result
- **Exit Code:** 0
- **Type Errors:** 0
- **TypeScript Version:** 5.4.3
- **Output:** Clean compilation, strict null checks satisfied across all components, hooks, and pages.

---

## 5. Next.js Production Build Validation

### Command Executed
```bash
cd frontend ; npm run build
```

### Result
- **Exit Code:** 0
- **Next.js Version:** 14.2.35
- **Build Output:**
```
Route (app)                              Size     First Load JS
┌ ○ /                                    17.1 kB         118 kB
├ ○ /_not-found                          873 B          88.2 kB
├ ○ /insights                            356 kB          456 kB
├ ○ /notifications                       3.28 kB         104 kB
├ ○ /orders                              4.03 kB         105 kB
├ ƒ /orders/[id]                         5.8 kB          106 kB
└ ○ /timeline                            1.92 kB         102 kB
+ First Load JS shared by all            87.3 kB
  ├ chunks/117-ba612f9800b0b62c.js       31.7 kB
  ├ chunks/fd9d1056-86af8b28552becb8.js  53.6 kB
  └ other shared chunks (total)          1.94 kB
```
- **Prerendered Static Pages (○):** 7
- **Server-Rendered Dynamic Pages (ƒ):** 1 (`/orders/[id]`)

---

## 6. Remote GitHub Actions CI Verification

### Command Executed
```bash
gh run list --limit 1
```

### Result
- **Run ID:** `42812406951`
- **Workflow:** `CI`
- **Trigger Commit:** `86bcf85` (`fix(submission): address all Devpost PayPal hackathon audit requirements`)
- **Status:** `completed`
- **Conclusion:** `success`
- **Elapsed Duration:** 47s
- **Verification Date:** 2026-11-10T12:02:43Z

