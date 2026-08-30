# MYNTRA WISHLIST DECISION STUDIO
## Evaluations (Evals)

How we know the MVP is correct: **deterministic checks first**, then **grounded Groq checks**, then the **demo journey**. This is not a production ML leaderboard. The product is decision support inside Wishlist.

Sources: `Docs/Architecture.md`, `Docs/Phase_wise_Implementation.md`, `Docs/Edgecase.md`, `Docs/Doc_Alignment.md`.

---

## 1. What we evaluate (and what we don’t)

| Evaluate | Do not treat as success |
|---|---|
| Grounded, explainable decisions from stored evidence | More Wishlist adds |
| Correct price/review/compare **math** | Longer sessions / more Groq calls |
| Groq **only** when the user asks for language | “AI confidence 97%” |
| Shopping works with Groq off | Fluency of ungrounded prose |
| Primary demo story on **Wishlist** (no extra pages) | Recreating all of Myntra |

**North star (qualitative):** the user can move from “I like these but don’t know which to buy” to “I understand the trade-offs.”

---

## 2. Eval layers

```text
L1  Unit        Decision Engine, ingest validation, alerts, overload
L2  API         Wishlist / compare / questions / bag  (Groq mocked)
L3  Grounding   Groq output vs evidence pack  (fixtures + live optional)
L4  Contract    No Groq on Wishlist GET; no forbidden routes; no key in FE
L5  Demo        Human / scripted click-through of the primary story
```

A phase does not pass because the UI “looks smart.” It passes its **exit criteria** plus the evals tagged for that phase.

---

## 3. Golden fixtures (required)

Keep a tiny, versioned fixture set (not the full 50–100 catalog) so evals are stable.

### 3.1 Trade-off triple (Context / Architecture demo)

| id | Role | Price | Rating | Rating count |
|---|---|---|---|---|
| `FIX_A` | Best balance | ₹999 | 4.2 | (honest small N in reviews table) |
| `FIX_B` | Best reviewed | ₹1,299 | 4.5 | higher than A and C |
| `FIX_C` | Best value / cheapest | ₹899 | 4.1 | lowest volume |

**L1 expect**

- `best_value` = `FIX_C`  
- `best_reviewed` = `FIX_B`  
- `best_balance` = `FIX_A`  

Groq (L3) must **not** change these labels.

### 3.2 Sparse product `FIX_SPARSE`

- No reviews, no price history, material null  
- Expect: `missing` includes reviews / price_history / material as applicable  
- Review copy: *Not enough review data to assess this reliably.*  
- Price copy: *Price history unavailable.*  
- **L3:** answering `WORTH_THE_PRICE` or `IS_FIT_RELIABLE` must **not** call Groq if pack is empty of usable evidence (Architecture: empty pack → no LLM)

### 3.3 Few-review product `FIX_FEW`

- Exactly 3 reviews; two mention comfort; one mentions thin fabric  
- Forbidden in any generated text: `Most buyers`, `everyone`, `all customers`  
- Required pattern: `Among the available reviews` (or equivalent that names the small N)

### 3.4 Preference flip `FIX_PREFS`

Same triple as 3.1.

- User `priority = ["price"]` → BEST MATCH leans `FIX_C` or `FIX_A`, **not** unexplained `FIX_B` as “for you” if B is over budget  
- User `priority = ["Quality","Comfort"]` and `price_max` covers B → MATCH may be `FIX_B` or `FIX_A` with explicit trade-off  
- BEST VALUE / BEST REVIEWED **unchanged** by prefs

### 3.5 Overload / alerts

- Wishlist: 3 similar dresses from seed Group 1 → overload **on**  
- Wishlist: 2 similar → overload **off**  
- `saved_price` 1499, current 1199 → drop payload save ₹300  
- Second scan → still one undismissed `PRICE_DROP`

---

## 4. L1 — Deterministic evals (no Groq)

