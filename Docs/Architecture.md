# MYNTRA WISHLIST DECISION STUDIO
## Technical Architecture — MVP

This document is the technical architecture for the Myntra Wishlist Decision Studio MVP. It is derived from `Docs/Context.md.md` and `Docs/ProblemStatement.md`.

It answers one question:

> **What data do we collect → where do we store it → how do we process it → what is precomputed offline → what happens online → when does AI get called → what does the user finally see inside Wishlist?**

**This document does not include application code or UI design.** Canonical API/`saved_price`/phase locks: `Docs/Doc_Alignment.md`.

**Stack constraint:** the MVP uses **only free / open-source tooling** plus **Groq’s free LLM API**. No paid model APIs (OpenAI, Gemini paid), no paid search/vector products, no paid databases or hosting as a requirement. Local-first is the default.

---

## 1. Architecture Overview

The product is a small Myntra-like shopping MVP. The innovation is not a new page. **Wishlist becomes an embedded decision workspace.**

The architecture has two zones:

| Zone | Purpose | When it runs | Cost profile |
|---|---|---|---|
| **Offline layer** | Collect, clean, normalize, and precompute catalog intelligence | Batch / scheduled / on data change | Expensive, repeatable, not user-specific |
| **Online layer** | Serve shopping + decision support for a specific user | Per request | Fast, user-specific, LLM only when the user asks |

The system is a **modular monolith**, not microservices.

```text
DATA SOURCE (seed JSON first, replaceable ingestion later)
        ↓
OFFLINE PIPELINE  (Python)
        ↓
SQLITE  (source of truth)
        ↓
FASTAPI  +  DETERMINISTIC DECISION ENGINE
        ↓
GROQ LLM  (free tier, synthesis only, on demand)
        ↓
REACT + VITE  (Wishlist is the decision surface)
        ↓
USER
```

**Core rule:** the frontend never scrapes, never reads raw files, and never calls the LLM directly. The Decision Engine never invents facts. The LLM only explains evidence that already exists in the database.

---

## 2. High-Level Architecture Diagram

```text
                         ┌─────────────────────────┐
                         │     EXTERNAL / SEED     │
                         │  products · reviews ·   │
                         │      price history      │
                         └────────────┬────────────┘
                                      │
====================== OFFLINE =================================
                                      ↓
                         ┌─────────────────────────┐
                         │   INGESTION ADAPTER     │
                         │  SeedFileSource         │
                         │  (ExternalSource later) │
                         └────────────┬────────────┘
                                      ↓
                         ┌─────────────────────────┐
                         │     RAW DATA STORE      │
                         │  immutable snapshots    │
                         └────────────┬────────────┘
                                      ↓
                         ┌─────────────────────────┐
                         │   BATCH PROCESSORS      │
                         │  clean · normalize      │
                         │  validate · analyze     │
                         └────────────┬────────────┘
                                      ↓
                         ┌─────────────────────────┐
                         │     MAIN DATABASE       │
                         │  products · reviews     │
                         │  insights · prices      │
                         │  similarity · alerts    │
                         └────────────┬────────────┘
                                      │
======================= ONLINE =================================
                                      ↓
         USER ──► FRONTEND ──► BACKEND API
                                      │
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
              SHOPPING APIs     DECISION ENGINE    ALERT APIs
              products          evidence pack      price drop
              wishlist          scores             similar product
              bag               confidence         overload
              profile                 │
                                      ↓
                              GROQ LLM ADAPTER
                            (Llama, only if needed)
                                      ↓
                                 FRONTEND
                               Wishlist workspace
                                      ↓
                                    USER
```

---

## 3. Offline Architecture

The offline layer exists because catalog work is **expensive, shared, and independent of any one shopper**. Running it at request time would make Wishlist slow, costly, and likely to hallucinate.

### What belongs offline, and why

| Capability | Why offline |
|---|---|
| Data collection / scraping | External, slow, legally and operationally constrained |
| Cleaning, normalization, validation | Shared catalog work; do once, reuse many times |
| Review theme extraction | LLM-heavy; must not rerun on every question |
| Review aggregation | Stable until new reviews arrive |
| Price history statistics | Deterministic and catalog-level |
| Attribute-based similarity | Catalog-level; needed instantly at runtime |
| Price-drop scan vs saved prices | Periodic comparison, not a live market feed |
| Seed / snapshot of similar-product alerts | Derived from catalog + current wishlists |

### Offline modules

```text
offline/
  ingestion/
    sources/          SeedFileSource | ExternalSource
    parsers/
    validators/
  processors/
    product_normalizer
    review_normalizer
    price_normalizer
    review_analyzer      ← Groq LLM used here (batch)
    price_aggregator
    similarity_builder
    alert_scanner
  jobs/
    ingest_catalog
    rebuild_insights
    rebuild_similarity
    scan_price_alerts
```

### Offline outputs written to the database

- `products` (normalized)
- `reviews` (normalized, still available as evidence)
- `review_insights` (theme counts + summaries)
- `price_history` + `price_stats`
- `product_similarity`
- `alerts` (price drop / similar product, generated by jobs)

Offline processing **does not** know a user’s current comparison selection or the question they just tapped. That is online work.

---

## 4. Online Architecture

The online layer exists because decisions are **user-specific**: this Wishlist, these 2–3 selected items, this question, these preferences.

### What belongs online, and why

