"""Decision need + trade-off priority helpers for shortlist and compare."""

from typing import Any

from backend.decision.product_scores import fit_score, quality_score, rating_score, value_score

NEED_OCCASIONS: dict[str, list[str]] = {
    "Workwear": ["Office", "Casual"],
    "Casual": ["Casual", "Everyday"],
    "Party": ["Party", "Festive"],
    "Sports": ["Sports"],
    "Vacation": ["Vacation"],
}

NEED_STRONG_FIT = 0.5
NEED_OVERALL_WEIGHT = 0.4

TRADEOFF_PRIORITIES = frozenset({"FIT", "VALUE", "QUALITY", "VERSATILITY"})

TRADEOFF_BALANCE_WEIGHTS: dict[str, tuple[float, float, float, float]] = {
    "FIT": (0.15, 0.20, 0.15, 0.50),
    "VALUE": (0.55, 0.20, 0.15, 0.10),
    "QUALITY": (0.15, 0.25, 0.45, 0.15),
    "VERSATILITY": (0.25, 0.25, 0.25, 0.25),
}


def normalize_tradeoff(value: str | None) -> str:
    if not value:
        return "QUALITY"
    key = value.strip().upper()
    return key if key in TRADEOFF_PRIORITIES else "QUALITY"


def infer_occasions(product: dict) -> set[str]:
    """Derive occasion tags from category, subcategory, and name when seed data is generic."""
    cat = (product.get("category") or "").strip()
    sub = (product.get("subcategory") or "").strip().lower()
    name = (product.get("name") or "").lower()
    style = (product.get("style") or "").lower()
    inferred: set[str] = set()

    if sub in ("party", "evening") or any(k in name for k in ("party", "sequin", "embellish", "cocktail")):
        inferred.update(["Party", "Festive"])
    if sub == "heel" or any(k in name for k in ("heel", "stiletto", "pump")):
        inferred.update(["Party", "Festive"])
    if sub == "anarkali" or (cat == "Kurtas" and "festive" in name):
        inferred.update(["Festive", "Office"])
    elif cat == "Kurtas":
        inferred.update(["Festive", "Office", "Casual"])

    if cat == "Sneakers" or sub in ("running", "sports") or "running" in name:
        inferred.update(["Sports", "Casual"])
    if cat == "Activewear":
        inferred.update(["Sports"])
    if cat == "Sandals" and sub == "sports":
        inferred.update(["Sports", "Casual"])

    if sub in ("formal", "office") or "formal" in name or "sheath" in name:
        inferred.update(["Office"])
    if cat in ("Jeans", "Tops") and "Office" not in inferred:
        inferred.update(["Office", "Casual"])
    if cat == "Dresses" and sub in ("casual dresses",) and "Party" not in inferred:
        inferred.update(["Casual", "Everyday"])

    if cat == "Sunglasses" or style == "floral" or "vacation" in name:
        inferred.update(["Vacation", "Casual"])
    if cat == "Handbags":
        inferred.update(["Casual", "Everyday"])
    if cat == "Watches":
        inferred.update(["Office", "Casual"])
    if cat == "Shorts":
        inferred.update(["Sports", "Casual", "Vacation"])

    return inferred


def effective_occasions(product: dict) -> set[str]:
    return set(product.get("occasions") or []) | infer_occasions(product)


def need_fit_score(product: dict, need: str | None) -> float:
    if not need:
        return 0.5
    target = NEED_OCCASIONS.get(need, [])
    product_occ = effective_occasions(product)
    if not target:
        return 0.5
    overlap = len(set(target) & product_occ)
    return overlap / len(target)


