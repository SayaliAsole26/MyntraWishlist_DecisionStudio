#!/usr/bin/env bash
# Demo setup — ingest, derived stats, optional insights and price drop.
# Run from project root: bash scripts/demo_setup.sh

set -euo pipefail
cd "$(dirname "$0")/.."

echo "1/4 ingest_catalog"
python -m offline.ingest_catalog

echo "2/4 rebuild price_stats + similarity"
python -m offline.rebuild_price_stats
python -m offline.rebuild_similarity

echo "3/4 rebuild_insights (Groq if GROQ_API_KEY set, else deterministic)"
python -m offline.rebuild_insights

echo "4/4 optional price-drop demo (P002 -> 999 if on wishlist)"
python -m offline.simulate_price_drop P002 999 || echo "  (skipped — add P002 to Wishlist first for alert demo)"

echo ""
echo "Demo data ready. Start servers:"
echo "  uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
echo "  cd frontend && npm run dev"