| Capability | Why online |
|---|---|
| Browse / PDP / Wishlist / Bag / Profile | Live user state |
| Load Wishlist with decision signals | Join user rows to precomputed catalog facts |
| Compare selected products | Selection exists only at request time |
| Ask Me a Question | User-triggered, context-specific |
| Recommendation explanation | Depends on current shortlist + preferences |
| Decision-overload prompt | Depends on current Wishlist grouping |
| Add to Bag / mock checkout | Transactional user action |

### What must NOT happen online

- Scraping Myntra (or any site) on a page load
- Re-analyzing all reviews with an LLM when Wishlist opens
- Recomputing catalog-wide similarity on every request
- Calling the LLM just to render product cards, prices, ratings, or decision-signal badges

### Online request path

```text
USER
  ↓
FRONTEND (React + Vite)
  ↓
HTTP API (FastAPI)
  ↓
DOMAIN SERVICES
  wishlist | products | bag | alerts | questions | comparison
  ↓
REPOSITORIES  →  SQLITE
  ↓
DECISION ENGINE  (deterministic evidence + scores)
  ↓
GROQ LLM ADAPTER  (only for compare explain / Q&A / recommendation copy)
  ↓
JSON RESPONSE
  ↓
WISHLIST UI
```

---

## 5. Offline vs Online Boundary

This boundary is the most important architectural rule.

```text
====================== OFFLINE ======================
Runs: batch job, seed load, or scheduled scan
Input: external/seed catalog
Output: database rows anyone can read
LLM: yes, for review theme extraction only
User context: none

External / seed data
     ↓
Ingestion adapter
     ↓
Raw snapshot store
     ↓
Clean → normalize → validate
     ↓
Review analysis (LLM batch)
     ↓
Price statistics
     ↓
Attribute similarity graph
     ↓
Scheduled alert scan
     ↓
MAIN DATABASE
     ↓
Precomputed insights ready for all users


======================= ONLINE =======================
Runs: HTTP request
Input: user_id + product_ids + question_id
Output: Wishlist UI payloads
LLM: only when the user compares, asks, or requests a recommendation
User context: Wishlist, preferences, selection

User
 ↓
Frontend
 ↓
API
 ↓
Load Wishlist / selection / preferences
 ↓
Read precomputed product + insight + price + similarity rows
 ↓
Decision Engine (deterministic)
 ↓
LLM only if this request needs language
 ↓
Response
 ↓
User sees signals / comparison / answer / alert inside Wishlist
```

### Offline vs online decision table

| Operation | Offline | Online | Why |
|---|---|---|---|
| Product collection / scraping | ✓ | | External, slow, must not block UX |
| Product normalization / validation | ✓ | | Shared catalog contract |
| Raw snapshot storage | ✓ | | Replay and source replacement |
| Review cleaning / dedup | ✓ | | Stable corpus |
| Review theme extraction (LLM) | ✓ | | Avoid repeated LLM cost/latency |
| Review insight aggregation | ✓ | | Precompute for every Wishlist render |
| Price history ingest | ✓ | | Catalog fact |
| Price statistics (min/max/position) | ✓ | | Deterministic, reused |
| Product similarity graph | ✓ | | Fast, explainable lookup |
| Seed catalog load | ✓ | | MVP starts here |
| Wishlist / Bag CRUD | | ✓ | User-specific, real time |
| Wishlist page load | | ✓ | Join user rows to precomputed facts |
| Decision-signal badges | | ✓* | *Computed online from stored insights; no LLM |
| Price insight for one product | | ✓* | *Uses stored `price_stats` + `saved_price` |
| Compare 2–3 products (numbers) | | ✓ | Selection is request-specific |
| Compare trade-off explanation | | ✓ | LLM synthesis of Decision Engine evidence |
| Ask Me a Question | | ✓ | User-triggered |
| Recommendation score | | ✓ | Deterministic, uses preferences |
| Recommendation explanation | | ✓ | LLM |
| Decision-overload detection | | ✓ | Current Wishlist grouping |
| Price-drop detection | ✓ scheduled | serve online | Scan in job; display on Wishlist load |
| Similar-product alert | ✓ scheduled **or** on Wishlist add | serve online | Simplest MVP: check on add + on Wishlist load |
| Add to Bag / mock purchase | | ✓ | User action |
| LLM grounded answer | | ✓ | Needs live evidence pack |

---

## 6. Data Ingestion / Scraping Pipeline

### Principle

**DATA SOURCE is replaceable. APPLICATION LOGIC is not coupled to HTML.**

The MVP must **not** depend on a live Myntra scraper. The first source is a designed seed dataset (50–100 products) that creates real decision scenarios.

