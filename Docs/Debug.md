# Debug Reference — Myntra Wishlist Decision Studio

Chronological log of issues encountered during build and demo, with symptoms, root causes, fixes, and how to verify. Use this as a runbook when something breaks locally.

---

## Quick recovery (most common)

```powershell
# From project root
.\scripts\start_dev.ps1
```

Or manually:

```powershell
cd c:\Users\AKASH\MyntraWishlist_DecisionStudio
python -c "from backend.db.init_db import init_database; init_database()"
python -m offline.ingest_catalog
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8002

# Second terminal
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173** (or `localhost:5173`) and hard-refresh (**Ctrl+Shift+R**).

| Check | Expected |
|-------|----------|
| `http://127.0.0.1:8002/health` | `{"status":"ok","phase":6,...}` |
| `http://127.0.0.1:5173/api/products` | 62 products |
| Home page | Categories + featured grid (no HTTP 500) |

**Do not run `pytest` while the dev server is using `backend/app.db`** — tests delete/recreate the DB and can cause HTTP 500 until re-init.

---

## Current dev setup (after all fixes)

| Service | URL | Notes |
|---------|-----|--------|
| Backend | `http://127.0.0.1:8002` | FastAPI + SQLite |
| Frontend | `http://127.0.0.1:5173` | Vite dev server |
| API from browser | Same origin `/api/*` | Proxied to 8002 via `frontend/vite.config.js` |
| `frontend/.env` | `VITE_API_URL=` (empty) | Empty = use proxy, avoid CORS/port mismatch |

---

## Debug log (start → end)

### 1. “Failed to fetch” on Home / Wishlist

| | |
|---|---|
| **Symptom** | Red error banner; network tab shows failed API calls |
| **Root cause** | Port conflict — another app on **8000** / stale process on **8001**; frontend pointed at wrong backend |
| **Fix** | Standardized on **port 8002**; Vite proxy for `/api` and `/health`; `VITE_API_URL=` empty in `frontend/.env` |
| **Files** | `frontend/vite.config.js`, `frontend/.env`, `frontend/src/api/client.js`, `scripts/start_dev.ps1` |
| **Verify** | `Invoke-RestMethod http://127.0.0.1:5173/api/products` returns product list |

---

### 2. “Method Not Allowed” (405) on Narrow them down / shortlist

| | |
|---|---|
| **Symptom** | POST to shortlist returns 405; compare/shortlist broken |
| **Root cause** | Ghost backend on 8001 without `/shortlist` route; request matched `DELETE /api/wishlist/{product_id}` with `product_id="shortlist"` |
| **Fix** | Fresh server on **8002**; delete route restricted with `Path(..., pattern=r"^P\d+$")` |
| **Files** | `backend/api/routes/wishlist.py` |
| **Verify** | `POST /api/wishlist/shortlist` with valid body → 200 |

---

### 3. Blank white page at localhost:5173

| | |
|---|---|
| **Symptom** | Empty white screen; no UI |
| **Root cause A** | `ProductCard.jsx` referenced undefined `wishlistIds` → React crash |
| **Root cause B** | Vite bound to IPv6 `[::1]:5173` only; some browsers hit `127.0.0.1` inconsistently |
| **Fix A** | Use `inWishlist` prop in `WishlistHeart` |
| **Fix B** | `server.host: "127.0.0.1"` in Vite config; `ErrorBoundary` in `main.jsx` |
| **Files** | `frontend/src/components/ProductCard.jsx`, `frontend/vite.config.js`, `frontend/src/main.jsx`, `frontend/src/components/ErrorBoundary.jsx` |
| **Verify** | Home renders header + hero; console has no `wishlistIds is not defined` |

---

### 4. HTTP 500 on Home (“HTTP 500” in error banner)

| | |
|---|---|
| **Symptom** | Home fails loading categories/products |
| **Root cause** | `sqlite3.OperationalError: no such table: products` — DB wiped (often by pytest) while uvicorn still running |
| **Fix** | Re-run `init_database()` + `ingest_catalog`; added `ensure_catalog_ready()` on product routes |
| **Files** | `backend/db/init_db.py`, `backend/api/routes/products.py` |
| **Verify** | `GET /api/products/categories/list` → 12 categories |

---

### 5. Missing catalog / empty products

