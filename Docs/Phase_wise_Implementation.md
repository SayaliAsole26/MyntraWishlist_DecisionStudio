# MYNTRA WISHLIST DECISION STUDIO
## Phase-wise Implementation Plan

This document turns `Docs/Architecture.md` into a build sequence. It also respects `Docs/Context.md.md` (do not start with advanced AI) and `Docs/ProblemStatement.md` (Wishlist is the decision workspace; no separate Decision Studio page).

**Canonical locks** (API paths, `saved_price`, price-drop ₹1, Phase 0): `Docs/Doc_Alignment.md`. If this file disagrees with another doc, Alignment wins.

**Do not implement a later phase until the current phase’s exit criteria pass.**

---

## How to use this document

Each phase has:

- **Goal** — what must exist when the phase is done
- **Why this order** — architectural reason
- **Offline vs online** — which zone you are building
- **Work** — backend, frontend, data, Groq
- **Do not build yet** — traps that skip ahead
- **Exit criteria** — the phase is not done without these
- **Demo check** — what a person can click through

Stack for every phase (locked):

| Layer | Choice |
|---|---|
| Frontend | React + Vite |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite |
| LLM | Groq free tier, behind `LlmClient` only |
| Catalog | Seed JSON → ingest job → SQLite |

---

## Rules that apply to every phase

1. No separate Decision Studio, comparison, AI, or alerts **page**. All of that lands inside Wishlist.
2. Frontend never scrapes, never reads `raw/`, never calls Groq.
3. Decision Engine never invents facts. Missing data stays missing.
4. Do not call Groq to render Wishlist cards.
5. Deterministic math (price, discount, min/max, similarity score) is code, not the model.
6. Stay on the free stack. No OpenAI, Gemini paid, vector DB, Redis, Kafka, Kubernetes.
7. Build one end-to-end slice per phase. Test that slice before moving on.
8. Do not rewrite unrelated working features when starting the next phase.

---

## Phase map

```text
Phase 0  Foundation
   ↓
Phase 1  Shopping shell          ← no Groq, no Decision Engine
   ↓
Phase 2  Catalog pipeline        ← offline ingest, still no Groq
   ↓
Phase 3  Wishlist decision UI    ← deterministic signals / compare / insights
   ↓
Phase 4  Groq + Ask a Question   ← first LLM use (offline insights + online copy)
   ↓
Phase 5  Smart alerts            ← price drop, similar product, overload
   ↓
Phase 6  Polish + demo story     ← empty/error states, reliability, primary journey
```

```text
         OFFLINE                         ONLINE
Phase 0  folders, .env                   health API, Vite app
Phase 1  —                               Home → PDP → Wishlist → Bag
Phase 2  seed, ingest, SQLite            APIs read DB instead of mocks
Phase 3  price_stats, similarity         signals, compare table, insights
Phase 4  Groq review analyzer            Q&A + compare/recommend explanations
Phase 5  alert scan job                  alerts on Wishlist load
Phase 6  simulate_price_drop job         polish every surface
```

---

## Phase 0 — Foundation

### Goal

An empty but runnable project: frontend, backend, SQLite file path, env for Groq (unused), folder layout from Architecture §22.

### Why this order

Nothing else can be tested until both processes start locally at $0 cost.

### Offline vs online

Scaffold only. No catalog intelligence. No user journeys.

### Work

**Repo**

```text
frontend/          React + Vite
backend/           FastAPI
  api/
  services/
  decision/        empty package
  llm/             LlmClient stub (not called)
offline/           empty jobs package
data/              empty seed folder
raw/               gitkeep
Docs/              existing markdown
.env.example       GROQ_API_KEY, GROQ_MODEL_FAST, GROQ_MODEL_QUALITY
```

**Backend**

- FastAPI app, CORS for the Vite origin, `GET /health`
- SQLite connection helper (file under `backend/` or project root, gitignored)
- `python-dotenv` loads `.env`
- `.gitignore`: `.env`, `*.db`, `node_modules`, `raw/*` snapshots except `.gitkeep`

**Frontend**

