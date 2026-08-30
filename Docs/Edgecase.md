# MYNTRA WISHLIST DECISION STUDIO
## Edge Cases

This document lists edge cases the MVP must handle without fabricating data, leaving Wishlist, or calling Groq when it should not.

Sources: `Docs/Architecture.md`, `Docs/Phase_wise_Implementation.md`, `Docs/Doc_Alignment.md`.

**Severity**

| Level | Meaning |
|---|---|
| **P0** | Breaks trust or the demo (hallucination, wrong money, Groq on Wishlist GET) |
| **P1** | Feature unusable or misleading |
| **P2** | Awkward but recoverable |

**Expected copy** (do not invent alternatives)

| Condition | User-facing text |
|---|---|
| No reviews | Not enough review data to assess this reliably. |
| Few reviews | Among the available reviews… (never “Most buyers…”) |
| No price history | Price history unavailable. |
| No size data | Size availability information unavailable. |
| No similar products | No closely matching products found. |
| Groq down / 429 | Decision insight temporarily unavailable. You can still compare price, rating, and reviews. |
| Empty evidence pack | Do **not** call Groq; return the fallback from code. |

---

## 1. Product and navigation

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| NAV-01 | User tries to open frontend `/studio`, `/compare`, `/ai`, `/insights`, `/alerts` | Those **pages** must not exist. Decision UX stays on `/wishlist`. API `POST /api/wishlist/compare` is allowed | P0 | 1+ |
| NAV-02 | Compare / Q&A / alerts opened | Drawer, sheet, or modal **on Wishlist**, not a new page | P0 | 3–5 |
| NAV-03 | Deep-link to unknown `product_id` | 404 / “Product unavailable”; no invented PDP | P1 | 1 |
| NAV-04 | Empty catalog after failed ingest | Listing empty state; app still boots | P1 | 2, 6 |
| NAV-05 | Mobile narrow viewport with compare + question sheet | Usable; no horizontal trap; no desktop-only page | P1 | 6 |
| NAV-06 | UI copy says “AI says…” | Forbidden. Use “Decision insight”, “Price insight”, “Based on buyer reviews” | P1 | 4–6 |

---

## 2. Wishlist and Bag

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| WL-01 | Add same product twice | Idempotent; one row; `saved_price` **not** overwritten (first save wins) | P0 | 1 |
| WL-02 | Remove product then add again | New `saved_price` = **current** price at re-add | P1 | 1 |
| WL-03 | Add to Wishlist while already in Bag | Allowed; independent lists | P2 | 1 |
| WL-04 | Add to Bag from Wishlist after remove from Wishlist | Bag unchanged unless user also removes from Bag | P2 | 1 |
| WL-05 | Empty Wishlist | Empty state; no fake signals, no Groq, no overload | P1 | 1, 6 |
| WL-06 | Empty Bag → mock checkout | Block checkout; empty Bag message | P1 | 6 |
| WL-07 | Product deleted from catalog but still on Wishlist | Hide or “unavailable”; do not show invented specs | P1 | 2 |
| WL-08 | Wishlist GET | **Zero Groq calls** (assert in logs) | P0 | 3+ |
| WL-09 | `saved_price` missing on old row | Treat as unknown; no “you save ₹X”; no alert math | P1 | 5 |
| WL-10 | Refresh after add | Item persists (SQLite from Phase 2) | P0 | 2 |
| WL-11 | Select 0 or 1 product and tap Compare | Disable Compare or 400: need 2–3 ids | P1 | 3 |
| WL-12 | Select 4+ products | Cap at 3; cannot compare 4 | P1 | 3 |
| WL-13 | Compare ids not on this user’s Wishlist | 400; do not leak other users’ items (even with only `U001`) | P1 | 3 |
| WL-14 | Compare mix of unrelated categories (dress + sneaker) | Still return numbers; similarity/overload logic must not force them into one “similar dresses” group | P1 | 3, 5 |
| WL-15 | Duplicate `product_id` in compare payload | Dedupe or 400 | P2 | 3 |

---

