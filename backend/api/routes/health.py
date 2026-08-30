from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.db.init_db import ensure_catalog_ready
from backend.db.session import DB_PATH, get_connection

router = APIRouter()


def _catalog_status() -> dict:
    conn = get_connection()
    try:
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    required = {"products", "wishlist_items", "bag_items", "reviews"}
    schema_ok = required.issubset(tables)
    catalog_ready = schema_ok and product_count > 0
    return {
        "schema_ok": schema_ok,
        "catalog_ready": catalog_ready,
        "product_count": product_count,
        "tables_present": sorted(tables & required),
    }


@router.get("/health")
def health():
    """Liveness + readiness for Railway. Returns 503 until catalog is loaded."""
    try:
        status = _catalog_status()
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "phase": 6,
                "detail": str(exc),
                "db_path": str(DB_PATH),
            },
        )

    if not status["catalog_ready"]:
        ensure_catalog_ready()
        try:
            status = _catalog_status()
        except Exception as exc:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "phase": 6,
                    "detail": str(exc),
                    "db_path": str(DB_PATH),
                },
            )

    if not status["catalog_ready"]:
        return JSONResponse(
            status_code=503,
            content={
                "status": "starting",
                "phase": 6,
                "catalog_ready": False,
                "product_count": status["product_count"],
                "db_path": str(DB_PATH),
            },
        )

    return {
        "status": "ok",
        "phase": 6,
        "catalog_ready": True,
        "product_count": status["product_count"],
        "schema_ok": status["schema_ok"],
        "db_path": str(DB_PATH),
    }
