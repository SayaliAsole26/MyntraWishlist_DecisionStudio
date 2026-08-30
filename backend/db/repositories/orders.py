import json
import sqlite3
import uuid
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_order(
    conn: sqlite3.Connection,
    user_id: str,
    product_ids: list[str],
    total: int,
) -> dict:
    order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"
    created_at = _now_iso()
    conn.execute(
        """
        INSERT INTO orders (order_id, user_id, product_ids, created_at, status)
        VALUES (?, ?, ?, ?, 'CONFIRMED')
        """,
        (order_id, user_id, json.dumps(product_ids), created_at),
    )
    return {
        "order_id": order_id,
        "user_id": user_id,
        "product_ids": product_ids,
        "total": total,
        "item_count": len(product_ids),
        "created_at": created_at,
        "status": "CONFIRMED",
    }
