import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.db.session import DB_PATH
from backend.llm.client import LlmClient, LlmNotConfiguredError
from backend.main import app
from offline.rebuild_insights import rebuild_insights


MOCK_LLM_JSON = json.dumps(
    {
        "answer": "Mostly worth the price based on available evidence",
        "facts": ["Current price is ₹1299"],
        "evidence": ["Quality themes are positive among available reviews"],
        "interpretation": "It balances price and buyer feedback.",
        "recommendation": "Choose this if quality matters more than minimizing price.",
        "tradeoffs": ["A cheaper Wishlist alternative exists"],
    }
)

MOCK_COMPARE_JSON = json.dumps(
    {
        "interpretation": "P003 is cheapest while P002 leads on ratings.",
        "tradeoffs": ["Price vs rating trade-off"],
    }
)


@pytest.fixture()
def client():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as c:
        c.get("/health")
        yield c
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_health_phase4(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["phase"] == 6


def test_rebuild_insights_populates_themes(client):
    conn = __import__("backend.db.session", fromlist=["get_connection"]).get_connection()
    try:
        rebuild_insights(conn, use_groq=False)
        count = conn.execute("SELECT COUNT(*) FROM review_insights").fetchone()[0]
        assert count > 0
        fit = conn.execute(
            "SELECT theme FROM review_insights WHERE product_id = 'P002' AND theme = 'FIT'"
        ).fetchone()
        assert fit is not None
    finally:
        conn.close()


def test_wishlist_get_still_no_groq(client):
    with patch.object(LlmClient, "complete", side_effect=AssertionError("Groq on Wishlist GET")):
        client.post("/api/wishlist", json={"product_id": "P001"})
        assert client.get("/api/wishlist").status_code == 200


def test_review_insight_available_after_rebuild(client):
    res = client.get("/api/products/P002/review-insight")
    assert res.status_code == 200
    body = res.json()
    assert body["review_count"] > 0
    assert body["available"] is True


def test_compare_explanation_fallback_without_key(client):
    for pid in ("P001", "P002", "P003"):
        client.post("/api/wishlist", json={"product_id": pid})
    with patch.object(
        LlmClient,
        "complete_quality",
        side_effect=LlmNotConfiguredError("no key"),
    ):
        res = client.post(
            "/api/wishlist/compare",
            json={"product_ids": ["P001", "P002", "P003"]},
        )
    body = res.json()
    assert body["explanation"]["available"] is True
    assert body["explanation"]["groq_used"] is False
    assert body["explanation"]["text"]
    assert "temporarily unavailable" not in body["explanation"]["text"].lower()
    assert body["labels"]["best_value"] == "P003"


def test_compare_explanation_with_mock_groq(client):
    for pid in ("P001", "P002", "P003"):
        client.post("/api/wishlist", json={"product_id": pid})
    with patch.object(LlmClient, "complete", return_value=MOCK_COMPARE_JSON):
        res = client.post(
            "/api/wishlist/compare",
            json={"product_ids": ["P001", "P002", "P003"]},
        )
    body = res.json()
    assert body["explanation"]["groq_used"] is True


def test_worth_the_price_question(client):
    client.post("/api/wishlist", json={"product_id": "P002"})
    with patch.object(LlmClient, "complete", return_value=MOCK_LLM_JSON):
        res = client.post(
            "/api/questions/answer",
            json={"question_id": "WORTH_THE_PRICE", "product_id": "P002"},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["groq_used"] is True
    assert "will drop" not in body.get("interpretation", "").lower()


def test_should_i_wait_no_history(client):
    client.post("/api/wishlist", json={"product_id": "P026"})
    res = client.post(
        "/api/questions/answer",
        json={"question_id": "SHOULD_I_WAIT", "product_id": "P026"},
    )
    assert res.status_code == 200
    text = (res.json().get("interpretation") or "") + (res.json().get("recommendation") or "")
    assert "tomorrow" not in text.lower()


def test_which_one_conditional_language(client):
    for pid in ("P001", "P002", "P003"):
        client.post("/api/wishlist", json={"product_id": pid})
    res = client.post(
        "/api/questions/answer",
        json={
            "question_id": "WHICH_ONE_SHOULD_I_BUY",
            "product_ids": ["P001", "P002", "P003"],
        },
    )
    assert res.status_code == 200
    rec = res.json().get("recommendation") or res.json().get("interpretation") or ""
    assert "definitely the best" not in rec.lower()


def test_invalid_question_rejected(client):
    client.post("/api/wishlist", json={"product_id": "P001"})
    res = client.post(
        "/api/questions/answer",
        json={"question_id": "FREE_TEXT_CHAT", "product_id": "P001"},
    )
    assert res.status_code == 400


def test_list_questions(client):
    res = client.get("/api/questions", params={"product_count": 3})
    assert res.status_code == 200
    ids = {q["question_id"] for q in res.json()["questions"]}
    assert "WHICH_ONE_SHOULD_I_BUY" in ids