- Vite React app
- Placeholder layout: header, nav (Home, Wishlist, Bag, Profile)
- API base URL via env (`VITE_API_URL`)

**Groq**

- Do **not** call Groq.
- `LlmClient` interface may exist as a stub that raises “not configured” if invoked.

### Do not build yet

- Scrapers
- Review analysis
- Compare drawer
- Auth products
- Docker / cloud deploy

### Exit criteria

- `uvicorn` serves `/health` → 200
- `npm run dev` shows the shell chrome
- `.env.example` documents Groq keys; real `.env` is not committed

### Demo check

Open the frontend and the health endpoint. That is enough.

---

## Phase 1 — Shopping shell

### Goal

A Myntra-like click path with **one demo user** (`U001`). Products may still be a small in-memory or JSON list **served by the API**, not scraped, not Groq.

Context: *first make the basic shopping experience work.*

### Why this order

Decision support is worthless if save → Wishlist → Bag is not real. Architecture forbids a Decision Studio destination, so the shell’s Wishlist page is the future workspace.

### Offline vs online

**Online only.** Catalog is temporary. Offline pipeline is Phase 2.

### Work

**Backend**

- `GET /api/products` (list, optional category filter)
- `GET /api/products/{id}`
- `GET/POST /api/wishlist` and `DELETE /api/wishlist/{productId}` for `U001`
- `GET/POST /api/bag` and `DELETE /api/bag/{productId}`
- `GET/PATCH /api/profile` (size, budget, occasions, priorities)
- Wishlist add stores `saved_price` = current price at **first** add (idempotent; first save wins; see Doc_Alignment)
- No LLM, no comparison endpoint

**Frontend**

| Screen | Must include |
|---|---|
| Home | Categories / featured products |
| Listing | Product cards: image, brand, name, price, rating |
| Product detail | Image, price, MRP, rating, sizes, Add to Wishlist, Add to Bag |
| Wishlist | Image, name, price, remove — **not** decision badges yet |
| Bag | Line items, proceed to mock checkout stub |
| Profile | Editable preferences |

- Toast or confirmation on Wishlist add
- No ChatGPT-like panel
- Mobile-friendly layout from the start (even if not polished)

**Data**

- 8–15 products is enough if Phase 2 is next immediately
- Backend may read `data/products.json`; **frontend never reads seed files** (API only)

### Do not build yet

- Compare
- Ask Me a Question
- Review theme UI
- Price history charts
- Alerts
- Groq
- Separate routes named `/studio`, `/compare`, `/ai`

### Exit criteria

- Browse → PDP → Wishlist → Bag works for `U001`
- Refresh keeps Wishlist/Bag if using SQLite already; if still in-memory, document that Phase 2 will persist
- Profile fields save and reload
- Frontend talks only to the API

### Demo check

Add two products to Wishlist, open Wishlist, add one to Bag.

---

## Phase 2 — Catalog data pipeline (offline, no Groq)

### Goal

Replaceable ingestion: seed JSON → raw snapshot → normalize → validate → SQLite. Shopping APIs read **processed tables**, not files.

Architecture: DATA SOURCE is replaceable; application logic is not coupled to HTML.

### Why this order

Wishlist decision features need a designed catalog (similar groups, reviews, price history). Building Groq on mock strings would teach the wrong contract.

### Offline vs online

**Offline:** ingest job.  
**Online:** same shopping APIs, now backed by SQLite.

### Work

**Seed dataset (design, do not scrape)**

Target (Architecture / Context):

| Asset | Size |
|---|---|
| Products | 50–100 |
| Categories | 5–10 |
| Similar groups | Dresses, Sneakers, Handbags, Tops, Jeans (3–5 each) |
| Products with reviews | 10–15 |
| Reviews per those products | 20–50 |
| Price history | On those 10–15 plus a few more |

Internal consistency: if `rating_count` is 2,800, do not ship three reviews and claim “most buyers” later. Keep review volume honest **or** keep `rating_count` aligned with the demo corpus. Prefer honest small counts plus language “among the available reviews.”

Include deliberate trade-off triples (cheap vs best-reviewed vs balanced).

Files:

