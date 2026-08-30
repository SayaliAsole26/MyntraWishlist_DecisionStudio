"""Shortlist service — 17→3 automatic relevance filter."""

import sqlite3

from backend.decision.shortlist import rank_and_shortlist


def shortlist_products(
    conn: sqlite3.Connection,
    product_ids: list[str],
    user_id: str = "U001",
    *,
    need: str | None = None,
    tradeoff_priority: str | None = None,
) -> dict:
    return rank_and_shortlist(
        conn,
        product_ids,
        user_id=user_id,
        need=need,
        tradeoff_priority=tradeoff_priority,
        limit=3,
    )
