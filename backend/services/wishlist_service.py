"""Wishlist orchestration with deterministic decision signals."""

import sqlite3

from backend.db.repositories import price_stats as price_stats_repo
from backend.db.repositories import review_insights as insights_repo
from backend.db.repositories import reviews as reviews_repo
from backend.db.repositories import wishlist as wishlist_repo
from backend.db.repositories.users import get_profile
from backend.decision.signals import build_item_signals
from backend.models import AlertOut, OverloadOut, ProductOut, WishlistItemWithSignals
from backend.services import alert_service


def _row_to_stats(row) -> dict | None:
    if not row:
        return None
    rel = row["relative_position"]
    if rel is not None:
        rel = float(rel)
    return {
        "current_price": row["current_price"],
        "min_price": row["min_price"],
        "max_price": row["max_price"],
        "avg_price": row["avg_price"],
        "min_date": row["min_date"],
        "relative_position": rel,
    }


def get_wishlist_with_signals(conn: sqlite3.Connection, user_id: str) -> dict:
    items = wishlist_repo.list_wishlist(conn, user_id)
    profile = get_profile(conn, user_id)
    user = {
        "size": profile.size if profile else None,
        "price_min": profile.price_min if profile else None,
        "price_max": profile.price_max if profile else None,
        "occasions": profile.occasions if profile else [],
        "priorities": profile.priorities if profile else [],
    }

    product_ids = [i.product_id for i in items]
    stats_map = price_stats_repo.list_price_stats_for_products(conn, product_ids)
    insights_map = insights_repo.list_insights_for_products(conn, product_ids)
    review_counts = reviews_repo.count_reviews_for_products(conn, product_ids)

    enriched: list[WishlistItemWithSignals] = []
    for item in items:
        pid = item.product_id
        stats = _row_to_stats(stats_map.get(pid))
        insights = insights_map.get(pid, [])
        review_count = review_counts.get(pid, 0)
        product_dict = item.product.model_dump()
        signal_payload = build_item_signals(
            product_dict,
            stats=stats,
            insights=insights,
            review_count=review_count,
            user=user,
        )
        enriched.append(
            WishlistItemWithSignals(
                product_id=item.product_id,
                added_at=item.added_at,
                saved_price=item.saved_price,
                occasion=item.occasion,
                size=item.size,
                product=item.product,
                signals=signal_payload["signals"],
                concerns=signal_payload["concerns"],
                missing=signal_payload["missing"],
            )
        )

    alert_service.refresh_alerts(conn, user_id)
    alerts: list[AlertOut] = alert_service.get_wishlist_alerts(conn, user_id)
    overload: list[OverloadOut] = alert_service.sync_overload_alerts(conn, user_id)

    return {
        "items": enriched,
        "count": len(enriched),
        "alerts": alerts,
        "overload": overload,
    }
