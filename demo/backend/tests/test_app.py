from unittest.mock import patch

from app import (
    _sample_value,
    _topic_details,
    create_app,
)


PLATFORM_PAYLOAD = {
    "collected_at": "2026-08-30T14:00:00+00:00",
    "release": "abc123",
    "data_policy": "live-only",
    "robot": {
        "source": "Prometheus / Robotek ROS exporter",
        "available": True,
        "exporter_up": True,
        "nodes": 7,
        "topics": 11,
        "collection_errors": 0,
        "runtime_uptime_seconds": 7200,
        "container_restarts": 0,
        "node_names": ["/robotek_ros_exporter"],
        "topic_details": [
            {
                "topic": "/odom",
                "publishers": 1,
                "subscribers": 2,
            }
        ],
    },
    "cluster": {
        "source": "Prometheus / kube-state-metrics / node-exporter",
        "nodes_ready": 1,
        "nodes_total": 1,
        "pods_ready": 4,
        "pods_total": 4,
        "deployments_available": 4,
        "deployments_desired": 4,
        "cpu_percent": 21.4,
        "memory_percent": 48.2,
        "uptime_seconds": 86400,
    },
    "observability": {
        "source": "Prometheus HTTP API",
        "prometheus_reachable": True,
        "targets_up": 19,
        "targets_total": 20,
        "gitops_synced": 2,
        "gitops_healthy": 2,
        "gitops_total": 2,
        "grafana_url": "http://localhost:3000",
        "prometheus_url": "http://localhost:9090",
    },
    "database": {
        "connected": True,
        "database": "robotek",
        "last_checked_at": "2026-08-30T14:00:00+00:00",
    },
    "alerts": {
        "source": "Prometheus ALERTS",
        "critical_firing": 0,
        "warning_firing": 0,
        "items": [],
    },
}


def test_health_only_reports_backend_process():
    response = create_app().test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "component": "backend",
        "status": "ok",
    }


def test_readiness_requires_database():
    application = create_app()

    with patch("app.database_is_ready", return_value=True):
        response = application.test_client().get("/ready")

    assert response.status_code == 200
    assert response.get_json() == {
        "database": "connected",
        "status": "ready",
    }


def test_platform_endpoint_returns_live_data_contract():
    application = create_app()

    with patch("app.collect_platform", return_value=PLATFORM_PAYLOAD):
        response = application.test_client().get("/api/platform")

    assert response.status_code == 200
    assert response.get_json()["data_policy"] == "live-only"
    assert response.get_json()["robot"]["nodes"] == 7
    assert response.get_json()["robot"]["runtime_uptime_seconds"] == 7200
    assert response.get_json()["cluster"]["pods_ready"] == 4
    assert response.get_json()["cluster"]["uptime_seconds"] == 86400


def test_prometheus_sample_value_parsing():
    samples = [{"metric": {}, "value": [1234567890, "42.5"]}]

    assert _sample_value(samples) == 42.5
    assert _sample_value([]) is None


def test_topic_vectors_are_merged_without_inventing_values():
    publishers = [
        {
            "metric": {"topic": "/odom"},
            "value": [1234567890, "1"],
        }
    ]
    subscribers = [
        {
            "metric": {"topic": "/odom"},
            "value": [1234567890, "2"],
        },
        {
            "metric": {"topic": "/scan"},
            "value": [1234567890, "1"],
        },
    ]

    assert _topic_details(publishers, subscribers) == [
        {
            "topic": "/odom",
            "publishers": 1,
            "subscribers": 2,
        },
        {
            "topic": "/scan",
            "publishers": None,
            "subscribers": 1,
        },
    ]
