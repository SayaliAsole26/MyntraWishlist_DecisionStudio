import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.db.session import DB_PATH, get_connection
from backend.llm.client import LlmClient
from backend.main import app
from offline.simulate_price_drop import simulate_price_drop


@pytest.fixture()
def client():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as c:
        c.get("/health")
        yield c
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_health_phase5(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["phase"] == 6


def test_wishlist_includes_alerts_and_overload_fields(client):
    res = client.get("/api/wishlist")
    assert res.status_code == 200
    body = res.json()
    assert "alerts" in body
    assert "overload" in body
    assert isinstance(body["alerts"], list)
    assert isinstance(body["overload"], list)


def test_wishlist_get_still_no_groq_with_alerts(client):
    with patch.object(LlmClient, "complete", side_effect=AssertionError("Groq on Wishlist GET")):
        client.post("/api/wishlist", json={"product_id": "P001"})
        assert client.get("/api/wishlist").status_code == 200


def test_simulate_price_drop_creates_alert(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    conn = get_connection()
    try:
        simulate_price_drop(conn, "P002", 999)
    finally:
        conn.close()

    res = client.get("/api/wishlist")
    assert res.status_code == 200
    alerts = [a for a in res.json()["alerts"] if a["type"] == "PRICE_DROP"]
    assert len(alerts) >= 1
    drop = next(a for a in alerts if a["product_id"] == "P002")
    assert drop["payload"]["from"] == 1299
    assert drop["payload"]["to"] == 999
    assert drop["payload"]["save_amount"] == 300


def test_price_drop_deduped(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    conn = get_connection()
    try:
        simulate_price_drop(conn, "P002", 999)
        simulate_price_drop(conn, "P002", 899)
    finally:
        conn.close()

    res = client.get("/api/wishlist")
    price_alerts = [a for a in res.json()["alerts"] if a["type"] == "PRICE_DROP" and a["product_id"] == "P002"]
    assert len(price_alerts) == 1


def test_dismiss_alert_persists(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    conn = get_connection()
    try:
        simulate_price_drop(conn, "P002", 999)
    finally:
        conn.close()

    res = client.get("/api/wishlist")
    alert_id = next(a["alert_id"] for a in res.json()["alerts"] if a["type"] == "PRICE_DROP")

    dismiss = client.patch(f"/api/alerts/{alert_id}/dismiss")
    assert dismiss.status_code == 200

    res2 = client.get("/api/wishlist")
    remaining = [a for a in res2.json()["alerts"] if a["alert_id"] == alert_id]
    assert remaining == []


def test_overload_at_three_dresses(client):
    for pid in ("P001", "P002", "P003"):
        client.post("/api/wishlist", json={"product_id": pid})

    res = client.get("/api/wishlist")
    assert res.status_code == 200
    overload = res.json()["overload"]
    assert len(overload) >= 1
    group = overload[0]
    assert group["count"] >= 3
    assert len(group["product_ids"]) >= 3
    assert "dress" in group["label"]


def test_overload_not_triggered_at_two(client):
    for pid in ("P001", "P002"):
        client.post("/api/wishlist", json={"product_id": pid})

    res = client.get("/api/wishlist")
    dress_overload = [o for o in res.json()["overload"] if "dress" in o.get("label", "")]
    assert dress_overload == []


def test_overload_returns_after_dismiss(client):
    for pid in ("P001", "P002", "P003"):
        client.post("/api/wishlist", json={"product_id": pid})

    res = client.get("/api/wishlist")
    overload = res.json()["overload"]
    assert overload
    alert_id = overload[0]["alert_id"]
    assert alert_id

    client.patch(f"/api/alerts/{alert_id}/dismiss")
    res2 = client.get("/api/wishlist")
    assert len(res2.json()["overload"]) >= 1


def test_similar_product_alert_has_reason(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    res = client.get("/api/wishlist")
    similar = [a for a in res.json()["alerts"] if a["type"] == "SIMILAR_PRODUCT"]
    if similar:
        alert = similar[0]
        assert alert["payload"].get("reason")
        assert alert["similar_product"] is not None
