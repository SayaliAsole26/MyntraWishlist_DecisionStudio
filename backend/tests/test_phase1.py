import pytest
from fastapi.testclient import TestClient

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


def test_health_phase1(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["phase"] == 6


def test_products_seeded(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    products = res.json()["products"]
    assert len(products) >= 8
    assert products[0]["product_id"]


def test_product_detail(client):
    res = client.get("/api/products/P001")
    assert res.status_code == 200
    assert res.json()["brand"] == "Roadster"


def test_category_filter(client):
    res = client.get("/api/products", params={"category": "Dresses"})
    assert res.status_code == 200
    assert all(p["category"] == "Dresses" for p in res.json()["products"])


def test_wishlist_flow_first_save_wins(client):
    add1 = client.post("/api/wishlist", json={"product_id": "P001"})
    assert add1.status_code == 200
    saved1 = add1.json()["saved_price"]

    add2 = client.post("/api/wishlist", json={"product_id": "P001"})
    assert add2.status_code == 200
    assert add2.json()["saved_price"] == saved1

    wl = client.get("/api/wishlist")
    assert wl.json()["count"] == 1

    client.delete("/api/wishlist/P001")
    add3 = client.post("/api/wishlist", json={"product_id": "P001"})
    assert add3.json()["saved_price"] == add3.json()["product"]["price"]


def test_bag_flow(client):
    res = client.post("/api/bag", json={"product_id": "P002"})
    assert res.status_code == 200
    bag = client.get("/api/bag")
    assert bag.json()["count"] == 1
    assert bag.json()["total"] > 0


def test_profile_update(client):
    get = client.get("/api/profile")
    assert get.status_code == 200
    assert get.json()["user_id"] == "U001"

    bad = client.patch("/api/profile", json={"price_min": 2000, "price_max": 500})
    assert bad.status_code == 400

    ok = client.patch(
        "/api/profile",
        json={"size": "L", "priorities": ["Price", "Comfort"]},
    )
    assert ok.status_code == 200
    assert ok.json()["size"] == "L"
    assert "Price" in ok.json()["priorities"]


def test_profile_clear(client):
    client.patch(
        "/api/profile",
        json={"size": "L", "price_min": 100, "price_max": 5000},
    )
    res = client.post("/api/profile/clear")
    assert res.status_code == 200
    body = res.json()
    assert body["display_name"] is None
    assert body["size"] is None
    assert body["price_min"] is None
    assert body["price_max"] is None
    assert body["occasions"] == []
    assert body["priorities"] == []


def test_unknown_user_rejected(client):
    res = client.get("/api/wishlist", headers={"X-User-Id": "U999"})
    assert res.status_code == 403


def test_llm_requires_api_key():
    llm = LlmClient(api_key="")
    with pytest.raises(LlmNotConfiguredError):
        llm.complete("unused", [{"role": "user", "content": "hi"}])
