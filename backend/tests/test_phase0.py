import pytest
from fastapi.testclient import TestClient

from backend.db.session import DB_PATH
from backend.llm.client import LlmClient, LlmNotConfiguredError
from backend.main import app


def test_health_ok():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "ok"
        assert body["phase"] == 6
        assert body["catalog_ready"] is True
        assert body["product_count"] > 0


def test_llm_requires_api_key():
    llm = LlmClient(api_key="")
    with pytest.raises(LlmNotConfiguredError):
        llm.complete("unused", [{"role": "user", "content": "hi"}])
