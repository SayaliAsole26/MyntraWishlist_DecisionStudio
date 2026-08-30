"""Price insight from saved_price + price_stats. No future-price claims."""

from typing import Any


def price_insight(
    product: dict,
    saved_price: int | None,
    stats: dict | None,
) -> dict[str, Any]:
    current = int(product.get("price") or 0)
    mrp = int(product.get("mrp") or 0)
    discount = product.get("discount")
    if discount is None and mrp > 0:
        discount = round((1 - current / mrp) * 100)

    missing: list[str] = []
    messages: list[str] = []
    copy_key = "unavailable"
    has_range = False

    if stats and stats.get("min_price") is not None and stats.get("max_price") is not None:
        min_p = int(stats["min_price"])
        max_p = int(stats["max_price"])
        has_range = max_p > min_p
        rel = stats.get("relative_position")
        if rel is not None:
            rel = float(rel)

        if has_range and rel is not None:
            if rel <= 0.15:
                messages.append("Current price is close to the recent low.")
                copy_key = "close_to_low"
            elif rel >= 0.85:
                messages.append("Current price is near the recent high for this item.")
                copy_key = "near_high"
            else:
                messages.append("Current price is within the usual observed range.")
                copy_key = "mid_range"

            if current < min_p:
                messages.append("This item has previously dropped below the current price.")
        elif has_range:
            messages.append("Current price is within the usual observed range.")
            copy_key = "mid_range"
        else:
            messages.append("Price history unavailable.")
            copy_key = "unavailable"
            missing.append("price_history")
    else:
        missing.append("price_history")
        messages.append("Price history unavailable.")

    saved_delta = None
    if saved_price is not None:
        saved_delta = current - saved_price
        if saved_delta < 0:
            messages.append(f"Price dropped ₹{abs(saved_delta)} since you saved it.")
        elif saved_delta > 0:
            messages.append(f"Price increased ₹{saved_delta} since you saved it.")
        else:
            messages.append("Price unchanged since you saved it.")

    rel_out = stats.get("relative_position") if stats else None
    if rel_out is not None:
        rel_out = float(rel_out)

    return {
        "current_price": current,
        "mrp": mrp,
        "discount": discount,
        "saved_price": saved_price,
        "saved_delta": saved_delta,
        "min_price": stats.get("min_price") if stats else None,
        "max_price": stats.get("max_price") if stats else None,
        "avg_price": stats.get("avg_price") if stats else None,
        "relative_position": rel_out,
        "history_available": has_range,
        "copy_key": copy_key,
        "summary": " ".join(messages),
        "missing": missing,
    }
