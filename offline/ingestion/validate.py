"""Validate normalized catalog rows. Fail fast — never invent missing fields."""

from offline.ingestion.normalize import normalize_price_point, normalize_product, normalize_review


class ValidationError(Exception):
    def __init__(self, entity: str, entity_id: str, message: str):
        self.entity = entity
        self.entity_id = entity_id
        self.message = message
        super().__init__(f"{entity} {entity_id}: {message}")


def validate_products(products: list[dict]) -> None:
    seen: set[str] = set()
    for raw in products:
        p = normalize_product(raw, "validate")
        pid = p["product_id"]
        if pid in seen:
            raise ValidationError("product", pid, "duplicate product_id")
        seen.add(pid)

        for field in ("brand", "name"):
            if not p[field]:
                raise ValidationError("product", pid, f"missing {field}")

        if p["price"] <= 0:
            raise ValidationError("product", pid, "price must be positive")
        if p["mrp"] <= 0:
            raise ValidationError("product", pid, "mrp must be positive")
        if p["price"] > p["mrp"]:
            raise ValidationError("product", pid, "price must be <= mrp")

        if p["rating"] is not None and not (0 <= p["rating"] <= 5):
            raise ValidationError("product", pid, "rating must be between 0 and 5")
        if p["rating_count"] is not None and p["rating_count"] < 0:
            raise ValidationError("product", pid, "rating_count must be >= 0")


def validate_reviews(reviews: list[dict], product_ids: set[str]) -> None:
    seen: set[str] = set()
    for raw in reviews:
        r = normalize_review(raw, "validate")
        rid = r["review_id"]
        if rid in seen:
            raise ValidationError("review", rid, "duplicate review_id")
        seen.add(rid)

        if r["product_id"] not in product_ids:
            raise ValidationError("review", rid, f"unknown product_id {r['product_id']}")

        if r["rating"] is not None and not (0 <= r["rating"] <= 5):
            raise ValidationError("review", rid, "rating must be between 0 and 5")

        if not r["review_text"]:
            raise ValidationError("review", rid, "review_text is required")


def validate_price_history(points: list[dict], product_ids: set[str]) -> None:
    seen: set[tuple[str, str]] = set()
    for raw in points:
        pt = normalize_price_point(raw, "validate")
        key = (pt["product_id"], pt["date"])
        if key in seen:
            raise ValidationError(
                "price_history",
                f"{pt['product_id']}@{pt['date']}",
                "duplicate date for product",
            )
        seen.add(key)

        if pt["product_id"] not in product_ids:
            raise ValidationError(
                "price_history",
                pt["product_id"],
                "unknown product_id",
            )
        if pt["price"] <= 0:
            raise ValidationError(
                "price_history",
                f"{pt['product_id']}@{pt['date']}",
                "price must be positive",
            )


def validate_users(users: list[dict]) -> None:
    seen: set[str] = set()
    for raw in users:
        uid = str(raw["user_id"]).strip()
        if uid in seen:
            raise ValidationError("user", uid, "duplicate user_id")
        seen.add(uid)
        if not uid:
            raise ValidationError("user", uid or "?", "user_id is required")
