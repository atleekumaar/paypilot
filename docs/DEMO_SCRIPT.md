# PayPilot — 3-Minute Hackathon Demonstration Script

## Overview
- **Product:** PayPilot Autonomous Commerce Platform
- **Duration:** 2 minutes 45 seconds
- **Key Integrations Showcased:** Channel3, Elasticsearch, Groq LLM, PayPal Sandbox, Bryntum, Astropods.

---

### Segment 1: Multi-Retailer Discovery via Channel3 & Elastic (0:00 - 0:45)
- **Speaker:** *"Welcome to PayPilot, the AI-powered autonomous commerce platform built for the PayPal AI Hackathon. Traditional e-commerce restricts shoppers to siloed sites. PayPilot connects directly to Channel3's product graph of over 25,000 retailers."*
- **Action on Screen:**
  - On the home page (`http://localhost:3000`), switch discovery selector to **Channel3 Retailers**.
  - Type query: *"Find me noise cancelling headphones for travel under $380"* and click **Search**.
  - Point out live retailer attribution badges: **Sony WH-1000XM5 from Best Buy ($348.00)** and **Bose QuietComfort Ultra from Amazon ($379.00)**.
  - Explain: *"Simultaneously, Elasticsearch executes hybrid Reciprocal Rank Fusion—merging BM25 keyword matching with dense vector semantic search to index and rank the most relevant candidate."*

---

### Segment 2: Grounded Recommendation & Purchase Plan Formulation (0:45 - 1:20)
- **Speaker:** *"Our Groq-powered reasoning engine evaluates user requirements and customer reviews without hallucination. It selects the Sony WH-1000XM5 as the top pick due to its 30-hour battery life and $348 price."*
- **Action on Screen:**
  - Click **View Details & Buy**.
  - Show the **Authoritative Purchase Plan Modal**.
  - Highlight: Total amount `$348.00 USD` is strictly bound on the server; the buyer must explicitly review and sign off before payment.

---

### Segment 3: Human-in-the-Loop & PayPal Sandbox Checkout (1:20 - 1:55)
- **Speaker:** *"PayPilot enforces strict Astropods safety guardrails: the AI is structurally forbidden from charging funds autonomously. It requires explicit Human-in-the-Loop authorization."*
- **Action on Screen:**
  - Click **Approve Purchase Plan**.
  - The official PayPal Sandbox button renders. Click **PayPal**.
  - Log in with Sandbox buyer credentials and complete authorization.
  - PayPilot captures the funds server-side via the PayPal Orders API v2.
  - Show the instant **Order Confirmed** receipt screen with PayPal Transaction ID and Order ID (`ORD-...`).

---

### Segment 4: Bryntum Commerce Timeline & Astropods Control Plane (1:55 - 2:45)
- **Speaker:** *"Post-purchase, PayPilot doesn't leave you with a static receipt. Let's inspect the Commerce Timeline powered by Bryntum."*
- **Action on Screen:**
  - Navigate to `/timeline` in the top navbar.
  - Show the Bryntum interactive scheduling tracks:
    1. **Approval Milestone (Emerald)**
    2. **PayPal Capture Milestone (Blue)**
    3. **Merchant Fulfillment (Indigo)**
    4. **FastShip In-Transit (Purple)**
    5. **Estimated Delivery (Amber)**
  - Click any milestone to pop open the **Milestone Inspector** showing the authoritative PayPal Capture ID and carrier tracking number.
  - Point to the right-side **Astropods Control Plane Card**:
    - Mode: `LOCAL` / `CLOUD`
    - Traced turns and tool execution latency.
    - Active guardrails: `Secret Redaction Active`, `Human-in-the-Loop Active`.
- **Closing (2:40 - 2:45):** *"From natural language discovery to verified PayPal settlement and lifecycle logistics, PayPilot makes autonomous agentic commerce transparent, reliable, and secure."*

