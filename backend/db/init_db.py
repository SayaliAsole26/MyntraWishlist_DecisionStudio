"""Apply schema, ingest catalog, and rebuild derived stats when empty."""

import sqlite3
from pathlib import Path

from backend.db.session import get_connection

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _ensure_derived_stats(conn) -> None:
    stats_count = conn.execute("SELECT COUNT(*) FROM price_stats").fetchone()[0]
    sim_count = conn.execute("SELECT COUNT(*) FROM product_similarity").fetchone()[0]
    insights_count = conn.execute("SELECT COUNT(*) FROM review_insights").fetchone()[0]
    product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    review_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]

    if product_count == 0:
        return
    if stats_count == 0:
        from offline.rebuild_price_stats import rebuild_price_stats

        rebuild_price_stats(conn)
    if sim_count == 0:
        from offline.rebuild_similarity import rebuild_similarity

        rebuild_similarity(conn)
    if insights_count == 0 and review_count > 0:
        from offline.rebuild_insights import rebuild_insights

        rebuild_insights(conn, use_groq=False)


def _migrate_schema(conn) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(wishlist_items)").fetchall()}
    if "occasion" not in cols:
        conn.execute("ALTER TABLE wishlist_items ADD COLUMN occasion TEXT DEFAULT 'General'")
        conn.commit()
    if "size" not in cols:
        conn.execute("ALTER TABLE wishlist_items ADD COLUMN size TEXT")
        conn.commit()


def init_database() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
        _migrate_schema(conn)

        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            from offline.ingestion.pipeline import ingest_catalog

            ingest_catalog()

        _ensure_derived_stats(conn)
    finally:
        conn.close()


def ensure_catalog_ready() -> None:
    """Recover if app.db was wiped while the server is still running (e.g. during pytest)."""
    conn = get_connection()
    recreate = False
    try:
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            from offline.ingestion.pipeline import ingest_catalog

            ingest_catalog()
            _ensure_derived_stats(conn)
    except sqlite3.OperationalError:
        recreate = True
    finally:
        conn.close()
    if recreate:
        init_database()
