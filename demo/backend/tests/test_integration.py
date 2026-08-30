import json
import os
import urllib.request


BASE_URL = os.getenv("DEMO_BASE_URL", "http://127.0.0.1:8080")


def get(path: str):
    with urllib.request.urlopen(
        f"{BASE_URL}{path}",
        timeout=5,
    ) as response:
        return response.status, response.read().decode("utf-8")


def test_frontend_is_served():
    status, body = get("/")

    assert status == 200
    assert "Robotek Delivery Robot" in body
    assert "Operations Control" in body


def test_frontend_reaches_backend_health_and_readiness():
    status, body = get("/health")
    assert status == 200
    assert json.loads(body) == {
        "component": "backend",
        "status": "ok",
    }

    status, body = get("/ready")
    assert status == 200
    assert json.loads(body) == {
        "database": "connected",
        "status": "ready",
    }


def test_complete_frontend_backend_database_flow():
    status, body = get("/api/platform")
    payload = json.loads(body)

    assert status == 200
    assert payload["data_policy"] == "live-only"
    assert payload["release"] == "local"
    assert payload["database"]["connected"] is True
    assert payload["database"]["database"] == "robotek"

    # Local Compose intentionally has no Prometheus server. The API must
    # report telemetry as unavailable instead of substituting demo numbers.
    assert payload["observability"]["prometheus_reachable"] is False
    assert payload["robot"]["nodes"] is None
    assert payload["robot"]["topics"] is None
