import sqlite3
from datetime import datetime, timezone

from backend.db.repositories.products import get_product
from backend.models import BagItemOut


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_bag(conn: sqlite3.Connection, user_id: str) -> list[BagItemOut]:
    rows = conn.execute(
        """
        SELECT b.product_id, b.quantity, b.added_at
        FROM bag_items b
        WHERE b.user_id = ?
        ORDER BY b.added_at DESC
        """,
        (user_id,),
    ).fetchall()
    items = []
    for r in rows:
        product = get_product(conn, r["product_id"])
        if not product:
            continue
        items.append(
            BagItemOut(
                product_id=r["product_id"],
                quantity=r["quantity"],
                added_at=r["added_at"],
                product=product,
            )
        )
    return items


def add_to_bag(conn: sqlite3.Connection, user_id: str, product_id: str) -> BagItemOut | None:
    product = get_product(conn, product_id)
    if not product:
        return None

    existing = conn.execute(
        "SELECT * FROM bag_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    ).fetchone()
    if existing:
        quantity = existing["quantity"] + 1
        conn.execute(
            "UPDATE bag_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
            (quantity, user_id, product_id),
        )
        conn.commit()
        return BagItemOut(
            product_id=product_id,
            quantity=quantity,
            added_at=existing["added_at"],
            product=product,
        )

    added_at = _now_iso()
    conn.execute(
        """
        INSERT INTO bag_items (user_id, product_id, quantity, added_at)
        VALUES (?, ?, 1, ?)
        """,
        (user_id, product_id, added_at),
    )
    conn.commit()
    return BagItemOut(
        product_id=product_id,
        quantity=1,
        added_at=added_at,
        product=product,
    )


def remove_from_bag(conn: sqlite3.Connection, user_id: str, product_id: str) -> bool:
    cur = conn.execute(
        "DELETE FROM bag_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    )
    conn.commit()
    return cur.rowcount > 0
