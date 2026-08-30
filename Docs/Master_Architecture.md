# MYNTRA WISHLIST DECISION STUDIO
## Master Architecture (Implementation-Ready)

This is the architecture to implement against. It inspects the repo as it exists today, maps it to the product requirements, and specifies frontend, backend, data, AI, APIs, schema, prompts, folders, and build order.

**Implementation has not started.** This document is the brief for further proceedings. Canonical locks (paths, `saved_price`, ₹1 drop, Phase 0): `Docs/Doc_Alignment.md`. Do not code until the next explicit implementation request.

Related docs:

| Doc | Role |
|---|---|
| `Docs/Context.md.md` | Product requirements |
| `Docs/ProblemStatement.md` | Problem to solve |
| `Docs/Architecture.md` | Offline vs online, Groq, storage principles |
| `Docs/Phase_wise_Implementation.md` | Build sequence and exit criteria |
| **This file** | Inspection + detailed design for implementation |

---

# STEP 1 — Existing project inspection

Inspected the workspace `MyntraWishlist_DecisionStudio` recursively.

**There is no application yet.** No `package.json`, no Python project, no database, no `.env`, no `frontend/`, no `backend/`, no git metadata in the tree at inspection time.

### Files that exist

```text
Docs/Context.md.md
Docs/ProblemStatement.md
Docs/Architecture.md
Docs/Phase_wise_Implementation.md
Docs/Master_Architecture.md   ← this file
```

### What does not exist

- React/Vite app
- FastAPI app
- SQLite file
- Seed JSON (`products.json`, `reviews.json`, `price-history.json`)
- Groq client
- Components, routes, tests
- Authentication
- Docker / CI

### Inspection conclusions

| Question | Finding |
|---|---|
| Framework | None — greenfield |
| Frontend architecture | None |
| Backend architecture | None |
| Database | None (target: SQLite) |
| API layer | None |
| Components | None |
| Auth / state | None (MVP: single demo user `U001`) |
| Env config | None (target: `.env` + `GROQ_API_KEY`) |
| Reusable code | **None.** Reuse is documentation only. |

This is **not** a rewrite of a working app. It is a new modular monolith built from the docs.

---

# STEP 2 — Current stack vs target stack

| Layer | Today | Target (locked, free) |
|---|---|---|
| Frontend | — | React + Vite |
| Styling | — | CSS + optional Tailwind (OSS) |
| Icons | — | Lucide (OSS) |
| Backend | — | Python FastAPI + Uvicorn |
| Database | — | SQLite |
| LLM | — | Groq free tier behind `LlmClient` |
| Catalog | — | Seed JSON → ingest → SQLite |
| Hosting | — | Local (Node + Python) |

No reason to deviate: there is no existing stack to preserve.

---

# STEP 3 — Requirements mapped to the empty repo

| Requirement | Status | Plan |
|---|---|---|
| Home / listing / PDP / Wishlist / Bag / Profile | Missing | Phase 1 |
| No Decision Studio page | N/A | Never add those routes |
| Catalog 50–100 products | Missing | Phase 2 seed |
| Wishlist CRUD + `saved_price` | Missing | Phase 1–2 |
| Compare 2–3 with trade-offs | Missing | Phase 3 numbers, Phase 4 Groq copy |
| Price intelligence | Missing | Phase 3 (`price_stats`) |
| Review themes (not % sentiment) | Missing | Phase 4 offline Groq; optional hand insights in Phase 3 |
| Ask Me a Question (enum only) | Missing | Phase 4 |
| Explainable recommendation score | Missing | Phase 3 engine + Phase 4 explain |
| Attribute similarity (no vector DB) | Missing | Phase 3 job |
| Decision overload | Missing | Phase 5 |
| Price-drop + similar alerts | Missing | Phase 5 |
| Replaceable ingest, no live scrape | Missing | Phase 2 `SeedFileSource` |
| Groq server-side only | Missing | Phase 0 stub, Phase 4 live |
| AI fallback; shopping works without Groq | Missing | Phase 3 usable without LLM |
| Mock checkout | Missing | Phase 1 stub, Phase 6 complete |

