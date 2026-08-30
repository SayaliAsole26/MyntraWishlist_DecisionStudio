import logging

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.db.session import DB_PATH, get_connection
from backend.llm.client import LlmClient
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


def test_health_phase6(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["phase"] == 6


def test_checkout_creates_order_and_clears_bag(client):
    client.post("/api/bag", json={"product_id": "P001"})
    client.post("/api/bag", json={"product_id": "P003"})

    bag_before = client.get("/api/bag").json()
    assert bag_before["count"] == 2

    res = client.post("/api/checkout")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "CONFIRMED"
    assert body["order_id"].startswith("ORD-")
    assert body["item_count"] == 2
    assert body["total"] > 0
    assert len(body["product_ids"]) == 2

    bag_after = client.get("/api/bag").json()
    assert bag_after["count"] == 0

    conn = get_connection()
    try:
        order = conn.execute(
            "SELECT status FROM orders WHERE order_id = ?", (body["order_id"],)
        ).fetchone()
        assert order is not None
        assert order["status"] == "CONFIRMED"
    finally:
        conn.close()


def test_checkout_empty_bag_rejected(client):
    res = client.post("/api/checkout")
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_groq_usage_logged(caplog):
    from unittest.mock import MagicMock

    caplog.set_level(logging.INFO, logger="groq.usage")
    llm = LlmClient(api_key="test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"answer":"ok"}'}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        llm.complete("test-model", [{"role": "user", "content": "hi"}], context="test/endpoint")

    assert any("groq_call" in r.message and "test/endpoint" in r.message for r in caplog.records)


def test_wishlist_get_still_no_groq_phase6(client):
    with patch.object(LlmClient, "complete", side_effect=AssertionError("Groq on Wishlist GET")):
        client.post("/api/wishlist", json={"product_id": "P001"})
        assert client.get("/api/wishlist").status_code == 200
