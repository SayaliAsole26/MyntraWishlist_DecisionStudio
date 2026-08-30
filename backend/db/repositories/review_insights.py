import sqlite3

from backend.db.util import parse_json_list


def list_insights_for_product(conn: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT theme, positive_count, negative_count, summary,
               evidence_review_ids, confidence
        FROM review_insights
        WHERE product_id = ?
        ORDER BY theme
        """,
        (product_id,),
    ).fetchall()
    return [
        {
            "theme": r["theme"],
            "positive_count": r["positive_count"],
            "negative_count": r["negative_count"],
            "summary": r["summary"],
            "evidence_review_ids": parse_json_list(r["evidence_review_ids"]),
            "confidence": r["confidence"],
        }
        for r in rows
    ]


def list_insights_for_products(
    conn: sqlite3.Connection, product_ids: list[str]
) -> dict[str, list[dict]]:
    if not product_ids:
        return {}
    placeholders = ",".join("?" * len(product_ids))
    rows = conn.execute(
        f"""
        SELECT product_id, theme, positive_count, negative_count, summary,
               evidence_review_ids, confidence
        FROM review_insights
        WHERE product_id IN ({placeholders})
        ORDER BY product_id, theme
        """,
        product_ids,
    ).fetchall()
    out: dict[str, list[dict]] = {pid: [] for pid in product_ids}
    for r in rows:
        out[r["product_id"]].append(
            {
                "theme": r["theme"],
                "positive_count": r["positive_count"],
                "negative_count": r["negative_count"],
                "summary": r["summary"],
                "evidence_review_ids": parse_json_list(r["evidence_review_ids"]),
                "confidence": r["confidence"],
            }
        )
    return out