**Gap:** 100% of product and technical surface. **Asset:** four specification docs that already agree on Wishlist-as-workspace, deterministic-then-AI, and free stack.

---

# STEP 4 — What can be reused

- Product vision, constraints, demo story, data models (conceptual)
- Offline/online split and Groq policy (`Architecture.md`)
- Phase exit criteria (`Phase_wise_Implementation.md`)

**No source code to reuse.**

---

# STEP 5 — What must be added vs never added

### Add

Application code, seed data, SQLite schema, ingest jobs, Decision Engine, Groq adapter, Wishlist-embedded UI, tests.

### Do not add (MVP)

- Routes: `/studio`, `/compare`, `/ai`, `/insights`, `/alerts` as pages
- Kubernetes, microservices, Kafka, Redis, Elasticsearch, vector DB
- OpenAI / Gemini paid / Anthropic
- Live Myntra scraper, payment gateway, production auth
- Open-ended chatbot; frontend LLM keys
- Static “if product A return best” answers as the real path

### Do not change later without cause

Once built: Wishlist as the only decision surface; `LlmClient` as the only Groq entry; repositories as the only DB access; seed ingest as the only catalog writer for MVP.

---

# STEP 6 — Final architecture

## A. High-level architecture

```text
                         USER
                          |
                          ↓
                   REACT + VITE
              ┌───────────┴───────────┐
              │                       │
         Commerce UX            Wishlist UX
         Home, Listing,         signals, compare,
         PDP, Bag, Profile      insights, Q&A, alerts
              │                       │
              └───────────┬───────────┘
                          ↓
                    API LAYER (FastAPI)
                          ↓
                 APPLICATION SERVICES
                          |
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
   ProductService   WishlistService   Decision services
   BagService       AlertService      Comparison
   ProfileService                     Price / Review
                                      Question / Recommend
                          ↓
                   DECISION ENGINE
              (deterministic scores + evidence pack)
                          ↓
                    LlmClient (Groq)
                    only if user asked
                    and pack is non-empty
                          ↓
                  STRUCTURED JSON ANSWER
                          ↓
                         UI
                          |
                          ↓
                       SQLITE
                          ↑
                    OFFLINE INGEST
                   Seed JSON → raw/ → normalize → DB
```

**Every layer**

| Layer | Responsibility |
|---|---|
| Frontend | Fashion-commerce UI. Wishlist hosts all decision chrome. No Groq SDK. |
| API | HTTP, validation, `question_id` allowlist. |
| Services | Use-cases. No SQL in route handlers. No Groq in ProductService. |
| Decision Engine | Price math, similarity use, scores, confidence, `missing[]`, evidence pack. |
| LlmClient | Groq only. Review batch (offline) + synthesis (online). |
| Repositories | SQLite only. |
| Offline jobs | Ingest, `price_stats`, similarity, review insights, alert scan. |

Wishlist GET **never** calls Groq.

## B. Frontend architecture

```text
pages/          routes only (no Decision Studio)
components/     reusable UI
api/            fetch wrappers
state/          UI state (not a second catalog)
hooks/          wishlist, bag, compare, questions
```

**Pages (and only these commerce pages)**

| Route | Page | Decision features |
|---|---|---|
| `/` | Home | None |
| `/category/:id` or `/products` | Listing | Heart → Wishlist |
| `/product/:id` | PDP | Add to Wishlist / Bag |
| `/wishlist` | Wishlist | **All decision UX** |
| `/bag` | Bag | Mock checkout |
| `/profile` | Profile | Preferences that feed scoring |

**Components (Wishlist-centered)**

`ProductCard`, `WishlistCard`, `WishlistHeader`, `DecisionSignal`, `CompareSelector`, `CompareDrawer`, `ComparisonTable`, `PriceInsight`, `ReviewInsight`, `QuestionSheet`, `QuestionOption`, `RecommendationCard`, `SimilarProductAlert`, `PriceAlert`, `DecisionOverloadModal`, `AddToBagButton`, `Toast`, `BottomSheet`.

**State**

