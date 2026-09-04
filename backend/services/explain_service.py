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

    by_id = {p["product_id"]: p for p in products}

    def pname(pid: str) -> str:
        p = by_id.get(pid, {})
        return f"{p.get('brand', '')} {p.get('name', '')}".strip() or pid

    facts = []
    for p in products:
        facts.append(
            f"{p.get('brand')} {p.get('name')} is ₹{p.get('price')} (rating {p.get('rating')})."
        )

    best = labels.get("best_balance") or labels.get("best_value")
    if not best and products:
        best = min(products, key=lambda p: (p.get("price") or 10**9)).get("product_id")

    reviewed = labels.get("best_reviewed")
    value = labels.get("best_value")

    if q == "WHICH_ONE_SHOULD_I_BUY" and best:
        interpretation = (
            f"{pname(best)} is the strongest overall pick from this shortlist "
            f"based on price, rating, and balance across your options."
        )
        recommendation = interpretation
        if value and value != best:
            facts.append(f"{pname(value)} leads if you care most about price.")
        if reviewed and reviewed != best:
            facts.append(f"{pname(reviewed)} leads on buyer ratings.")
    elif q in ("WHICH_BEST_VALUE",) and (value or best):
        pick = value or best
        interpretation = f"{pname(pick)} offers the best value in this set."
        recommendation = interpretation
    elif q in ("WHICH_MOST_REVIEWED",) and (reviewed or best):
        pick = reviewed or best
        interpretation = f"{pname(pick)} has the strongest rating signal among these items."
        recommendation = interpretation
    elif q in ("PRICE_VS_QUALITY",) and best:
        interpretation = (
            f"{pname(best)} balances price and quality best in this comparison."
        )
        recommendation = interpretation
    elif q == "WORTH_THE_PRICE":
        interpretation = (
            "Use the price and review panels with the comparison table to judge value. "
            "Current list prices and ratings are shown in Facts."
        )
        recommendation = interpretation
    elif q == "SHOULD_I_WAIT":
        if "price_history" in missing:
            interpretation = (
                "Recent price history isn’t available yet, so a wait-vs-buy call isn’t reliable. "
                "Compare current prices and ratings instead."
            )
        else:
            interpretation = (
                "Check price insight for where today’s price sits in the recent range, "
                "then decide with the comparison table."
            )
        recommendation = interpretation
    elif best:
        interpretation = f"From the available scores, {pname(best)} looks like the safest pick."
        recommendation = interpretation
    else:
        interpretation = (
            "You can still compare price, rating, and reviews in the table above to decide."
        )
        recommendation = interpretation

    base.update(
        {
            "facts": facts,
            "interpretation": interpretation,
            "recommendation": recommendation,
            "answer": recommendation,
            "tradeoffs": [],
            # Keep missing for engine/debug, but UI no longer surfaces it.
            "missing": missing,
            "groq_used": False,
            "available": True,
        }
    )
    return base
