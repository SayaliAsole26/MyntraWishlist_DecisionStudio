import sqlite3

from backend.db.util import parse_json_list
from backend.models import ProductOut


def row_to_product(row: sqlite3.Row) -> ProductOut:
    return ProductOut(
        product_id=row["product_id"],
        brand=row["brand"],
        name=row["name"],
        gender=row["gender"],
        category=row["category"],
        subcategory=row["subcategory"],
        style=row["style"],
        price=row["price"],
        mrp=row["mrp"],
        discount=row["discount"],
        rating=row["rating"],
        rating_count=row["rating_count"],
        image_url=row["image_url"],
        product_url=row["product_url"],
        sizes=parse_json_list(row["sizes"]),
        colors=parse_json_list(row["colors"]),
        fit=row["fit"],
        material=row["material"],
        occasions=parse_json_list(row["occasions"]),
    )


def list_products(conn: sqlite3.Connection, category: str | None = None) -> list[ProductOut]:
    if category:
        rows = conn.execute(
            "SELECT * FROM products WHERE category = ? ORDER BY name",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    return [row_to_product(r) for r in rows]


def get_product(conn: sqlite3.Connection, product_id: str) -> ProductOut | None:
    row = conn.execute(
        "SELECT * FROM products WHERE product_id = ?", (product_id,)
    ).fetchone()
    return row_to_product(row) if row else None


def list_categories(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    rows = conn.execute(
        """
        SELECT category, COUNT(*) AS cnt
        FROM products
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY category
        """
    ).fetchall()
    return [(r["category"], r["cnt"]) for r in rows]
