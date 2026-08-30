# Start backend + frontend for local dev.
# Run from project root: .\scripts\start_dev.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "Initializing database..."
python -c "from backend.db.init_db import init_database; init_database(); print('Database ready')"

Write-Host ""
Write-Host "Starting backend on http://127.0.0.1:8002 ..."
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$PWD'; python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8002"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173 ..."
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$PWD\frontend'; npm run dev"
)

Write-Host ""
Write-Host "Open http://localhost:5173 in your browser."
Write-Host "Backend API: http://127.0.0.1:8002/health"
