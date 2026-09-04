"""Smart alerts — price drop, similar product, decision overload."""

import json
import sqlite3

from backend.db.repositories import alerts as alerts_repo
from backend.db.repositories import product_similarity as sim_repo
from backend.db.repositories import wishlist as wishlist_repo
from backend.db.repositories.products import get_product
from backend.decision.overload import (
    OVERLOAD_THRESHOLD,
    detect_overload_groups,
    products_from_wishlist_items,
)
from backend.models import AlertOut, OverloadOut

PRICE_DROP_MIN_DELTA = 1
SIMILAR_SCORE_THRESHOLD = 0.45


def _format_benefits(source_price: int, source_rating: float | None, alt) -> list[str]:
    benefits: list[str] = []
    if alt.price < source_price:
        diff = source_price - alt.price
        benefits.append(f"₹{diff:,} cheaper")
    if alt.rating and source_rating and alt.rating > source_rating:
        benefits.append("Higher rating")
    elif alt.rating and source_rating is None and alt.rating >= 4.0:
        benefits.append("Higher rating")
    return benefits


def scan_price_alerts(conn: sqlite3.Connection, user_id: str | None = None) -> dict:
    """Scan wishlist items for price drops vs saved_price."""
    if user_id:
        user_ids = [user_id]
    else:
        rows = conn.execute("SELECT DISTINCT user_id FROM wishlist_items").fetchall()
        user_ids = [r["user_id"] for r in rows]

    created = 0
    for uid in user_ids:
        items = wishlist_repo.list_wishlist(conn, uid)
        for item in items:
            current = item.product.price
            saved = item.saved_price
            if current > saved - PRICE_DROP_MIN_DELTA:
                continue
            if alerts_repo.has_undismissed_alert(conn, uid, "PRICE_DROP", item.product_id):
                continue
            payload = {
                "from": saved,
                "to": current,
                "save_amount": saved - current,
            }
            alerts_repo.insert_alert(conn, uid, "PRICE_DROP", item.product_id, payload)
            created += 1

    conn.commit()
    return {"alerts_created": created}


def ensure_similar_alerts(conn: sqlite3.Connection, user_id: str) -> int:
    """Create similar-product alerts for wishlist items (deduped)."""
    items = wishlist_repo.list_wishlist(conn, user_id)
    wishlist_ids = {i.product_id for i in items}
    created = 0

    for item in items:
        if alerts_repo.has_undismissed_alert(conn, user_id, "SIMILAR_PRODUCT", item.product_id):
            continue

        similar = sim_repo.list_similar_for_product(conn, item.product_id, limit=20)
        best = None

        for entry in similar:
            if entry["score"] < SIMILAR_SCORE_THRESHOLD:
                continue
            alt = get_product(conn, entry["similar_product_id"])
            if not alt:
                continue

            cheaper = alt.price < item.product.price
            better_rated = (
                alt.rating is not None
                and item.product.rating is not None
                and alt.rating > item.product.rating
            )
            if not cheaper and not better_rated:
                continue

            on_wishlist = alt.product_id in wishlist_ids
            # Prefer catalog alternatives not already saved; fall back to better wishlist peer
            priority = (0 if not on_wishlist else 1, -entry["score"])
            if best is None or priority < best[0]:
                benefits = _format_benefits(item.product.price, item.product.rating, alt)
                if not benefits:
                    continue
                best = (
                    priority,
                    {
                        "similar_product_id": alt.product_id,
                        "reason": entry["reason"],
                        "benefits": benefits,
                        "score": entry["score"],
                        "on_wishlist": on_wishlist,
                    },
                )

        if best is None:
            continue

        payload = best[1]
        alerts_repo.insert_alert(conn, user_id, "SIMILAR_PRODUCT", item.product_id, payload)
        created += 1

    conn.commit()
    return created


def sync_overload_alerts(conn: sqlite3.Connection, user_id: str) -> list[OverloadOut]:
    """Detect overload groups and return active (non-dismissed) signals."""
    items = wishlist_repo.list_wishlist(conn, user_id)
    products = products_from_wishlist_items(items)
    groups = detect_overload_groups(conn, products, threshold=OVERLOAD_THRESHOLD)

    active: list[OverloadOut] = []
    for group in groups:
        existing = alerts_repo.get_overload_alert_for_group(conn, user_id, group["group_key"])
        alert_id: str | None = existing["alert_id"] if existing else None

        if existing and existing["dismissed_at"]:
            # Re-show if the cluster grew after dismiss (new similar saves).
            try:
                prev = json.loads(existing["payload_json"] or "{}")
            except json.JSONDecodeError:
                prev = {}
            prev_count = int(prev.get("count") or 0) if isinstance(prev, dict) else 0
            if group["count"] <= prev_count:
                continue
            alert_id = alerts_repo.insert_alert(
                conn,
                user_id,
                "DECISION_OVERLOAD",
                None,
                group,
            )
        elif not existing:
            alert_id = alerts_repo.insert_alert(
                conn,
                user_id,
                "DECISION_OVERLOAD",
                None,
                group,
            )

        active.append(
            OverloadOut(
                alert_id=alert_id,
                group_key=group["group_key"],
                count=group["count"],
                label=group["label"],
                category=group.get("category"),
                subcategory=group.get("subcategory"),
                product_ids=group["product_ids"],
            )
        )

    conn.commit()
    return active


def refresh_alerts(conn: sqlite3.Connection, user_id: str) -> None:
    """Run online alert checks on Wishlist load (no Groq)."""
    scan_price_alerts(conn, user_id)
    ensure_similar_alerts(conn, user_id)


def get_wishlist_alerts(conn: sqlite3.Connection, user_id: str) -> list[AlertOut]:
    """Return undismissed PRICE_DROP and SIMILAR_PRODUCT alerts."""
    all_alerts = alerts_repo.list_undismissed_alerts(conn, user_id)
    return [a for a in all_alerts if a.type in ("PRICE_DROP", "SIMILAR_PRODUCT")]


def dismiss_alert(conn: sqlite3.Connection, user_id: str, alert_id: str) -> bool:
    return alerts_repo.dismiss_alert(conn, user_id, alert_id)
