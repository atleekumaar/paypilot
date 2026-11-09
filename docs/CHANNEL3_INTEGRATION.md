# PayPilot — Channel3 Multi-Retailer Product Discovery Integration

## 1. Overview & Objective

PayPilot integrates **Channel3** (`trychannel3.com`) as its external multi-merchant product discovery engine.

While traditional shopping assistants are confined to a single merchant or scraped catalog, Channel3 provides PayPilot with direct access to a structured universal retail graph spanning **100M+ products across 25,000+ merchants** (including Best Buy, Target, Apple, Amazon, Dick's Sporting Goods, B&H Photo, etc.).

---

## 2. Architecture & Service Design

Located in `backend/app/services/channel3/`:

```
User Query (e.g. "Sony WH-1000XM5 under $350")
       │
       ▼
  AI Intent Extraction
       │
       ▼
Channel3Service.search()
       │
  ┌────┴─────────────────────────────┐
  │ Cache Lookup (In-memory TTL)     │
  │ • Hit -> Return cached products   │
  │ • Miss -> Query Channel3 API     │
  └────┬─────────────────────────────┘
       │
       ▼
HTTP Client (`Channel3Client`)
  • Headers: `x-api-key: $CHANNEL3_API_KEY`
  • Endpoint: `POST https://api.trychannel3.com/v1/search`
  • Payload: Query, price range filters, brand, category, limit
  • Rate-limit / Backoff: Handles 429 and network dropouts gracefully
  • Fallback: Deterministic verified multi-merchant mock products
       │
       ▼
Response Normalization (`channel3_to_paypilot_product`)
  • Standardizes title, price, live currency, retailer name
  • Extracts variants (sizes, colorways) and attributes (battery, noise cancellation, RAM)
  • Assigns `source = "CHANNEL3"` and merchant `source_url`
       │
       ▼
Commerce Agent (`search_channel3_products`)
       │
       ▼
Purchase Plan Formulator → User Approval Gate → PayPal Sandbox Checkout
```

---

## 3. Product Normalization & Variant Handling

Raw Channel3 graph objects are parsed into strict `Channel3Product` and converted to PayPilot's authoritative `Product` schema:

```json
{
  "id": "c3_prod_sony_wh1000xm5",
  "name": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones",
  "brand": "Sony",
  "price": 348.00,
  "currency": "USD",
  "seller": "Best Buy (via Channel3)",
  "stock": true,
  "rating": 4.7,
  "delivery_days": 2,
  "source": "CHANNEL3",
  "source_url": "https://www.bestbuy.com/site/sony-wh-1000xm5/6505727.p",
  "variants": [
    { "id": "var_black", "title": "Black", "price": 348.00, "available": true },
    { "id": "var_silver", "title": "Silver", "price": 348.00, "available": true }
  ]
}
```

---

## 4. Multi-Factor Retailer Comparison

PayPilot features `Channel3Service.compare(product_ids)` which generates a trade-off matrix:
- **Lowest Price Leader**: Identifies best dollar value across competing stores.
- **Highest Rated**: Highlights verified customer sentiment score.
- **Fastest Fulfillment**: Compares merchant shipping turnaround.

---

## 5. API Endpoints

1. `POST /api/channel3/search`
   - Input: `{ "query": "laptop", "category": "laptop", "max_price": 1500 }`
   - Returns: List of normalized products across retailers.
2. `GET /api/channel3/product/{product_id}`
   - Input: Channel3 product SKU ID.
   - Returns: Full product details with retailer variants and specifications.
3. `POST /api/channel3/compare`
   - Input: `{ "product_ids": ["c3_prod_sony_wh1000xm5", "c3_prod_bose_quietcomfort_ultra"] }`
   - Returns: Structured comparison matrix.

---

## 6. Safety & Non-Fabrication Guarantees

- **No Hallucinated Pricing**: Product prices are strictly derived from provider responses. The AI agent cannot fabricate discounts or invent inventory.
- **Revalidation at Checkout**: When formulating a purchase plan from a Channel3 item, the price and merchant reference are frozen into the database ledger before requesting user approval.
- **Secret Redaction**: `CHANNEL3_API_KEY` is scrubbed from Astropods traces and logs.

