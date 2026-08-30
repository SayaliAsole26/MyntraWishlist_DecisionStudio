import sqlite3


def count_reviews_for_product(conn: sqlite3.Connection, product_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM reviews WHERE product_id = ?",
        (product_id,),
    ).fetchone()
    return int(row["cnt"]) if row else 0


def list_reviews_for_product(conn: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT review_id, product_id, rating, review_text, review_date
        FROM reviews
        WHERE product_id = ?
        ORDER BY review_date DESC
        """,
        (product_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_product_ids_with_reviews(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT product_id
        FROM reviews
        ORDER BY product_id
        """
    ).fetchall()
    return [r["product_id"] for r in rows]


def count_reviews_for_products(
    conn: sqlite3.Connection, product_ids: list[str]
) -> dict[str, int]:
    if not product_ids:
        return {}
    placeholders = ",".join("?" * len(product_ids))
    rows = conn.execute(
        f"""
        SELECT product_id, COUNT(*) AS cnt
        FROM reviews
        WHERE product_id IN ({placeholders})
        GROUP BY product_id
        """,
        product_ids,
    ).fetchall()
    counts = {pid: 0 for pid in product_ids}
    for r in rows:
        counts[r["product_id"]] = int(r["cnt"])
    return counts
