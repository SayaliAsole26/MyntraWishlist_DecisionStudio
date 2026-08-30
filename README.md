# Myntra Wishlist Decision Studio

Myntra-like shopping MVP. Wishlist is the decision workspace — there is **no** Decision Studio page.

Reference storefront (inspiration only): https://www.myntra.com/

## Quick start (demo script)

From the project root:

```powershell
# Windows
.\scripts\demo_setup.ps1
```

```bash
# macOS / Linux
bash scripts/demo_setup.sh
```

This runs, in order:

1. `ingest_catalog`
2. `rebuild_price_stats` + `rebuild_similarity`
3. `rebuild_insights` (Groq FAST when `GROQ_API_KEY` is set)
4. Optional `simulate_price_drop` (if P002 is on Wishlist)

Then start the app:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

cd frontend && npm install && npm run dev
```

- API: http://127.0.0.1:8000/health  
- App: http://localhost:5173  

Demo user: **U001** (no auth). Set `GROQ_API_KEY` in `.env` for live Decision insight copy.

## Primary demo story (inside Wishlist)

1. Browse → open a PDP → add to Wishlist  
2. Save 3 similar dresses (P001, P002, P003) → overload prompt → Compare  
3. Read Decision insight → Ask “Which one should I buy?”  
4. Run `python -m offline.simulate_price_drop P002 999` → price-drop alert  
5. Add chosen item to Bag → **Place order** → confirmation  

Walk the story twice: with Groq on, and with `GROQ_API_KEY` removed (numbers + fallbacks still work).

## Phase summary

| Phase | What shipped |
|---|---|
| 0 | Scaffold, health, SQLite |
| 1 | Home → PDP → Wishlist → Bag → Profile |
| 2 | Seed ingest, catalog in SQLite |
| 3 | Decision signals, compare, price/review insights (no Groq on Wishlist GET) |
| 4 | Groq review themes + Ask a Question + compare explanations |
| 5 | Price-drop, similar-product, overload alerts on Wishlist |
| 6 | Mock checkout, empty/error/loading states, demo script, Groq usage logs |

## Offline jobs

| Command | Purpose |
|---|---|
| `python -m offline.ingest_catalog` | Seed JSON → raw snapshot → SQLite |
| `python -m offline.rebuild_price_stats` | Price history → `price_stats` |
| `python -m offline.rebuild_similarity` | Attribute similarity graph |
| `python -m offline.rebuild_insights` | Review themes (Groq or deterministic) |
| `python -m offline.scan_price_alerts` | Scan wishlist for price drops |
| `python -m offline.simulate_price_drop P002 999` | Demo price drop + alert |

## API (MVP)

| Method | Path |
|---|---|
| GET | `/health` |
| GET/POST/DELETE | `/api/wishlist`, `/api/bag` |
| POST | `/api/wishlist/compare`, `/api/questions/answer`, `/api/checkout` |
| PATCH | `/api/alerts/{id}/dismiss` |
| GET | `/api/products`, `/api/products/{id}/price-insight`, `/api/products/{id}/review-insight` |
| GET/PATCH | `/api/profile` |

**Wishlist GET includes alerts and overload — zero Groq calls.** Groq usage is logged as `groq.usage` (endpoint, model, tokens) for compare and Q&A only.

## Seed data

| File | Purpose |
|---|---|
| `data/products.json` | 62 products, similar groups |
| `data/reviews.json` | Reviews on 14 products |
| `data/price-history.json` | Price points for 17 products |
| `data/users.json` | Demo user U001 |

Regenerate (optional): `python scripts/generate_seed_data.py`

## Tests

```bash
pytest backend/tests -q
```

## Docs

Start with `Docs/Doc_Alignment.md`, then `Docs/Phase_wise_Implementation.md`.
