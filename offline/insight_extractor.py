"""Deterministic review theme extraction when Groq is unavailable or for tests."""

import json
import re
from typing import Any

THEMES = [
    "FIT",
    "SIZE",
    "FABRIC",
    "QUALITY",
    "COMFORT",
    "COLOR",
    "DURABILITY",
    "APPEARANCE",
    "VALUE",
    "OCCASION",
    "IMAGE_ACCURACY",
    "COMPLAINTS",
]

THEME_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "FIT": [
        (r"\bfit\b|\btrue to size\b|\bcomfortable\b", "positive"),
        (r"\bruns small\b|\bruns large\b|\btighter\b|\btight\b|\bshort sleeves\b", "negative"),
    ],
    "SIZE": [
        (r"\btrue to size\b|\busual size\b", "positive"),
        (r"\bruns small\b|\bruns large\b|\border one size\b", "negative"),
    ],
    "FABRIC": [
        (r"\bfabric\b|\bmaterial\b|\bsoft\b|\bbreathable\b", "positive"),
        (r"\bthin\b|\bsee-through\b|\bstiff\b|\bpill", "negative"),
    ],
    "QUALITY": [
        (r"\bquality\b|\bstitching\b|\bdurable\b|\bwell made\b", "positive"),
        (r"\bloose threads\b|\bzipper\b|\bfaded\b|\bdisappointing\b", "negative"),
    ],
    "COMFORT": [
        (r"\bcomfortable\b|\bwear(s)? well\b", "positive"),
        (r"\bstiff\b|\buncomfortable\b", "negative"),
    ],
    "APPEARANCE": [
        (r"\blooks\b|\bcolor\b|\bcompliments\b|\bvibrant\b|\bmatches\b", "positive"),
        (r"\bdull\b|\bcheaper in person\b|\boff\b", "negative"),
    ],
    "VALUE": [
        (r"\bworth\b|\bvalue\b|\bgreat buy\b|\bgood buy\b", "positive"),
        (r"\boverpriced\b|\bnot worth\b|\bwait for\b|\bfull mrp\b", "negative"),
    ],
    "IMAGE_ACCURACY": [
        (r"\bexactly like\b|\bmatches the listing\b|\bproduct photos\b", "positive"),
        (r"\bwebsite images\b|\bduller than\b", "negative"),
    ],
    "COMPLAINTS": [
        (r"\bdisappoint", "negative"),
    ],
}


def extract_themes_from_reviews(reviews: list[dict]) -> list[dict[str, Any]]:
    """Keyword-based theme counts grounded in review text."""
    if not reviews:
        return []

    tallies: dict[str, dict[str, Any]] = {
        theme: {"positive": 0, "negative": 0, "evidence": []} for theme in THEMES
    }

    for review in reviews:
        text = (review.get("review_text") or "").lower()
        rating = float(review.get("rating") or 3)
        rid = review.get("review_id")
        if not text:
            continue

        matched_any = False
        for theme, patterns in THEME_PATTERNS.items():
            for pattern, sentiment in patterns:
                if re.search(pattern, text):
                    matched_any = True
                    if sentiment == "positive" or rating >= 4:
                        tallies[theme]["positive"] += 1
                    else:
                        tallies[theme]["negative"] += 1
                    if rid and len(tallies[theme]["evidence"]) < 3:
                        tallies[theme]["evidence"].append(rid)

        if not matched_any and rating <= 3:
            tallies["COMPLAINTS"]["negative"] += 1
            if rid and len(tallies["COMPLAINTS"]["evidence"]) < 3:
                tallies["COMPLAINTS"]["evidence"].append(rid)

    volume_prefix = "Among the available reviews, " if len(reviews) < 100 else ""
    results = []
    for theme, data in tallies.items():
        total = data["positive"] + data["negative"]
        if total == 0:
            continue
        if data["negative"] > data["positive"]:
            summary = f"{volume_prefix}{theme.lower()} concerns appear in several reviews."
        elif data["positive"] > data["negative"]:
            summary = f"{volume_prefix}buyers often mention positive {theme.lower()} feedback."
        else:
            summary = f"{volume_prefix}mixed {theme.lower()} feedback in available reviews."

        confidence = "LOW" if len(reviews) < 10 else ("MEDIUM" if len(reviews) < 25 else "HIGH")
        results.append(
            {
                "theme": theme,
                "positive_count": data["positive"],
                "negative_count": data["negative"],
                "summary": summary,
                "evidence_review_ids": data["evidence"],
                "confidence": confidence,
            }
        )
    return results
