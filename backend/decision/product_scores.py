"""Shared product score components for compare and shortlist."""

import math


def value_score(price: int, mrp: int, max_price: int) -> float:
    discount = (1 - price / mrp) if mrp > 0 else 0
    price_norm = 1 - (price / max(max_price, 1))
    return round(discount * 0.45 + price_norm * 0.55, 4)


def rating_score(rating: float, rating_count: int) -> float:
    return round(rating * min(1.0, math.log10(rating_count + 1) / 3), 4)


def quality_score(rating: float, rating_count: int, insights: list[dict]) -> float:
    base = rating_score(rating, rating_count)
    if not insights:
        return round(base, 4)
    positive = sum(i.get("positive_count") or 0 for i in insights)
    negative = sum(i.get("negative_count") or 0 for i in insights)
    total = positive + negative
    sentiment = (positive - negative) / total if total else 0
    return round(base * 0.7 + max(0, sentiment) * 0.3, 4)


def fit_score(insights: list[dict]) -> float | None:
    fit_themes = {"FIT", "SIZE"}
    relevant = [i for i in insights if i.get("theme") in fit_themes]
    if not relevant:
        return None
    positive = sum(i.get("positive_count") or 0 for i in relevant)
    negative = sum(i.get("negative_count") or 0 for i in relevant)
    total = positive + negative
    if total == 0:
        return None
    return round(positive / total, 4)
