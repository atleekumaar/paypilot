# APIMatic Integration Guide for PayPilot

This guide explains how **APIMatic ContextMatic** is integrated into the PayPilot development workflow and how developers and AI coding agents (Antigravity, Cursor, Claude Code, VS Code) use it to work accurately with PayPal APIs and internal contracts.

---

## 1. Overview & Objective

When building or modifying API integrations (such as PayPal checkout, order capture, webhooks, or carrier telemetry), general-purpose AI coding agents frequently hallucinate method signatures, parameter names, or deprecated fields due to outdated training data.

**APIMatic ContextMatic** bridges this gap by acting as a live, SDK-native context provider powered by the Model Context Protocol (MCP). It delivers:
- Version-accurate PayPal Server SDK method signatures and response models.
- Idiomatic client initialization and authentication patterns.
- Direct schema lookup without guessing payloads or headers.

---

## 2. Integration Architecture

APIMatic is configured on the **developer-side only** and is completely decoupled from application runtime code:

```
Developer / AI Agent Layer
  │
  ├── MCP Protocol (Remote: https://chatbotapi.apimatic.io/mcp/plugins)
  │     └── Exposes tools: fetch_api, ask, endpoint_search, model_search
  │
  ├── Agent Customizations (.agents/plugins/context-matic/)
  │     ├── skills/integrate-context-matic/SKILL.md
  │     ├── skills/onboard-context-matic/SKILL.md
  │     └── rules/AGENTS.md
  │
  └── Offline Grounding Contracts (docs/api-specs/)
        ├── paypal/checkout_orders_v2.json  (Official PayPal Orders API v2 OpenAPI spec)
        ├── paypal/payments_payment_v2.json (Official PayPal Payments API v2 OpenAPI spec)
        ├── paypal/APIMATIC-META.json       (APIMatic metadata configuration)
        └── paypilot/paypilot_openapi.json  (PayPilot backend OpenAPI spec)

───────────────────────────────────────────────────────────── (Runtime Boundary)

Application Runtime Layer (100% Isolated & Untouched)
  ├── backend/app/services/paypal/ (auth.py, orders.py, config.py)
  ├── backend/app/api/payments.py
  └── frontend/ (Next.js & @paypal/react-paypal-js)
```

---

## 3. The 4 ContextMatic MCP Tools

ContextMatic exposes four tools to the coding agent:

| Tool | Purpose | Example Usage in PayPilot |
|---|---|---|
| `fetch_api` | Discovers available APIs in the catalog or checks for an exact match by `key` and `language`. | `fetch_api(language="python", key="paypal")` |
| `ask` | Asks the API Copilot for step-by-step guidance, SDK configuration, or framework patterns. | `ask(key="paypal", language="python", query="How do I create and capture an order with PayPal Orders v2?")` |
| `endpoint_search` | Fetches method signature, required parameters, and response shape for a specific endpoint. | `endpoint_search(key="paypal", language="python", query="createOrder")` |
| `model_search` | Returns full model definition and typed schema properties. | `model_search(key="paypal", language="python", query="Order")` |

---

## 4. How to Use in Coding Tasks

### Running the Interactive Onboarding Tour
To explore the APIMatic tools interactively, invoke the onboarding skill:
```text
/onboard-context-matic
```
The agent will:
1. Detect your current project language (`python` or `typescript`).
2. List available API SDKs from APIMatic.
3. Walk through live demonstrations of `model_search` and `endpoint_search` using PayPal as the example.

### Executing an API Task with Context Grounding
When implementing or modifying an API feature, prompt your agent with:
```text
/integrate-context-matic Look up the PayPal Orders API v2 capture endpoint and verify the response structure for successful captures.
```
The agent will automatically:
1. Look up the `paypal` API entry.
2. Query `endpoint_search` for `captureOrder` / `capture`.
3. Check `model_search` for `Order` and `Capture`.
4. Implement or verify the code using authoritative types.

---

## 5. Editor Configuration Details

### Antigravity IDE
Antigravity automatically discovers:
- Plugin manifest at `.agents/plugins/context-matic/plugin.json`
- MCP configuration at `.agents/plugins/context-matic/mcp_config.json`
- Agent skills under `.agents/plugins/context-matic/skills/`
- Workspace rules under `.agents/plugins/context-matic/rules/AGENTS.md`

### VS Code
Uses `.mcp.json` at the project root:
```json
{
  "mcpServers": {
    "context-matic": {
      "type": "http",
      "url": "https://chatbotapi.apimatic.io/mcp/plugins",
      "headers": {
        "X-Apimatic-Mcp-Client": "Antigravity"
      }
    }
  }
}
```

### Cursor
Uses `.cursor-mcp.json` at the project root:
```json
{
  "mcpServers": {
    "context-matic": {
      "type": "http",
      "url": "https://chatbotapi.apimatic.io/mcp/plugins",
      "headers": {
        "X-Apimatic-Mcp-Client": "Cursor"
      }
    }
  }
}
```

### Claude Code
Run from your terminal in the workspace:
```bash
/plugin marketplace add apimatic/context-matic
/plugin install context-matic@apimatic-context-matic
/reload-plugins
```

---

## 6. Authentication & Manual Steps (If Required)

ContextMatic's public catalog for standard APIs (including PayPal) operates directly over the MCP endpoint. However, if your development environment requires authenticated access to private APIMatic services, custom API portals, or an APIMatic Validator account:

1. **Obtain an APIMatic Account / API Key**:
   - Sign up or log in at [https://apimatic.io](https://apimatic.io).
   - Navigate to **Account Settings > API Keys** to generate an API key.
2. **If Using APIMatic CLI**:
   ```bash
   apimatic auth login --auth-key=<YOUR_APIMATIC_API_KEY>
   ```
3. **If Using Private MCP Services**:
   Add your authorization header to `.mcp.json`:
   ```json
   {
     "mcpServers": {
       "context-matic": {
         "type": "http",
         "url": "https://chatbotapi.apimatic.io/mcp/plugins",
         "headers": {
           "Authorization": "Bearer <YOUR_APIMATIC_TOKEN>"
         }
       }
     }
   }
   ```
*(For standard development with PayPilot and PayPal public specs, no manual API key is required).*

---

## 7. Safety & Runtime Isolation Summary

- **Payment Logic**: `backend/app/services/paypal/` remains 100% authoritative.
- **Price Security**: All amounts are bound to server-side `PurchasePlan` instances.
- **Secrets Management**: No API keys, credentials, or client secrets are committed or modified.