| Server state (fetch from API, don’t duplicate as source of truth) | UI state (React) |
|---|---|
| Products, PDP, Wishlist, Bag, profile, insights, alerts | Selected product ids (2–3), drawer/sheet open, selected `question_id`, alert visible, loading/error |

No Redux required. React Query or simple `useEffect` + context is enough at this scale. Prefer one `WishlistWorkspace` context for selection + sheets.

**API layer (frontend)**

`frontend/src/api/*.ts` — typed `fetch` to FastAPI. Never import `data/*.json`.

## C. Backend architecture

```text
api/routes        HTTP
services          Product, Wishlist, Bag, Profile, Comparison,
                  Price, Review, Question, Recommendation, Alert
decision          scores, evidence_pack, confidence, overload
llm               LlmClient, prompts, parse/validate structured output
offline           ingest, analyzers, jobs
db                connection, schema, repositories
```

| Piece | Does |
|---|---|
| Routes | Parse/validate, call one service, return JSON |
| Services | Orchestrate repositories + Decision Engine + LlmClient |
| Repositories | CRUD / queries |
| Decision Engine | Never I/O to Groq |
| LlmClient | Never SQL |
| Jobs | CLI; may call LlmClient (insights) or AlertService scan |

Modular **monolith** — one Uvicorn process.

## D. Data architecture (relationships)

```text
users 1──N wishlist_items N──1 products
users 1──N bag_items      N──1 products
users 1──N orders
users 1──N alerts
products 1──N reviews
products 1──N review_insights
products 1──N price_history
products 1──1 price_stats
products 1──N product_similarity (self)
```

Catalog is written **offline**. Wishlist/Bag/alerts are written **online**.

## E. AI architecture

```text
User selects question_id (enum)
        ↓
Question registry (required_data per id)
        ↓
Evidence retrieval (SQL only for those keys)
        ↓
Decision Engine (deterministic)
        ↓
Structured evidence pack + missing[]
        ↓
If empty / only missing → fallback, skip Groq
        ↓
LlmClient (Groq QUALITY) + JSON schema
        ↓
Validate output against pack (no new prices/ratings)
        ↓
UI renders fields (not raw prose)
```

Offline: `rebuild_insights` uses Groq FAST on reviews per product → `review_insights`.

No RAG. No vector DB. Closed questions only.

## F. Data ingestion architecture

```text
SeedFileSource (MVP)
        +
ExternalSource (interface only; not implemented)
        ↓
raw/{batch_id}/ snapshots (immutable)
        ↓
normalize + validate
        ↓
SQLite processed tables
        ↓
jobs: price_stats, similarity
        ↓
job: review_insights (Groq, Phase 4)
```

Frontend never reads seed or raw files. No live scrape. No anti-bot bypass design.

---

# STEP 7 — Why these decisions

| Decision | Why |
|---|---|
| Greenfield React + FastAPI + SQLite | Nothing exists; matches Architecture.md; all free |
| Groq not OpenAI | Project lock: free LLM |
| Modular monolith | MVP; services are modules not processes |
| Wishlist-only decision UX | Non-negotiable product constraint |
| Decision Engine before Groq | Explainability; no hallucinated math |
| Precompute insights/similarity/prices | Don’t call Groq on Wishlist open; stay in free-tier |
| Structured LLM JSON | UI must not parse essays |
| Question registry | New questions without rewriting the app |
| Seed-first ingest adapter | Replaceable source; legal/ops safety |
| Single user `U001` | No auth product in MVP |
| Attribute similarity | Explainable alerts; vector DB not needed |
| Alerts as rows + Wishlist fetch | No Kafka; demo-reliable |
| Confidence HIGH/MEDIUM/LOW | Evidence strength, not fake model % |

---

# STEP 8 — Database schema

SQLite. Types below are logical; JSON stored as TEXT.

### `users`

| Column | Type | Notes |
|---|---|---|
| user_id | TEXT PK | `U001` |
| display_name | TEXT | |
| size | TEXT | e.g. M |
| price_min | INTEGER | rupees |
| price_max | INTEGER | |
| occasions | TEXT JSON | `["Casual","Office"]` |
| priorities | TEXT JSON | `["Quality","Comfort"]` |
| created_at | TEXT | ISO |

