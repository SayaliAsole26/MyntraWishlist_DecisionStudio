"""Per-item Wishlist decision signals — no LLM."""

from typing import Any

from backend.decision.confidence import collect_missing


def build_item_signals(
    product: dict,
    *,
    stats: dict | None,
    insights: list[dict],
    review_count: int,
    user: dict,
) -> dict[str, Any]:
    signals: list[str] = []
    concerns: list[str] = []

    rating = float(product.get("rating") or 0)
    rating_count = int(product.get("rating_count") or 0)
    if rating >= 4.3 and rating_count >= 300:
        signals.append("Highly rated")

    price = int(product.get("price") or 0)
    mrp = int(product.get("mrp") or 0)
    discount = product.get("discount") or (round((1 - price / mrp) * 100) if mrp else 0)
    rel_pos = stats.get("relative_position") if stats else None
    if rel_pos is not None:
        rel_pos = float(rel_pos)
    has_range = stats and stats.get("max_price") != stats.get("min_price")
    near_low = has_range and rel_pos is not None and rel_pos <= 0.2
    if discount >= 45 or near_low:
        signals.append("Good value")

    user_size = user.get("size")
    sizes = product.get("sizes") or []
    if user_size and sizes and user_size not in sizes:
        concerns.append("Size unavailable in your profile")

    for insight in insights:
        theme = insight.get("theme") or ""
        neg = insight.get("negative_count") or 0
        pos = insight.get("positive_count") or 0
        if theme in ("FIT", "SIZE") and neg > pos:
            concerns.append("Fit concerns")
            break

    has_history = bool(stats and stats.get("max_price") != stats.get("min_price"))
    missing = collect_missing(
        has_price_history=has_history,
        review_count=review_count,
        insight_count=len(insights),
        size_available=None if not user_size else user_size in sizes,
    )

    return {
        "signals": signals,
        "concerns": concerns,
        "missing": missing,
    }


def review_insight_payload(
    product_id: str,
    insights: list[dict],
    review_count: int,
) -> dict[str, Any]:
    if review_count == 0:
        return {
            "product_id": product_id,
            "available": False,
            "summary": "Not enough review data to assess this reliably.",
            "likes": [],
            "concerns": [],
            "themes": [],
            "review_count": 0,
            "volume_band": "none",
            "confidence": "LOW",
            "missing": ["reviews"],
        }

    if not insights:
        band = "low" if review_count < 10 else "medium" if review_count < 25 else "high"
        return {
            "product_id": product_id,
            "available": False,
            "summary": "Not enough review data to assess this reliably.",
            "likes": [],
            "concerns": [],
            "themes": [],
            "review_count": review_count,
            "volume_band": band,
            "confidence": "LOW",
            "missing": ["review_insights"],
        }

    likes = []
    concerns = []
    themes = []
    for i in insights:
        themes.append(
            {
                "theme": i["theme"],
                "positive_count": i.get("positive_count"),
                "negative_count": i.get("negative_count"),
                "summary": i.get("summary"),
            }
        )
        if (i.get("positive_count") or 0) > (i.get("negative_count") or 0):
            likes.append(i["theme"].title())
        elif (i.get("negative_count") or 0) > 0:
            concerns.append(i["theme"].title())

    band = "low" if review_count < 10 else "medium" if review_count < 25 else "high"
    prefix = "Among the available reviews, " if review_count < 100 else ""
    top = max(insights, key=lambda x: (x.get("positive_count") or 0) + (x.get("negative_count") or 0))
    summary = prefix + (top.get("summary") or "Review themes extracted from available buyer feedback.")

    return {
        "product_id": product_id,
        "available": True,
        "summary": summary,
        "likes": likes[:4],
        "concerns": concerns[:4],
        "themes": themes,
        "review_count": review_count,
        "volume_band": band,
        "confidence": "MEDIUM" if band == "medium" else ("HIGH" if band == "high" else "LOW"),
        "missing": [],
    }
