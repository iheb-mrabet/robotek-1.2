import json
import os
import urllib.request


BASE_URL = os.getenv("DEMO_BASE_URL", "http://127.0.0.1:8080")


def get(path: str):
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5) as response:
        return response.status, response.read().decode("utf-8")


def test_frontend_is_served():
    status, body = get("/")
    assert status == 200
    assert "Robotek Delivery Robot" in body


def test_frontend_reaches_backend_health():
    status, body = get("/health")
    assert status == 200
    assert json.loads(body) == {"status": "ok"}


def test_complete_frontend_backend_database_flow():
    status, body = get("/api/robot")
    payload = json.loads(body)
    assert status == 200
    assert payload["name"] == "Robotek-01"
    assert payload["status"] == "ONLINE"
    assert payload["release"] == "base-v1"
