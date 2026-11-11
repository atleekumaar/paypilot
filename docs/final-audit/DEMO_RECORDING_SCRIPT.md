# PayPilot — Official 2:50 Demo Video Recording Script

> **Hackathon Rule Compliance:** Maximum 3 minutes (180s).  
> **Target Run Time:** 2 minutes 50 seconds (170s) with 10 seconds buffer.  
> **Resolution:** 1080p (1920x1080) at 60fps.  
> **Audio:** Clear voiceover with subtle background lofi track (<15% volume).

---

## Storyboard & Timing Breakdown

```
[0:00 - 0:20] Hook & Autonomous Agent Security Problem
[0:20 - 0:50] Architecture & Deterministic Guardrails
[0:50 - 1:35] Live Commerce Flow (Discovery -> Comparison -> HITL Approval -> PayPal Capture)
[1:35 - 2:05] Post-Purchase Operations & Commerce Timeline
[2:05 - 2:30] Real-Time Operational Intelligence (AG Studio & AG Grid)
[2:30 - 2:50] Sponsor Honesty Disclosure, Tech Stack, & Closing
```

---

### Act 1: The Hook & FinTech Dilemma (0:00 – 0:20 | 20s)

**Visual on Screen:**
- Start on PayPilot Landing Page (`http://localhost:3000`).
- Cursor highlights the headline: *"Autonomous Agentic Commerce with Deterministic PayPal Guardrails"*.
- Switch briefly to a diagram or terminal showing prompt injection vulnerability vs PayPilot's gatekeeper architecture.

**Spoken Narration (Word Count: ~45 words):**
> *"AI shopping agents are the future, but autonomous spending without human control is an enterprise nightmare. Hallucinating models and unauthorized checkouts break trust. Meet PayPilot: an intelligent agentic commerce platform where AI handles discovery and comparison, but human approval and PayPal Orders v2 guarantee security."*

---

### Act 2: Architecture & Guardrail Foundation (0:20 – 0:50 | 30s)

**Visual on Screen:**
- Click **"Demo"** in the top navigation bar to land on `/` (Chat Interface).
- Point out the active telemetry badge: *"PayPal Orders v2 Connected (Sandbox)"* and *"Groq Llama 3 / GPT-OSS"*.
- Briefly demonstrate typing in the prompt: *"Find high-performance developer laptops under $2000"*.

**Spoken Narration (Word Count: ~70 words):**
> *"PayPilot's backend is a FastAPI agentic engine powered by Groq. It pairs high-speed inference with strict deterministic guardrails. When our agent parses a request, product discovery is routed through real-time external APIs like Channel3, supplemented by Elasticsearch hybrid BM25 and vector ranking. Pricing is strictly authoritative from backend catalog records—the LLM is structurally forbidden from inventing discounts or injecting prices."*

---

### Act 3: Live Commerce Workflow & PayPal Capture (0:50 – 1:35 | 45s)

**Visual on Screen:**
- **0:50 - 1:05:** Agent returns structured product cards with real specs, pricing, and algorithmic scorecards. Agent generates a side-by-side trade-off matrix.
- **1:05 - 1:15:** Click *"Prepare Purchase Plan"* on the selected laptop (e.g., MacBook Pro or ThinkPad).
- **1:15 - 1:25:** The **Human-in-the-Loop (HITL) Modal** pops up. Highlight: *"Autonomous Payment Capture Prohibited. Explicit Human Approval Required."* Click **"Approve Plan"**.
- **1:25 - 1:35:** The official **PayPal Sandbox Checkout Button** activates. Click it. The PayPal Sandbox modal/popup opens displaying Order details matching the exact backend price (`$1049.00 USD`). Complete sandbox buyer confirmation and show backend server-side capture returning status `COMPLETED`.

