"""Rank wishlist candidates and return top 3 by need + trade-off relevance."""

from typing import Any

from backend.db.repositories import products as products_repo
from backend.db.repositories import review_insights as insights_repo
from backend.decision.tradeoff import relevance_score


def rank_and_shortlist(
    conn,
    product_ids: list[str],
    *,
    user_id: str = "U001",
    need: str | None = None,
    tradeoff_priority: str | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    if not product_ids:
        raise ValueError("product_ids required")

    products = []
    for pid in product_ids:
        p = products_repo.get_product(conn, pid)
        if p:
            products.append(p.model_dump())

    if not products:
        raise ValueError("No valid products to rank")

    insights_map = insights_repo.list_insights_for_products(conn, [p["product_id"] for p in products])
    max_price = max(int(p.get("price") or 0) for p in products)
    tradeoff = tradeoff_priority or "QUALITY"

    ranked: list[dict[str, Any]] = []
    for product in products:
        pid = product["product_id"]
        insights = insights_map.get(pid, [])
        scored = relevance_score(
            product,
            insights,
            need=need,
            tradeoff=tradeoff,
            max_price=max_price,
        )
        ranked.append(scored)

    ranked.sort(key=lambda r: r["overall"], reverse=True)
    top = ranked[:limit]

    return {
        "from_count": len(product_ids),
        "product_ids": [r["product_id"] for r in top],
        "ranked": top,
        "need": need,
        "tradeoff_priority": tradeoff,
    }
