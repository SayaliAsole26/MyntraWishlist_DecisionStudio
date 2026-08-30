# DOC ALIGNMENT — CANONICAL LOCKS

Read this before Phase 0. If two docs disagree, **this file wins**.

Related docs: `Context.md.md` (product), `ProblemStatement.md` (problem), `Architecture.md` (system), `Master_Architecture.md` (implementation spec), `Phase_wise_Implementation.md` (build order), `Edgecase.md`, `evals.md`.

**Status:** Docs are aligned for implementation. Remaining differences below are **locked**, not left open.

---

## 1. What already agreed (do not reopen)

| Topic | Lock |
|---|---|
| Product | Wishlist is the decision workspace. No Decision Studio / compare / AI / alerts **page**. |
| Journey | Save → uncertainty → evidence → compare/ask → decide → Bag → mock purchase |
| Stack | React + Vite, FastAPI, SQLite, Groq free tier, seed JSON ingest |
| User | Single demo user `U001`. No production auth. |
| AI split | Code for math/CRUD/similarity. Groq for review batch (offline) and explanations (on demand). |
| Wishlist GET | **Zero** Groq calls |
| Retrieval | Structured SQL. No vector DB, Kafka, Redis, K8s, paid LLMs |
| Catalog size | 50–100 products, similar groups, honest review rows (20–50 on 10–15 SKUs) |
| Reference URL | [https://www.myntra.com/](https://www.myntra.com/) — inspiration only; never scrape |
| Overload | Threshold **3** similar items in one cluster |
| Confidence | HIGH / MEDIUM / LOW from evidence — never a percentage |
| Implementation order | Shopping first, Groq in Phase 4 |

---

## 2. Conflicts found and how they are locked

### 2.1 Phase numbers

`Context.md.md` §58 starts at PHASE 1 (shell). Implementation adds **Phase 0** (repo scaffold) because the repo is greenfield.

| Context §58 | Implementation |
|---|---|
| — | **Phase 0** Foundation |
| PHASE 1 shell | Phase 1 |
| PHASE 2 data | Phase 2 |
| PHASE 3 decision UI | Phase 3 |
| PHASE 4 AI / questions | Phase 4 |
| PHASE 5 alerts | Phase 5 |
| PHASE 6 polish | Phase 6 |

Follow `Phase_wise_Implementation.md`. Start at Phase 0.

### 2.2 Compare API path

Was: `/api/compare` (Architecture, Phase-wise) vs `/api/wishlist/compare` (Master).

**Lock:** `POST /api/wishlist/compare`  
Body: `{ "product_ids": ["P001","P002"] }` (length 2 or 3).

Frontend route `/compare` still **must not exist**. Nested API ≠ a comparison page.

### 2.3 Alerts API

Was: `GET /api/wishlist?include=alerts` vs `GET /api/alerts` vs `GET /api/wishlist/alerts`.

**Lock:**

- `GET /api/wishlist` **includes** undismissed alerts + overload signal (no extra query required).
- `PATCH /api/alerts/{id}/dismiss`
- Do not build a separate alerts page. A dedicated GET is optional and not required for MVP.

### 2.4 Wishlist DELETE

**Lock:** `DELETE /api/wishlist/{productId}`  
**Lock:** `DELETE /api/bag/{productId}`  
**Lock:** `POST /api/wishlist` and `POST /api/bag` with `{ "product_id": "P001" }`

### 2.5 `saved_price`

**Lock: first save wins.**  
If the product is already on Wishlist, POST is idempotent and does **not** change `saved_price`.  
Remove then add again → `saved_price` = current price at re-add.  
Re-ingest catalog does **not** rewrite existing `saved_price`.

### 2.6 Price-drop threshold

Was: “₹1 or 5%”.

**Lock:** `current_price <= saved_price - 1` (₹1).  
Demo drops are hundreds of rupees. No percentage rule in MVP.

### 2.7 Who may read seed JSON

Was: Phase-wise “prefer frontend reading products.json”. Architecture: frontend never reads JSON.

**Lock:** Frontend talks **only** to the API. Backend (or an ingest job) may read `data/*.json`. Never `raw/` from the UI.

### 2.8 Ask Me a Question surface

**Lock:** Questions run from **Wishlist** only (item or 2–3 selected). PDP has no question sheet in MVP.  
`product_id` in the request must be on that user’s Wishlist (or in the selected compare set).

### 2.9 `rating_count` vs review rows

Context asked catalog counts to “feel” like 2,800 ratings. Review NLP only has 20–50 texts.

**Lock:**

- `products.rating` / `rating_count` are **catalog fields** (may be large for a Myntra-like card).
- Review insight **language** uses **stored review rows** only (“Among the available reviews…”).
- Groq must not say “2,800 buyers mentioned thin fabric” unless 2,800 review **texts** exist.
- Seed may keep a marketing-like `rating_count` on the card; do not fake 2,800 review records.

### 2.10 Missing-data copy

Context §32 vs §47 used two price strings. **Lock to §47 / Edgecase:**

| Missing | Copy |
|---|---|
| Reviews | Not enough review data to assess this reliably. |
| Price history | Price history unavailable. |
| Size data | Size availability information unavailable. |
| Similar products | No closely matching products found. |
| Groq down | Decision insight temporarily unavailable. You can still compare price, rating, and reviews. |

### 2.11 Empty evidence pack

**Lock:** Do **not** call Groq. Return the fallback from code.

### 2.12 “Decision Studio” wording

The **product concept** is Wishlist Decision Studio. The **app** has no page or route by that name. Pipeline text “use in Decision Studio” means **use inside Wishlist**.

### 2.13 Bag `quantity`

Schema may include `quantity` default 1. MVP UI does not need quantity steppers.

### 2.14 Question registry (complete set)

```text
WORTH_THE_PRICE
WHAT_BUYERS_DISLIKE
IS_FIT_RELIABLE
FABRIC_QUALITY
BETTER_OPTION_IN_WISHLIST
WHICH_ONE_SHOULD_I_BUY
WHY_BETTER_THAN_B
SHOULD_I_WAIT
```

No free-text questions.

### 2.15 Hand-authored insights in Phase 3

Allowed **only** if copied from real seed review text (no invented themes). Phase 4 Groq may replace them. Skip the hand file if you go straight to Groq after the compare table works.

---

## 3. Canonical API list (implement this)

| Method | Path |
|---|---|
| GET | `/health` |
| GET | `/api/products` |
| GET | `/api/products/{id}` |
| GET | `/api/wishlist` |
| POST | `/api/wishlist` |
| DELETE | `/api/wishlist/{productId}` |
| POST | `/api/wishlist/compare` |
| GET | `/api/products/{id}/price-insight` |
| GET | `/api/products/{id}/review-insight` |
| POST | `/api/questions/answer` |
| PATCH | `/api/alerts/{id}/dismiss` |
| GET | `/api/bag` |
| POST | `/api/bag` |
| DELETE | `/api/bag/{productId}` |
| GET | `/api/profile` |
| PATCH | `/api/profile` |
| POST | `/api/checkout` |

---

## 4. Read order for implementers

```text
1. Doc_Alignment.md          ← you are here
2. Phase_wise_Implementation.md
3. Master_Architecture.md    (schema, folders, prompts)
4. Edgecase.md + evals.md    (before calling a phase done)
5. Architecture.md           (offline vs online why)
6. ProblemStatement.md / Context.md.md  (product intent)
```

---

## 5. Ready for Phase 0?

**Yes**, once these locks are applied in the other files (same commit as this document).

Phase 0 work: Vite + FastAPI + SQLite path + `.env.example` + folder tree. No Groq calls. No Decision Studio route.