### `products`

| Column | Type |
|---|---|
| product_id | TEXT PK |
| brand, name | TEXT |
| gender, category, subcategory, style | TEXT |
| price, mrp, discount | INTEGER |
| rating | REAL |
| rating_count | INTEGER |
| image_url, product_url | TEXT |
| sizes, colors, occasions | TEXT JSON |
| fit, material | TEXT |
| attributes_json | TEXT JSON |
| updated_at | TEXT |

Indexes: `(category)`, `(subcategory)`, `(category, subcategory)`.

### `reviews`

| Column | Type |
|---|---|
| review_id | TEXT PK |
| product_id | TEXT FK |
| rating | INTEGER |
| review_text | TEXT |
| review_date | TEXT |
| source_batch_id | TEXT |

Index: `(product_id)`.

### `review_insights`

| Column | Type |
|---|---|
| id | INTEGER PK |
| product_id | TEXT FK |
| theme | TEXT |
| positive_count, negative_count | INTEGER |
| summary | TEXT |
| evidence_review_ids | TEXT JSON |
| confidence | TEXT | HIGH/MEDIUM/LOW |
| updated_at | TEXT |

Unique: `(product_id, theme)`. Index: `(product_id)`.

### `price_history`

| Column | Type |
|---|---|
| id | INTEGER PK |
| product_id | TEXT FK |
| date | TEXT |
| price | INTEGER |

Index: `(product_id, date)`.

### `price_stats`

| Column | Type |
|---|---|
| product_id | TEXT PK FK |
| current_price, min_price, max_price, avg_price | INTEGER / REAL |
| min_date | TEXT |
| relative_position | REAL nullable |
| updated_at | TEXT |

### `product_similarity`

| Column | Type |
|---|---|
| product_id | TEXT |
| similar_product_id | TEXT |
| score | REAL |
| matched_attributes | TEXT JSON |
| reason | TEXT |

PK: `(product_id, similar_product_id)`. Index: `(product_id, score DESC)`.

### `wishlist_items`

| Column | Type |
|---|---|
| user_id | TEXT FK |
| product_id | TEXT FK |
| added_at | TEXT |
| saved_price | INTEGER |

PK: `(user_id, product_id)`.

### `bag_items`

| Column | Type |
|---|---|
| user_id | TEXT FK |
| product_id | TEXT FK |
| quantity | INTEGER DEFAULT 1 |
| added_at | TEXT |

PK: `(user_id, product_id)`.

### `orders`

| Column | Type |
|---|---|
| order_id | TEXT PK |
| user_id | TEXT FK |
| product_ids | TEXT JSON |
| created_at | TEXT |
| status | TEXT | `CONFIRMED` mock |

### `alerts`

| Column | Type |
|---|---|
| alert_id | TEXT PK |
| user_id | TEXT FK |
| type | TEXT | `PRICE_DROP` \| `SIMILAR_PRODUCT` \| `DECISION_OVERLOAD` |
| product_id | TEXT nullable |
| payload_json | TEXT |
| created_at, dismissed_at, seen_at | TEXT nullable |

Index: `(user_id, dismissed_at, type)`.

---

# STEP 9 — API structure

Base: `/api`. Demo user header or query `user_id=U001` (MVP; validate allowlist).

