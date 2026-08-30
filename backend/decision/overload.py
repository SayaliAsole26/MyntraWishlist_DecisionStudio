"""Decision overload — cluster Wishlist items online (no LLM)."""

import sqlite3

OVERLOAD_THRESHOLD = 6
SIMILARITY_EDGE_THRESHOLD = 0.45


def _group_label(category: str | None, subcategory: str | None) -> str:
    cat = (category or "items").lower()
    if subcategory:
        sub = subcategory.lower()
        if "dress" in sub or cat == "dresses":
            return "dresses"
        if "sneaker" in sub or "shoe" in sub:
            return "sneakers"
        if "bag" in sub or "handbag" in sub:
            return "handbags"
        if "jean" in sub:
            return "jeans"
        if "top" in sub:
            return "tops"
    return cat


def _category_groups(products: list[dict]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for p in products:
        key = f"{p.get('category') or ''}|{p.get('subcategory') or ''}"
        groups.setdefault(key, []).append(p["product_id"])
    return groups


def _similarity_clusters(
    conn: sqlite3.Connection, product_ids: list[str]
) -> list[list[str]]:
    if len(product_ids) < OVERLOAD_THRESHOLD:
        return []

    id_set = set(product_ids)
    edges: dict[str, set[str]] = {pid: set() for pid in product_ids}

    placeholders = ",".join("?" * len(product_ids))
    rows = conn.execute(
        f"""
        SELECT product_id, similar_product_id, score
        FROM product_similarity
        WHERE product_id IN ({placeholders})
          AND similar_product_id IN ({placeholders})
          AND score >= ?
        """,
        (*product_ids, *product_ids, SIMILARITY_EDGE_THRESHOLD),
    ).fetchall()

    for row in rows:
        a, b = row["product_id"], row["similar_product_id"]
        if a in id_set and b in id_set:
            edges[a].add(b)
            edges[b].add(a)

    visited: set[str] = set()
    clusters: list[list[str]] = []

    for pid in product_ids:
        if pid in visited:
            continue
        stack = [pid]
        component: list[str] = []
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            for neighbor in edges[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
        if len(component) >= OVERLOAD_THRESHOLD:
            clusters.append(sorted(component))

    return clusters


def detect_overload_groups(
    conn: sqlite3.Connection,
    products: list[dict],
    threshold: int = OVERLOAD_THRESHOLD,
) -> list[dict]:
    """Return overload groups with count >= threshold."""
    if len(products) < threshold:
        return []

    seen_keys: set[str] = set()
    groups: list[dict] = []

    for key, pids in _category_groups(products).items():
        if len(pids) < threshold:
            continue
        category, subcategory = key.split("|", 1) if "|" in key else (key, "")
        sample = next(p for p in products if p["product_id"] in pids)
        label = _group_label(sample.get("category"), sample.get("subcategory"))
        group_key = f"cat:{key}"
        if group_key in seen_keys:
            continue
        seen_keys.add(group_key)
        groups.append(
            {
                "group_key": group_key,
                "category": category or None,
                "subcategory": subcategory or None,
                "count": len(pids),
                "product_ids": sorted(pids),
                "label": label,
            }
        )

    product_ids = [p["product_id"] for p in products]
    for component in _similarity_clusters(conn, product_ids):
        if len(component) < threshold:
            continue
        group_key = f"sim:{','.join(component)}"
        if group_key in seen_keys:
            continue
        # Skip if already covered by a larger category group with same ids
        subset_of_cat = any(
            set(component).issubset(set(g["product_ids"])) and g["count"] >= threshold
            for g in groups
        )
        if subset_of_cat:
            continue
        seen_keys.add(group_key)
        sample = next(p for p in products if p["product_id"] == component[0])
        groups.append(
            {
                "group_key": group_key,
                "category": sample.get("category"),
                "subcategory": sample.get("subcategory"),
                "count": len(component),
                "product_ids": component,
                "label": _group_label(sample.get("category"), sample.get("subcategory")),
            }
        )

    groups.sort(key=lambda g: g["count"], reverse=True)
    return groups


def products_from_wishlist_items(items) -> list[dict]:
    return [
        {
            "product_id": item.product_id,
            "category": item.product.category,
            "subcategory": item.product.subcategory,
            "price": item.product.price,
            "rating": item.product.rating,
            "occasions": item.product.occasions or [],
        }
        for item in items
    ]
