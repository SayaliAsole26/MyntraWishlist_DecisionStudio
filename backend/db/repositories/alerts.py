"""Alerts persistence — price drop, similar product, decision overload."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from backend.db.repositories.products import get_product
from backend.models import AlertOut, ProductOut


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_payload(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _row_to_alert(row: sqlite3.Row, product: ProductOut | None = None) -> AlertOut:
    payload = _parse_payload(row["payload_json"])
    similar_product: ProductOut | None = None
    sid = payload.get("similar_product_id")
    if sid and row["type"] == "SIMILAR_PRODUCT":
        similar_product = product  # caller may pass preloaded similar product

    return AlertOut(
        alert_id=row["alert_id"],
        type=row["type"],
        product_id=row["product_id"],
        payload=payload,
        created_at=row["created_at"],
        product=product if row["type"] != "SIMILAR_PRODUCT" else None,
        similar_product=similar_product,
    )


def has_undismissed_alert(
    conn: sqlite3.Connection,
    user_id: str,
    alert_type: str,
    product_id: str | None = None,
    group_key: str | None = None,
) -> bool:
    if alert_type == "DECISION_OVERLOAD" and group_key:
        rows = conn.execute(
            """
            SELECT payload_json FROM alerts
            WHERE user_id = ? AND type = ? AND dismissed_at IS NULL
            """,
            (user_id, alert_type),
        ).fetchall()
        for r in rows:
            payload = _parse_payload(r["payload_json"])
            if payload.get("group_key") == group_key:
                return True
        return False

    if product_id is None:
        return False

    row = conn.execute(
        """
        SELECT 1 FROM alerts
        WHERE user_id = ? AND type = ? AND product_id = ? AND dismissed_at IS NULL
        LIMIT 1
        """,
        (user_id, alert_type, product_id),
    ).fetchone()
    return row is not None


def insert_alert(
    conn: sqlite3.Connection,
    user_id: str,
    alert_type: str,
    product_id: str | None,
    payload: dict,
) -> str:
    alert_id = f"A-{uuid.uuid4().hex[:12]}"
    created_at = _now_iso()
    conn.execute(
        """
        INSERT INTO alerts (alert_id, user_id, type, product_id, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (alert_id, user_id, alert_type, product_id, json.dumps(payload), created_at),
    )
    return alert_id


def list_undismissed_alerts(conn: sqlite3.Connection, user_id: str) -> list[AlertOut]:
    rows = conn.execute(
        """
        SELECT alert_id, type, product_id, payload_json, created_at
        FROM alerts
        WHERE user_id = ? AND dismissed_at IS NULL
        ORDER BY created_at DESC
        """,
        (user_id,),
    ).fetchall()

    alerts: list[AlertOut] = []
    for row in rows:
        payload = _parse_payload(row["payload_json"])
        product: ProductOut | None = None
        similar_product: ProductOut | None = None

        if row["type"] == "SIMILAR_PRODUCT":
            if row["product_id"]:
                product = get_product(conn, row["product_id"])
            sid = payload.get("similar_product_id")
            if sid:
                similar_product = get_product(conn, sid)
        elif row["product_id"]:
            product = get_product(conn, row["product_id"])

        alerts.append(
            AlertOut(
                alert_id=row["alert_id"],
                type=row["type"],
                product_id=row["product_id"],
                payload=payload,
                created_at=row["created_at"],
                product=product,
                similar_product=similar_product,
            )
        )
    return alerts


def dismiss_alert(conn: sqlite3.Connection, user_id: str, alert_id: str) -> bool:
    dismissed_at = _now_iso()
    cur = conn.execute(
        """
        UPDATE alerts SET dismissed_at = ?
        WHERE alert_id = ? AND user_id = ? AND dismissed_at IS NULL
        """,
        (dismissed_at, alert_id, user_id),
    )
    conn.commit()
    return cur.rowcount > 0


def get_overload_alert_for_group(
    conn: sqlite3.Connection, user_id: str, group_key: str
) -> sqlite3.Row | None:
    rows = conn.execute(
        """
        SELECT alert_id, type, product_id, payload_json, created_at, dismissed_at
        FROM alerts
        WHERE user_id = ? AND type = 'DECISION_OVERLOAD'
        ORDER BY created_at DESC
        """,
        (user_id,),
    ).fetchall()
    for row in rows:
        payload = _parse_payload(row["payload_json"])
        if payload.get("group_key") == group_key:
            return row
    return None