| Method | Path | Request | Response (purpose) | Phase |
|---|---|---|---|---|
| GET | `/health` | — | `{ status }` | 0 |
| GET | `/api/products` | `category?` | product list cards | 1 |
| GET | `/api/products/{id}` | — | full product | 1 |
| GET | `/api/wishlist` | — | items + **signals** + **overload** + undismissed **alerts** | 1, then 3/5 |
| POST | `/api/wishlist` | `{ product_id }` | item with `saved_price` (first save wins) | 1 |
| DELETE | `/api/wishlist/{productId}` | — | 204 | 1 |
| POST | `/api/wishlist/compare` | `{ product_ids: [2..3] }` | table metrics, labels, `missing[]`, optional `explanation` | 3–4 |
| GET | `/api/products/{id}/price-insight` | — | current, mrp, saved, min, position, copy_key | 3 |
| GET | `/api/products/{id}/review-insight` | — | likes, concerns, volume_band, confidence | 3–4 |
| POST | `/api/questions/answer` | `{ question_id, product_id?, product_ids? }` | structured answer JSON | 4 |
| PATCH | `/api/alerts/{id}/dismiss` | — | 204 | 5 |
| GET | `/api/bag` | — | bag | 1 |
| POST | `/api/bag` | `{ product_id }` | item | 1 |
| DELETE | `/api/bag/{productId}` | — | 204 | 1 |
| GET/PATCH | `/api/profile` | prefs | user | 1 |
| POST | `/api/checkout` | — | mock order | 6 |

**Compare response (shape)**

```json
{
  "products": [{ "product_id": "P001", "name": "...", "price": 999, "rating": 4.2, "rating_count": 1200 }],
  "rows": [{ "metric": "price", "values": { "P001": 999, "P002": 1299 } }],
  "labels": { "best_value": "P003", "best_reviewed": "P002", "best_balance": "P001" },
  "scores": {},
  "confidence": "MEDIUM",
  "missing": [],
  "explanation": null
}
```

`explanation` is null until Phase 4 (or Groq down).

**Question request**

```json
{ "question_id": "WORTH_THE_PRICE", "product_id": "P001" }
```

Illegal `question_id` → 400. Never forward free text to Groq. MVP: `product_id` / `product_ids` must be on the user’s Wishlist.

**Question / LLM response (render this, not a blob)**

```json
{
  "answer": "Mostly worth the price",
  "confidence": "HIGH",
  "facts": ["Current price is ₹1299"],
  "evidence": ["..."],
  "positive_signals": ["Comfort"],
  "concerns": ["Thin fabric"],
  "tradeoffs": ["A cheaper Wishlist alternative exists"],
  "interpretation": "...",
  "recommendation": "Choose this if comfort matters more than minimizing price.",
  "missing": []
}
```

---

# STEP 10 — AI architecture (detail)

### Registry (`backend/llm/question_registry.json`)

| question_id | Label | required_data |
|---|---|---|
| `WORTH_THE_PRICE` | Is this worth the price? | product, price_stats, review_insights, wishlist_similars, user |
| `WHAT_BUYERS_DISLIKE` | What do buyers dislike? | review_insights, optional reviews |
| `IS_FIT_RELIABLE` | Is the fit reliable? | product.fit, FIT/SIZE insights |
| `FABRIC_QUALITY` | How is the fabric quality? | material, FABRIC/QUALITY/COMFORT |
| `BETTER_OPTION_IN_WISHLIST` | Better option in Wishlist? | similarity, scores |
| `WHICH_ONE_SHOULD_I_BUY` | Which one should I buy? | full pack for 2–3 + prefs |
| `WHY_BETTER_THAN_B` | Why this vs B? | pairwise |
| `SHOULD_I_WAIT` | Should I wait? | price_stats only; no future price |

### Groq models (env, not business logic)

- `GROQ_MODEL_FAST` — offline review themes  
- `GROQ_MODEL_QUALITY` — compare / Q&A / recommend copy  

### Prompt strategy (all grounded)

**Shared system rules**

- Use only the evidence JSON.  
- If `missing` is set, say so.  
- Separate facts, evidence, interpretation, recommendation.  
- No future price predictions.  
- No “most buyers” when volume is low.  
- No inventing ratings, prices, materials, fit.  
- Return **only** the JSON schema provided.  
- Confidence in the output must echo the engine’s HIGH/MEDIUM/LOW, not a percentage.

**Review analysis (offline)**  
Input: reviews for one `product_id`. Output: per-theme positive/negative counts, short summary, evidence review ids. Empty list → no insert / explicit no-data.

**Comparison explainer**  
Input: evidence pack + deterministic labels (BEST VALUE etc.). Output: trade-off paragraph fields. Must not change the labels.

**Question answerer**  
Input: pack for that `question_id` only. Output: schema above.