def need_fit_detail(product: dict, need: str | None) -> dict[str, Any]:
    """Human-readable suitability for a shopping need."""
    if not need:
        return {
            "score": 0.5,
            "suitable": True,
            "level": "unknown",
            "reason": "No need selected — comparing on price, reviews, and quality only.",
        }

    target = NEED_OCCASIONS.get(need, [])
    product_occ = sorted(effective_occasions(product))
    stored_occ = sorted(set(product.get("occasions") or []))
    target_set = set(target)
    overlap = sorted(target_set & set(product_occ))
    missing = sorted(target_set - set(product_occ))
    score = need_fit_score(product, need)

    name = f"{product.get('brand', '')} {product.get('name', '')}".strip()
    category = product.get("category") or "item"

    if score >= 0.99:
        return {
            "score": round(score, 4),
            "suitable": True,
            "level": "strong",
            "reason": (
                f"{name} is tagged for {', '.join(overlap)} — a strong match for your "
                f"{need.lower()} need."
            ),
        }
    if score > 0:
        gap = f" It lacks {', '.join(missing)} tags." if missing else ""
        return {
            "score": round(score, 4),
            "suitable": False,
            "level": "partial",
            "reason": (
                f"{name} ({category}) is only partly suited to {need.lower()}: "
                f"tagged {', '.join(product_occ) or 'with no occasions'}, "
                f"while {need.lower()} works best for {', '.join(target)}.{gap}"
            ),
        }
    return {
        "score": round(score, 4),
        "suitable": False,
        "level": "poor",
        "reason": (
            f"{name} ({category}) does not fit {need.lower()}: "
            f"tagged {', '.join(product_occ) or 'with no occasions'}, "
            f"not {', '.join(target)}."
        ),
    }


def tradeoff_label(tradeoff: str | None) -> str:
    key = normalize_tradeoff(tradeoff)
    labels = {
        "FIT": "fit",
        "VALUE": "value for money",
        "QUALITY": "build quality and reviews",
        "VERSATILITY": "versatility across occasions",
    }
    return labels.get(key, "overall balance")


def versatility_score(product: dict, need: str | None) -> float:
    occasions = product.get("occasions") or []
    breadth = min(1.0, len(occasions) / 4)
    return round(need_fit_score(product, need) * 0.6 + breadth * 0.4, 4)


def product_component_scores(
    product: dict,
    insights: list[dict],
    *,
    max_price: int,
) -> dict[str, float | None]:
    price = int(product.get("price") or 0)
    mrp = int(product.get("mrp") or 0)
    rating = float(product.get("rating") or 0)
    rating_count = int(product.get("rating_count") or 0)
    return {
        "value": value_score(price, mrp, max_price),
        "rating": rating_score(rating, rating_count),
        "quality": quality_score(rating, rating_count, insights),
        "fit": fit_score(insights),
    }


def weighted_balance(
    components: dict[str, float | None],
    tradeoff: str,
    *,
    product: dict | None = None,
    need: str | None = None,
) -> float:
    key = normalize_tradeoff(tradeoff)
    w_value, w_rating, w_quality, w_fit = TRADEOFF_BALANCE_WEIGHTS[key]
    fit_component = components.get("fit")
    if key == "VERSATILITY" and product is not None:
        fit_component = versatility_score(product, need)
    elif key == "FIT" and product is not None and need:
        base_fit = fit_component if fit_component is not None else 0.5
        fit_component = round(base_fit * 0.45 + need_fit_score(product, need) * 0.55, 4)
    elif fit_component is None:
        fit_component = 0.5
        fit_component = 0.5
    return round(
        (components["value"] or 0) * w_value
        + (components["rating"] or 0) * w_rating
        + (components["quality"] or 0) * w_quality
        + fit_component * w_fit,
        4,
    )


def relevance_score(
    product: dict,
    insights: list[dict],
    *,
    need: str | None,
    tradeoff: str,
    max_price: int,
) -> dict[str, Any]:
    components = product_component_scores(product, insights, max_price=max_price)
    balance = weighted_balance(
        components,
        tradeoff,
        product=product,
        need=need,
    )
    need_boost = need_fit_score(product, need)
    overall = round(
        balance * (1 - NEED_OVERALL_WEIGHT) + need_boost * NEED_OVERALL_WEIGHT, 4
    )
    return {
        "product_id": product["product_id"],
        "overall": overall,
        "balance": balance,
        "need_fit": round(need_boost, 4),
        "components": components,
    }