```text
data/products.json
data/reviews.json
data/price-history.json
data/users.json          ← U001 preferences
```

**Offline jobs**

```text
SeedFileSource
  → snapshot into raw/{batch_id}/
  → normalizeProduct / normalizeReview / normalizePriceHistory
  → validate (price ≤ mrp, rating range, required ids)
  → UPSERT products, reviews, price_history
  → seed users, empty or sample wishlist
```

Do **not** run Groq. Leave `review_insights`, `price_stats`, `product_similarity` empty or unpopulated.

**Schema (create now, fill later)**

Create all Architecture §9 tables so later phases only UPSERT:

- products, reviews, price_history
- review_insights, price_stats, product_similarity (empty)
- users, wishlist_items, bag_items, orders, alerts (empty)

**Backend**

- Repositories read SQLite
- Listing/PDP/Wishlist/Bag use `product_id` from DB
- Frontend should not change except broken mocks

### Do not build yet

- Live Myntra scraper
- Embedding / vector index
- Review LLM
- Kafka-style ingest

### Exit criteria

- One CLI command loads seed → SQLite
- Raw snapshot exists for that batch
- Killing and restarting the API still shows the same catalog
- Shopping flow of Phase 1 works on the full seed
- Invalid seed rows fail validation rather than inventing fields

### Demo check

Filter a category, open a reviewed product, add it to Wishlist, restart backend, Wishlist still there.

---

## Phase 3 — Wishlist decision workspace (deterministic)

### Goal

Wishlist shows **decision signals**. User can compare 2–3 items and see price + review + value **numbers**. All of this is Decision Engine + SQL. **Groq is still not required** to render the workspace.

Architecture: do not call the LLM just to display Wishlist.

### Why this order

Precompute what can be precomputed. If explanations come before scores, the model will be asked to do arithmetic.

### Offline vs online

**Offline (code, not Groq)**

- `price_aggregator` → `price_stats` (current, min, max, avg, relative_position)
- `similarity_builder` → `product_similarity` (attribute score + `reason` + matched attributes)

**Online**

- Wishlist GET joins products + stats + insight rows (insights may still be empty)
- Compare POST returns a **numeric table** + BEST VALUE / BEST REVIEWED / BEST BALANCE from code
- Price insight payload from `saved_price` + `price_stats`
- Review insight UI: if `review_insights` empty, show fallback *“Not enough review data…”* — do **not** fabricate themes

**Optional bridge (allowed):** hand-authored `data/review_insights.json` derived **only** from seed review text for a few products, loaded by ingest. That lets the review panel be designed before Phase 4 Groq. If you skip this, Phase 4 fills the table.

### Work

**Decision Engine (start here)**

- `price_insight(product, saved_price, stats)` — never future-price claims
- `preference_match(product, user)`
- `comparison_scores(products)` → labels, not an unexplained winner
- `confidence(evidence)` → HIGH / MEDIUM / LOW from volume/agreement, never “95%”
- `missing[]` flags: no history, no reviews, no size

**APIs**

- `GET /api/wishlist` includes per-item signals (Highly rated, Good value, Fit concerns if insight exists)
- `POST /api/wishlist/compare` `{ product_ids: [2..3] }` → table + scores + missing + **no Groq copy yet** (or a template sentence from scores)
- `GET /api/products/{id}/price-insight`
- `GET /api/products/{id}/review-insight`

**Frontend (inside Wishlist only)**

- `WishlistCard` decision signals
- `CompareSelector` + `CompareDrawer` / sheet (not a new route)
- `ComparisonTable`
- `PriceInsight` / `ReviewInsight` cards or sheets
- Copy rules: “Current price is close to the recent low” / “Price history unavailable”
- Never “The price will drop tomorrow”

### Do not build yet

- Groq explanations (placeholder copy from scores is OK)
- Ask Me a Question
- Alert popups
- Vector search

### Exit criteria

- Opening Wishlist does **zero** Groq calls (log/assert)
- Compare three dresses/sneakers from a similar group: table shows price, rating, rating count, value/fit/quality columns
- BEST VALUE / BEST REVIEWED / BEST BALANCE match the numbers
- Product with no history shows the unavailable fallback
- Similarity table is populated; can be queried even if UI only uses it lightly

