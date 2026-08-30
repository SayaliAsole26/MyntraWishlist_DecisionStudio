"""Ask Me a Question — closed enum, evidence pack, optional Groq."""

import json
import sqlite3
from pathlib import Path

from backend.decision.evidence_pack import (
    build_question_pack,
    load_context,
    pack_has_evidence,
)
from backend.services.explain_service import answer_from_pack, _fallback_answer

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "llm" / "question_registry.json"


def _load_registry() -> dict[str, dict]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {q["question_id"]: q for q in data["questions"]}


REGISTRY = _load_registry()
VALID_QUESTIONS = set(REGISTRY.keys())


def _resolve_product_ids(
    question_id: str,
    product_id: str | None,
    product_ids: list[str] | None,
    wishlist_ids: set[str],
) -> list[str]:
    meta = REGISTRY[question_id]
    if product_ids:
        ids = product_ids
    elif product_id:
        ids = [product_id]
    else:
        ids = []

    if len(ids) < meta["min_products"]:
        raise ValueError(f"{question_id} requires at least {meta['min_products']} product(s) on Wishlist")
    if len(ids) > meta["max_products"]:
        raise ValueError(f"{question_id} allows at most {meta['max_products']} products")

    for pid in ids:
        if pid not in wishlist_ids:
            raise ValueError(f"Product {pid} must be on your Wishlist")

    return ids


def answer_question(
    conn: sqlite3.Connection,
    user_id: str,
    question_id: str,
    product_id: str | None = None,
    product_ids: list[str] | None = None,
) -> dict:
    if question_id not in VALID_QUESTIONS:
        raise ValueError(f"Unknown question_id: {question_id}")

    from backend.db.repositories import wishlist as wishlist_repo

    wl = wishlist_repo.list_wishlist(conn, user_id)
    wishlist_ids = {i.product_id for i in wl}
    ids = _resolve_product_ids(question_id, product_id, product_ids, wishlist_ids)

    context = load_context(conn, user_id, ids)
    pack = build_question_pack(question_id, context, product_id=product_id or (ids[0] if len(ids) == 1 else None))

    if not pack_has_evidence(pack):
        return _fallback_answer(
            pack,
            {
                "confidence": pack.get("confidence", "LOW"),
                "missing": pack.get("missing", []),
                "facts": [],
                "evidence": [],
                "positive_signals": [],
                "concerns": [],
                "tradeoffs": [],
                "interpretation": "Not enough data to answer this reliably.",
                "recommendation": "",
                "answer": "Not enough data",
                "groq_used": False,
                "question_id": question_id,
            },
        )

    result = answer_from_pack(pack)
    result["question_id"] = question_id
    result["labels"] = context.get("labels", {})

    for pid, themes in context.get("reviews", {}).items():
        for t in themes:
            if (t.get("positive") or 0) > (t.get("negative") or 0):
                result.setdefault("positive_signals", []).append(t["theme"].title())
            elif (t.get("negative") or 0) > 0:
                result.setdefault("concerns", []).append(t["theme"].title())

    return result


def list_questions(product_count: int = 1, offset: int = 0, limit: int = 4) -> list[dict]:
    eligible = []
    for qid, meta in REGISTRY.items():
        if product_count >= meta["min_products"] and product_count <= meta["max_products"]:
            eligible.append({"question_id": qid, "label": meta["label"]})

    if not eligible:
        return []

    start = offset % len(eligible)
    rotated = eligible[start:] + eligible[:start]
    return rotated[: min(limit, len(rotated))]