**Recommendation explainer**  
Input: ranked scores + pack. Output: BEST MATCH FOR YOU + why + trade-off. Conditional language.

### Validation after Groq

Reject / strip claims that introduce numbers not in the pack. On parse failure or 429: return engine numbers + `"Decision insight temporarily unavailable. You can still compare price, rating, and reviews."`

### Logging (no PII dump)

`question_id`, `product_id`(s), latency, model, success/fail. Not full user profile, not API key.

---

# STEP 11 — Data ingestion architecture (detail)

```text
data/products.json
data/reviews.json
data/price-history.json
data/users.json
        ↓
offline/jobs/ingest_catalog.py
        ↓
raw/{batch_id}/  (copy of inputs + manifest)
        ↓
normalize* + validate*
        ↓
UPSERT SQLite
        ↓
rebuild_price_stats.py      (code)
rebuild_similarity.py       (code)
rebuild_insights.py         (Groq FAST, Phase 4+)
scan_price_alerts.py        (Phase 5)
simulate_price_drop.py      (demo)
```

**Seed design (required for a meaningful demo)**

- 50–100 products, 5–10 categories  
- Groups: dresses, sneakers, handbags, tops, jeans (3–5 similar each)  
- Trade-off triple: cheap vs best-reviewed vs balanced  
- 10–15 products with 20–50 honest reviews (positive and negative themes)  
- Price history that supports a drop vs `saved_price`  
- Do not invent review counts that contradict the corpus; prefer honest small N + “among the available reviews”

`DataSource` protocol: `fetch_products()`, `fetch_reviews()`, `fetch_prices()`. Only `SeedFileSource` in MVP.

---

# STEP 12 — Final folder structure

Nothing to preserve except `Docs/`. Create:

```text
MyntraWishlist_DecisionStudio/
  Docs/
    Context.md.md
    ProblemStatement.md
    Architecture.md
    Phase_wise_Implementation.md
    Master_Architecture.md
  frontend/
    src/
      pages/          Home, ProductListing, ProductDetail, Wishlist, Bag, Profile
      components/     (list in §B)
      api/
      state/
      hooks/
      styles/
    public/           product images
    index.html
    package.json
  backend/
    main.py
    api/routes/
    services/
    decision/
    llm/              client.py, prompts/, question_registry.json
    db/               schema.sql, session.py, repositories/
    tests/
  offline/
    ingestion/sources/
    processors/
    jobs/
  data/               seed JSON
  raw/                snapshots (gitkeep; ignore contents)
  .env.example
  .gitignore
  README.md
```

---

# STEP 13 — Implementation sequence

Follow `Docs/Phase_wise_Implementation.md` without skipping exit criteria.

```text
0  Foundation          Vite + FastAPI + SQLite path + LlmClient stub
1  Shopping shell      Home → PDP → Wishlist → Bag → Profile (no Groq)
2  Catalog pipeline    Seed → raw → SQLite; APIs read DB
3  Decision workspace  Signals, compare table, price/review insights (code)
4  Groq + Q&A          Insights job + registry + structured answers
5  Alerts              Price drop, similar, overload (in Wishlist)
6  Polish              Mock purchase, empty/error, primary demo story
```

**Do not start with Groq.** Shopping must work first. AI is an enhancement, never a single point of failure.

**Definition of done** — user can complete Context §54 / Architecture primary story: browse → save 3 similar → overload → compare → “which one should I buy?” → price insight → Bag → mock purchase. All decision tools stay on Wishlist.

---

# STEP 14 — Implementation status

**Not started.** Architecture is recorded for further proceedings.

When implementation begins, start at **Phase 0** only. Do not invent a Decision Studio route. Do not put `GROQ_API_KEY` in the frontend.

---

# Core principle (non-negotiable)

> **Don’t help users save more products. Help them confidently resolve which saved product is right for them.**

This is a **Wishlist-centered decision-support experience**. Groq, reviews, price intelligence, comparison, recommendations, and alerts are supporting capabilities — not the product itself.

From:

> “I like these products but I don’t know which one to buy.”

To:

> “I understand the trade-offs and know which one is right for me.”