Reference storefront (look-and-feel only): [https://www.myntra.com/](https://www.myntra.com/). If the live site is down or in maintenance, the MVP still runs entirely from seed data.

```text
                    DATA SOURCES
                         |
           ┌─────────────┴─────────────┐
           ↓                           ↓
     SeedFileSource              ExternalSource
     data/products.json          (optional later)
     data/reviews.json           compliant collection
     data/price-history.json     terms-respecting only
           |                           |
           └─────────────┬─────────────┘
                         ↓
                  Ingestion Adapter
                         ↓
              parse → snapshot raw files
                         ↓
         normalizeProduct()
         normalizeReview()
         normalizePriceHistory()
                         ↓
                   validate()
                         ↓
                  MAIN DATABASE
```

### MVP ingestion (Phase 1)

```text
data/*.json
    ↓
ingest_catalog job
    ↓
raw/ snapshots
    ↓
normalized tables
```

No network scrape is required to demo the product.

### Later ingestion (optional)

If real product data is added:

- Collect only through a **compliant** method (public APIs, licensed data, or user-provided exports).
- Respect terms, copyright, privacy, and rate limits.
- **Do not** design around bypassing anti-bot protections.
- Parser output must still be the same normalized objects.
- Frontend and Decision Engine remain unchanged.

### What is never scraped at runtime

Product listing, PDP, Wishlist, comparison, and Q&A all read the database. A failed or paused ingestion job must not take down shopping.

---

## 7. Raw Data → Processed Data Pipeline

Keep **raw** and **processed** separate so the source can change without breaking the app.

### RAW DATA (immutable snapshots)

```text
raw/
  products/{batch_id}.json
  reviews/{batch_id}.json
  prices/{batch_id}.json
  _manifest.json          source, timestamp, record counts
```

Purpose:

- Replay a bad transform
- Debug “why does product P001 look like this?”
- Swap SeedFileSource for ExternalSource without rewriting APIs
- Prove the app never read HTML

### PROCESSED DATA (application contract)

```text
products
reviews
review_insights
price_history
price_stats
product_similarity
```

Plus user data (never from scrape):

```text
users
wishlist_items
bag_items
alerts
```

### Pipeline

```text
RAW SNAPSHOT
    ↓
Clean
  - trim text, fix encoding
  - drop empty reviews
  - coerce types (price → integer paise/rupees)
    ↓
Deduplicate
  - products by product_id
  - reviews by review_id / (product_id + text hash)
    ↓
Normalize
  - canonical schema (see §9)
    ↓
Validate
  - required fields
  - price ≤ mrp
  - rating in range
  - unknown category flagged, not invented
    ↓
Enrich (offline)
  - review insights (LLM batch)
  - price_stats
  - similarity edges
    ↓
UPSERT into processed tables
```

### Why this split matters

If ingestion starts as JSON and later becomes an external feed, only the adapter and raw snapshots change. Wishlist, comparison, and the LLM evidence pack still query `products`, `review_insights`, and `price_stats`.

**Hard rule:** missing fields stay missing. The pipeline must not invent ratings, reviews, fit claims, or prices to “complete” a row.

---

## 8. Data Storage Architecture

Simplest storage that fits a 50–100 product MVP:

```text
                 DATA STORAGE (MVP)

        ┌────────────────────────────────┐
        │  FILE STORE                    │
        │  data/*.json     (seed source) │
        │  raw/            (snapshots)   │
        │  public/images   (product imgs)│
        └──────────────┬─────────────────┘
                       ↓
        ┌────────────────────────────────┐
        │  RELATIONAL DATABASE           │
        │  SQLite (MVP — free, local)    │
        │                                │
        │  catalog + insights + users    │
        └────────────────────────────────┘

        NO Kafka
        NO Kubernetes
        NO Elasticsearch
        NO Redis
        NO Vector DB
        NO object-store cluster
```

| Store | What lives there | Why |
|---|---|---|
| Seed JSON | Initial catalog | Easy to edit demo scenarios |
| Raw files | Immutable ingest snapshots | Source replacement + replay |
| SQLite | All runtime reads/writes | One source of truth; free, zero ops |
| Local image files / URLs | Product imagery | Fashion UI needs images; not a CDN for MVP |

### What the MVP does **not** need

| Technology | Needed? | Reason |
|---|---|---|
| Kafka | No | No high-volume event stream |
| Kubernetes | No | One app, one process (or two) |
| Elasticsearch | No | Catalog is tiny; SQL filters are enough |
| Redis | No | No hot-path cache problem at this scale |
| Vector DB | No | Questions are predefined; retrieval is structured (see §16) |
| Microservices | No | Adds ops cost; modules in one backend are enough |
| Paid LLM (OpenAI / Gemini / Anthropic) | No | Groq free tier covers synthesis |

---

## 9. Database Architecture

One relational database. Logical modules, not separate services.

### Catalog (mostly written offline)

**products**  
`product_id`, brand, name, gender, category, subcategory, style, price, mrp, discount, rating, rating_count, image_url, product_url, sizes, colors, fit, material, occasions, attributes_json, updated_at

**reviews**  
`review_id`, product_id, rating, review_text, review_date, source_batch_id

**review_insights**  
`product_id`, theme, positive_count, negative_count, summary, evidence_review_ids, confidence, updated_at

**review_insight_rollups** (optional, can be a view)  
`product_id`, likes_summary, concerns_summary, overall_signal, review_volume_band

**price_history**  
`id`, product_id, date, price

**price_stats**  
`product_id`, current_price, min_price, max_price, avg_price, min_date, relative_position, updated_at

**product_similarity**  
`product_id`, similar_product_id, score, matched_attributes, reason

### User (online)

**users**  
`user_id`, size, price_min, price_max, occasions, priorities, display_name

**wishlist_items**  
`user_id`, product_id, added_at, saved_price

**bag_items**  
`user_id`, product_id, added_at

**orders** (mock)  
`order_id`, user_id, product_ids, created_at, status

### Derived signals (job or on write)

**alerts**  
`alert_id`, user_id, type (`PRICE_DROP` \| `SIMILAR_PRODUCT` \| `DECISION_OVERLOAD`), product_id, payload_json, created_at, dismissed_at, seen_at

### Relationships (conceptual)

```text
users 1───N wishlist_items N───1 products
users 1───N bag_items      N───1 products
products 1───N reviews
products 1───N review_insights
products 1───N price_history
products 1───1 price_stats
products 1───N product_similarity (self)
users 1───N alerts
```

SQLite JSON columns are acceptable for `occasions`, `sizes`, `priorities`, and alert payloads. PostgreSQL is also free/open-source but is **not** required for this MVP.

---

## 10. Review Intelligence Architecture

Review intelligence is the highest-value offline AI job. Runtime must **not** send every review to the LLM.

```text
====================== OFFLINE ======================

Raw reviews
   ↓
Clean / normalize
   ↓
Deduplicate
   ↓
Batch by product (only products with reviews)
   ↓
LLM / NLP analysis  ← THE expensive AI call
   ↓
Theme extraction + sentiment by theme
   Themes: FIT, SIZE, FABRIC, QUALITY, COMFORT,
           COLOR, DURABILITY, APPEARANCE, VALUE,
           OCCASION, IMAGE_ACCURACY, COMPLAINTS
   ↓
Aggregate counts
   ↓
Write review_insights
   ↓
Write short grounded summaries
   (e.g. "Among available reviews, fabric thinness is the main concern.")
   ↓
Confidence band from volume + agreement
   HIGH / MEDIUM / LOW


======================= ONLINE =======================

Question or Wishlist insight
   ↓
SELECT review_insights WHERE product_id = ?
   ↓
Optional: SELECT 1–3 raw reviews whose ids are in evidence_review_ids
   ↓
Decision Engine evidence pack
   ↓
LLM synthesizes an answer from THIS pack only
```

### Raw reviews stay in the database

Yes. Processed insights are the default runtime input. Raw reviews remain for:

- Grounding (“among the available reviews…”)
- Displaying 1–3 supporting quotes the model is allowed to cite
- Re-running the analyzer after prompt changes

The online path retrieves **already-selected** evidence rows. It does not re-cluster the corpus.

### Grounding rules encoded in the processor

| Condition | Stored / returned language |
|---|---|
| 0 reviews | `Not enough review data to assess this reliably.` |
| Few reviews | `Among the available reviews…` never `Most buyers…` |
| Theme absent | Theme omitted; do not say “fit is excellent” |
| Conflicting theme | Both positive and negative counts kept; signal = mixed |

---

## 11. Price Intelligence Architecture

Price math is **deterministic**. The LLM must not compute min/max or invent a future drop.

```text
====================== OFFLINE ======================

price_history rows
   ↓
For each product:
   current_price   = latest point (or products.price)
   min_price       = MIN(history)
   max_price       = MAX(history)
   avg_price       = AVG(history)
   relative_position = (current - min) / (max - min)
                     if max == min → "only one observed price"
   ↓
UPSERT price_stats


======================= ONLINE =======================

Wishlist item
   ↓
products.price + wishlist_items.saved_price + price_stats
   ↓
Decision Engine.price_insight():
   discount vs MRP
   delta vs saved_price
   delta vs historical min
   relative position label
   ↓
Language rules (code, not LLM):
   "Current price is close to the recent low."
   "This item has previously dropped below the current price."
   NEVER: "The price will drop tomorrow."
   If no history: "Price history unavailable."
```

LLM may **rephrase** a price insight only when answering a question, and only using the numbers in the evidence pack.

---

## 12. Product Similarity Architecture

**MVP choice: attribute-based, precomputed, explainable. Not embeddings.**

```text
====================== OFFLINE ======================

For each product pair in the small catalog (or within category):
   score =
       category_match
     + subcategory_match
     + style_match
     + occasion_overlap
     + material_match
     + fit_match
     + color_overlap
     + price_proximity
     + brand_related (weak)

   keep edges above threshold
   store matched_attributes + human reason
     e.g. "Same category, similar price, both casual sneakers"

product_similarity table


======================= ONLINE =======================

Given wishlist product P:
   SELECT similar rows
   Prefer catalog items not already on Wishlist (for "better option")
   Prefer other Wishlist items (for overload + "better option in Wishlist")
```

| Approach | MVP? | Why |
|---|---|---|
| Rule / attribute-based | **Yes** | Explainable, cheap, fits 50–100 SKUs |
| Embedding-based | Later | Adds vector infra without helping predefined questions |
| Hybrid | Later | Only if attribute matching misses style nuance |

Similarity must be explainable because alerts and comparison copy need a **why**.

---

## 13. Decision Engine Architecture

The Decision Engine sits **between stored evidence and the LLM**. It is ordinary code.

```text
Product rows
Review insights
Price stats
Similarity edges
User preferences
Wishlist context (saved_price, selected ids)
        ↓
   DECISION ENGINE
        ↓
Structured Evidence Pack  +  Deterministic Scores
        ↓
   LLM (optional)
        ↓
Explanation
```

### Deterministic responsibilities (never LLM)

- Discount, saved-price delta, historical position
- Rating and rating-count comparison
- Theme count comparison
- Attribute similarity lookup
- Preference match (budget, occasion, size, priority weights)
- Recommendation score
- Confidence band: HIGH / MEDIUM / LOW from evidence strength
- Missing-data flags

**Scoring (explainable, not ML):**

```text
relevance(product, user, context) =
    price_fit
  + occasion_fit
  + quality_match
  + rating_signal
  + review_signal
  + user_priority_match
```

If the user priority is price, raise `price_fit`. If quality/comfort, raise review/quality weights.

Comparison labels from scores, not from the model:

- BEST VALUE
- BEST REVIEWED
- BEST BALANCE
- BEST MATCH FOR YOU (preference-weighted)

The engine **does not** declare an unexplained winner.

### Evidence pack (the only object the LLM may see)

```text
{
  question_id or task: "COMPARE" | "WORTH_THE_PRICE" | ...,
  products: [{ id, name, brand, price, mrp, rating, rating_count, fit, material, occasions }],
  price: [{ current, saved, min, max, relative_position, history_available }],
  reviews: [{ theme, positive, negative, summary, volume_band }],
  similar: [{ id, score, reason }],
  user: { budget, occasions, priorities, size },
  scores: { value, rating, balance, preference_match },
  confidence: "HIGH|MEDIUM|LOW",
  missing: ["price_history", "fit_reviews", ...],
  language_rules: ["do not invent", "do not predict future prices", "separate fact/evidence/interpretation"]
}
```

If `missing` is non-empty, the LLM is instructed to say so. If the pack is empty, **do not call the LLM**; return the fallback string from code.

---

## 14. Ask Me a Question Architecture

This is **not** a chatbot. The user picks a predefined question. A router loads only the data that question needs.

```text
User
 ↓
Wishlist (product or 2–3 selected products)
 ↓
Ask Me a Question sheet
 ↓
question_id  (enum, not free text)
 ↓
API POST /api/questions/answer
 ↓
Question Router
 ↓
Evidence Retriever for that question_id
 ↓
Decision Engine
 ↓
Structured Evidence Pack
 ↓
LLM Adapter  (grounded prompt)
 ↓
Structured Answer
  fact / evidence / interpretation / recommendation
  confidence
  missing[]
 ↓
Frontend renders inside Wishlist (sheet / card)
```

### Question catalog (MVP)

| question_id | Retrieves |
|---|---|
| `WORTH_THE_PRICE` | price, MRP, history, rating, themes, similar Wishlist items, preferences |
| `WHAT_BUYERS_DISLIKE` | review_insights (negative themes) + optional quote reviews |
| `IS_FIT_RELIABLE` | fit attribute + FIT/SIZE themes + volume |
| `FABRIC_QUALITY` | material + FABRIC/QUALITY/COMFORT themes |
| `BETTER_OPTION_IN_WISHLIST` | similarity among Wishlist + scores |
| `WHICH_ONE_SHOULD_I_BUY` | full pack for selected set + preference weights |
| `WHY_BETTER_THAN_B` | pairwise evidence for A vs B |
| `SHOULD_I_WAIT` | price_stats only; no future prediction |

### Example: “Is this worth the price?”

```text
1. Router → WorthThePriceHandler
2. DB: product, price_stats, review_insights, wishlist peers, user
3. Engine:
     price_position
     quality/review evidence
     similar Wishlist value comparison
     preference match
     confidence
4. If history missing → missing += price_history
5. LLM explains the pack
6. UI shows Mostly / Yes / No-with-caveat + bullets + verdict
```

No step scrapes. No step re-analyzes the full review corpus.

---

## 15. AI / LLM Architecture

Use AI only where synthesis adds value.

```text
┌──────────────────────────────────────────────┐
│              LLM ADAPTER                     │
│  default provider: Groq (free tier)          │
│  models: open Llama via Groq inference       │
│  interface: LlmClient  (replaceable)         │
│                                              │
│  jobs:                                       │
│   OFFLINE  analyze_reviews(batch)            │
│   ONLINE   explain_comparison(pack)          │
│   ONLINE   answer_question(pack)             │
│   ONLINE   explain_recommendation(pack)      │
└──────────────────────────────────────────────┘
```

### Groq as the MVP LLM

Groq is the **only LLM provider in the MVP**. It serves open models at no charge on the free tier. That matches the project rule: no paid AI APIs.

| Job | Recommended Groq model (free tier) | Why |
|---|---|---|
| Offline review theme extraction | Fast Llama (e.g. Llama 3.1 8B Instant) | Many short batches; stay inside rate limits |
| Compare / Q&A / recommendation copy | Stronger Llama (e.g. Llama 3.3 70B Versatile) | Better trade-off language from a small evidence pack |

Exact model IDs are configured in env (`GROQ_MODEL_FAST`, `GROQ_MODEL_QUALITY`), not hardcoded in business logic. If Groq renames models, only the adapter config changes.

**Free-tier implications (this is why offline-first still matters):**

- Rate limits exist. Do **not** call Groq when Wishlist merely opens.
- Review analysis is batched offline so a demo is not blocked by quota.
- Online Groq calls happen only on Compare, Ask, or Recommend.
- If Groq is unavailable, return Decision Engine numbers + a static fallback string. Never invent insights.

Auth: `GROQ_API_KEY` from [Groq Console](https://console.groq.com) (free signup). The key stays in `.env` and is never committed.

| Use | When | Input |
|---|---|---|
| Review theme extraction | Offline batch | Normalized reviews for one product |
| Comparison trade-off copy | User taps Compare | Evidence pack for 2–3 products |
| Question answer | User picks a question | Evidence pack for that handler |
| Recommendation copy | User asks which to buy | Scores + pack |

| Never use LLM for | Use instead |
|---|---|
| Discount, min/max, sort, filter | SQL / Python |
| Wishlist CRUD | API + DB |
| Similarity score | Attribute function |
| Badge “Highly rated” | Threshold on rating + count |
| “Price dropped ₹300” | Arithmetic |
| Filling missing catalog fields | Explicit unavailable |

### Prompt contract

Every online prompt includes:

1. The evidence pack JSON  
2. Instruction: claims only from the pack  
3. Instruction: FACT vs EVIDENCE vs INTERPRETATION vs RECOMMENDATION  
4. Instruction: no future price certainty  
5. Instruction: conditional recommendation language  
6. `missing[]` must appear in the answer if present  

**Default provider is Groq. The interface stays replaceable.** Application code talks to `LlmClient`, not to `groq` SDK calls scattered across services. A future free provider (another Groq model, a local Ollama instance) plugs in behind the same interface.

**Do not hard-code final answers** when data can produce them. Static copy is allowed only for true fallbacks (no data or Groq quota exceeded).

---

## 16. RAG / Vector Database Decision

### Options

| Option | Description | Fit for this MVP |
|---|---|---|
| **A. Structured DB + deterministic retrieval** | SQL by product_id, question_id, wishlist set | **Recommended** |
| B. DB + full-text search | Rank review text by keywords | Optional later for quote picking |
| C. Embeddings / vector DB | Semantic recall over reviews/catalog | **Not needed** |
| D. Hybrid | SQL + vectors | Future, if free-text chat is added |

### Recommendation: **Option A**

Reasons:

- Questions are a **closed enum**, not open retrieval
- Needed facts are **typed rows** (price, themes, attributes)
- Catalog is **50–100 products**, not millions
- Grounding is easier when the model sees a constructed pack, not “top 8 chunks”
- Vector infra would violate “avoid unnecessary infrastructure”

LIKE queries on `review_text` are enough if a handler wants a supporting quote. That is still Option A/B-lite, not a vector database.

### If embeddings are added later (not now)

| Question | Later answer |
|---|---|
| What gets embedded? | Review paragraphs or product attribute text |
| When generated? | Offline, on ingest |
| Where stored? | A column or a later vector store |
| What retrieves them? | Only free-text or fuzzy style search |
| Why necessary? | Only if Q&A becomes open-ended |

---

## 17. Price Alert Architecture

MVP: **scheduled (or on-demand job) comparison**, not a real-time pricing bus.

```text
====================== OFFLINE / SCHEDULED ======================

PRICE DATA (products.price + price_history latest)
   ↓
JOB: scan_price_alerts
   ↓
For each wishlist_item:
   if current_price <= saved_price - 1   (₹1 minimum; MVP lock)
      and no undismissed PRICE_DROP for this pair
         INSERT alert
           type: PRICE_DROP
           payload: { from, to, save_amount }
   ↓
alerts table


======================= ONLINE =======================

GET /api/wishlist   (undismissed alerts included)
   ↓
Return undismissed alerts
   ↓
Frontend: modal / bottom sheet / inline card
   [View Item] [Dismiss]
   ↓
PATCH alert dismissed_at
```

| Mode | MVP choice |
|---|---|
| Offline / scheduled | **Yes** — cron or manual “simulate price drop” job for demo |
| Online on Wishlist load | **Serve** alerts; optionally re-check (cheap at this scale) |
| Event-driven (Kafka) | No |

**Demo trick:** seed a later `price_history` point (or update `products.price`) and run the scan job so the alert is deterministic.

Never generate an alert that implies a predicted future price.

---

## 18. Similar-Product Alert Architecture

```text
====================== OFFLINE ======================

product_similarity graph rebuilt when catalog changes


======================= ONLINE (simplest MVP) ======================

On Wishlist add  OR  on Wishlist GET:

  For new/saved product P:
    find similar Q with higher rating or lower price
    if Q not on Wishlist (or is, for "better option")
    if score >= threshold
      create SIMILAR_PRODUCT alert (deduped)

Frontend: contextual card
  Adidas Sneakers  ₹3,999  ⭐ 4.5
  ₹1,000 cheaper · Higher rating
  [Compare] [Dismiss]
```

Scheduled generation is also valid: job joins `wishlist_items` × `product_similarity`. For a demo, **compute on Wishlist load** is simpler and still cheap.

The alert must include the stored `reason` so the UI can explain the match.

---

## 19. Decision-Overload Architecture

No new page. Detect groups on Wishlist read.

```text
USER WISHLIST (online)
      ↓
Load product_ids
      ↓
GROUP by (category, subcategory) and/or similarity clusters
      using product_similarity among wishlist items
      ↓
COUNT per group
      ↓
If count >= threshold (MVP: 3)
      ↓
DECISION_OVERLOAD signal in Wishlist payload
      ↓
Frontend prompt (card / sheet):

"You have 5 similar dresses saved.
Want help narrowing them down?"

[Compare My Options]  →  opens Compare with that group preselected
```

| Step | Where |
|---|---|
| Cluster Wishlist items | Online, Decision Engine |
| Threshold | Config (default 3) |
| Persistence | Optional alert row so it can be dismissed |
| Compare | Existing compare API; still inside Wishlist |

This is user-specific and must not run as a global offline job (except caching dismissed state).

---

## 20. End-to-End Wishlist Decision Flow

Primary demo story, tagged by layer.

```text
User opens Wishlist
        │  FRONTEND
        ↓
GET /api/wishlist
        │  ONLINE API
        ↓
Load wishlist_items, products, review_insights,
price_stats, similarity, alerts, user prefs
        │  DATABASE RETRIEVAL
        ↓
Decision Engine builds per-item signals
  Highly rated / Good value / Fit concerns
  Overload groups · undismissed alerts
        │  DETERMINISTIC
        ↓
JSON → Wishlist cards  (NO LLM)
        │  FRONTEND RENDER
        ↓
User selects 3 products → Compare
        │  FRONTEND
        ↓
POST /api/wishlist/compare  { product_ids[3] }
        │  ONLINE API
        ↓
Retrieve products, insights, prices
        │  DATABASE RETRIEVAL
        ↓
Decision Engine:
  table metrics, BEST VALUE / REVIEWED / BALANCE
  confidence, missing flags
        │  DETERMINISTIC
        ↓
LLM explain_comparison(evidence_pack)
        │  AI PROCESSING
        ↓
Comparison table + trade-off copy
        │  FRONTEND RENDER
        ↓
User asks: "Which one should I buy?"
        │  FRONTEND  question_id=WHICH_ONE_SHOULD_I_BUY
        ↓
Question Router → full pack + preference weights
        │  DATABASE + DETERMINISTIC
        ↓
LLM answer_question(pack)
        │  AI PROCESSING
        ↓
BEST MATCH FOR YOU + trade-off
        │  FRONTEND RENDER
        ↓
User Add to Bag → mock checkout
        │  ONLINE WRITE  (NO LLM)
```

### Layer legend

| Step | Database | Deterministic | AI | Frontend |
|---|---|---|---|---|
| Open Wishlist | ✓ | signals | | render |
| Price / review badges | ✓ | ✓ | | render |
| Price-drop popup | ✓ alerts | job earlier | | modal |
| Overload prompt | ✓ | cluster | | sheet |
| Compare numbers | ✓ | ✓ | | table |
| Compare “why” | | pack | ✓ | copy |
| Ask question | ✓ | router | ✓ | sheet |
| Add to Bag | write | | | confirm |

---

## 21. Data Freshness Strategy

For the MVP, “periodic” means a script the developer runs or a simple cron. There is no live market feed.

| Data | Freshness | Mechanism |
|---|---|---|
| Product metadata | Periodic / on seed change | Re-run ingest |
| Reviews | Periodic / on seed change | Re-run ingest |
| Review insights | When new reviews are ingested | Re-run review analyzer for touched products |
| Current price | Seeded; update when demonstrating drops | Edit seed or `products.price` + ingest |
| Price history / stats | When prices change | Rebuild `price_stats` |
| Price alerts | After price update, or on a short schedule | `scan_price_alerts` |
| Product similarity | When catalog changes | Rebuild graph |
| Similar-product alerts | On Wishlist add/load or after similarity rebuild | Online check or job |
| Wishlist | Real time | API writes |
| User preferences | Real time | Profile API |
| Bag / mock order | Real time | API writes |
| AI answer | On demand | No cache required for MVP; optional TTL cache later |

**Demo control:** keep a `jobs/simulate_price_drop.py` (or equivalent) that updates one SKU and inserts the alert so the story is reliable.

---

## 22. Recommended MVP Technology Stack

**Constraint: every layer is free.** Open-source libraries locally, plus Groq’s free inference API. No paid LLM, no paid database, no paid hosting required to run the demo.

The repo currently has **no application stack**. This is the stack to implement.

| Layer | Choice (all free) | What it does | Why it is free and enough | Do not use |
|---|---|---|---|---|
| Frontend | **React + Vite** | Home, listing, PDP, **Wishlist workspace**, Bag, Profile | MIT/open-source; no Next.js hosting bill | Paid UI kits |
| Styling | **CSS + a free utility layer** (plain CSS or Tailwind) | Fashion-commerce look | Open-source | Paid design systems |
| Icons | **Lucide** (or similar OSS) | Navigation / alerts | Open-source | Font Awesome Pro |
| Backend | **Python FastAPI + Uvicorn** | HTTP API, Decision Engine, jobs | BSD/MIT; same language as offline jobs | Paid BaaS |
| Database | **SQLite** | Source of truth | Public domain; zero ops | Supabase/Firebase as a requirement |
| Seed data | **JSON files in repo** | Catalog, reviews, prices | Editable; no data-vendor fee | Paid product APIs |
| Raw store | **Local `raw/` directory** | Ingest snapshots | No S3 | AWS/GCP object storage |
| Images | **Local `/public` or free placeholder URLs** | Product imagery | No CDN contract | Paid stock |
| Offline jobs | **Python scripts + CLI** | Ingest, insights, similarity, alerts | stdlib + FastAPI project | Airflow Cloud |
| Scheduling | **Manual run / Windows Task Scheduler / cron** | Price-drop scan | OS-native | Paid job queues |
| LLM | **Groq API (free tier)** behind `LlmClient` | Review batch + explanations | Free Llama inference; no GPU | OpenAI, Gemini paid, Anthropic |
| LLM SDK | **`groq` Python package** | Calls Groq | Free SDK | Vendor lock-in outside the adapter |
| Secrets | **`.env` + python-dotenv** | `GROQ_API_KEY` | Local only; never commit the key | Paid secret managers |
| Ingestion | **SeedFileSource** first | Replaceable adapter | App not tied to scrape | Live paid scrapers |
| Run locally | **Node (frontend) + Python (backend)** on the developer machine | Full demo | $0 | Required cloud deploy |

### Groq wiring

```text
.env
  GROQ_API_KEY=...
  GROQ_MODEL_FAST=llama-3.1-8b-instant        # example; confirm current Groq IDs
  GROQ_MODEL_QUALITY=llama-3.3-70b-versatile  # example; confirm current Groq IDs

offline/review_analyzer  →  LlmClient.complete(model=FAST)
backend compare / Q&A   →  LlmClient.complete(model=QUALITY)
```

Groq is inference-only. It does **not** replace SQLite, and it does **not** store products or reviews.

### Explicitly out of MVP stack

Paid or unnecessary: OpenAI, Google Gemini (paid), Anthropic, Kafka, Kubernetes, Elasticsearch, Redis, Pinecone/Chroma, Celery clusters, Docker Compose fleets, auth vendors, payment gateways, Supabase-as-requirement, AWS/GCP as requirement.

Free and allowed later if needed: PostgreSQL (OSS), Ollama (local models as a Groq fallback), Tailwind, Lucide.

### Suggested module layout (logical, not a mandate)

```text
frontend/          React app
backend/           FastAPI monolith
  api/
  services/        wishlist, compare, questions, alerts
  decision/        evidence + scores
  llm/             adapter + prompts
offline/           ingest + analyzers + jobs
data/              seed JSON
raw/               snapshots
Docs/              Context, ProblemStatement, Architecture
```

---

## 23. MVP vs Future Architecture

### MVP (build this)

```text
Seed JSON
  + SQLite
  + FastAPI modular monolith
  + React + Vite
  + Offline Python jobs
  + Precomputed review insights & similarity
  + Deterministic Decision Engine
  + Groq free-tier LLM on demand
  + Alerts table + Wishlist fetch
  + All free / OSS  (no paid APIs required)
```

Enough to prove: **SAVE → COMPARE → UNDERSTAND → QUESTION → EVALUATE → DECIDE → BAG.**

### Future (only if the product graduates)

```text
Compliant data pipeline
  + PostgreSQL (still free OSS) if SQLite is outgrown
  + Object storage for raw dumps
  + Incremental review re-analysis on Groq
  + Optional Redis for API cache
  + Optional full-text search for quotes
  + Optional local Ollama fallback if Groq quota is tight
  + Event-driven price updates
  + Real notification channel
  + Stronger auth and real checkout
  + Dedicated ranking service
```

Future may add paid services. The **MVP must not**.

Do not pull future boxes into the first demo. They do not reduce purchase uncertainty for 50–100 seeded products.

---

## 24. Key Architectural Decisions and Rationale

| Decision | Choice | Rationale |
|---|---|---|
| Two-zone design | Offline catalog intelligence / online user decisions | Expensive shared work vs cheap user-specific work |
| Wishlist-centric APIs | No Decision Studio service or route | Product constraint: workspace is Wishlist |
| Modular monolith | One backend | MVP simplicity; still separable modules |
| Replaceable `DataSource` | Seed first | App must not depend on live scraping |
| Raw vs processed | Immutable snapshots + normalized tables | Source can change; contract stays stable |
| Free-only stack | React, FastAPI, SQLite, Groq | No paid APIs or hosted products required |
| SQLite | Default DB | Free, local, matches data scale |
| No vector DB / RAG | Structured retrieval | Closed questions + typed evidence |
| Attribute similarity | Precomputed graph | Explainable alerts and overload clusters |
| Decision Engine before LLM | Scores and facts in code | Prevents hallucinated math and fake winners |
| LLM provider | Groq free tier (Llama) | Fast, $0 inference; still rate-limited so offline-first |
| LLM uses | Offline reviews; online explanation only | Groq quota, latency, grounding |
| Alerts | Job + table + fetch on Wishlist | Reliable demo; no Kafka |
| Overload | Online cluster of current Wishlist | User-specific by definition |
| Missing data | Flags in evidence pack; skip LLM if empty | Integrity from Problem Statement |
| AI provider | Groq behind `LlmClient` | Free default; replaceable; not the product |
| Confidence | HIGH/MEDIUM/LOW from evidence | Not “model confidence 95%” |

---

## Architecture Principles (enforced)

1. Offline-first for expensive processing  
2. Online-first for user-specific decisions  
3. Precompute what can be precomputed  
4. Calculate deterministic metrics in code  
5. Use AI for synthesis and explanation  
6. Do not call the LLM to render Wishlist  
7. Keep raw data separate from processed data  
8. Keep data ingestion replaceable  
9. Keep the AI provider replaceable; **default is Groq (free)**  
10. Keep the architecture modular  
11. Avoid unnecessary infrastructure  
12. Wishlist remains the central product surface  
13. AI must be grounded in stored evidence  
14. Missing data must not become hallucinated data  
15. **Use only free stacks for the MVP** (OSS locally + Groq free tier; no paid LLM)  

---

## One-Page Summary

```text
COLLECT     seed JSON (replaceable later with compliant external data)
    ↓
STORE RAW   file snapshots
    ↓
PROCESS     clean → normalize → validate
    ↓
PRECOMPUTE  review insights (Groq Llama, batch)
            price_stats (code)
            similarity graph (attributes)
            price-drop rows (scheduled scan)
    ↓
STORE       SQLite  =  source of truth
    ↓
ONLINE      Wishlist GET joins user + precomputed facts
            signals, alerts, overload  →  NO GROQ CALL
    ↓
ON DEMAND   Compare / Ask / Recommend
            Decision Engine builds evidence pack
            Groq explains pack only
    ↓
USER SEES   inside Wishlist:
            badges, comparison, price insight,
            review themes, Q&A, alerts, recommendation
            → Add to Bag
```

That is the architecture of the MVP.
