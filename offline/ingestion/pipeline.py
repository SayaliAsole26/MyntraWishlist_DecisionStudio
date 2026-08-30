"""Seed JSON → raw snapshot → normalize → validate → SQLite UPSERT."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from backend.config import ROOT_DIR
from backend.db.session import DB_PATH, get_connection
from offline.ingestion.normalize import (
    normalize_price_point,
    normalize_product,
    normalize_review,
    normalize_user,
)
from offline.ingestion.sources.seed_file_source import SeedFileSource
from offline.ingestion.validate import (
    validate_price_history,
    validate_products,
    validate_reviews,
    validate_users,
)

RAW_DIR = ROOT_DIR / "raw"
SCHEMA_PATH = ROOT_DIR / "backend" / "db" / "schema.sql"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _batch_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def snapshot_raw(bundle, batch_id: str) -> Path:
    batch_dir = RAW_DIR / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    (batch_dir / "products.json").write_text(
        json.dumps(bundle.products, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (batch_dir / "reviews.json").write_text(
        json.dumps(bundle.reviews, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (batch_dir / "price-history.json").write_text(
        json.dumps(bundle.price_history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (batch_dir / "users.json").write_text(
        json.dumps(bundle.users, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    manifest = {
        "batch_id": batch_id,
        "source": "SeedFileSource",
        "timestamp": _now_iso(),
        "counts": {
            "products": len(bundle.products),
            "reviews": len(bundle.reviews),
            "price_history": len(bundle.price_history),
            "users": len(bundle.users),
        },
    }
    (batch_dir / "_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return batch_dir


def upsert_catalog(
    conn: sqlite3.Connection,
    products: list[dict],
    reviews: list[dict],
    price_history: list[dict],
    users: list[dict],
    batch_id: str,
) -> dict:
    now = _now_iso()
    counts = {"products": 0, "reviews": 0, "price_history": 0, "users": 0}

    for raw in products:
        p = normalize_product(raw, batch_id)
        conn.execute(
            """
            INSERT INTO products (
                product_id, brand, name, gender, category, subcategory, style,
                price, mrp, discount, rating, rating_count, image_url, product_url,
                sizes, colors, fit, material, occasions, attributes_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                brand = excluded.brand,
                name = excluded.name,
                gender = excluded.gender,
                category = excluded.category,
                subcategory = excluded.subcategory,
                style = excluded.style,
                price = excluded.price,
                mrp = excluded.mrp,
                discount = excluded.discount,
                rating = excluded.rating,
                rating_count = excluded.rating_count,
                image_url = excluded.image_url,
                product_url = excluded.product_url,
                sizes = excluded.sizes,
                colors = excluded.colors,
                fit = excluded.fit,
                material = excluded.material,
                occasions = excluded.occasions,
                attributes_json = excluded.attributes_json,
                updated_at = excluded.updated_at
            """,
            (
                p["product_id"],
                p["brand"],
                p["name"],
                p["gender"],
                p["category"],
                p["subcategory"],
                p["style"],
                p["price"],
                p["mrp"],
                p["discount"],
                p["rating"],
                p["rating_count"],
                p["image_url"],
                p["product_url"],
                p["sizes"],
                p["colors"],
                p["fit"],
                p["material"],
                p["occasions"],
                p["attributes_json"],
                now,
            ),
        )
        counts["products"] += 1

    for raw in reviews:
        r = normalize_review(raw, batch_id)
        conn.execute(
            """
            INSERT INTO reviews (
                review_id, product_id, rating, review_text, review_date, source_batch_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(review_id) DO UPDATE SET
                product_id = excluded.product_id,
                rating = excluded.rating,
                review_text = excluded.review_text,
                review_date = excluded.review_date,
                source_batch_id = excluded.source_batch_id
            """,
            (
                r["review_id"],
                r["product_id"],
                r["rating"],
                r["review_text"],
                r["review_date"],
                r["source_batch_id"],
            ),
        )
        counts["reviews"] += 1

    for raw in price_history:
        pt = normalize_price_point(raw, batch_id)
        conn.execute(
            """
            INSERT INTO price_history (product_id, date, price)
            VALUES (?, ?, ?)
            ON CONFLICT(product_id, date) DO UPDATE SET
                price = excluded.price
            """,
            (pt["product_id"], pt["date"], pt["price"]),
        )
        counts["price_history"] += 1

    for raw in users:
        u = normalize_user(raw)
        existing = conn.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (u["user_id"],)
        ).fetchone()
        if existing:
            continue
        conn.execute(
            """
            INSERT INTO users (
                user_id, display_name, size, price_min, price_max,
                occasions, priorities, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                u["user_id"],
                u["display_name"],
                u["size"],
                u["price_min"],
                u["price_max"],
                u["occasions"],
                u["priorities"],
                now,
            ),
        )
        counts["users"] += 1

    conn.commit()
    return counts


def ingest_catalog(data_dir: Path | None = None, db_path: Path | None = None) -> dict:
    """Run full ingest: load seed, snapshot raw, validate, UPSERT."""
    source = SeedFileSource(data_dir=data_dir)
    bundle = source.load()

    product_ids = {str(p["product_id"]).strip() for p in bundle.products}
    validate_products(bundle.products)
    validate_reviews(bundle.reviews, product_ids)
    validate_price_history(bundle.price_history, product_ids)
    validate_users(bundle.users)

    batch_id = _batch_id()
    batch_dir = snapshot_raw(bundle, batch_id)

    if db_path and db_path != DB_PATH:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
    else:
        conn = get_connection()

    try:
        ensure_schema(conn)
        counts = upsert_catalog(
            conn,
            bundle.products,
            bundle.reviews,
            bundle.price_history,
            bundle.users,
            batch_id,
        )
    finally:
        conn.close()

    return {
        "batch_id": batch_id,
        "raw_snapshot": str(batch_dir),
        "db_path": str(db_path or DB_PATH),
        "counts": counts,
    }