## 3. Profile and scoring

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| PF-01 | `price_max` < `price_min` | Reject on PATCH | P1 | 1 |
| PF-02 | Empty priorities | Score without preference boost; do not invent “you care about quality” | P1 | 3–4 |
| PF-03 | Product over budget | `price_fit` low; recommendation may still mention it as trade-off, not “within your budget” | P0 | 3–4 |
| PF-04 | Occasion mismatch (Office user, Vacation-only SKU) | Lower `occasion_fit`; do not claim “suitable for office” | P0 | 4 |
| PF-05 | User size `M`, product sizes `["S","L"]` | Flag size gap; “Size availability information unavailable” only if sizes null — if sizes exist and M missing, say M is not listed | P1 | 3–4 |
| PF-06 | Priority = price vs priority = quality on same triple | BEST MATCH FOR YOU can change; BEST VALUE / BEST REVIEWED stay number-driven | P0 | 3–4 |

---

## 4. Catalog ingest and seed

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| IN-01 | `price` > `mrp` | Validation fail; no upsert of that row | P0 | 2 |
| IN-02 | Negative price / discount | Reject | P0 | 2 |
| IN-03 | Rating outside 0–5 | Reject | P0 | 2 |
| IN-04 | Duplicate `product_id` in seed | Last valid wins **or** fail batch; ingest must be idempotent on re-run | P1 | 2 |
| IN-05 | Review for unknown `product_id` | Reject review; do not create a ghost product | P0 | 2 |
| IN-06 | Duplicate review text / id | Dedup; do not double-count themes | P1 | 2, 4 |
| IN-07 | Empty `review_text` | Drop | P2 | 2 |
| IN-08 | `rating_count` = 2800 but only 3 reviews in DB | Do not let Groq say “2,800 buyers said…” from review rows. Engine may show catalog `rating_count` as a **product field** but review language must follow **actual review rows** (“among the available reviews”) | P0 | 2, 4 |
| IN-09 | Product `fit = Regular` but all reviews say “very tight” | Keep conflict; mixed signal; do not overwrite `fit` from reviews | P1 | 2, 4 |
| IN-10 | Missing optional fields (material, occasions) | Store null; `missing[]` at runtime; never fill from Groq | P0 | 2–4 |
| IN-11 | Re-ingest | No duplicate Wishlist rows; catalog updates; `saved_price` on existing wishlist **unchanged** | P0 | 2 |
| IN-12 | Failed mid-batch | Raw snapshot still on disk; DB not half-poisoned (transaction) | P1 | 2 |
| IN-13 | Frontend reads `data/*.json` or `raw/` | Forbidden | P0 | 1+ |
| IN-14 | Live scrape on page load | Forbidden | P0 | all |

---

## 5. Price intelligence

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| PX-01 | No `price_history` rows | “Price history unavailable.” No “lowest price”, no relative position | P0 | 3 |
| PX-02 | Single history point (`max == min`) | Not a range; “only one observed price”; do not divide by zero | P0 | 3 |
| PX-03 | Current = historical min | May say close to / at recent low. **Never** “will drop tomorrow” | P0 | 3–4 |
| PX-04 | Current > historical min | “This item has previously dropped below the current price.” | P1 | 3 |
| PX-05 | Current < `saved_price` | Delta arithmetic in **code**; Groq may rephrase numbers in pack only | P0 | 3–4 |
| PX-06 | Current > `saved_price` (price rose) | No PRICE_DROP alert; may show “higher than when you saved” | P1 | 3, 5 |
| PX-07 | Current == `saved_price` | No drop alert | P1 | 5 |
| PX-08 | Groq invents a min/max not in pack | Validator strips / reject response; fallback | P0 | 4 |
| PX-09 | `SHOULD_I_WAIT` with no history | `missing: [price_history]`; no wait/buy-now prophecy | P0 | 4 |
| PX-10 | `SHOULD_I_WAIT` with history | Position language only; **never** predict next move | P0 | 4 |
| PX-11 | Discount display when mrp missing | Don’t compute fake % | P1 | 3 |
| PX-12 | Price in paise vs rupees mix | One unit (rupees INTEGER) everywhere | P0 | 2 |

---

