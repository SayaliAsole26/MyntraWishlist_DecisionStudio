"""Groq explainers with JSON parsing and fallbacks."""

import json
from pathlib import Path
from typing import Any

from backend.llm.client import LlmClient, LlmNotConfiguredError, LlmUnavailableError

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "llm" / "prompts"

FALLBACK_MSG = (
    "Decision insight temporarily unavailable. "
    "You can still compare price, rating, and reviews."
)


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _parse_json_object(raw: str) -> dict[str, Any]:
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start < 0 or end <= start:
        raise LlmUnavailableError("No JSON object in LLM response")
    return json.loads(raw[start:end])


def _call_quality(
    pack: dict[str, Any], prompt_file: str, *, context: str
) -> dict[str, Any]:
    llm = LlmClient()
    system = _load_prompt(prompt_file)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(pack, ensure_ascii=False)},
    ]
    raw = llm.complete_quality(messages, context=context)
    return _parse_json_object(raw)


def explain_comparison(pack: dict[str, Any]) -> dict[str, Any]:
    try:
        data = _call_quality(pack, "compare_explain.txt", context="POST /api/wishlist/compare")
        interpretation = (data.get("interpretation") or "").strip()
        if not interpretation:
            return _fallback_compare_explanation(pack)
        return {
            "available": True,
            "groq_used": True,
            "interpretation": interpretation,
            "tradeoffs": data.get("tradeoffs") or [],
            "text": interpretation,
        }
    except (LlmNotConfiguredError, LlmUnavailableError, json.JSONDecodeError):
        return _fallback_compare_explanation(pack)


def _fallback_compare_explanation(pack: dict[str, Any]) -> dict[str, Any]:
    labels = pack.get("labels") or {}
    products = pack.get("products") or []
    by_id = {p["product_id"]: p for p in products}
    need = pack.get("need")
    tradeoff = pack.get("tradeoff_priority") or "QUALITY"
    need_assessment = pack.get("need_assessment") or {}

    def pname(pid: str) -> str:
        p = by_id.get(pid, {})
        return f"{p.get('brand', '')} {p.get('name', '')}".strip() or pid

    best_id = labels.get("best_balance")
    tradeoffs: list[str] = []

    if best_id:
        top_need = need_assessment.get(best_id, {})
        if need and top_need.get("reason"):
            tradeoffs.append(top_need["reason"])

        for pid in labels.values():
            if pid == best_id:
                continue
            alt = need_assessment.get(pid, {})
            if need and alt.get("level") in ("strong", "partial") and top_need.get("level") == "poor":
                tradeoffs.append(
                    f"{pname(pid)} may suit {need.lower()} better: {alt.get('reason', '')}"
                )

    if labels.get("best_value") and labels.get("best_value") != best_id:
        tradeoffs.append(f"{pname(labels['best_value'])} leads on value if price matters most.")

    if labels.get("best_reviewed") and labels.get("best_reviewed") != best_id:
        tradeoffs.append(f"{pname(labels['best_reviewed'])} has the strongest buyer ratings.")

    priority_map = {
        "FIT": "fit and sizing signals",
        "VALUE": "price and discount",
        "QUALITY": "review quality themes",
        "VERSATILITY": "occasion versatility",
    }
    priority_txt = priority_map.get(str(tradeoff).upper(), "overall balance")

    if best_id:
        interpretation = (
            f"Top pick for {need.lower() if need else 'this shortlist'} "
            f"(prioritising {priority_txt}): {pname(best_id)}."
        )
        if need and need_assessment.get(best_id, {}).get("level") == "poor":
            interpretation += (
                " This choice scores well on your priority but is a weak match for your stated need — "
                "see the need-fit notes below."
            )
    else:
        interpretation = FALLBACK_MSG

    if not tradeoffs:
        tradeoffs = [
            "Change need or trade-off priority above to re-rank this shortlist.",
        ]

    return {
        "available": True,
        "groq_used": False,
        "interpretation": interpretation,
        "tradeoffs": tradeoffs,
        "text": interpretation,
    }


def answer_from_pack(pack: dict[str, Any]) -> dict[str, Any]:
    confidence = pack.get("confidence", "LOW")
    missing = pack.get("missing") or []

    base = {
        "confidence": confidence,
        "missing": missing,
        "facts": [],
        "evidence": [],
        "positive_signals": [],
        "concerns": [],
        "tradeoffs": [],
        "interpretation": "",
        "recommendation": "",
        "answer": "",
        "groq_used": False,
    }

    if not pack.get("products"):
        base["answer"] = "Not enough data to answer this reliably."
        base["interpretation"] = base["answer"]
        return base

    try:
        data = _call_quality(
            pack,
            "question_answer.txt",
            context="POST /api/questions/answer",
        )
        base.update(
            {
                "answer": data.get("answer") or "",
                "facts": data.get("facts") or [],
                "evidence": data.get("evidence") or [],
                "interpretation": data.get("interpretation") or "",
                "recommendation": data.get("recommendation") or "",
                "tradeoffs": data.get("tradeoffs") or [],
                "groq_used": True,
            }
        )
        return base
    except (LlmNotConfiguredError, LlmUnavailableError, json.JSONDecodeError):
        return _fallback_answer(pack, base)


def _fallback_answer(pack: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    q = pack.get("question_id", "")
    products = pack.get("products") or []
    labels = pack.get("labels") or {}
    missing = pack.get("missing") or []

    facts = []
    for p in products:
        facts.append(f"{p.get('brand')} {p.get('name')} is ₹{p.get('price')} (rating {p.get('rating')}).")

    if "price_history" in missing:
        facts.append("Price history is unavailable for at least one item.")

    interpretation = FALLBACK_MSG
    recommendation = ""

    if q == "WHICH_ONE_SHOULD_I_BUY" and labels:
        best = labels.get("best_balance") or labels.get("best_value")
        prefs = (pack.get("user") or {}).get("priorities") or []
        pref_txt = prefs[0] if prefs else "your preferences"
        recommendation = (
            f"Based on scores only, {best} is the best balance. "
            f"A full recommendation needs Groq — weigh {pref_txt.lower()} against the comparison table."
        )
        interpretation = recommendation
    elif q == "WORTH_THE_PRICE":
        interpretation = (
            "Compare current price to saved price and review themes using the insight panels. "
            + FALLBACK_MSG
        )
    elif q == "SHOULD_I_WAIT":
        interpretation = (
            "Price history alone cannot predict future drops. "
            + ("Historical range is unavailable." if "price_history" in missing else "See price insight for position in recent range.")
        )

    base.update(
        {
            "facts": facts,
            "interpretation": interpretation,
            "recommendation": recommendation or interpretation,
            "answer": recommendation or "See comparison numbers",
            "tradeoffs": [FALLBACK_MSG],
        }
    )
    return base
