"""Mock checkout — creates order and clears bag."""

import sqlite3

from backend.db.repositories import bag as bag_repo
from backend.db.repositories import orders as orders_repo
from backend.models import CheckoutOut


def checkout(conn: sqlite3.Connection, user_id: str) -> CheckoutOut:
    items = bag_repo.list_bag(conn, user_id)
    if not items:
        raise ValueError("Your bag is empty")

    product_ids = [i.product_id for i in items]
    total = sum(i.product.price * i.quantity for i in items)

    order = orders_repo.create_order(conn, user_id, product_ids, total)
    conn.execute("DELETE FROM bag_items WHERE user_id = ?", (user_id,))
    conn.commit()

    return CheckoutOut(**order)
