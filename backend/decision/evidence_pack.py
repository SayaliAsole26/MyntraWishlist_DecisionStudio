"""Build structured evidence packs for LLM explainers."""

import sqlite3
from typing import Any

from backend.db.repositories import price_stats as price_stats_repo
from backend.db.repositories import product_similarity as similarity_repo
from backend.db.repositories import products as products_repo
from backend.db.repositories import review_insights as insights_repo
from backend.db.repositories import reviews as reviews_repo
from backend.db.repositories import wishlist as wishlist_repo
from backend.db.repositories.users import get_profile
from backend.decision.comparison_scores import comparison_scores
from backend.decision.confidence import confidence_from_evidence, collect_missing
from backend.decision.preference_match import preference_match
from backend.decision.price_insight import price_insight


LANGUAGE_RULES = [
    "Use only evidence in this pack",
    "Do not predict future prices",
    "Separate fact, evidence, interpretation, recommendation",
    "If a field is present in the pack, do not claim it is missing",
]


def _user_dict(profile) -> dict:
    if not profile:
        return {}
    return {
        "size": profile.size,
        "budget": {"min": profile.price_min, "max": profile.price_max},
        "occasions": profile.occasions,
        "priorities": profile.priorities,
    }


def _review_themes(insights: list[dict], review_count: int) -> list[dict]:
    band = "low" if review_count < 10 else ("medium" if review_count < 25 else "high")
    return [
        {
            "theme": i["theme"],
            "positive": i.get("positive_count"),
            "negative": i.get("negative_count"),
            "summary": i.get("summary"),
            "volume_band": band,
        }
        for i in insights
    ]


def load_context(
    conn: sqlite3.Connection,
    user_id: str,
    product_ids: list[str],
    *,
    need: str | None = None,
    tradeoff_priority: str | None = None,
) -> dict[str, Any]:
    profile = get_profile(conn, user_id)
    user = _user_dict(profile)

    products = []
    for pid in product_ids:
        p = products_repo.get_product(conn, pid)
        if p:
            products.append(p.model_dump())

    stats_map = price_stats_repo.list_price_stats_for_products(conn, product_ids)
    insights_map = insights_repo.list_insights_for_products(conn, product_ids)
    review_counts = reviews_repo.count_reviews_for_products(conn, product_ids)

    wl_items = wishlist_repo.list_wishlist(conn, user_id)
    saved_prices = {i.product_id: i.saved_price for i in wl_items}
    wl_ids = [i.product_id for i in wl_items]

    price_blocks = []
    for pid in product_ids:
        stats_row = stats_map.get(pid)
        product = next((p for p in products if p["product_id"] == pid), None)
        if not product:
            continue
        stats = None
        if stats_row:
            stats = {
                "min_price": stats_row["min_price"],
                "max_price": stats_row["max_price"],
                "avg_price": stats_row["avg_price"],
                "relative_position": float(stats_row["relative_position"])
                if stats_row["relative_position"] is not None
                else None,
            }
        insight = price_insight(product, saved_prices.get(pid), stats)
        price_blocks.append(
            {
                "product_id": pid,
                "current": insight["current_price"],
                "saved": insight["saved_price"],
                "min": insight["min_price"],
                "max": insight["max_price"],
                "relative_position": insight["relative_position"],
                "history_available": insight["history_available"],
            }
        )

    similar = []
    if product_ids:
        for edge in similarity_repo.list_similar_for_product(conn, product_ids[0], limit=5):
            if edge["similar_product_id"] in wl_ids:
                similar.append(
                    {
                        "id": edge["similar_product_id"],
                        "score": edge["score"],
                        "reason": edge["reason"],
                    }
                )

    compare = (
        comparison_scores(
            products,
            insights_map,
            tradeoff_priority=tradeoff_priority,
            need=need,
        )
        if len(products) >= 2
        else None
    )

    has_history = any(pb.get("history_available") for pb in price_blocks)
    avg_reviews = sum(review_counts.get(pid, 0) for pid in product_ids) // max(len(product_ids), 1)
    avg_insights = sum(len(insights_map.get(pid, [])) for pid in product_ids) // max(
        len(product_ids), 1
    )

    missing = collect_missing(
        has_price_history=has_history,
        review_count=avg_reviews,
        insight_count=avg_insights,
    )

    pref_scores = {
        p["product_id"]: preference_match(p, user) for p in products
    }

    return {
        "products": products,
        "price": price_blocks,
        "reviews": {
            pid: _review_themes(insights_map.get(pid, []), review_counts.get(pid, 0))
            for pid in product_ids
        },
        "review_counts": review_counts,
        "similar": similar,
        "user": user,
        "scores": compare["scores"] if compare else {},
        "labels": compare["labels"] if compare else {},
        "need_assessment": compare.get("need_assessment", {}) if compare else {},
        "need": need,
        "tradeoff_priority": compare.get("tradeoff_priority") if compare else tradeoff_priority,
        "preference_match": pref_scores,
        "confidence": confidence_from_evidence(
            has_price_history=has_history,
            review_count=avg_reviews,
            insight_count=avg_insights,
            compare_count=len(product_ids),
        ),
        "missing": missing,
        "language_rules": LANGUAGE_RULES,
    }


