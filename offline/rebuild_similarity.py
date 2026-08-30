"""Attribute-based product_similarity graph. Explainable, no embeddings."""

import json
import sqlite3
from datetime import datetime, timezone

from backend.db.session import get_connection
from backend.db.util import parse_json_list


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _attrs(row: sqlite3.Row) -> dict:
    try:
        data = json.loads(row["attributes_json"] or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _occasion_overlap(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    overlap = len(set(a) & set(b))
    return overlap / max(len(set(a) | set(b)), 1)


def _price_proximity(price_a: int, price_b: int) -> float:
    hi = max(price_a, price_b, 1)
    return max(0.0, 1.0 - abs(price_a - price_b) / hi)


def _similarity_score(row_a: sqlite3.Row, row_b: sqlite3.Row) -> tuple[float, list[str], str]:
    attrs_a = _attrs(row_a)
    attrs_b = _attrs(row_b)
    occasions_a = parse_json_list(row_a["occasions"])
    occasions_b = parse_json_list(row_b["occasions"])
    colors_a = parse_json_list(row_a["colors"])
    colors_b = parse_json_list(row_b["colors"])

    matched: list[str] = []
    score = 0.0

    if row_a["category"] and row_a["category"] == row_b["category"]:
        score += 0.25
        matched.append("category")
    if row_a["subcategory"] and row_a["subcategory"] == row_b["subcategory"]:
        score += 0.15
        matched.append("subcategory")
    if row_a["style"] and row_a["style"] == row_b["style"]:
        score += 0.1
        matched.append("style")
    if row_a["material"] and row_a["material"] == row_b["material"]:
        score += 0.1
        matched.append("material")
    if row_a["fit"] and row_a["fit"] == row_b["fit"]:
        score += 0.1
        matched.append("fit")
    if row_a["brand"] == row_b["brand"]:
        score += 0.05
        matched.append("brand")

    occ = _occasion_overlap(occasions_a, occasions_b)
    if occ > 0:
        score += occ * 0.15
        matched.append("occasions")

    if colors_a and colors_b and set(colors_a) & set(colors_b):
        score += 0.05
        matched.append("colors")

    score += _price_proximity(int(row_a["price"]), int(row_b["price"])) * 0.15
    matched.append("price_proximity")

    group_a = attrs_a.get("similar_group")
    group_b = attrs_b.get("similar_group")
    if group_a and group_a == group_b:
        score += 0.35
        matched.append("similar_group")

    score = round(min(score, 1.0), 3)

    if group_a and group_a == group_b:
        reason = f"Same {row_a['category'] or 'category'} group with similar attributes"
    elif row_a["category"] == row_b["category"]:
        reason = f"Same category ({row_a['category']}), similar price and style"
    else:
        reason = "Related attributes and price range"

    return score, matched, reason


def rebuild_similarity(conn: sqlite3.Connection | None = None, threshold: float = 0.45) -> dict:
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    products = conn.execute("SELECT * FROM products ORDER BY product_id").fetchall()
    conn.execute("DELETE FROM product_similarity")
    edges = 0

    for i, row_a in enumerate(products):
        for row_b in products[i + 1 :]:
            score, matched, reason = _similarity_score(row_a, row_b)
            if score < threshold:
                continue
            attrs_json = json.dumps(matched)
            for pid, sid in ((row_a["product_id"], row_b["product_id"]), (row_b["product_id"], row_a["product_id"])):
                conn.execute(
                    """
                    INSERT INTO product_similarity (
                        product_id, similar_product_id, score, matched_attributes, reason
                    ) VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(product_id, similar_product_id) DO UPDATE SET
                        score = excluded.score,
                        matched_attributes = excluded.matched_attributes,
                        reason = excluded.reason
                    """,
                    (pid, sid, score, attrs_json, reason),
                )
                edges += 1

    conn.commit()
    if own_conn:
        conn.close()
    return {"edges_written": edges, "products": len(products)}


def main() -> int:
    result = rebuild_similarity()
    print(f"similarity graph: {result['edges_written']} edges for {result['products']} products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