| | |
|---|---|
| **Symptom** | “Catalog not loaded yet” or 500 on `/api/products` |
| **Root cause** | Empty or incomplete `backend/app.db` |
| **Fix** | `python -m offline.ingest_catalog` (62 products) |
| **Verify** | `SELECT COUNT(*) FROM products` → 62 |

---

### 6. Product images broken / wrong category photos

| | |
|---|---|
| **Symptom** | Broken image icons; dress showing sneaker photo |
| **Root cause** | Truncated Unsplash IDs in seed generator; dead 404 URLs |
| **Fix** | `scripts/product_images.py` per-product URLs; verified HTTP 200; regenerated `data/products.json` |
| **Files** | `data/products.json`, `scripts/generate_seed_data.py`, `scripts/product_images.py` |
| **Verify** | All 62 `image_url` values return 200 |

---

### 7. CSS regression on PDP (layout broken)

| | |
|---|---|
| **Symptom** | Product detail page grid/image styling wrong |
| **Root cause** | Merge conflict left duplicate/incomplete `.pdp-grid` / `.pdp-image` rules |
| **Fix** | Restored `.pdp-image` block in `app.css` |
| **Files** | `frontend/src/styles/app.css` |

---

### 8. Size buttons not working on PDP

| | |
|---|---|
| **Symptom** | Size chips not selectable / no size info |
| **Root cause** | Missing click handlers and size guide wiring |
| **Fix** | Clickable size chips + `frontend/src/lib/sizeGuide.js` measurement copy |
| **Files** | `frontend/src/pages/ProductDetail.jsx`, `frontend/src/lib/sizeGuide.js` |

---

### 9. Wishlist add flow — size then occasion

| | |
|---|---|
| **Symptom** | Needed choose-size-first, then occasion |
| **Root cause** | Flow only had occasion step |
| **Fix** | `useWishlistAdd` steps: `size` → `occasion`; modals; `size` column on `wishlist_items` |
| **Files** | `frontend/src/hooks/useWishlistAdd.js`, `WishlistSizeModal.jsx`, `WishlistAddModals.jsx`, `backend/db/init_db.py`, wishlist repo/API |

---

### 10. Overload modal showing too early / narrow-down behavior

| | |
|---|---|
| **Symptom** | Modal at 3–5 items; narrow-down didn’t open compare like manual pick |
| **Root cause** | Threshold too low; narrow-down not wired to shortlist + compare drawer |
| **Fix** | `OVERLOAD_THRESHOLD = 6` (>5 items); `narrowDown()` calls shortlist API, selects top 3, opens compare |
| **Files** | `backend/decision/overload.py`, `frontend/pages/Wishlist.jsx`, `DecisionOverloadModal.jsx` |

---

### 11. Decision Studio — need / priority not changing top pick

| | |
|---|---|
| **Symptom** | Party need still picks sneakers (e.g. Adidas Galaxy 6) instead of heels/party dress |
| **Root cause A** | Seed data tagged almost everything `Casual, Office` — even “Sequin Party Dress” and “Block Heel Sandals” |
| **Root cause B** | Need fit only 15% weight; sneakers won on ratings when all need_fit = 0 |
| **Root cause C** | Compare explanation pack rebuilt without need/tradeoff context |
| **Fix A** | `infer_occasions()` from category/subcategory/name; patched all 62 products in `data/products.json` |
| **Fix B** | Need-first top pick (exclude zero-fit items when better matches exist); 40% need weight |
| **Fix C** | Pass `need` / `tradeoff_priority` through `load_context` → `build_compare_pack` |
| **Files** | `backend/decision/tradeoff.py`, `comparison_scores.py`, `evidence_pack.py`, `compare_service.py`, `explain_service.py` |
| **Verify** | Compare P005 + P057 + P058 with `need: Party` → top pick P057 or P058, not P005 |

---

### 12. Decision Studio — step numbers out of sequence

| | |
|---|---|
| **Symptom** | Steps labeled 01, 03, 05 |
| **Root cause** | Placeholder numbers from original spec |
| **Fix** | Renumbered to **01, 02, 03** in `DecisionStudioSetup.jsx` |

---

### 13. “Decision insight temporarily unavailable” in Decision Studio

