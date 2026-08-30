import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.db.session import DB_PATH
from backend.llm.client import LlmClient, LlmNotConfiguredError
from backend.main import app


@pytest.fixture()
def client():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as c:
        c.get("/health")
        yield c
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_health_phase3(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["phase"] == 6


def test_wishlist_includes_signals(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    res = client.get("/api/wishlist")
    assert res.status_code == 200
    item = res.json()["items"][0]
    assert "signals" in item
    assert "Highly rated" in item["signals"]
    assert "concerns" in item
    assert "missing" in item


def test_wishlist_get_does_not_call_groq(client):
    with patch.object(LlmClient, "complete", side_effect=AssertionError("Groq must not run on Wishlist GET")):
        client.post("/api/wishlist", json={"product_id": "P001"})
        res = client.get("/api/wishlist")
        assert res.status_code == 200


def test_compare_dress_triple(client):
    for pid in ("P001", "P002", "P003"):
        client.post("/api/wishlist", json={"product_id": pid})

    res = client.post(
        "/api/wishlist/compare",
        json={"product_ids": ["P001", "P002", "P003"]},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["labels"]["best_value"] == "P003"
    assert body["labels"]["best_reviewed"] == "P002"
    assert "explanation" in body
    assert body["explanation"]["text"]

    metrics = {r["metric"] for r in body["rows"]}
    assert {"price", "rating", "rating_count", "value_score", "quality_score"}.issubset(metrics)


def test_compare_requires_wishlist_items(client):
    client.post("/api/wishlist", json={"product_id": "P001"})
    res = client.post(
        "/api/wishlist/compare",
        json={"product_ids": ["P001", "P999"]},
    )
    assert res.status_code == 400


def test_price_insight_with_history(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    res = client.get("/api/products/P002/price-insight")
    assert res.status_code == 200
    body = res.json()
    assert body["history_available"] is True
    assert body["saved_price"] is not None
    assert "will drop" not in body["summary"].lower()


def test_price_insight_no_history_product(client):
    client.post("/api/wishlist", json={"product_id": "P026"})
    res = client.get("/api/products/P026/price-insight")
    assert res.status_code == 200
    assert res.json()["history_available"] is False
    assert "unavailable" in res.json()["summary"].lower()


def test_review_insight_with_themes(client):
    res = client.get("/api/products/P002/review-insight")
    assert res.status_code == 200
    body = res.json()
    assert body["review_count"] > 0
    assert body["available"] is True


def test_similarity_populated(client):
    conn = __import__("backend.db.session", fromlist=["get_connection"]).get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM product_similarity").fetchone()[0]
        assert count > 0
    finally:
        conn.close()


def test_price_stats_populated(client):
    conn = __import__("backend.db.session", fromlist=["get_connection"]).get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM price_stats").fetchone()[0]
        assert count >= 50
    finally:
        conn.close()


def test_llm_requires_api_key():
    llm = LlmClient(api_key="")
    with pytest.raises(LlmNotConfiguredError):
        llm.complete("unused", [{"role": "user", "content": "hi"}])
