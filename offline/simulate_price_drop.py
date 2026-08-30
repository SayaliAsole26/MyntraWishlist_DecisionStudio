"""Demo control: drop a product price, rebuild stats, and scan alerts."""

import argparse
from datetime import date

from backend.db.schema import ensure_schema
from backend.db.session import get_connection
from backend.services.alert_service import scan_price_alerts
from offline.rebuild_price_stats import rebuild_price_stats


def simulate_price_drop(
    conn,
    product_id: str,
    new_price: int,
    user_id: str | None = None,
) -> dict:
    row = conn.execute(
        "SELECT product_id, price FROM products WHERE product_id = ?",
        (product_id,),
    ).fetchone()
    if not row:
        raise ValueError(f"Product {product_id} not found")

    old_price = int(row["price"])
    today = date.today().isoformat()

    conn.execute(
        "UPDATE products SET price = ?, updated_at = datetime('now') WHERE product_id = ?",
        (new_price, product_id),
    )
    conn.execute(
        """
        INSERT INTO price_history (product_id, date, price)
        VALUES (?, ?, ?)
        ON CONFLICT(product_id, date) DO UPDATE SET price = excluded.price
        """,
        (product_id, today, new_price),
    )
    conn.commit()

    rebuild_price_stats(conn)
    scan_result = scan_price_alerts(conn, user_id)

    return {
        "product_id": product_id,
        "old_price": old_price,
        "new_price": new_price,
        "alerts_created": scan_result["alerts_created"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate a price drop for demo alerts")
    parser.add_argument("product_id", help="Product id, e.g. P002")
    parser.add_argument("new_price", type=int, help="New price in rupees")
    parser.add_argument("--user", default=None, help="Limit alert scan to one user id")
    args = parser.parse_args()

    conn = get_connection()
    try:
        ensure_schema(conn)
        result = simulate_price_drop(conn, args.product_id, args.new_price, args.user)
    finally:
        conn.close()

    print(
        f"{result['product_id']}: ₹{result['old_price']} → ₹{result['new_price']} "
        f"({result['alerts_created']} price-drop alert(s) created)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
