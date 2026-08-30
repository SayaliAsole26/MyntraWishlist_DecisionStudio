"""Confidence band from evidence volume — never a percentage."""

from typing import Any


def confidence_from_evidence(
    *,
    has_price_history: bool,
    review_count: int,
    insight_count: int,
    compare_count: int = 1,
) -> str:
    score = 0
    if has_price_history:
        score += 2
    if review_count >= 20:
        score += 2
    elif review_count >= 5:
        score += 1
    if insight_count >= 3:
        score += 2
    elif insight_count >= 1:
        score += 1
    if compare_count >= 2:
        score += 1

    if score >= 5:
        return "HIGH"
    if score >= 2:
        return "MEDIUM"
    return "LOW"


def collect_missing(
    *,
    has_price_history: bool,
    review_count: int,
    insight_count: int,
    size_available: bool | None = None,
) -> list[str]:
    missing: list[str] = []
    if not has_price_history:
        missing.append("price_history")
    if review_count == 0:
        missing.append("reviews")
    if insight_count == 0:
        missing.append("review_insights")
    if size_available is False:
        missing.append("size")
    return missing
