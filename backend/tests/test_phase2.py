import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.db.session import DB_PATH
from backend.main import app
from offline.ingestion.pipeline import ingest_catalog
from offline.ingestion.validate import ValidationError, validate_products


@pytest.fixture()
def client():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as c:
        c.get("/health")
        yield c
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_health_phase2(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["phase"] == 6


def test_catalog_size_after_ingest(client):
    res = client.get("/api/products")
    products = res.json()["products"]
    assert len(products) >= 50
    categories = {p["category"] for p in products}
    assert len(categories) >= 5


def test_reviews_ingested(client):
    conn = __import__("backend.db.session", fromlist=["get_connection"]).get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        assert count >= 200
        reviewed = conn.execute(
            "SELECT COUNT(DISTINCT product_id) FROM reviews"
        ).fetchone()[0]
        assert reviewed >= 10
    finally:
        conn.close()


def test_price_history_ingested(client):
    conn = __import__("backend.db.session", fromlist=["get_connection"]).get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM price_history").fetchone()[0]
        assert count >= 100
    finally:
        conn.close()


def test_derived_tables_phase3(client):
    conn = __import__("backend.db.session", fromlist=["get_connection"]).get_connection()
    try:
        assert conn.execute("SELECT COUNT(*) FROM review_insights").fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM price_stats").fetchone()[0] >= 50
        assert conn.execute("SELECT COUNT(*) FROM product_similarity").fetchone()[0] > 0
    finally:
        conn.close()


def test_wishlist_persists_after_reingest(client):
    client.post("/api/wishlist", json={"product_id": "P001"})
    saved = client.get("/api/wishlist").json()["items"][0]["saved_price"]

    result = ingest_catalog()
    assert result["counts"]["products"] >= 50

    wl = client.get("/api/wishlist").json()
    assert wl["count"] == 1
    assert wl["items"][0]["saved_price"] == saved


def test_raw_snapshot_created():
    if DB_PATH.exists():
        DB_PATH.unlink()
    result = ingest_catalog()
    batch_dir = Path(result["raw_snapshot"])
    assert batch_dir.exists()
    assert (batch_dir / "products.json").exists()
    assert (batch_dir / "_manifest.json").exists()
    manifest = json.loads((batch_dir / "_manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["products"] >= 50
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_validation_rejects_bad_price():
    bad = [
        {
            "product_id": "PX99",
            "brand": "Test",
            "name": "Bad Price",
            "price": 5000,
            "mrp": 1000,
        }
    ]
    with pytest.raises(ValidationError, match="price must be <= mrp"):
        validate_products(bad)


def test_reviewed_product_accessible(client):
    res = client.get("/api/products/P002")
    assert res.status_code == 200
    assert res.json()["brand"] == "MANGO"
