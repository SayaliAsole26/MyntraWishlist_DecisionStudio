"""Comparison scores and BEST VALUE / REVIEWED / BALANCE labels."""

from typing import Any

from backend.decision.product_scores import fit_score, quality_score, rating_score, value_score
from backend.decision.tradeoff import (
    NEED_OVERALL_WEIGHT,
    NEED_STRONG_FIT,
    need_fit_detail,
    need_fit_score,
    normalize_tradeoff,
    tradeoff_label,
    weighted_balance,
)


def comparison_scores(
    products: list[dict],
    insights_by_product: dict[str, list[dict]],
    *,
    tradeoff_priority: str | None = None,
    need: str | None = None,
) -> dict[str, Any]:
    if len(products) < 2:
        raise ValueError("Need at least 2 products to compare")

    max_price = max(int(p.get("price") or 0) for p in products)
    per_product: dict[str, dict[str, Any]] = {}

    for p in products:
        pid = p["product_id"]
        price = int(p.get("price") or 0)
        mrp = int(p.get("mrp") or 0)
        rating = float(p.get("rating") or 0)
        rating_count = int(p.get("rating_count") or 0)
        insights = insights_by_product.get(pid, [])

        per_product[pid] = {
            "value": value_score(price, mrp, max_price),
            "rating": rating_score(rating, rating_count),
            "quality": quality_score(rating, rating_count, insights),
            "fit": fit_score(insights),
            "need_fit": need_fit_score(p, need),
            "balance": 0.0,
            "overall": 0.0,
        }
        per_product[pid]["balance"] = weighted_balance(
            per_product[pid],
            normalize_tradeoff(tradeoff_priority),
            product=p,
            need=need,
        )
        if need:
            per_product[pid]["overall"] = round(
                per_product[pid]["balance"] * (1 - NEED_OVERALL_WEIGHT)
                + per_product[pid]["need_fit"] * NEED_OVERALL_WEIGHT,
                4,
            )
        else:
            per_product[pid]["overall"] = per_product[pid]["balance"]

    def _pick_best_balance() -> str:
        if not need:
            return max(products, key=lambda p: per_product[p["product_id"]]["balance"])[
                "product_id"
            ]
        strong = [
            p
            for p in products
            if per_product[p["product_id"]]["need_fit"] >= NEED_STRONG_FIT
        ]
        partial = [
            p for p in products if per_product[p["product_id"]]["need_fit"] > 0
        ]
        pool = strong or partial or products
        return max(pool, key=lambda p: per_product[p["product_id"]]["overall"])[
            "product_id"
        ]

    labels = {
        "best_value": max(products, key=lambda p: per_product[p["product_id"]]["value"])[
            "product_id"
        ],
        "best_reviewed": max(
            products, key=lambda p: per_product[p["product_id"]]["rating"]
        )["product_id"],
        "best_balance": _pick_best_balance(),
    }

    need_assessment = {
        p["product_id"]: need_fit_detail(p, need) for p in products
    }
    top_need = need_assessment.get(labels["best_balance"], {})

    rows = _build_rows(products, per_product)
    summary = _template_summary(
        products,
        labels,
        per_product,
        need=need,
        tradeoff_priority=tradeoff_priority,
        need_assessment=need_assessment,
    )

    missing: list[str] = []
    if any(fit_score(insights_by_product.get(p["product_id"], [])) is None for p in products):
        missing.append("fit_insights")

    return {
        "scores": per_product,
        "labels": labels,
        "rows": rows,
        "summary": summary,
        "need_assessment": need_assessment,
        "top_pick_need_fit": top_need,
        "missing": missing,
        "need": need,
        "tradeoff_priority": normalize_tradeoff(tradeoff_priority),
    }


def _build_rows(products: list[dict], scores: dict[str, dict]) -> list[dict]:
    ids = [p["product_id"] for p in products]

    def values(key: str, *, from_product: bool = False) -> dict[str, Any]:
        if from_product:
            field = key
            return {p["product_id"]: p.get(field) for p in products}
        return {pid: scores[pid].get(key) for pid in ids}

    return [
        {"metric": "price", "label": "Price (₹)", "values": values("price", from_product=True)},
        {"metric": "rating", "label": "Rating", "values": values("rating", from_product=True)},
        {"metric": "rating_count", "label": "Rating count", "values": values("rating_count", from_product=True)},
        {"metric": "need_fit_score", "label": "Need fit", "values": values("need_fit")},
        {"metric": "value_score", "label": "Value score", "values": values("value")},
        {"metric": "fit_score", "label": "Fit score", "values": values("fit")},
        {"metric": "quality_score", "label": "Quality score", "values": values("quality")},
    ]


def _template_summary(
    products: list[dict],
    labels: dict[str, str],
    scores: dict[str, dict],
    *,
    need: str | None = None,
    tradeoff_priority: str | None = None,
    need_assessment: dict[str, dict] | None = None,
) -> str:
    by_id = {p["product_id"]: p for p in products}
    need_assessment = need_assessment or {}

    def name(pid: str) -> str:
        p = by_id[pid]
        return f"{p.get('brand', '')} {p.get('name', '')}".strip()

    tradeoff_txt = tradeoff_label(tradeoff_priority)
    top_id = labels["best_balance"]
    top_name = name(top_id)
    top_need = need_assessment.get(top_id, {})

    parts = [
        f"For {need.lower()} with {tradeoff_txt} as your priority, "
        f"{top_name} ranks highest overall."
        if need
        else f"With {tradeoff_txt} as your priority, {top_name} ranks highest overall.",
        f"{name(labels['best_value'])} offers the strongest value score.",
        f"{name(labels['best_reviewed'])} leads on buyer rating signal.",
    ]

    if need and top_need.get("level") == "partial":
        parts.append(
            f"Note: {top_name} is only a partial match for {need.lower()} — "
            f"{top_need.get('reason', '')}"
        )
    elif need and top_need.get("level") == "poor":
        parts.append(
            f"Caution: {top_name} is a weak match for {need.lower()} despite leading on "
            f"{tradeoff_txt}. {top_need.get('reason', '')} "
            f"Consider a better-suited alternative from your shortlist if available."
        )

    return " ".join(parts)