These are the backbone. They must pass with `GROQ_API_KEY` unset.

| Eval ID | Checks | Phase | Pass |
|---|---|---|---|
| E-VAL-01 | Discount = f(mrp, price); no LLM | 2–3 | Exact |
| E-VAL-02 | `relative_position`; `max==min` no divide-by-zero | 3 | Exact |
| E-VAL-03 | No history → flag + fallback string | 3 | Exact |
| E-VAL-04 | Compare labels on fixture triple | 3 | Exact |
| E-VAL-05 | Tie-break documented and stable | 3 | Exact |
| E-VAL-06 | Similarity score uses attributes only; `reason` non-empty above threshold | 3 | Exact |
| E-VAL-07 | Unrelated category pair below threshold or no “same dresses” reason | 3 | Exact |
| E-VAL-08 | Recommendation score weights follow priorities | 3 | Directional + snapshot |
| E-VAL-09 | Product over `price_max` not described as in-budget by **engine** flags | 3 | Exact |
| E-VAL-10 | Confidence HIGH/MEDIUM/LOW from volume/conflict rules (never a %) | 3 | Exact |
| E-VAL-11 | Overload count ≥ 3 same cluster; mixed categories not one cluster | 5 | Exact |
| E-VAL-12 | Price drop iff `current_price <= saved_price - 1`; rise = no drop | 5 | Exact |
| E-VAL-13 | Alert dedup one undismissed per user+product+type | 5 | Exact |
| E-VAL-14 | Ingest rejects price > mrp, bad rating, orphan reviews | 2 | Exact |
| E-VAL-15 | Re-ingest idempotent; wishlist `saved_price` preserved | 2 | Exact |

Map to `Docs/Edgecase.md` IDs in test names (`E-VAL-03` ↔ `PX-01`).

---

## 5. L2 — API / integration evals

Run with Groq **mocked** (returns canned JSON or raises).

| Eval ID | Scenario | Pass |
|---|---|---|
| E-API-01 | Browse → PDP → POST wishlist → GET wishlist → POST bag | 200s; `saved_price` set |
| E-API-02 | GET `/api/wishlist` with mock that **fails if Groq invoked** | Mock never called |
| E-API-03 | POST `/api/wishlist/compare` 1 id → 400; 2–3 ids → 200; 4 ids → 400 | |
| E-API-04 | POST compare ids not on wishlist → 400 | |
| E-API-05 | POST `/api/questions/answer` unknown id or free `prompt` field → 400 | |
| E-API-06 | `FIX_SPARSE` price-insight / review-insight fallbacks; 200 not 500 | |
| E-API-07 | Mock Groq 429 on compare → table + scores still 200; explanation fallback | |
| E-API-08 | DELETE wishlist; GET omits item | |
| E-API-09 | PATCH profile invalid min/max → 400 | |
| E-API-10 | GET `/studio` etc. → 404 (no routes) | |
| E-API-11 | Checkout empty bag → 400; with items → mock order | Phase 6 |
| E-API-12 | Dismiss alert; GET wishlist omits it | Phase 5 |

---

## 6. L3 — Groq grounding evals

Only after Phase 4. Two modes:

1. **Replay (CI):** frozen evidence pack → frozen model output **or** a validator-only run if live Groq is flaky  
2. **Live (pre-demo):** real Groq against fixtures; judge with **programmatic guards**, not vibe

### 6.1 Must-call vs must-not-call Groq

| Situation | Groq |
|---|---|
| GET wishlist | **Never** |
| GET price-insight / review-insight | **Never** (precomputed + engine copy) |
| POST compare (explanation) | Yes, if pack has products |
| POST questions/answer with usable pack | Yes |
| Empty / missing-only pack | **Never** |
| `rebuild_insights` product with 0 reviews | **Never** |

Eval **E-AI-CALL-01:** instrument `LlmClient` counter in tests.

### 6.2 Output schema

