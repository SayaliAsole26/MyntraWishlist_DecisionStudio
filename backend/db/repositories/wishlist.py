import sqlite3
from datetime import datetime, timezone

from backend.db.repositories.products import get_product
from backend.models import WishlistItemOut


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _item_from_row(row, product) -> WishlistItemOut:
    occasion = row["occasion"] if "occasion" in row.keys() else "General"
    size = row["size"] if "size" in row.keys() else None
    return WishlistItemOut(
        product_id=row["product_id"],
        added_at=row["added_at"],
        saved_price=row["saved_price"],
        occasion=occasion or "General",
        size=size,
        product=product,
    )


def list_wishlist(conn: sqlite3.Connection, user_id: str) -> list[WishlistItemOut]:
    rows = conn.execute(
        """
        SELECT w.product_id, w.added_at, w.saved_price, w.occasion, w.size
        FROM wishlist_items w
        WHERE w.user_id = ?
        ORDER BY w.added_at DESC
        """,
        (user_id,),
    ).fetchall()
    items = []
    for r in rows:
        product = get_product(conn, r["product_id"])
        if not product:
            continue
        items.append(_item_from_row(r, product))
    return items


def add_to_wishlist(
    conn: sqlite3.Connection,
    user_id: str,
    product_id: str,
    occasion: str | None = "General",
    size: str | None = None,
) -> WishlistItemOut | None:
    product = get_product(conn, product_id)
    if not product:
        return None

    occasion = (occasion or "General").strip() or "General"
    size = (size or "").strip() or None

    existing = conn.execute(
        "SELECT * FROM wishlist_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    ).fetchone()
    if existing:
        return _item_from_row(existing, product)

    added_at = _now_iso()
    saved_price = product.price
    conn.execute(
        """
        INSERT INTO wishlist_items (user_id, product_id, added_at, saved_price, occasion, size)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, product_id, added_at, saved_price, occasion, size),
    )
    conn.commit()
    return WishlistItemOut(
        product_id=product_id,
        added_at=added_at,
        saved_price=saved_price,
        occasion=occasion,
        size=size,
        product=product,
    )


def remove_from_wishlist(conn: sqlite3.Connection, user_id: str, product_id: str) -> bool:
    cur = conn.execute(
        "DELETE FROM wishlist_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    )
    conn.commit()
    return cur.rowcount > 0
