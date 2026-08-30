"""Price and review insight endpoints."""

import sqlite3

from backend.db.repositories import price_stats as price_stats_repo
from backend.db.repositories import products as products_repo
from backend.db.repositories import review_insights as insights_repo
from backend.db.repositories import reviews as reviews_repo
from backend.db.repositories import wishlist as wishlist_repo
from backend.decision.price_insight import price_insight as build_price_insight
from backend.decision.signals import review_insight_payload


def _stats_row(row) -> dict | None:
    if not row:
        return None
    rel = row["relative_position"]
    if rel is not None:
        rel = float(rel)
    return {
        "min_price": row["min_price"],
        "max_price": row["max_price"],
        "avg_price": row["avg_price"],
        "relative_position": rel,
    }


def get_price_insight_for_product(
    conn: sqlite3.Connection,
    user_id: str,
    product_id: str,
) -> dict:
    product = products_repo.get_product(conn, product_id)
    if not product:
        return None

    saved_price = None
    wl_items = wishlist_repo.list_wishlist(conn, user_id)
    for item in wl_items:
        if item.product_id == product_id:
            saved_price = item.saved_price
            break

    stats_row = price_stats_repo.get_price_stats(conn, product_id)
    payload = build_price_insight(
        product.model_dump(),
        saved_price,
        _stats_row(stats_row),
    )
    payload["product_id"] = product_id
    return payload


def get_review_insight_for_product(conn: sqlite3.Connection, product_id: str) -> dict | None:
    product = products_repo.get_product(conn, product_id)
    if not product:
        return None
    insights = insights_repo.list_insights_for_product(conn, product_id)
    review_count = reviews_repo.count_reviews_for_product(conn, product_id)
    return review_insight_payload(product_id, insights, review_count)
