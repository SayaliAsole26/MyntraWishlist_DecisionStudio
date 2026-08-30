# Demo setup — ingest, derived stats, optional insights and price drop.
# Run from project root: .\scripts\demo_setup.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "1/4 ingest_catalog"
python -m offline.ingest_catalog

Write-Host "2/4 rebuild price_stats + similarity"
python -m offline.rebuild_price_stats
python -m offline.rebuild_similarity

Write-Host "3/4 rebuild_insights (Groq if GROQ_API_KEY set, else deterministic)"
python -m offline.rebuild_insights

Write-Host "4/4 optional price-drop demo (P002 -> 999 if on wishlist)"
python -m offline.simulate_price_drop P002 999 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  (skipped simulate_price_drop — add P002 to Wishlist first for alert demo)"
}

Write-Host ""
Write-Host "Demo data ready. Start servers:"
Write-Host "  uvicorn backend.main:app --reload --host 127.0.0.1 --port 8002"
Write-Host "  cd frontend; npm run dev"
