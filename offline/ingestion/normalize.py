"""Normalize raw seed records into DB-ready dicts."""

import json
from typing import Any


def normalize_product(raw: dict, batch_id: str) -> dict:
    attrs = raw.get("attributes") or {}
    if not isinstance(attrs, dict):
        attrs = {}

    return {
        "product_id": str(raw["product_id"]).strip(),
        "brand": str(raw["brand"]).strip(),
        "name": str(raw["name"]).strip(),
        "gender": raw.get("gender"),
        "category": raw.get("category"),
        "subcategory": raw.get("subcategory"),
        "style": raw.get("style"),
        "price": int(raw["price"]),
        "mrp": int(raw["mrp"]),
        "discount": _optional_int(raw.get("discount")),
        "rating": _optional_float(raw.get("rating")),
        "rating_count": _optional_int(raw.get("rating_count")),
        "image_url": raw.get("image_url"),
        "product_url": raw.get("product_url"),
        "sizes": _json_list(raw.get("sizes")),
        "colors": _json_list(raw.get("colors")),
        "fit": raw.get("fit"),
        "material": raw.get("material"),
        "occasions": _json_list(raw.get("occasions")),
        "attributes_json": json.dumps(attrs, ensure_ascii=False),
        "source_batch_id": batch_id,
    }


def normalize_review(raw: dict, batch_id: str) -> dict:
    return {
        "review_id": str(raw["review_id"]).strip(),
        "product_id": str(raw["product_id"]).strip(),
        "rating": _optional_float(raw.get("rating")),
        "review_text": (raw.get("review_text") or "").strip() or None,
        "review_date": raw.get("review_date"),
        "source_batch_id": batch_id,
    }


def normalize_price_point(raw: dict, batch_id: str) -> dict:
    return {
        "product_id": str(raw["product_id"]).strip(),
        "date": str(raw["date"]).strip(),
        "price": int(raw["price"]),
        "source_batch_id": batch_id,
    }


def normalize_user(raw: dict) -> dict:
    return {
        "user_id": str(raw["user_id"]).strip(),
        "display_name": raw.get("display_name"),
        "size": raw.get("size"),
        "price_min": _optional_int(raw.get("price_min")),
        "price_max": _optional_int(raw.get("price_max")),
        "occasions": _json_list(raw.get("occasions")),
        "priorities": _json_list(raw.get("priorities")),
    }


def _json_list(value: Any) -> str:
    if value is None:
        return "[]"
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return json.dumps(value)
    return "[]"


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