Parsed JSON must include (names may match Master Architecture):  
`answer`, `confidence` ∈ {HIGH,MEDIUM,LOW}, `facts`, `evidence` or equivalent, `positive_signals`, `concerns`, `tradeoffs`, `interpretation`, `recommendation`, `missing`.

Malformed → fail (same as production fallback path).

### 6.3 Numeric grounding (hard fail)

For every number in Groq output (prices, ratings, counts, deltas):

- It appears in the evidence pack, **or**
- It is a trivial restatement of pack arithmetic already in `scores` (optional allowlist)

**Fail** if the model emits a price, rating, or rating_count **not** in the pack.

### 6.4 Forbidden strings (hard fail)

Case-insensitive, unless noted:

| Pattern | Why |
|---|---|
| `will drop tomorrow` / `will go down` / `definitely drop` | Future price |
| `AI confidence` / `\d{2,3}%` confidence | Fake confidence |
| `definitely the best` / `guaranteed` | Overclaim |
| `most buyers` / `most customers` when review N < 10 | Overgeneralization |
| `AI says` | UX rule |
| Invented theme not in pack insights | Hallucinated opinion |

`FIX_FEW`: fail if `most buyers` present.

`SHOULD_I_WAIT`: fail if any future-tense price prediction.

### 6.5 Required behaviors (soft + hard)

| Eval ID | Check | Bar |
|---|---|---|
| E-GND-01 | `missing[]` from engine appears in answer when non-empty | Hard |
| E-GND-02 | FACT vs INTERPRETATION separable in schema | Hard |
| E-GND-03 | Compare explainer does not change BEST VALUE/REVIEWED/BALANCE | Hard |
| E-GND-04 | `WHICH_ONE_SHOULD_I_BUY` names a trade-off if two products differ on price vs rating | Hard |
| E-GND-05 | `WORTH_THE_PRICE` without history does not claim lowest historical price | Hard |
| E-GND-06 | `IS_FIT_RELIABLE` with no fit evidence uses unavailable language | Hard |
| E-GND-07 | Recommendation language is conditional on stated prefs | Hard |
| E-GND-08 | Offline insights theme counts ≤ actual review mentions (spot-check fixture) | Hard (human+script) |
| E-GND-09 | Quotes only from `evidence_review_ids` | Hard |

### 6.6 Human rubric (live Groq, 1–5)

Use on the primary story once per demo freeze. Average ≥ 4 to ship Phase 4.

| Dimension | 1 | 5 |
|---|---|---|
| Grounding | Invents facts | Every claim traceable to pack |
| Trade-offs | Picks a silent winner | Names what you give up |
| Humility | “Most buyers” on 3 reviews | Matches volume |
| Usefulness | Generic chatbot | Answers the selected question |
| Commerce feel | “AI app” | Insight secondary to product |

---

## 7. L4 — Architectural / contract evals

| Eval ID | Check | Phase |
|---|---|---|
| E-CTR-01 | Frontend bundle has no `gsk_` / `GROQ_API_KEY` | 4 |
| E-CTR-02 | `.env` gitignored | 0 |
| E-CTR-03 | Wishlist GET Groq invocations = 0 (integration log) | 4–6 |
| E-CTR-04 | No page routes for studio/compare/ai/alerts | 1+ |
| E-CTR-05 | `question_id` allowlist only | 4 |
| E-CTR-06 | DataSource: app does not import scraper HTML | 2 |
| E-CTR-07 | Phase 0–3 test suite green with Groq stub that **throws** | 0–3 |

---

## 8. L5 — Primary demo eval (Phase 6 Definition of Done)

Script (manual or Playwright). **Fail** if any step needs a page that is not Home / Listing / PDP / Wishlist / Bag / Profile.

