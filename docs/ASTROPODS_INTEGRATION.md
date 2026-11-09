# PayPilot — Astropods Agent Control Plane & Observability Integration

## 1. Overview & Objective

PayPilot integrates **Astropods** as the agent-native control plane, declarative deployment specification, and observability engine for its multi-turn autonomous commerce workflows.

This integration ensures:
- Declarative Blueprint-driven configuration via standard `astropods.yml`.
- Standardized Agent Card discovery via root `AGENTS.md`.
- Strict secret redaction across all telemetry spans (masking PayPal sandbox secrets, Groq inference keys, and authorization bearer tokens).
- Dual-mode runtime adapter: **LOCAL** (in-memory zero-dependency tracing for rapid local development and CI testing) and **CLOUD** (remote telemetry streaming when `ASTROPODS_API_KEY` is provided).
- Continuous turn and tool-level span instrumentation into `AgentOrchestrator`.

---

## 2. Declarative Blueprint (`astropods.yml`)

The root `astropods.yml` blueprint defines PayPilot's agentic boundaries:

- **Agent Metadata**: Identity, version `1.0.0`, description, tags (`paypal-hackathon`, `autonomous-commerce`, `agentic-payments`).
- **Runtime Environment**: Python 3.12+ / 3.14 compatible, FastAPI framework.
- **Model Provisioning**: Dual configuration supporting Groq (`openai/gpt-oss-20b`, `llama-3.3-70b-versatile`) with strict fallback rules.
- **Knowledge Grounding**: Local merchant catalog schema and search index.
- **External Integrations**: Official PayPal Orders v2 Sandbox with masked credential references.
- **Safety Guardrails**:
  - `human_in_the_loop`: Non-negotiable user confirmation required before any PayPal order creation or capture.
  - `prompt_injection_defense`: Heuristic token pattern blocking.
  - `secret_redaction`: Regex pattern enforcement wiping tokens before persistence or export.
  - `spending_limits`: Configurable per-turn and lifetime caps.

---

## 3. Agent Card (`AGENTS.md`)

The root `AGENTS.md` provides standardized machine- and human-readable documentation of:
- **Agent Identity**: PayPilot Autonomous Commerce Navigator.
- **Operational Boundaries**: Can compare, rank, and formulate purchase plans; cannot unilaterally capture payments without signed user approval.
- **Security Protocols**: Idempotency keys (`PP-ORD-*`), HMAC-SHA256 session signatures, zero secret leaks in traces.
- **Telemetry Specifications**: OpenTelemetry-aligned span hierarchy (`tool_call`, `planning`, `llm_inference`, `guardrail_evaluation`).

---

## 4. Telemetry Adapter Architecture (`astropods_service.py`)

Located at `backend/app/services/astropods_service.py`:

```
User Turn / Prompt
      │
      ▼
AstropodsService.start_trace(session_id, user_id, query)
      │
      ├──> Redact Secrets (PayPal client secrets, Groq API keys, Bearer tokens)
      │
      ├──> AstropodsService.start_span(session_id, "search_products")
      │         │
      │         └──> AstropodsService.finish_span(status="success", latency_ms=12.4)
      │
      ├──> AstropodsService.start_span(session_id, "policy_guardrail")
      │         │
      │         └──> AstropodsService.finish_span(status="success", metadata={"decision": "REQUIRE_APPROVAL"})
      │
      ▼
AstropodsService.finish_trace(status="completed")
      │
      ├── Mode == LOCAL -> Cached in memory for inspection API
      └── Mode == CLOUD -> Dispatched to Astropods control plane
```

### Secret Redaction Engine
Enforces regex pattern scrubbing before any trace or span is recorded:
- PayPal sandbox secret keys (`paypal_client_secret: ...` -> `[REDACTED_SECRET]`)
- Groq API keys (`gsk_<token>` -> `[REDACTED_GROQ_KEY]`)
- HTTP Authorization tokens (`Bearer ...` -> `[REDACTED_TOKEN]`)
- Generic API keys (`api_key=...` -> `[REDACTED_KEY]`)

---

## 5. API Endpoints

1. **`GET /api/agent/{session_id}/astropods-traces`**
   - Retrieves granular traces and child execution spans for a specific conversational session.
   - Outputs duration, status, tool names, and redacted parameters.

2. **`GET /api/agent/astropods/overview`**
   - Returns global control plane telemetry metrics:
     - `mode`: `"LOCAL"` or `"CLOUD"`
     - `project_id`: `"paypilot-ai-commerce"`
     - `total_traces`: Count of completed agent turns
     - `total_spans`: Count of executed tool calls
     - `failed_spans`: Count of failed tool attempts
     - `average_turn_latency_ms`: Mean duration
     - `guardrails`: Status of active safety policies

---

## 6. Verification & Test Coverage

Verified via automated test suite in `backend/tests/test_astropods.py`:
- `test_redact_sensitive_data`: Verifies regex redaction across nested objects and query strings.
- `test_astropods_trace_lifecycle`: Verifies trace creation, multi-span tracking, status completion, and metrics calculation.
- `test_astropods_overview_metrics`: Verifies aggregated cross-session stats.
- `test_astropods_api_endpoints`: Verifies FastAPI routes return 200 OK with expected JSON envelope.

