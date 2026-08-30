"""Tests for decision shortlist (17→3 relevance filter)."""

import pytest
from fastapi.testclient import TestClient

from backend.db.session import DB_PATH
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


def test_shortlist_api_returns_top_three(client):
    for pid in ("P001", "P002", "P003", "P004", "P005"):
        client.post("/api/wishlist", json={"product_id": pid})
    res = client.post(
        "/api/wishlist/shortlist",
        json={
            "product_ids": ["P001", "P002", "P003", "P004", "P005"],
            "need": "Workwear",
            "tradeoff_priority": "VALUE",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["from_count"] == 5
    assert len(data["product_ids"]) == 3
    assert len(data["ranked"]) == 3


def test_shortlist_api_preserves_small_sets(client):
    client.post("/api/wishlist", json={"product_id": "P001"})
    client.post("/api/wishlist", json={"product_id": "P002"})
    res = client.post(
        "/api/wishlist/shortlist",
        json={"product_ids": ["P001", "P002"], "need": "Casual", "tradeoff_priority": "FIT"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["product_ids"]) == 2


def test_compare_accepts_tradeoff(client):
    for pid in ("P001", "P002"):
        client.post("/api/wishlist", json={"product_id": pid})
    res = client.post(
        "/api/wishlist/compare",
        json={
            "product_ids": ["P001", "P002"],
            "need": "Workwear",
            "tradeoff_priority": "FIT",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "labels" in body
    assert "need_assessment" in body


def test_compare_party_need_prefers_heels_over_sneakers(client):
    """Party need should not pick running shoes when heels/party dress are in the set."""
    for pid in ("P005", "P057", "P058"):
        client.post("/api/wishlist", json={"product_id": pid})
    res = client.post(
        "/api/wishlist/compare",
        json={
            "product_ids": ["P005", "P057", "P058"],
            "need": "Party",
            "tradeoff_priority": "FIT",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["labels"]["best_balance"] in ("P057", "P058")
    assert body["need_assessment"]["P005"]["level"] == "poor"
    assert body["need_assessment"]["P057"]["level"] == "strong"


def test_compare_top_pick_changes_with_need(client):
    """Office dress (P002) should beat running shoes (P005) for Workwear; reverse for Sports."""
    for pid in ("P002", "P005"):
        client.post("/api/wishlist", json={"product_id": pid})

    workwear = client.post(
        "/api/wishlist/compare",
        json={
            "product_ids": ["P002", "P005"],
            "need": "Workwear",
            "tradeoff_priority": "VERSATILITY",
        },
    ).json()
    sports = client.post(
        "/api/wishlist/compare",
        json={
            "product_ids": ["P002", "P005"],
            "need": "Sports",
            "tradeoff_priority": "VERSATILITY",
        },
    ).json()

    assert workwear["labels"]["best_balance"] == "P002"
    assert sports["labels"]["best_balance"] == "P005"
    assert workwear["need_assessment"]["P005"]["level"] in ("partial", "poor")
    assert sports["need_assessment"]["P002"]["level"] in ("partial", "poor")