### Demo check

Save the designed triple (cheap / best-reviewed / balanced). Compare. See trade-off **numbers** without a chat box.

---

## Phase 4 — Groq, review intelligence, Ask Me a Question

### Goal

First real LLM use, in two places only:

1. **Offline:** Groq FAST model extracts themes → `review_insights`
2. **Online:** Groq QUALITY model explains an **evidence pack** for Compare, Ask, Recommend

Architecture §14–§16: closed question enum, structured retrieval, no vector DB.

### Why this order

Insights and questions need stored evidence. Groq on an empty pack would hallucinate. Free-tier limits also require batching reviews offline.

### Offline vs online

```text
OFFLINE
  reviews → LlmClient(FAST) → themes + counts + grounded summaries
  skip products with 0 reviews
  never invent counts

ONLINE
  user picks question_id
  router → SQL evidence → Decision Engine pack
  if pack empty or only missing[] → NO Groq; return fallback
  else LlmClient(QUALITY) → fact / evidence / interpretation / recommendation
```

### Work

**LlmClient**

- `complete(model, messages)` using `GROQ_API_KEY`
- Timeouts, retry-once on 429, then fallback
- Prompts live in `backend/llm/prompts/`, not in React
- Online prompt always includes the evidence pack + grounding rules (Architecture §15)

**Offline job** `rebuild_insights`

- Batch by product
- Themes: FIT, SIZE, FABRIC, QUALITY, COMFORT, COLOR, DURABILITY, APPEARANCE, VALUE, OCCASION, IMAGE_ACCURACY, COMPLAINTS
- Store `evidence_review_ids` for optional quotes
- Language: few reviews → “Among the available reviews…”

**Question router (enum only)**

| question_id | Handler |
|---|---|
| `WORTH_THE_PRICE` | price + stats + rating + themes + Wishlist peers + prefs |
| `WHAT_BUYERS_DISLIKE` | negative themes + optional quotes |
| `IS_FIT_RELIABLE` | fit attribute + FIT/SIZE themes |
| `FABRIC_QUALITY` | material + FABRIC/QUALITY/COMFORT |
| `BETTER_OPTION_IN_WISHLIST` | similarity among Wishlist + scores |
| `WHICH_ONE_SHOULD_I_BUY` | full pack + preference weights |
| `WHY_BETTER_THAN_B` | pairwise A vs B |
| `SHOULD_I_WAIT` | price_stats only; no future prediction |

**APIs**

- `POST /api/questions/answer` `{ question_id, product_id?, product_ids? }`
- Compare endpoint: after deterministic table, attach Groq trade-off paragraph
- Recommendation is `WHICH_ONE_SHOULD_I_BUY` (or same engine + explain)

**Frontend (Wishlist sheets, not a chatbot)**

- `QuestionSheet` + radio options
- Answer card: FACT / EVIDENCE / INTERPRETATION / RECOMMENDATION
- Confidence band from engine, not model
- Loading and “Groq unavailable” fallback showing scores only

### Do not build yet

- Free-text chat
- RAG / embeddings
- Calling Groq from the browser
- Hard-coded fake answers when data exists

### Exit criteria

- `rebuild_insights` fills themes that match seed review text (spot-check; no invented specs)
- Wishlist GET still does not call Groq
- “Is this worth the price?” returns pack-grounded copy; no history → says unavailable
- “Which one should I buy?” is conditional (“best match based on your preference for…”) not “definitely the best”
- Disconnect Groq: UI still shows Phase 3 numbers

### Demo check

Compare three items → read explanation → ask “Which one should I buy?” → Add recommended item to Bag.

---

## Phase 5 — Smart alerts

### Goal

Three contextual signals **on Wishlist**, no new pages:

1. Price drop vs `saved_price`
2. Similar catalog (or Wishlist) alternative
3. Decision overload (threshold default **3** similar items)

### Why this order

Alerts need `price_stats`, `product_similarity`, and a real Wishlist. Overload is user-specific and computed **online** (Architecture §19).