| Step | Action | Pass look |
|---|---|---|
| 1 | Open app | Home loads |
| 2 | Browse listing | Cards: image, brand, price, rating |
| 3 | Open PDP | Add to Wishlist works; toast |
| 4 | Save **3 similar** products (Group 1) | Wishlist count 3 |
| 5 | Open Wishlist | Signals visible **without** waiting on Groq |
| 6 | Overload | “similar … saved” + Compare My Options |
| 7 | Compare | Table: price, rating, count, fit/quality/value; labels match engine |
| 8 | Explanation | Groq copy **or** fallback; labels unchanged |
| 9 | Price insight | History or “unavailable”; no future drop |
| 10 | Review insight | Themes or “not enough review data” |
| 11 | Ask “Which one should I buy?” | Structured answer; trade-off |
| 12 | Similar and/or price-drop | Contextual card; dismiss works |
| 13 | Add chosen to Bag | Bag has item |
| 14 | Mock checkout | Confirmation; no payment SDK |
| 15 | Repeat 5–11 with Groq key removed | Numbers remain; insight fallback |

**E-DEMO-GROQ-OFF** is mandatory. AI is an enhancement, not a single point of failure.

---

## 9. Phase gate (evals vs implementation plan)

A phase is **not done** until its exit criteria **and** these evals pass.

| Phase | Must pass |
|---|---|
| 0 | Health 200; `.env.example`; E-CTR-02 |
| 1 | E-API-01 (shell); E-CTR-04; empty Wishlist UI |
| 2 | E-VAL-14, E-VAL-15; restart persists catalog |
| 3 | E-VAL-01–10; E-API-02 (if LlmClient exists, still unused); PX fallbacks |
| 4 | E-AI-CALL-01; E-GND-01–07; E-API-05–07; E-CTR-01, E-CTR-03; Groq-off still compares |
| 5 | E-VAL-11–13; E-API-12; simulate_price_drop demo |
| 6 | L5 full table; E-DEMO-GROQ-OFF; empty/error states |

Do not start Phase N+1 to “make evals green” by skipping N.

---

## 10. Metrics worth logging (MVP-light)

Log in dev/demo; not a full analytics stack.

| Signal | Why |
|---|---|
| Groq calls per endpoint | Catch Wishlist GET regressions |
| Question_id mix | Demo coverage |
| Fallback rate (Groq fail / empty pack) | Reliability |
| Compare size (2 vs 3) | UX |
| Overload shown / dismissed | Intervention quality |

**Not** success metrics: raw Groq token count, session length, Wishlist adds.

Conceptual product metric (not implemented): Wishlist → Bag → mock purchase within the demo session.

---

## 11. Suggested test mapping

| Kind | Location (when code exists) | Covers |
|---|---|---|
| Unit | `backend/tests/test_decision_engine.py` | L1 |
| Unit | `backend/tests/test_ingest_validate.py` | IN-* |
| Unit | `backend/tests/test_alerts.py` | AL-*, OV-* |
| API | `backend/tests/test_api.py` | L2 |
| Grounding | `backend/tests/test_grounding.py` | L3 guards on fixtures |
| Contract | `frontend` grep / bundle check | L4 |
| E2E | `frontend` e2e optional | L5 subset |

CI default: L1 + L2 + L4 + L3 **guards with mocked Groq**. Live Groq: manual/pre-demo.

---

## 12. Pass / fail summary

**Pass the MVP** when:

1. Fixture triple labels are stable and Groq cannot override them.  
2. Missing data uses the Architecture fallback strings.  
3. Wishlist GET never calls Groq.  
4. Questions are enum-only and pack-grounded.  
5. Groq-down still shops, compares numbers, and adds to Bag.  
6. The primary story completes on Wishlist.  
7. No Decision Studio (or sibling) page exists.

**Fail the MVP** if any P0 in `Docs/Edgecase.md` is reproducible on the demo path.

---

## 13. One-line eval principle

> If the Decision Engine would not claim it, Groq must not claim it. If the data is missing, the system says so. If Groq is missing, the shopper can still decide with numbers.
