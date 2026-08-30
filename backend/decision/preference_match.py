"""Preference match against user profile — deterministic weights."""

import math
from typing import Any


def preference_match(product: dict, user: dict) -> dict[str, Any]:
    price = int(product.get("price") or 0)
    price_min = user.get("price_min")
    price_max = user.get("price_max")
    user_size = user.get("size")
    sizes = product.get("sizes") or []
    occasions = product.get("occasions") or []
    user_occasions = user.get("occasions") or []
    priorities = user.get("priorities") or []

    price_fit = 0.0
    if price_min is not None and price_max is not None and price_max >= price_min:
        if price_min <= price <= price_max:
            price_fit = 1.0
        elif price < price_min:
            price_fit = 0.7
        else:
            over = price - price_max
            price_fit = max(0.0, 1.0 - over / max(price_max, 1))

    occasion_fit = 0.0
    if user_occasions and occasions:
        overlap = len(set(user_occasions) & set(occasions))
        occasion_fit = overlap / len(set(user_occasions))

    size_fit = 1.0 if not user_size else (1.0 if user_size in sizes else 0.0)

    rating = float(product.get("rating") or 0)
    rating_count = int(product.get("rating_count") or 0)
    rating_signal = rating * min(1.0, math.log10(rating_count + 1) / 3)

    priority_weights = {
        "Price": {"price_fit": 0.5, "rating_signal": 0.2, "occasion_fit": 0.15, "size_fit": 0.15},
        "Quality": {"price_fit": 0.15, "rating_signal": 0.45, "occasion_fit": 0.2, "size_fit": 0.2},
        "Comfort": {"price_fit": 0.2, "rating_signal": 0.35, "occasion_fit": 0.25, "size_fit": 0.2},
        "Style": {"price_fit": 0.2, "rating_signal": 0.25, "occasion_fit": 0.4, "size_fit": 0.15},
    }
    weights = priority_weights.get(priorities[0] if priorities else "Quality", priority_weights["Quality"])

    overall = (
        price_fit * weights["price_fit"]
        + rating_signal / 5 * weights["rating_signal"]
        + occasion_fit * weights["occasion_fit"]
        + size_fit * weights["size_fit"]
    )

    return {
        "price_fit": round(price_fit, 3),
        "occasion_fit": round(occasion_fit, 3),
        "size_fit": round(size_fit, 3),
        "rating_signal": round(rating_signal, 3),
        "overall": round(overall, 3),
        "within_budget": price_min is not None and price_max is not None and price_min <= price <= price_max,
    }
