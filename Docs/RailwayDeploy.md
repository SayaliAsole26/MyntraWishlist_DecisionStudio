# Railway deployment — backend (quick reference)

Full step-by-step plan (Railway + Vercel): **[DeploymentPlan.md](./DeploymentPlan.md)**

## Quick start

1. Connect GitHub repo to Railway (project root)
2. Set variables: `CORS_ORIGINS`, optional `GROQ_API_KEY`, optional `DATABASE_PATH`
3. Generate public domain → verify `GET /health` returns `"status": "ok"`
4. Deploy frontend on Vercel with `VITE_API_URL=<railway-url>` (see DeploymentPlan Phase 2–3)

## Pre-deploy

```powershell
python -m pytest backend/tests/ -q
python -c "from backend.db.init_db import init_database; init_database()"
.\scripts\health_check.ps1 -BaseUrl http://127.0.0.1:8002
```

## Expected `/health`

```json
{
  "status": "ok",
  "phase": 6,
  "catalog_ready": true,
  "product_count": 62,
  "schema_ok": true
}
```

## Railway variables

| Variable | Required | Example |
|----------|----------|---------|
| `CORS_ORIGINS` | Yes (prod) | `https://your-app.vercel.app,http://localhost:5173` |
| `GROQ_API_KEY` | No | Groq console key |
| `DATABASE_PATH` | No | `/data/app.db` with Railway volume |

## Files

| File | Purpose |
|------|---------|
| `Procfile` | Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| `railway.toml` | Health check `/health`, 120s timeout |
| `requirements.txt` | Python dependencies |

## Troubleshooting

See [Debug.md](./Debug.md) and [DeploymentPlan.md](./DeploymentPlan.md).