## 6. Review intelligence

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| RV-01 | 0 reviews | Skip Groq analyzer; insight fallback string; confidence N/A or LOW | P0 | 4 |
| RV-02 | 1–3 reviews | “Among the available reviews…”; never “Most buyers…” | P0 | 4 |
| RV-03 | Theme with 0 mentions | Omit theme; do not say “fit is excellent” | P0 | 4 |
| RV-04 | Theme both positive and negative | Keep both counts; mixed; confidence MEDIUM/LOW if conflict | P0 | 4 |
| RV-05 | `rebuild_insights` invents a spec not in reviews (e.g. “silk” when text says viscose) | Fail eval; do not write that summary | P0 | 4 |
| RV-06 | Online question re-sends all raw reviews to Groq | Forbidden; use `review_insights` + optional 1–3 `evidence_review_ids` | P0 | 4 |
| RV-07 | Wishlist render runs review LLM | Forbidden | P0 | 4 |
| RV-08 | Sentiment-only “82% positive” as the only insight | Insufficient; themes required when reviews exist | P1 | 4 |
| RV-09 | Quote id not in pack | UI must not show that quote | P0 | 4 |
| RV-10 | Conflicting catalog material vs reviews | Surface conflict; do not silently pick one | P1 | 4 |

---

## 7. Comparison and recommendation

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| CMP-01 | Three products: cheap C, best-reviewed B, balanced A | Labels from **engine**, not Groq. Groq must not relabel | P0 | 3–4 |
| CMP-02 | Tie on price | Deterministic tie-break (e.g. higher rating, then id); document it | P1 | 3 |
| CMP-03 | Groq “definitely the best” | Forbidden; conditional “best match based on your stated preference…” | P0 | 4 |
| CMP-04 | BEST MATCH vs BEST VALUE disagree | Both shown; trade-off explained | P0 | 4 |
| CMP-05 | Compare with one product missing insights | Table still numbers; `missing[]`; explanation mentions gaps | P1 | 3–4 |
| CMP-06 | `WHICH_ONE_SHOULD_I_BUY` with 1 id | 400 or treat as worth-the-price; do not rank a set of one as a winner fight | P1 | 4 |
| CMP-07 | `WHY_BETTER_THAN_B` but B not selected / not on Wishlist | 400 | P1 | 4 |
| CMP-08 | Unexplained winner with no why/trade-off | Fail; engine always has reasons from scores | P0 | 3–4 |

---

## 8. Ask Me a Question

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| Q-01 | Free-text prompt from client | 400; only registry `question_id` | P0 | 4 |
| Q-02 | Unknown `question_id` | 400 | P0 | 4 |
| Q-03 | `IS_FIT_RELIABLE` with no FIT/SIZE themes and no fit attribute | Fallback; no “fit is excellent” | P0 | 4 |
| Q-04 | `BETTER_OPTION_IN_WISHLIST` with one item | No closely matching products / not enough to compare | P1 | 4 |
| Q-05 | `BETTER_OPTION_IN_WISHLIST` when peers exist | Use similarity + scores; explainable reason | P1 | 4 |
| Q-06 | Empty pack | **No Groq call** | P0 | 4 |
| Q-07 | Pack only `missing[]` | No Groq **or** Groq only to restate unavailability — prefer **no Groq** | P0 | 4 |
| Q-08 | Answer mixes interpretation as fact | Fail grounding eval | P0 | 4 |
| Q-09 | Confidence as “97%” | Forbidden; HIGH/MEDIUM/LOW from engine | P0 | 4 |
| Q-10 | Question for product not on Wishlist | 400. Questions are Wishlist-only in MVP | P1 | 4 |
| Q-11 | Double-submit question | Idempotent UX; don’t spam Groq (disable button while loading) | P1 | 4, 6 |

---

## 9. Groq / LlmClient

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| AI-01 | Missing `GROQ_API_KEY` | Shopping + Phase 3 numbers work; insight fallback | P0 | 0, 4 |
| AI-02 | 429 rate limit | Retry once, then fallback; do not invent | P0 | 4 |
| AI-03 | Timeout / 5xx | Fallback | P0 | 4 |
| AI-04 | Malformed JSON from model | Parse fail → fallback; do not show raw dump | P0 | 4 |
| AI-05 | Model invents a price | Validator reject | P0 | 4 |
| AI-06 | Groq called from browser | Forbidden | P0 | 4 |
| AI-07 | Groq SDK used outside `LlmClient` | Forbidden | P1 | 4 |
| AI-08 | Offline insights job fails mid-catalog | Products without insights stay empty; others OK; no fake themes | P1 | 4 |
| AI-09 | Wishlist GET Groq count > 0 | P0 regression | P0 | 4–6 |
| AI-10 | Hard-coded “Product A is best” | Forbidden except test fixtures labeled as such | P0 | 4 |