### Offline vs online

| Alert | Generate | Serve |
|---|---|---|
| PRICE_DROP | Job `scan_price_alerts` (and `simulate_price_drop`) | Wishlist GET |
| SIMILAR_PRODUCT | On Wishlist add **or** Wishlist GET (cheap at this scale) | Same |
| DECISION_OVERLOAD | Online cluster of current Wishlist | Payload + dismissible card |

### Work

**Backend**

- `alerts` rows: type, payload (`from`, `to`, `save_amount` / similar reason / group count), dismissed_at
- Dedup: one undismissed PRICE_DROP per user+product
- Drop rule: `current_price <= saved_price - 1` (₹1; see Doc_Alignment)
- `simulate_price_drop` updates `products.price` + history, rebuilds stats, scans alerts (demo control)
- Overload: group by category/subcategory and/or similarity edges; if count ≥ 3, include prompt; `[Compare My Options]` preselects that group
- Similar alert uses stored `reason` (explainable)

**Frontend**

- Modal / bottom sheet / inline card — not a notifications center page
- `[View Item]` `[Dismiss]` `[Compare]`
- Overload copy: “You have 5 similar dresses saved. Want help narrowing them down?”

### Do not build yet

- Push notifications, email, Kafka
- Predicting future price in the alert copy

### Exit criteria

- Run simulate job → open Wishlist → price-drop UI with correct rupee delta
- Wishlist with 3+ similar dresses → overload prompt → Compare opens with those ids
- Similar-product card shows cheaper/higher-rated neighbor and reason
- Dismiss persists across refresh

### Demo check

Full Architecture primary story: save 3 similar → overload → compare → question → price insight/alert → Bag.

---

## Phase 6 — Polish, mock purchase, demo hardening

### Goal

The MVP feels like fashion commerce, not an AI console. The 18-step success list in Context §54 is clickable. Missing data never becomes fake data.

### Why this order

Polish on a broken funnel wastes time. After Phase 5 the funnel exists.

### Work

**Product**

- Mock checkout + purchase confirmation from Bag (no payment gateway)
- Loading, empty, error states on every list (empty Wishlist, Groq 429, ingest missing)
- Responsive check: Wishlist compare/questions/alerts on a narrow viewport
- Visual hierarchy: product imagery first; AI copy secondary
- Labels: “Decision insight”, “Based on buyer reviews”, “Price insight” — not “AI says”
- Light motion only where it helps (sheet present, toast)

**Reliability**

- Log Groq usage (endpoint, model, tokens if available) to confirm Wishlist GET is silent
- Seed + jobs documented in README: ingest, insights, similarity, simulate drop
- One-command demo script order:

```text
1. ingest_catalog
2. rebuild price_stats + similarity
3. rebuild_insights (Groq)
4. optional simulate_price_drop
5. start API + Vite
```

**Not in this phase (still out of MVP)**

- Full Myntra catalog, real payments, production auth, live scrape, vector DB, unrestricted chatbot, separate Decision Studio

### Exit criteria (demo definition of done)

A user can:

1. Open the app  
2. Browse and open PDP  
3. Add products to Wishlist  
4. See decision signals  
5. Select 2–3 and compare (numbers + Groq explanation)  
6. See price analysis and review themes  
7. Ask a predefined question and get a grounded answer  
8. See similar-product and/or price-drop and/or overload  
9. Add chosen product to Bag  
10. Finish mock checkout  

Primary story (Architecture §20 / Context §55) runs without leaving Wishlist for decision tools.

### Demo check

Walk the primary story twice: once with Groq on, once with Groq key removed (numbers + fallbacks still work).

---

## Cross-phase dependency view

```text
Phase 0  app processes
   ↓
Phase 1  user journeys exist
   ↓
Phase 2  SQLite is source of truth
   ↓
     ┌────────────┴────────────┐
     ↓                         ↓
price_stats               similarity
review_insights (empty or seed)
     ↓                         ↓
Phase 3  Wishlist workspace (no Groq)
     ↓
Phase 4  LlmClient + insights job + Q&A
     ↓
Phase 5  alerts on top of 3+4
     ↓
Phase 6  mock purchase + polish
```

