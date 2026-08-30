"""Generate Phase 2 seed JSON files (products, reviews, price-history)."""

import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))

from scripts.category_reviews import CATEGORY_REVIEWS, GENERIC_REVIEWS
from scripts.product_images import PRODUCT_IMAGES
from backend.decision.tradeoff import infer_occasions

SIMILAR_GROUP_ATTRS = {
    "P001": {"similar_group": "dresses_casual", "decision_role": "balanced"},
    "P002": {"similar_group": "dresses_casual", "decision_role": "best_reviewed"},
    "P003": {"similar_group": "dresses_casual", "decision_role": "cheap"},
    "P004": {"similar_group": "sneakers_running", "decision_role": "mid"},
    "P005": {"similar_group": "sneakers_running", "decision_role": "best_reviewed"},
    "P012": {"similar_group": "sneakers_running", "decision_role": "mid"},
    "P006": {"similar_group": "tops_casual", "decision_role": "cheap"},
    "P007": {"similar_group": "tops_casual", "decision_role": "mid"},
    "P008": {"similar_group": "jeans_casual", "decision_role": "best_reviewed"},
    "P009": {"similar_group": "jeans_casual", "decision_role": "cheap"},
    "P010": {"similar_group": "handbags_casual", "decision_role": "cheap"},
    "P011": {"similar_group": "handbags_casual", "decision_role": "best_reviewed"},
}

EXTRA_SIMILAR = [
    ("P013", "dresses_casual", "Tokyo Talkies", "Women Ruffle Hem Casual Dress", "Women", "Dresses", "Casual Dresses", 1099, 2199, 4.0, 890, "Regular", "Rayon", "mid"),
    ("P014", "dresses_casual", "Sassafras", "Women Tiered Maxi Dress", "Women", "Dresses", "Casual Dresses", 1199, 2399, 4.3, 1100, "Relaxed", "Cotton Blend", "mid"),
    ("P015", "sneakers_running", "Reebok", "Floatride Energy Shoes", "Men", "Sneakers", "Running", 4299, 5499, 4.1, 520, "Regular", "Mesh", "cheap"),
    ("P016", "sneakers_running", "Asics", "Gel-Contend 8 Running Shoes", "Men", "Sneakers", "Running", 5499, 6499, 4.6, 980, "Regular", "Synthetic", "premium"),
    ("P017", "handbags_casual", "Caprese", "Women Structured Satchel Bag", "Women", "Handbags", "Casual", 1299, 2599, 4.4, 710, "Regular", "PU Leather", "mid"),
    ("P018", "handbags_casual", "DressBerry", "Women Mini Crossbody Bag", "Women", "Handbags", "Casual", 699, 1499, 3.9, 380, "Regular", "Faux Leather", "cheap"),
    ("P019", "handbags_casual", "Hidesign", "Women Leather Shoulder Bag", "Women", "Handbags", "Casual", 2499, 4499, 4.7, 430, "Regular", "Leather", "premium"),
    ("P020", "tops_casual", "Roadster", "Men Striped Polo T-Shirt", "Men", "Tops", "T-Shirts", 699, 1299, 4.1, 560, "Regular", "Cotton", "mid"),
    ("P021", "tops_casual", "UCB", "Men Logo Print T-Shirt", "Men", "Tops", "T-Shirts", 899, 1599, 4.4, 780, "Regular", "Cotton", "best_reviewed"),
    ("P022", "tops_casual", "HIGHLANDER", "Men Oversized Graphic Tee", "Men", "Tops", "T-Shirts", 549, 999, 3.8, 290, "Oversized", "Cotton", "cheap"),
    ("P023", "jeans_casual", "Pepe Jeans", "Men Regular Fit Blue Jeans", "Men", "Jeans", "Casual", 1799, 2999, 4.2, 940, "Regular", "Denim", "mid"),
    ("P024", "jeans_casual", "Wrangler", "Men Comfort Flex Jeans", "Men", "Jeans", "Casual", 1999, 3299, 4.3, 650, "Regular", "Denim", "mid"),
    ("P025", "jeans_casual", "Roadster", "Men Relaxed Fit Jeans", "Men", "Jeans", "Casual", 1399, 2499, 4.0, 520, "Relaxed", "Denim", "cheap"),
]