---

## 10. Similarity, overload, alerts

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| SM-01 | No edges above threshold | “No closely matching products found.” | P1 | 3, 5 |
| SM-02 | Similar alert for item already on Wishlist | Prefer **catalog** neighbor not on Wishlist; if only Wishlist peers, use overload/compare not “new similar found” | P1 | 5 |
| SM-03 | Similar alert without `reason` | Must have stored reason | P1 | 5 |
| OV-01 | 2 similar dresses | No overload (threshold **3**) | P0 | 5 |
| OV-02 | 3 similar dresses | Overload prompt; Compare preselects that group | P0 | 5 |
| OV-03 | 5 dresses + 3 sneakers | Two groups possible; prompt the group(s) ≥ 3; don’t mix dresses+sneakers | P0 | 5 |
| OV-04 | 5 unrelated categories, 1 each | No overload | P1 | 5 |
| OV-05 | Dismiss overload | Persists; no loop every load unless new add crosses threshold again (document: dismissed until new similar add) | P1 | 5 |
| AL-01 | Drop of at least ₹1 vs `saved_price` | Create PRICE_DROP once (`current <= saved - 1`) | P0 | 5 |
| AL-02 | Drop then scan twice | **One** undismissed PRICE_DROP per user+product | P0 | 5 |
| AL-03 | Price rises after drop alert | Do not keep claiming current drop if no longer true (dismiss or expire on scan) | P1 | 5 |
| AL-04 | Tiny drop under threshold | No alert | P1 | 5 |
| AL-05 | Dismiss then refresh | Stays dismissed | P0 | 5 |
| AL-06 | Alert copy predicts future price | Forbidden | P0 | 5 |
| AL-07 | `simulate_price_drop` | Wishlist shows correct from/to/save_amount | P0 | 5 |
| AL-08 | Alerts page | Must not exist | P0 | 5 |

---

## 11. Decision Engine / confidence

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| DE-01 | High rating_count + consistent themes + complete attrs | HIGH | P1 | 3 |
| DE-02 | Few reviews or conflict | MEDIUM or LOW | P0 | 3 |
| DE-03 | Missing attrs + few reviews | LOW; `missing[]` populated | P0 | 3 |
| DE-04 | Engine asks Groq for discount | Forbidden | P0 | 3 |
| DE-05 | Empty pack still calls Groq | Forbidden | P0 | 4 |

---

## 12. Security and privacy

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| SEC-01 | `GROQ_API_KEY` in frontend bundle | Forbidden | P0 | 0+ |
| SEC-02 | `.env` committed | Forbidden | P0 | 0 |
| SEC-03 | Arbitrary user_id creating other users’ Wishlist (when only U001) | Ignore / 403 unknown users | P1 | 1 |
| SEC-04 | Logs contain full profile + reviews dump | Don’t log sensitive blobs; log question_id, product_id, latency | P2 | 4 |
| SEC-05 | SQL injection via product_id | Parameterized queries | P0 | 1 |
| SEC-06 | Prompt injection via review text in pack | Model still cannot emit new prices; validator on numbers | P1 | 4 |

---

## 13. UI / polish

| ID | Case | Expected | Sev | Phase |
|---|---|---|---|---|
| UI-01 | Slow Groq on compare | Loading on explanation only; table visible first | P1 | 4, 6 |
| UI-02 | Image 404 | Placeholder; layout holds | P2 | 1, 6 |
| UI-03 | Toast on Wishlist add | Shown (Phase 1) | P2 | 1 |
| UI-04 | Mock checkout with empty Bag | Blocked | P1 | 6 |
| UI-05 | Backend down | Frontend error state; no fake catalog | P1 | 6 |

---

## 14. Cross-cutting invariants (always true)

1. Missing data stays missing.  
2. Interpretation is never presented as catalog fact.  
3. Groq does not run on Wishlist GET.  
4. No Decision Studio (or sibling) page.  
5. Deterministic labels beat model prose.  
6. Shopping works when Groq is dead.  
7. Frontend never scrapes, never reads `raw/`, never holds the Groq key.

Use these IDs in tests (`EC-WL-08`, `EC-AI-09`, …).
