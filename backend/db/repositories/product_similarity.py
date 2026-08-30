import sqlite3

from backend.db.util import parse_json_list


def list_similar_for_product(
    conn: sqlite3.Connection, product_id: str, limit: int = 10
) -> list[dict]:
    rows = conn.execute(
        """
        SELECT similar_product_id, score, matched_attributes, reason
        FROM product_similarity
        WHERE product_id = ?
        ORDER BY score DESC
        LIMIT ?
        """,
        (product_id, limit),
    ).fetchall()
    return [
        {
            "similar_product_id": r["similar_product_id"],
            "score": r["score"],
            "matched_attributes": parse_json_list(r["matched_attributes"]),
            "reason": r["reason"],
        }
        for r in rows
    ]
