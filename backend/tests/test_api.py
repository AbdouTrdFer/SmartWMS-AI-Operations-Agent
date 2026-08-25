from app.main import app
from fastapi.testclient import TestClient


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_rejects_empty_message() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/chat", json={"message": "   "})
    assert response.status_code == 422


def test_chat_returns_tools_and_sources() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"message": "Why is SKU-102 a high reorder priority at WH-NJ?"},
        )
    payload = response.json()
    assert response.status_code == 200
    assert payload["tools_used"]
    assert payload["sources"]
    assert "Facts from read-only WMS tools" in payload["answer"]