EXTRA_CATALOG = [
    ("P026", "Kurtas", "Men", "Kurtas", "Casual Kurtas", "Manyavar", "Embroidered Kurta", 2499, 3999, 4.3, 680),
    ("P027", "Kurtas", "Men", "Kurtas", "Casual Kurtas", "FabIndia", "Cotton Straight Kurta", 1899, 2999, 4.5, 920),
    ("P028", "Kurtas", "Women", "Kurtas", "Anarkali", "Biba", "Printed Anarkali Kurta", 1599, 2799, 4.2, 1100),
    ("P029", "Kurtas", "Women", "Kurtas", "Straight", "Aurelia", "Floral Straight Kurta", 999, 1799, 4.0, 540),
    ("P030", "Kurtas", "Women", "Kurtas", "A-Line", "W", "Solid A-Line Kurta", 799, 1499, 4.1, 430),
    ("P031", "Jackets", "Men", "Jackets", "Denim", "Levis", "Trucker Denim Jacket", 3499, 4999, 4.4, 870),
    ("P032", "Jackets", "Men", "Jackets", "Bomber", "Roadster", "Bomber Jacket", 1999, 3499, 4.1, 620),
    ("P033", "Jackets", "Women", "Jackets", "Leather", "ONLY", "Faux Leather Biker Jacket", 2799, 4499, 4.3, 510),
    ("P034", "Jackets", "Women", "Jackets", "Puffer", "H&M", "Lightweight Puffer Jacket", 2299, 3999, 4.2, 780),
    ("P035", "Jackets", "Men", "Jackets", "Windcheater", "Puma", "Running Windcheater", 2499, 3999, 4.0, 390),
    ("P036", "Watches", "Men", "Watches", "Analog", "Fossil", "Chronograph Watch", 8999, 12999, 4.5, 320),
    ("P037", "Watches", "Women", "Watches", "Analog", "Titan", "Rose Gold Dial Watch", 4999, 6999, 4.4, 560),
    ("P038", "Watches", "Men", "Watches", "Smart", "Noise", "ColorFit Smartwatch", 2999, 4999, 4.0, 1200),
    ("P039", "Watches", "Women", "Watches", "Analog", "Fastrack", "Minimalist Watch", 1499, 2499, 4.1, 890),
    ("P040", "Watches", "Unisex", "Watches", "Digital", "Casio", "Classic Digital Watch", 1999, 2999, 4.6, 2100),
    ("P041", "Shorts", "Men", "Shorts", "Casual", "Roadster", "Cotton Chino Shorts", 699, 1299, 4.0, 340),
    ("P042", "Shorts", "Men", "Shorts", "Sports", "Nike", "Dri-FIT Training Shorts", 1499, 2199, 4.3, 520),
    ("P043", "Shorts", "Women", "Shorts", "Denim", "H&M", "High-Rise Denim Shorts", 999, 1799, 4.1, 410),
    ("P044", "Shorts", "Women", "Shorts", "Active", "Puma", "Training Shorts", 899, 1499, 4.0, 280),
    ("P045", "Sunglasses", "Unisex", "Sunglasses", "Aviator", "Ray-Ban", "Classic Aviator", 6999, 8999, 4.7, 450),
    ("P046", "Sunglasses", "Women", "Sunglasses", "Cat Eye", "Vogue", "Cat Eye Sunglasses", 4999, 6499, 4.4, 310),
    ("P047", "Sunglasses", "Men", "Sunglasses", "Wayfarer", "Fastrack", "Wayfarer Sunglasses", 999, 1799, 4.2, 680),
    ("P048", "Sunglasses", "Unisex", "Sunglasses", "Round", "Lenskart", "Round Metal Frame", 1499, 2499, 4.0, 920),
    ("P049", "Activewear", "Women", "Activewear", "Leggings", "Nike", "One Tight Leggings", 2999, 3999, 4.4, 760),
    ("P050", "Activewear", "Men", "Activewear", "Track Pants", "Adidas", "Essentials Track Pants", 2499, 3499, 4.2, 540),
    ("P051", "Activewear", "Women", "Activewear", "Sports Bra", "Puma", "Medium Support Sports Bra", 1299, 1999, 4.1, 430),
    ("P052", "Activewear", "Men", "Activewear", "T-Shirt", "Decathlon", "Dry Fit Running Tee", 599, 999, 4.0, 890),
    ("P053", "Activewear", "Women", "Activewear", "Tank", "HRX", "Racerback Tank Top", 499, 899, 3.9, 320),
    ("P054", "Sandals", "Men", "Sandals", "Sports", "Puma", "Leadcat Slide Sandals", 1499, 1999, 4.2, 670),
    ("P055", "Sandals", "Women", "Sandals", "Flat", "Metro", "Embellished Flat Sandals", 999, 1799, 4.0, 510),
    ("P056", "Sandals", "Men", "Sandals", "Casual", "Woodland", "Outdoor Sandals", 1999, 2999, 4.1, 380),
    ("P057", "Sandals", "Women", "Sandals", "Heel", "Aldo", "Block Heel Sandals", 2499, 3999, 4.3, 290),
    ("P058", "Dresses", "Women", "Dresses", "Party", "Vero Moda", "Sequin Party Dress", 2799, 4499, 4.4, 620),
    ("P059", "Dresses", "Women", "Dresses", "Formal", "Marks & Spencer", "Sheath Formal Dress", 3199, 4999, 4.5, 480),
    ("P060", "Sneakers", "Women", "Sneakers", "Lifestyle", "New Balance", "327 Lifestyle Sneakers", 6999, 8999, 4.5, 540),
    ("P061", "Tops", "Women", "Tops", "Blouses", "AND", "Puff Sleeve Blouse", 1299, 2199, 4.2, 390),
    ("P062", "Jeans", "Women", "Jeans", "Skinny", "ONLY", "High-Rise Skinny Jeans", 1899, 2999, 4.3, 710),
]

