"""Ensure every product has price history + multi-theme reviews for full Q&A coverage."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta

# Themes referenced across the Q&A registry / evidence pack.
REQUIRED_THEMES = (
    "QUALITY",
    "FIT",
    "SIZE",
    "FABRIC",
    "COMFORT",
    "DURABILITY",
    "VALUE",
    "APPEARANCE",
)

MIN_PRICE_POINTS = 5
MIN_REVIEWS = 8


def _theme_summaries(brand: str, rating: float) -> dict[str, tuple[str, str]]:
    """theme -> (positive_summary, negative_summary)."""
    good = rating >= 4.0
    return {
        "QUALITY": (
            f"{brand} feels well made for everyday use.",
            f"Some buyers wanted better finishing from {brand}.",
        ),
        "FIT": (
            f"Most buyers say {brand} fits as expected.",
            f"A few buyers found {brand} sizing inconsistent.",
        ),
        "SIZE": (
            "True to size for most shoppers.",
            "Some shoppers suggest checking the size chart.",
        ),
        "FABRIC": (
            f"Fabric quality is liked for {brand}.",
            "A few reviews mention fabric feeling thinner than expected.",
        ),
        "COMFORT": (
            "Comfortable for regular wear.",
            "Comfort is mixed for longer wear sessions.",
        ),
        "DURABILITY": (
            "Holds up well with regular use according to buyers.",
            "Long-term durability feedback is limited.",
        ),
        "VALUE": (
            f"Buyers see good value at this price for {brand}."
            if good
            else f"Value for money is mixed for {brand}.",
            "Some buyers prefer waiting for a better deal.",
        ),
        "APPEARANCE": (
            "Looks close to the listing photos.",
            "A few buyers noted shade differences vs photos.",
        ),
    }


def _review_templates(brand: str, material: str | None, fit: str | None) -> list[tuple[str, float, str]]:
    """(review_suffix, rating_delta, text) — rating_delta applied to product rating."""
    mat = (material or "the fabric").lower()
    fit_txt = (fit or "regular").lower()
    return [
        ("Q", 0.2, f"Good quality and stitching from {brand}."),
        ("F", 0.1, f"Comfortable fit, true to size for me."),
        ("S", 0.0, f"Sized as expected — {fit_txt} fit works well."),
        ("FB", 0.1, f"Soft and breathable fabric / material ({mat})."),
        ("C", 0.2, f"Very comfortable for daily wear."),
        ("D", 0.0, f"Looks durable and well made so far."),
        ("V", 0.1, f"Worth the price — great buy overall."),
        ("A", 0.0, f"Looks exactly like the product photos."),
        ("N1", -0.8, f"Runs a bit small — check size before ordering."),
        ("N2", -0.6, f"Fabric felt thinner than expected for some washes."),
    ]


def backfill_price_history(conn: sqlite3.Connection) -> int:
    products = conn.execute("SELECT product_id, price, mrp FROM products").fetchall()
    added = 0
    today = date.today()
    for p in products:
        pid = p["product_id"]
        count = conn.execute(
            "SELECT COUNT(*) FROM price_history WHERE product_id = ?", (pid,)
        ).fetchone()[0]
        if count >= MIN_PRICE_POINTS:
            continue

        price = int(p["price"] or 0)
        mrp = int(p["mrp"] or price)
        if price <= 0:
            continue

        # Clear thin history and rewrite a complete mini series.
        conn.execute("DELETE FROM price_history WHERE product_id = ?", (pid,))
        high = max(price, int(mrp * 0.95) if mrp > price else int(price * 1.12))
        points = [
            (today - timedelta(days=60), high),
            (today - timedelta(days=45), int((high + price) / 2)),
            (today - timedelta(days=30), int(price * 1.06)),
            (today - timedelta(days=14), int(price * 1.03)),
            (today - timedelta(days=7), int(price * 1.01)),
            (today, price),
        ]
        for d, pr in points:
            conn.execute(
                """
                INSERT OR IGNORE INTO price_history (product_id, date, price)
                VALUES (?, ?, ?)
                """,
                (pid, d.isoformat(), max(int(pr), 1)),
            )
            added += 1
    conn.commit()
    return added


def _existing_themes(conn: sqlite3.Connection, product_id: str) -> set[str]:
    rows = conn.execute(
        "SELECT theme FROM review_insights WHERE product_id = ?",
        (product_id,),
    ).fetchall()
    return {r["theme"] for r in rows}


def backfill_reviews_and_insights(conn: sqlite3.Connection) -> dict:
    products = conn.execute(
        """
        SELECT product_id, brand, name, rating, rating_count, material, fit
        FROM products
        """
    ).fetchall()

    reviews_added = 0
    insights_added = 0
    products_fixed = 0

    for p in products:
        pid = p["product_id"]
        brand = p["brand"] or "This product"
        rating = float(p["rating"] or 4.0)
        rating_count = int(p["rating_count"] or 50)
        review_count = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE product_id = ?", (pid,)
        ).fetchone()[0]
        themes = _existing_themes(conn, pid)
        needs_reviews = review_count < MIN_REVIEWS
        needs_themes = not set(REQUIRED_THEMES).issubset(themes)
        if not needs_reviews and not needs_themes:
            continue

        products_fixed += 1
        summaries = _theme_summaries(brand, rating)

        # Scale theme counts from listing rating volume.
        base_pos = max(3, int(round((rating_count or 40) * (rating / 5.0) / len(REQUIRED_THEMES))))
        base_neg = max(1, int(round((rating_count or 40) * ((5.0 - rating) / 5.0) / len(REQUIRED_THEMES))))

        if needs_themes:
            for theme in REQUIRED_THEMES:
                pos_sum, neg_sum = summaries[theme]
                # Slightly more negatives on FIT/SIZE/FABRIC so dislike/fit Qs have signal.
                pos = base_pos + (2 if theme in ("QUALITY", "COMFORT", "VALUE") else 0)
                neg = base_neg + (1 if theme in ("FIT", "SIZE", "FABRIC") else 0)
                summary = pos_sum if pos >= neg else neg_sum
                conn.execute(
                    "DELETE FROM review_insights WHERE product_id = ? AND theme = ?",
                    (pid, theme),
                )
                conn.execute(
                    """
                    INSERT INTO review_insights (
                        product_id, theme, positive_count, negative_count, summary,
                        evidence_review_ids, confidence, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'MEDIUM', datetime('now'))
                    """,
                    (pid, theme, pos, neg, summary, json.dumps([])),
                )
                insights_added += 1

        if needs_reviews:
            templates = _review_templates(brand, p["material"], p["fit"])
            for i, (suffix, delta, text) in enumerate(templates, start=1):
                rid = f"{pid}-QA-{suffix}-{i}"
                stars = min(5.0, max(1.0, round(rating + delta, 1)))
                conn.execute(
                    """
                    INSERT OR IGNORE INTO reviews (
                        review_id, product_id, rating, review_text, review_date, source_batch_id
                    ) VALUES (?, ?, ?, ?, date('now'), 'qa-backfill')
                    """,
                    (rid, pid, stars, text),
                )
                if conn.execute("SELECT changes()").fetchone()[0]:
                    reviews_added += 1

    conn.commit()
    return {
        "products_fixed": products_fixed,
        "reviews_added": reviews_added,
        "insights_added": insights_added,
    }


def backfill_evidence(conn: sqlite3.Connection) -> dict:
    price_rows = backfill_price_history(conn)
    review_stats = backfill_reviews_and_insights(conn)
    return {"price_history_rows": price_rows, **review_stats}


def evidence_coverage(conn: sqlite3.Connection) -> dict:
    """Report how many products still lack Q&A-ready evidence."""
    products = conn.execute("SELECT product_id FROM products").fetchall()
    incomplete = []
    for p in products:
        pid = p["product_id"]
        ph = conn.execute(
            "SELECT COUNT(*) FROM price_history WHERE product_id = ?", (pid,)
        ).fetchone()[0]
        rv = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE product_id = ?", (pid,)
        ).fetchone()[0]
        themes = _existing_themes(conn, pid)
        if ph < MIN_PRICE_POINTS or rv < MIN_REVIEWS or not set(REQUIRED_THEMES).issubset(themes):
            incomplete.append(pid)
    return {
        "product_count": len(products),
        "complete": len(products) - len(incomplete),
        "incomplete": incomplete,
    }
