"""Compare 2–3 Wishlist products — deterministic table + optional Groq explanation."""

import sqlite3

from backend.db.repositories import price_stats as price_stats_repo
from backend.db.repositories import products as products_repo
from backend.db.repositories import review_insights as insights_repo
from backend.db.repositories import reviews as reviews_repo
from backend.decision.comparison_scores import comparison_scores
from backend.decision.confidence import confidence_from_evidence
from backend.decision.evidence_pack import build_compare_pack, load_context
from backend.services.explain_service import explain_comparison


def compare_products(
    conn: sqlite3.Connection,
    product_ids: list[str],
    user_id: str = "U001",
    *,
    need: str | None = None,
    tradeoff_priority: str | None = None,
    user_confidence: int | None = None,
) -> dict:
    products = []
    for pid in product_ids:
        p = products_repo.get_product(conn, pid)
        if not p:
            raise ValueError(f"Product not found: {pid}")
        products.append(p.model_dump())

    insights_map = insights_repo.list_insights_for_products(conn, product_ids)
    review_counts = reviews_repo.count_reviews_for_products(conn, product_ids)
    stats_map = price_stats_repo.list_price_stats_for_products(conn, product_ids)

    result = comparison_scores(
        products,
        insights_map,
        tradeoff_priority=tradeoff_priority,
        need=need,
    )

    has_history = any(
        stats_map.get(pid) and stats_map[pid]["max_price"] != stats_map[pid]["min_price"]
        for pid in product_ids
    )
    total_reviews = sum(review_counts.get(pid, 0) for pid in product_ids)
    total_insights = sum(len(insights_map.get(pid, [])) for pid in product_ids)

    confidence = confidence_from_evidence(
        has_price_history=has_history,
        review_count=total_reviews // max(len(product_ids), 1),
        insight_count=total_insights // max(len(product_ids), 1),
        compare_count=len(product_ids),
    )

    missing = list(result.get("missing") or [])
    if not has_history:
        missing.append("price_history")
    missing = list(dict.fromkeys(missing))

    context = load_context(
        conn,
        user_id,
        product_ids,
        need=need,
        tradeoff_priority=tradeoff_priority,
    )
    context["labels"] = result["labels"]
    context["scores"] = result["scores"]
    context["need_assessment"] = result.get("need_assessment", {})
    context["user_confidence"] = user_confidence
    compare_pack = build_compare_pack(context)
    explanation = explain_comparison(compare_pack)

    return {
        "products": products,
        "rows": result["rows"],
        "labels": result["labels"],
        "scores": result["scores"],
        "summary": result["summary"],
        "need_assessment": result.get("need_assessment", {}),
        "top_pick_need_fit": result.get("top_pick_need_fit", {}),
        "need": need,
        "tradeoff_priority": result.get("tradeoff_priority"),
        "confidence": confidence,
        "missing": missing,
        "explanation": explanation,
    }
