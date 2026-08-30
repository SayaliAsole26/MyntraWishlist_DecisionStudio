import sqlite3


def get_price_stats(conn: sqlite3.Connection, product_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM price_stats WHERE product_id = ?", (product_id,)
    ).fetchone()


def list_price_stats_for_products(
    conn: sqlite3.Connection, product_ids: list[str]
) -> dict[str, sqlite3.Row]:
    if not product_ids:
        return {}
    placeholders = ",".join("?" * len(product_ids))
    rows = conn.execute(
        f"SELECT * FROM price_stats WHERE product_id IN ({placeholders})",
        product_ids,
    ).fetchall()
    return {r["product_id"]: r for r in rows}
