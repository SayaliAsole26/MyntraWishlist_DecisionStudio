"""Decision overload — cluster Wishlist items online (no LLM)."""

import sqlite3

# Trigger after a few similar saves so the wishlist popup feels useful in demos.
OVERLOAD_THRESHOLD = 3
SIMILARITY_EDGE_THRESHOLD = 0.45


def _group_label(category: str | None, subcategory: str | None) -> str:
    cat = (category or "items").lower()
    sub = (subcategory or "").lower()
    if "dress" in sub or cat in ("dress", "dresses"):
        return "dresses"
    if "kurta" in cat or "kurta" in sub:
        return "kurtas"
    if "sneaker" in sub or "shoe" in sub or cat in ("sneakers", "shoes"):
        return "sneakers"
    if "sandal" in cat or "sandal" in sub:
        return "sandals"
    if "bag" in sub or "handbag" in sub or cat in ("bags", "handbags"):
        return "handbags"
    if "jean" in sub or cat == "jeans":
        return "jeans"
    if "top" in sub or cat in ("tops", "top"):
        return "tops"
    return cat


def _category_groups(products: list[dict]) -> dict[str, list[str]]:
    """Group by soft category label so similar styles still cluster across subcategories."""
    groups: dict[str, list[str]] = {}
    for p in products:
        label = _group_label(p.get("category"), p.get("subcategory"))
        groups.setdefault(label, []).append(p["product_id"])
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

    by_id = {p["product_id"]: p for p in products}
    seen_keys: set[str] = set()
    groups: list[dict] = []

    for label, pids in _category_groups(products).items():
        if len(pids) < threshold:
            continue
        sample = next(p for p in products if p["product_id"] in pids)
        group_key = f"cat:{label}"
        if group_key in seen_keys:
            continue
        seen_keys.add(group_key)
        groups.append(
            {
                "group_key": group_key,
                "category": sample.get("category"),
                "subcategory": sample.get("subcategory"),
                "count": len(pids),
                "product_ids": sorted(pids),
                "label": label,
            }
        )

    # Similarity clusters only within the same soft category — never mix kurtas + sandals.
    for label, pids in _category_groups(products).items():
        if len(pids) < threshold:
            continue
        # Already have a category group covering these ids.
        if any(g["label"] == label and set(pids).issubset(set(g["product_ids"])) for g in groups):
            continue
        for component in _similarity_clusters(conn, pids):
            if len(component) < threshold:
                continue
            group_key = f"sim:{label}:{','.join(component)}"
            if group_key in seen_keys:
                continue
            covered = any(
                set(component).issubset(set(g["product_ids"])) for g in groups
            )
            if covered:
                continue
            seen_keys.add(group_key)
            sample = by_id[component[0]]
            groups.append(
                {
                    "group_key": group_key,
                    "category": sample.get("category"),
                    "subcategory": sample.get("subcategory"),
                    "count": len(component),
                    "product_ids": component,
                    "label": label,
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