REVIEW_TEMPLATES = GENERIC_REVIEWS  # legacy alias for theme_mix keys

REVIEWED_PRODUCTS = [
    "P001", "P002", "P003",
    "P004", "P005", "P012",
    "P008", "P009",
    "P010", "P011",
    "P006", "P007",
    "P016", "P020",
]

PRICE_HISTORY_PRODUCTS = REVIEWED_PRODUCTS + ["P013", "P014", "P015"]


def _discount(price: int, mrp: int) -> int:
    return round((1 - price / mrp) * 100)


def _occasions_for(
    category: str, subcategory: str, name: str, style: str = "Casual"
) -> list[str]:
    inferred = infer_occasions(
        {"category": category, "subcategory": subcategory, "name": name, "style": style}
    )
    if inferred:
        return sorted(inferred)
    return ["Casual", "Office"]


def _product(
    product_id: str,
    brand: str,
    name: str,
    gender: str,
    category: str,
    subcategory: str,
    price: int,
    mrp: int,
    rating: float,
    rating_count: int,
    fit: str,
    material: str,
    attributes: dict,
    sizes: list[str] | None = None,
) -> dict:
    image_url = PRODUCT_IMAGES.get(
        product_id,
        PRODUCT_IMAGES.get("P006", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=500&fit=crop"),
    )
    return {
        "product_id": product_id,
        "brand": brand,
        "name": name,
        "gender": gender,
        "category": category,
        "subcategory": subcategory,
        "style": "Casual",
        "price": price,
        "mrp": mrp,
        "discount": _discount(price, mrp),
        "rating": rating,
        "rating_count": rating_count,
        "image_url": image_url,
        "product_url": "https://www.myntra.com/",
        "sizes": sizes or (["One Size"] if category == "Handbags" else ["S", "M", "L", "XL"]),
        "colors": ["Black"],
        "fit": fit,
        "material": material,
        "occasions": _occasions_for(category, subcategory, name),
        "attributes": attributes,
    }


BASE_PRODUCT_IDS = {f"P{i:03d}" for i in range(1, 13)}


def _load_base_products() -> list[dict]:
    """Load only P001–P012 from products.json to keep regeneration idempotent."""
    base_path = DATA / "products.json"
    if not base_path.exists():
        return []
    all_rows = json.loads(base_path.read_text(encoding="utf-8"))
    base = [p for p in all_rows if p.get("product_id") in BASE_PRODUCT_IDS]
    if len(base) == 12:
        return base
    # Recover if products.json was overwritten by a prior full generation.
    seen = set()
    recovered = []
    for p in all_rows:
        pid = p.get("product_id")
        if pid in BASE_PRODUCT_IDS and pid not in seen:
            recovered.append(p)
            seen.add(pid)
    return recovered


def build_products() -> list[dict]:
    base = _load_base_products()
    products = []
    for p in base:
        attrs = SIMILAR_GROUP_ATTRS.get(p["product_id"], {})
        p = dict(p)
        p["attributes"] = attrs
        if p["product_id"] in PRODUCT_IMAGES:
            p["image_url"] = PRODUCT_IMAGES[p["product_id"]]
        products.append(p)

    for row in EXTRA_SIMILAR:
        pid, group, brand, name, gender, cat, sub, price, mrp, rating, rc, fit, mat, role = row
        products.append(
            _product(pid, brand, name, gender, cat, sub, price, mrp, rating, rc, fit, mat,
                     {"similar_group": group, "decision_role": role})
        )

    for row in EXTRA_CATALOG:
        pid, img_cat, gender, cat, sub, brand, name, price, mrp, rating, rc = row
        products.append(
            _product(pid, brand, name, gender, cat, sub, price, mrp, rating, rc, "Regular", "Mixed", {})
        )

    return products


def _review_pool(product: dict, theme_key: str) -> list[str]:
    category = product.get("category") or "Tops"
    cat_templates = CATEGORY_REVIEWS.get(category, GENERIC_REVIEWS)
    return cat_templates.get(theme_key, GENERIC_REVIEWS.get(theme_key, ["Review mention."]))


def build_reviews(products_by_id: dict[str, dict]) -> list[dict]:
    reviews = []
    rid = 1
    rng = random.Random(42)

    theme_mix = {
        "P001": ["positive_fit", "positive_fabric", "positive_appearance", "negative_fabric"],
        "P002": ["positive_quality", "positive_fit", "positive_value", "positive_appearance"],
        "P003": ["positive_value", "negative_fabric", "negative_quality", "positive_fit"],
        "P004": ["positive_fit", "negative_fit", "positive_quality", "positive_value"],
        "P005": ["positive_quality", "positive_fit", "positive_value", "positive_appearance"],
        "P012": ["positive_appearance", "positive_fit", "negative_fit", "positive_fabric"],
        "P008": ["positive_quality", "positive_fit", "positive_value", "negative_fit"],
        "P009": ["positive_value", "negative_quality", "positive_fit", "negative_fabric"],
        "P010": ["positive_appearance", "positive_value", "negative_quality", "positive_fit"],
        "P011": ["positive_quality", "positive_appearance", "positive_value", "positive_fit"],
        "P006": ["positive_fabric", "positive_value", "negative_fabric", "positive_fit"],
        "P007": ["positive_appearance", "positive_fit", "negative_fit", "positive_quality"],
        "P016": ["positive_fit", "positive_quality", "negative_fit", "positive_value"],
        "P020": ["positive_value", "negative_fabric", "positive_fit", "positive_quality"],
    }

    for product_id in REVIEWED_PRODUCTS:
        product = products_by_id.get(product_id)
        if not product:
            continue
        themes = theme_mix.get(product_id, list(GENERIC_REVIEWS.keys()))
        count = 28 if product_id in ("P002", "P005", "P011") else 24
        for i in range(count):
            theme_key = themes[i % len(themes)]
            pool = _review_pool(product, theme_key)
            text = pool[i % len(pool)]
            rating = 5 if theme_key.startswith("positive") else rng.choice([2, 3, 3, 4])
            review_date = (date(2025, 1, 1) + timedelta(days=i * 3 + hash(product_id) % 10)).isoformat()
            reviews.append({
                "review_id": f"R{rid:04d}",
                "product_id": product_id,
                "rating": rating,
                "review_text": text,
                "review_date": review_date,
            })
            rid += 1

    return reviews


def build_price_history(products_by_id: dict[str, dict]) -> list[dict]:
    points = []
    rng = random.Random(7)
    end = date(2026, 8, 30)

    for product_id in PRICE_HISTORY_PRODUCTS:
        if product_id not in products_by_id:
            continue
        current = products_by_id[product_id]["price"]
        mrp = products_by_id[product_id]["mrp"]
        base = int(mrp * rng.uniform(0.85, 0.98))
        days = 45 if product_id in ("P002", "P003", "P009") else 35
        for d in range(days):
            dt = end - timedelta(days=days - d)
            drift = rng.randint(-80, 80)
            price = max(current - 400, min(mrp, base + drift + (d * 5)))
            if d == days - 1:
                price = current
            points.append({
                "product_id": product_id,
                "date": dt.isoformat(),
                "price": int(price),
            })

    return points


def main() -> None:
    products = build_products()
    products_by_id = {p["product_id"]: p for p in products}
    reviews = build_reviews(products_by_id)
    price_history = build_price_history(products_by_id)

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "products.json").write_text(json.dumps(products, indent=2), encoding="utf-8")
    (DATA / "reviews.json").write_text(json.dumps(reviews, indent=2), encoding="utf-8")
    (DATA / "price-history.json").write_text(json.dumps(price_history, indent=2), encoding="utf-8")

    categories = len({p["category"] for p in products})
    print(f"Wrote {len(products)} products ({categories} categories), "
          f"{len(reviews)} reviews, {len(price_history)} price points")


if __name__ == "__main__":
    main()