Cannot reorder into “Groq first”: there is nothing grounded to send.

---

## Suggested calendar (indicative, not a commitment)

Assumes one developer familiar with React and Python. Adjust freely.

| Phase | Focus | Relative effort |
|---|---|---|
| 0 | Scaffold | Small |
| 1 | Shell | Medium |
| 2 | Seed + ingest + schema | Medium–large (dataset quality matters) |
| 3 | Decision Engine + Wishlist UI | Large |
| 4 | Groq + questions | Medium |
| 5 | Alerts | Medium |
| 6 | Polish + demo | Medium |

Spend extra time on **Phase 2 seed design**. Bad data cannot be rescued by Groq.

---

## Per-phase Groq policy

| Phase | Groq |
|---|---|
| 0–3 | Off. Stub may exist; must not be on the Wishlist read path |
| 4 | On: FAST for `rebuild_insights`; QUALITY for compare/Q&A/recommend |
| 5–6 | Same as 4; alerts themselves are not LLM-generated |

---

## API surface by the end of Phase 6

| Method | Path | Introduced |
|---|---|---|
| GET | `/health` | 0 |
| GET | `/api/products` | 1 |
| GET | `/api/products/{id}` | 1 |
| GET | `/api/wishlist` | 1 (signals/alerts later) |
| POST | `/api/wishlist` | 1 |
| DELETE | `/api/wishlist/{productId}` | 1 |
| GET | `/api/bag` | 1 |
| POST | `/api/bag` | 1 |
| DELETE | `/api/bag/{productId}` | 1 |
| GET/PATCH | `/api/profile` | 1 |
| POST | `/api/checkout` (mock) | 6 (stub in 1 OK) |
| GET | `/api/products/{id}/price-insight` | 3 |
| GET | `/api/products/{id}/review-insight` | 3 |
| POST | `/api/wishlist/compare` | 3 (copy in 4) |
| POST | `/api/questions/answer` | 4 |
| PATCH | `/api/alerts/{id}/dismiss` | 5 |

Jobs (CLI, not HTTP required): `ingest_catalog`, `rebuild_insights`, `rebuild_similarity`, `rebuild_price_stats`, `scan_price_alerts`, `simulate_price_drop`.

---

## Frontend components by phase

| Component | Phase |
|---|---|
| App shell, nav, ProductCard | 1 |
| WishlistCard (basic) | 1 |
| WishlistCard signals, CompareSelector, CompareDrawer, ComparisonTable, PriceInsight, ReviewInsight | 3 |
| QuestionSheet, QuestionOption, RecommendationCard | 4 |
| PriceAlert, SimilarProductAlert, DecisionOverloadModal, Toast, BottomSheet | 5 |
| Empty/error/loading on all of the above | 6 |

Reuse these. Do not duplicate a second compare UI on a new route.

---

## Testing checklist (minimum)

| Phase | Prove |
|---|---|
| 1 | Add/remove Wishlist and Bag; confirmation shown |
| 2 | Re-ingest is idempotent; validation rejects bad prices |
| 3 | Compare labels match fixtures; no Groq in network log on Wishlist GET |
| 4 | Question with missing history does not claim “lowest price”; empty pack skips Groq |
| 5 | Simulate drop creates one alert; dismiss sticks; overload at 3 |
| 6 | Primary demo story; Groq-down fallback |

---

## What this plan explicitly never schedules (MVP)

- Entire Myntra catalog / live scraper on request
- Production payments, full auth, inventory, seller/OMS
- Unrestricted chatbot, RAG, vector database
- Separate Decision Studio or comparison site
- Kafka, Kubernetes, Elasticsearch, Redis, paid LLMs

Those belong to Architecture §23 **Future**, not to these phases.

---

## One-line reminder

> **Don’t help users save more products. Help them resolve which saved product is right for them — inside Wishlist, with Groq only when language is needed.**

Implement in phase order. Ship Phase 1 shopping. Then data. Then deterministic decisions. Then Groq. Then alerts. Then polish.