def build_compare_pack(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "task": "COMPARE",
        "products": context["products"],
        "price": context["price"],
        "reviews": context["reviews"],
        "labels": context.get("labels", {}),
        "scores": context.get("scores", {}),
        "need": context.get("need"),
        "tradeoff_priority": context.get("tradeoff_priority"),
        "need_assessment": context.get("need_assessment", {}),
        "user_confidence": context.get("user_confidence"),
        "confidence": context["confidence"],
        "missing": context["missing"],
        "language_rules": context["language_rules"],
    }


def build_question_pack(
    question_id: str,
    context: dict[str, Any],
    product_id: str | None = None,
) -> dict[str, Any]:
    pack: dict[str, Any] = {
        "question_id": question_id,
        "products": context["products"],
        "price": context["price"],
        "reviews": context["reviews"],
        "similar": context["similar"],
        "user": context["user"],
        "scores": context.get("scores", {}),
        "labels": context.get("labels", {}),
        "preference_match": context.get("preference_match", {}),
        "confidence": context["confidence"],
        "missing": list(context["missing"]),
        "language_rules": context["language_rules"],
    }

    if question_id == "WHAT_BUYERS_DISLIKE":
        pid = product_id or (context["products"][0]["product_id"] if context["products"] else None)
        themes = context["reviews"].get(pid, []) if pid else []
        pack["negative_themes"] = [t for t in themes if (t.get("negative") or 0) > 0]

    if question_id == "IS_FIT_RELIABLE":
        pid = product_id or (context["products"][0]["product_id"] if context["products"] else None)
        product = next((p for p in context["products"] if p["product_id"] == pid), None)
        pack["fit_attribute"] = product.get("fit") if product else None
        themes = context["reviews"].get(pid, []) if pid else []
        pack["fit_themes"] = [t for t in themes if t.get("theme") in ("FIT", "SIZE")]

    if question_id == "FABRIC_QUALITY":
        pid = product_id or (context["products"][0]["product_id"] if context["products"] else None)
        product = next((p for p in context["products"] if p["product_id"] == pid), None)
        pack["material"] = product.get("material") if product else None
        themes = context["reviews"].get(pid, []) if pid else []
        pack["fabric_themes"] = [
            t for t in themes if t.get("theme") in ("FABRIC", "QUALITY", "COMFORT")
        ]

    if question_id == "SHOULD_I_WAIT":
        pack["missing"] = [m for m in pack["missing"] if m != "price_history"]
        if not any(p.get("history_available") for p in context["price"]):
            pack["missing"].append("price_history")

    if question_id == "WHY_BETTER_THAN_B" and len(context["products"]) == 2:
        pack["pairwise"] = {
            "a": context["products"][0]["product_id"],
            "b": context["products"][1]["product_id"],
        }

    return pack


def pack_has_evidence(pack: dict[str, Any]) -> bool:
    """True if pack has enough data to call Groq (not only missing flags)."""
    if pack.get("products"):
        return True
    return False


def pack_only_missing(pack: dict[str, Any]) -> bool:
    missing = pack.get("missing") or []
    if not pack.get("products"):
        return True
    if question_id := pack.get("question_id"):
        if question_id == "SHOULD_I_WAIT" and "price_history" in missing:
            prices = pack.get("price") or []
            if not any(p.get("history_available") for p in prices):
                return True
        if question_id == "WHAT_BUYERS_DISLIKE":
            themes = pack.get("negative_themes") or []
            if not themes and "review_insights" in missing:
                return True
    return False
