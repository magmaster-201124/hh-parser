from fastapi.testclient import TestClient

from app.web import app

client = TestClient(app)


def test_index_serves_html() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Собрать trudvsem" in resp.text


def test_collect_unknown_source() -> None:
    assert client.post("/api/collect/nope").status_code == 400


def test_status_starts_empty() -> None:
    assert client.get("/api/status").json() == {}
