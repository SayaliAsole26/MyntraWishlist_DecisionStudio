"""Offline job: reviews → review_insights (Groq FAST or deterministic fallback)."""

import json
import sqlite3
from datetime import datetime, timezone

from backend.db.session import get_connection
from backend.llm.client import LlmClient, LlmNotConfiguredError, LlmUnavailableError
from backend.db.repositories.reviews import list_product_ids_with_reviews, list_reviews_for_product
from offline.insight_extractor import extract_themes_from_reviews

PROMPT_PATH = __import__("pathlib").Path(__file__).resolve().parent.parent / "backend" / "llm" / "prompts" / "review_analysis.txt"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _upsert_insights(conn: sqlite3.Connection, product_id: str, themes: list[dict]) -> int:
    now = _now_iso()
    conn.execute("DELETE FROM review_insights WHERE product_id = ?", (product_id,))
    count = 0
    for t in themes:
        conn.execute(
            """
            INSERT INTO review_insights (
                product_id, theme, positive_count, negative_count, summary,
                evidence_review_ids, confidence, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                t["theme"],
                t.get("positive_count", 0),
                t.get("negative_count", 0),
                t.get("summary"),
                json.dumps(t.get("evidence_review_ids") or []),
                t.get("confidence", "LOW"),
                now,
            ),
        )
        count += 1
    conn.commit()
    return count


def _analyze_with_groq(product_id: str, reviews: list[dict], llm: LlmClient) -> list[dict]:
    system = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else (
        "Extract themes from reviews. Return JSON array only."
    )
    payload = [
        {"review_id": r["review_id"], "rating": r["rating"], "text": r["review_text"]}
        for r in reviews[:50]
    ]
    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": json.dumps({"product_id": product_id, "reviews": payload}, ensure_ascii=False),
        },
    ]
    raw = llm.complete_fast(messages, context="offline/rebuild_insights")
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start < 0 or end <= start:
        raise LlmUnavailableError("Could not parse Groq theme JSON")
    themes = json.loads(raw[start:end])
    return themes


def rebuild_insights(conn: sqlite3.Connection | None = None, use_groq: bool = True) -> dict:
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    llm = LlmClient()
    product_ids = list_product_ids_with_reviews(conn)
    total_rows = 0
    groq_used = 0
    fallback_used = 0

    for product_id in product_ids:
        reviews = list_reviews_for_product(conn, product_id)
        if not reviews:
            continue

        themes: list[dict]
        if use_groq and llm.configured:
            try:
                themes = _analyze_with_groq(product_id, reviews, llm)
                groq_used += 1
            except (LlmNotConfiguredError, LlmUnavailableError, json.JSONDecodeError):
                themes = extract_themes_from_reviews(reviews)
                fallback_used += 1
        else:
            themes = extract_themes_from_reviews(reviews)
            fallback_used += 1

        total_rows += _upsert_insights(conn, product_id, themes)

    if own_conn:
        conn.close()

    return {
        "products_processed": len(product_ids),
        "insight_rows": total_rows,
        "groq_used": groq_used,
        "fallback_used": fallback_used,
    }


def main() -> int:
    result = rebuild_insights()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
