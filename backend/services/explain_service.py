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
    reviews = pack.get("reviews") or {}
    prices = pack.get("price") or []

    by_id = {p["product_id"]: p for p in products}

    def pname(pid: str) -> str:
        p = by_id.get(pid, {})
        return f"{p.get('brand', '')} {p.get('name', '')}".strip() or pid

    def themes_for(pid: str) -> list[dict]:
        return reviews.get(pid) or []

    def theme_summary(pid: str, names: set[str]) -> str | None:
        for t in themes_for(pid):
            if t.get("theme") in names and t.get("summary"):
                return str(t["summary"])
        return None

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
    primary = products[0]["product_id"] if products else None

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
    elif q == "WHY_BETTER_THAN_B" and len(products) >= 2:
        a, b = products[0]["product_id"], products[1]["product_id"]
        pick = best or a
        other = b if pick == a else a
        interpretation = (
            f"{pname(pick)} edges out {pname(other)} on the combined price and rating balance."
        )
        recommendation = interpretation
    elif q == "WORTH_THE_PRICE" and primary:
        tip = theme_summary(primary, {"VALUE", "QUALITY"}) or ""
        price_row = next((x for x in prices if x.get("product_id") == primary), {})
        pos = price_row.get("relative_position")
        price_note = (
            "Current price sits near the low end of its recent range."
            if isinstance(pos, (int, float)) and pos <= 0.35
            else "Current price is within its recent range."
            if isinstance(pos, (int, float))
            else "Current list price and rating are available to judge value."
        )
        interpretation = f"{price_note} {tip}".strip()
        recommendation = (
            f"{pname(primary)} looks reasonable at ₹{by_id[primary].get('price')} "
            f"given its {by_id[primary].get('rating')} rating."
        )
    elif q == "WHAT_BUYERS_DISLIKE" and primary:
        negatives = [
            t for t in themes_for(primary) if (t.get("negative") or 0) > 0
        ]
        if negatives:
            top = max(negatives, key=lambda t: t.get("negative") or 0)
            interpretation = (
                top.get("summary")
                or f"Buyers most often mention concerns around {str(top.get('theme')).title()}."
            )
            facts.extend(
                f"{str(t.get('theme')).title()}: {t.get('negative')} critical mentions"
                for t in negatives[:3]
            )
        else:
            interpretation = "No strong dislike themes stand out in the available buyer feedback."
        recommendation = interpretation
    elif q in ("IS_FIT_RELIABLE", "RUNS_TRUE_TO_SIZE") and primary:
        tip = theme_summary(primary, {"FIT", "SIZE"}) or "Fit feedback is available from buyers."
        fit_attr = by_id[primary].get("fit")
        interpretation = tip
        recommendation = (
            f"Listed fit is {fit_attr}. {tip}" if fit_attr else tip
        )
    elif q == "FABRIC_QUALITY" and primary:
        tip = theme_summary(primary, {"FABRIC", "QUALITY", "COMFORT"}) or (
            f"Material listed as {by_id[primary].get('material') or 'not specified'}."
        )
        interpretation = tip
        recommendation = tip
    elif q == "SHOULD_I_WAIT" and primary:
        price_row = next((x for x in prices if x.get("product_id") == primary), {})
        if price_row.get("history_available"):
            pos = price_row.get("relative_position")
            if isinstance(pos, (int, float)) and pos <= 0.3:
                interpretation = (
                    "Price is already near the lower end of its recent range — waiting may not help much."
                )
            elif isinstance(pos, (int, float)) and pos >= 0.7:
                interpretation = (
                    "Price is toward the higher end of its recent range — a short wait could help if deals matter."
                )
            else:
                interpretation = (
                    "Price is mid-range historically — buy if you like the product; otherwise watch for a small dip."
                )
        else:
            interpretation = (
                "Compare current price and rating now; historical movement isn’t the deciding factor alone."
            )
        recommendation = interpretation
    elif q in ("GOOD_FOR_DAILY_WEAR", "COMFORT_LEVEL") and primary:
        tip = theme_summary(primary, {"COMFORT", "FIT", "OCCASION"}) or (
            "Buyers generally comment on everyday comfort."
        )
        occasions = by_id[primary].get("occasions") or []
        occ_txt = f" Occasions tagged: {', '.join(occasions)}." if occasions else ""
        interpretation = f"{tip}{occ_txt}"
        recommendation = interpretation
    elif q == "DURABLE_ENOUGH" and primary:
        tip = theme_summary(primary, {"DURABILITY", "QUALITY"}) or (
            "Durability feedback is based on available buyer themes."
        )
        interpretation = tip
        recommendation = tip
    elif q == "STYLE_VERSATILE" and primary:
        occasions = by_id[primary].get("occasions") or []
        tip = theme_summary(primary, {"APPEARANCE", "OCCASION"}) or ""
        if occasions:
            interpretation = (
                f"Tagged for {', '.join(occasions)}, so it can work across those looks. {tip}"
            ).strip()
        else:
            interpretation = tip or "Style versatility depends on your wardrobe; check occasion tags on the listing."
        recommendation = interpretation
    elif q == "BETTER_OPTION_IN_WISHLIST" and primary:
        similars = pack.get("similar") or []
        if similars:
            alt = similars[0]
            interpretation = (
                f"A close Wishlist alternative is {pname(alt.get('id'))} "
                f"({alt.get('reason') or 'similar attributes'})."
            )
        else:
            interpretation = (
                f"No clearly better Wishlist peer stood out against {pname(primary)} right now."
            )
        recommendation = interpretation
    elif best:
        interpretation = f"From the available scores, {pname(best)} looks like the safest pick."
        recommendation = interpretation
    elif primary:
        interpretation = (
            f"{pname(primary)} has price, rating, and buyer themes available to decide with."
        )
        recommendation = interpretation
    else:
        interpretation = "Compare price, rating, and reviews to decide."
        recommendation = interpretation

    # Once evidence exists, don't advertise empty missing lists to callers.
    if any(p.get("history_available") for p in prices) and any(themes_for(p["product_id"]) for p in products):
        missing = [m for m in missing if m not in ("price_history", "reviews", "review_insights")]

    base.update(
        {
            "facts": facts,
            "interpretation": interpretation,
            "recommendation": recommendation,
            "answer": recommendation,
            "tradeoffs": [],
            "missing": missing,
            "groq_used": False,
            "available": True,
        }
    )
    return base