| | |
|---|---|
| **Symptom** | Generic unavailable message inside Decision Studio (confusing — app *is* the studio) |
| **Root cause** | Groq LLM fallback string shown when API key missing or empty LLM response |
| **Fix** | Deterministic `_fallback_compare_explanation()`; moved summary + label chips under **Decision insight**; hide generic unavailable text; product names instead of P00x IDs |
| **Files** | `backend/services/explain_service.py`, `frontend/src/pages/DecisionStudio.jsx`, `backend/llm/prompts/compare_explain.txt` |

---

### 14. Decision Studio analysis not refreshing on option change

| | |
|---|---|
| **Symptom** | Changing need/trade-off/confidence didn’t reload compare |
| **Root cause** | `loadCompare` deps missing `context.confidence`; stale closure |
| **Fix** | Added `context.confidence` to `useCallback` deps; pass `user_confidence` in compare API body |
| **Files** | `frontend/src/pages/DecisionStudio.jsx`, `frontend/src/lib/decisionContext.js`, `backend/models.py` |

---

### 15. Port / process hygiene

| | |
|---|---|
| **Symptom** | Random API behavior after many restarts |
| **Root cause** | Multiple uvicorn/node processes on 8000/8001/8002/5173 |
| **Fix** | Use `scripts/start_dev.ps1`; prefer **8002** + **5173** only |
| **Tip** | `netstat -ano | findstr ":8002.*LISTENING"` to see listeners |

---

### 16. pytest vs dev server DB lock

| | |
|---|---|
| **Symptom** | Teardown errors; dev server 500 after tests |
| **Root cause** | Tests `unlink` `app.db` while server holds connection |
| **Fix** | Stop dev server before pytest, or re-run `init_database()` after tests |
| **Files** | `backend/tests/*` fixtures |

---

## Key files reference

| Area | Path |
|------|------|
| Dev startup | `scripts/start_dev.ps1` |
| DB init + auto-recovery | `backend/db/init_db.py` |
| Catalog ingest | `offline/ingest_catalog.py` |
| Vite proxy | `frontend/vite.config.js` |
| API client | `frontend/src/api/client.js` |
| Need / trade-off scoring | `backend/decision/tradeoff.py`, `comparison_scores.py` |
| Compare API | `backend/api/routes/wishlist.py`, `backend/services/compare_service.py` |
| Decision Studio UI | `frontend/src/pages/DecisionStudio.jsx` |
| Product occasions (data) | `data/products.json` |
| Occasion inference (code) | `backend/decision/tradeoff.py` → `infer_occasions()` |

---

## API smoke tests (PowerShell)

```powershell
$h = @{ "X-User-Id" = "U001"; "Content-Type" = "application/json" }

# Health
Invoke-RestMethod http://127.0.0.1:8002/health

# Catalog
(Invoke-RestMethod http://127.0.0.1:5173/api/products).products.Count   # 62

# Compare with need (after adding items to wishlist)
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8002/api/wishlist/compare -Headers $h -Body (
  '{"product_ids":["P005","P057","P058"],"need":"Party","tradeoff_priority":"FIT"}'
) | Select-Object -ExpandProperty labels
```

---

## Decision Studio — expected need behavior (post-fix)

| Need | Sneakers (P005) | Block Heel Sandals (P057) | Sequin Party Dress (P058) |
|------|-----------------|----------------------------|---------------------------|
| Party | Poor fit | Strong fit | Strong fit |
| Sports | Strong fit | Poor fit | Poor fit |
| Workwear | Partial | Partial | Partial |

Top pick should come from the **strong-fit pool** when one exists, then rank by trade-off priority within that pool.

---

## Related tests

```powershell
python -m pytest backend/tests/test_shortlist.py -q
python -m pytest backend/tests/test_phase3.py -q
```

Includes: shortlist API, compare with tradeoff, party need prefers heels over sneakers, workwear vs sports top-pick swap.

---

## Related docs

- [StepWiseWorking.md](./StepWiseWorking.md) — frontend flows
- [DeploymentPlan.md](./DeploymentPlan.md) — Railway + Vercel deploy
- [RailwayDeploy.md](./RailwayDeploy.md) — backend quick reference

---

*Last updated: session covering Decision Studio BUILD, wishlist flow, overload, and local dev stabilization (port 8002, Vite proxy, catalog recovery).*