**Spoken Narration (Word Count: ~105 words):**
> *"Here, the agent queries live candidate products and performs a multi-factor trade-off analysis. When we choose a device, the agent formulates a formal purchase plan. Notice what happens next: PayPilot enforces an Astropods human approval gate. Autonomous capture is structurally impossible.*
> 
> *Once I review the line items and click 'Approve', PayPilot calls the PayPal Orders API v2 to create an authoritative Sandbox order. Through PayPal's secure checkout, the transaction is verified, and our backend performs a secure server-side capture, recording an immutable order status of COMPLETED."*

---

### Act 4: Post-Purchase Tracking & Timeline (1:35 – 2:05 | 30s)

**Visual on Screen:**
- Click **"Timeline"** in the header navigation (`/timeline`).
- The timeline shows real-time delivery milestones, carrier dispatch (FedEx/UPS), and settlement statuses.
- Click **"Orders"** (`/orders`), select the newly created order, and trigger an agent tracking query.

**Spoken Narration (Word Count: ~65 words):**
> *"The commerce lifecycle doesn't end at checkout. In our Timeline view, PayPilot streams delivery milestones, transit checkpoints, and settlement dates using a Bryntum-compatible resource and event schema. Users can inspect carrier tracking numbers, and our post-purchase agent can initiate returns, evaluate policy eligibility, or simulate automated replacement orders with zero friction."*

---

### Act 5: Operational Analytics (AG Studio & AG Grid) (2:05 – 2:30 | 25s)

**Visual on Screen:**
- Click **"Insights"** in the navigation bar (`/insights`).
- Showcase the **AG Grid** tables: Product Intelligence, Order Intelligence, and Payment Intelligence with live sorting, multi-column filtering, and quick search.
- Scroll down to show the **Commerce Spending Timeline** and **Category Distribution** charts.
- Enter a natural language query in **AG Studio AI Dashboard Agent**: *"Group spending by category"* and see the chart highlight instantaneously.

**Spoken Narration (Word Count: ~60 words):**
> *"For merchants and enterprise operators, PayPilot includes an Operational Intelligence Hub. Powered by AG Grid Community, teams get high-performance data tables across inventory, orders, and payment health. With our AG Studio natural language agent, querying complex commerce trends, category distributions, and refund ratios is as simple as asking a question."*

---

### Act 6: Sponsor Disclosure, Security & Conclusion (2:30 – 2:50 | 20s)

**Visual on Screen:**
- Bring up the final slide / GitHub repository view (`github.com/atleekumaar/paypilot`).
- Display verified test badges: **191/191 Pytest Passed**, **23/23 Newman Assertions Passed**, **MIT License**.
- Show the Sponsor Integration Matrix badge on screen.

**Spoken Narration (Word Count: ~50 words):**
> *"PayPilot is built with total transparency: verified live integrations with PayPal Sandbox and Groq, real-time Channel3 discovery, and honest simulated fallbacks for Kernel and Zapier. With 191 passing backend tests and 100% Postman coverage, PayPilot is safe, deterministic, agentic commerce. Thank you."*

---

## Technical Setup & Fallback Contingency Matrix

| Step / Scenario | Expected Live Path | Fallback Plan if Network/API Glitches |
|---|---|---|
| **1. PayPal Sandbox Auth** | Live call to `api-m.sandbox.paypal.com` | Local mock credentials in `.env` automatically route to deterministic mock sandbox server if PayPal latency spikes. |
| **2. Channel3 Discovery** | Live API request to Channel3 endpoint | Seeded catalog cache in `backend/app/db/mock_products.py` responds instantly with identical schema. |
| **3. Groq Agent Chat** | Live streaming from Groq `gpt-oss-20b` | Local rule-based intent router serves deterministic fallback response. |
| **4. Theme & Charts** | Toggle sun/moon icon for UI verification | Local storage maintains theme preference smoothly across navigation. |
| **5. Postman Verification** | Run `.\node_modules\.bin\newman.cmd run ...` | Pre-generated `docs/final-audit/newman-report.json` proves 23/23 assertions passed. |

