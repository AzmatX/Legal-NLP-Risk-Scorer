from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_invalid_extension() -> None:
    response = client.post(
        "/contracts/analyze",
        files={"file": ("contract.txt", b"invalid", "text/plain")},
    )
    assert response.status_code == 400
