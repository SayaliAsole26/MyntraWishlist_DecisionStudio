"""Aggregate price_history → price_stats. Deterministic, no LLM."""

import sqlite3
from datetime import datetime, timezone

from backend.db.session import get_connection
from backend.db.schema import ensure_schema


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rebuild_price_stats(conn: sqlite3.Connection | None = None) -> dict:
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
        ensure_schema(conn)

    now = _now_iso()
    products = conn.execute(
        "SELECT product_id, price FROM products ORDER BY product_id"
    ).fetchall()
    count = 0

    for p in products:
        pid = p["product_id"]
        history = conn.execute(
            """
            SELECT date, price FROM price_history
            WHERE product_id = ?
            ORDER BY date
            """,
            (pid,),
        ).fetchall()

        current_price = int(p["price"])
        if history:
            prices = [int(h["price"]) for h in history]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            min_date = history[prices.index(min_price)]["date"]
            if max_price > min_price:
                relative_position = (current_price - min_price) / (max_price - min_price)
            else:
                relative_position = None
        else:
            min_price = current_price
            max_price = current_price
            avg_price = float(current_price)
            min_date = None
            relative_position = None

        conn.execute(
            """
            INSERT INTO price_stats (
                product_id, current_price, min_price, max_price, avg_price,
                min_date, relative_position, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                current_price = excluded.current_price,
                min_price = excluded.min_price,
                max_price = excluded.max_price,
                avg_price = excluded.avg_price,
                min_date = excluded.min_date,
                relative_position = excluded.relative_position,
                updated_at = excluded.updated_at
            """,
            (
                pid,
                current_price,
                min_price,
                max_price,
                avg_price,
                min_date,
                relative_position,
                now,
            ),
        )
        count += 1

    conn.commit()
    if own_conn:
        conn.close()
    return {"products_updated": count}


def main() -> int:
    result = rebuild_price_stats()
    print(f"price_stats rebuilt for {result['products_updated']} products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
