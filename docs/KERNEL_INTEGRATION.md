# PayPilot — Kernel Cloud Browser Integration

## 1. Overview
[Kernel](https://paypalaihackathon.devpost.com/details/kernel) provides lightning-fast cloud browser infrastructure built specifically for AI agents, featuring:
- **Sub-30ms browser session initialization**.
- **Stealth anti-bot bypass** for interacting with modern, protected ecommerce storefronts.
- **24fps live session viewing & execution replays** at `https://app.onkernel.com/sessions/{id}/replay`.
- **Real-time DOM & merchant policy extraction**.

In PayPilot, Kernel acts as the **Autonomous Merchant Inspection Engine**. When an AI agent discovers candidate products (e.g. from Channel3 cross-retailer search), it uses Kernel to inspect the live merchant URL, verify real-time inventory, extract actual return windows (e.g. 30-day free returns), and ensure store legitimacy before presenting a purchase plan to the buyer.

---

## 2. Architecture & Components

```
                +---------------------------------------+
                |   User / Shopping Workspace UI        |
                +---------------------------------------+
                                   |
                +---------------------------------------+
                |  Commerce Agent (Groq / Astropods)    |
                +---------------------------------------+
                                   |
                Tool: browse_merchant_page (READ)
                                   |
                                   v
             +---------------------------------------------+
             |    KernelBrowserService (FastAPI)           |
             |    backend/app/services/kernel/             |
             +---------------------------------------------+
                                   |
             +---------------------------------------------+
             |    Kernel Cloud API (https://api.onkernel.com)|
             |    - Sub-30ms browser spinup                |
             |    - Anti-bot stealth verification           |
             |    - Live session replay generation         |
             +---------------------------------------------+
```

### Key Modules:
- `backend/app/services/kernel/client.py`: High-performance HTTP client with token authentication, live session handling, and deterministic mock simulation for offline testing.
- `backend/app/services/kernel/service.py`: High-level business service (`inspect_merchant_product()`, `verify_merchant_domain()`, `health()`).
- `backend/app/api/kernel.py`: FastAPI endpoints:
  - `POST /api/kernel/browse`: Inspect a live retailer URL.
  - `POST /api/kernel/verify-domain`: Domain trust and return SLA verification.
  - `GET /api/kernel/health`: Kernel connection status.
- `backend/app/agents/tools.py`: Tool `browse_merchant_page` registered with `ToolPermission.READ`.

---

## 3. Environment Configuration

Add the following to `.env`:
```ini
# Kernel Cloud Browser
KERNEL_API_KEY=your_kernel_api_key_here
KERNEL_BASE_URL=https://api.onkernel.com
```

*Note: If `KERNEL_API_KEY` is omitted, PayPilot automatically switches to high-fidelity local simulation mode with realistic latency metrics (~28ms).*

---

## 4. Verification & Testing

Run unit and agent execution tests:
```powershell
python -m pytest backend/tests/test_kernel.py -v
```
All 5 Kernel tests verify:
1. Configuration loading and detection.
2. High-fidelity browser simulation with return policy extraction.
3. Merchant domain trust verification.
4. Health endpoint check.
5. Groq agent autonomous tool execution and activity logging.

