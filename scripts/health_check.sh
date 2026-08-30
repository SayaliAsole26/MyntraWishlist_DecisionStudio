#!/usr/bin/env bash
# Pre-deploy / CI health smoke test. Exit 0 only when /health returns status ok.
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
echo "Checking ${BASE_URL}/health ..."

body="$(curl -sf "${BASE_URL}/health")"
echo "$body"

echo "$body" | python -c "
import json, sys
data = json.load(sys.stdin)
assert data.get('status') == 'ok', data
assert data.get('catalog_ready') is True, data
assert data.get('product_count', 0) > 0, data
print('Health OK — catalog ready with', data['product_count'], 'products')
"

echo "Checking ${BASE_URL}/api/products/categories/list ..."
count="$(curl -sf "${BASE_URL}/api/products/categories/list" | python -c "import json,sys; print(len(json.load(sys.stdin)))")"
echo "Categories: ${count}"
test "${count}" -gt 0

echo "All checks passed."
