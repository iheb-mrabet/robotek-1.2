import json
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

import psycopg
from flask import Flask, jsonify


PROMETHEUS_QUERIES = {
    "targets_up": "sum(up)",
    "targets_total": "count(up)",
    "ros_exporter_up": (
        'max(robotek_ros_exporter_up{namespace="robotek-staging"})'
    ),
    "ros_nodes": 'max(robotek_ros_nodes{namespace="robotek-staging"})',
    "ros_topics": 'max(robotek_ros_topics{namespace="robotek-staging"})',
    "ros_collection_errors": (
        'max(robotek_ros_collection_errors_total{namespace="robotek-staging"})'
    ),
    "robot_runtime_uptime_seconds": (
        'time() - max(kube_pod_start_time{namespace="robotek-staging"})'
    ),
    "robot_container_restarts": (
        'sum(kube_pod_container_status_restarts_total{'
        'namespace="robotek-staging",container="robotek"})'
    ),
    "ros_node_details": (
        'robotek_ros_node_up{namespace="robotek-staging"}'
    ),
    "ros_topic_publishers": (
        'robotek_ros_topic_publishers{namespace="robotek-staging"}'
    ),
    "ros_topic_subscribers": (
        'robotek_ros_topic_subscribers{namespace="robotek-staging"}'
    ),
    "cluster_nodes_ready": (
        'sum(kube_node_status_condition{condition="Ready",status="true"})'
    ),
    "cluster_nodes_total": "count(kube_node_info)",
    "cluster_pods_ready": (
        'sum((kube_pod_status_ready{'
        'namespace=~"robotek-staging|robotek-demo",condition="true"} == 1) '
        'unless on(namespace,pod) kube_pod_deletion_timestamp)'
    ),
    "cluster_pods_total": (
        'count((kube_pod_status_phase{'
        'namespace=~"robotek-staging|robotek-demo",phase=~"Pending|Running"} == 1) '
        'unless on(namespace,pod) kube_pod_deletion_timestamp)'
    ),
    "deployments_available": (
        'sum(kube_deployment_status_replicas_available{'
        'namespace=~"robotek-staging|robotek-demo"})'
    ),
    "deployments_desired": (
        'sum(kube_deployment_spec_replicas{'
        'namespace=~"robotek-staging|robotek-demo"})'
    ),
    "cluster_cpu_percent": (
        '100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])))'
    ),
    "cluster_memory_percent": (
        '100 * (1 - sum(node_memory_MemAvailable_bytes) '
        '/ sum(node_memory_MemTotal_bytes))'
    ),
    "cluster_uptime_seconds": "time() - max(node_boot_time_seconds)",
    "gitops_synced": (
        'sum(argocd_app_info{'
        'name=~"robotek-staging|robotek-demo",sync_status="Synced"})'
    ),
    "gitops_healthy": (
        'sum(argocd_app_info{'
        'name=~"robotek-staging|robotek-demo",health_status="Healthy"})'
    ),
    "gitops_total": (
        'count(count by(name) '
        '(argocd_app_info{name=~"robotek-staging|robotek-demo"}))'
    ),
    "critical_alerts": (
        '(count(ALERTS{service="robotek",severity="critical",'
        'alertstate="firing"}) or vector(0))'
    ),
    "warning_alerts": (
        '(count(ALERTS{service="robotek",severity="warning",'
        'alertstate="firing"}) or vector(0))'
    ),
    "alert_details": 'ALERTS{service="robotek",alertstate="firing"}',
}

_CACHE_TTL_SECONDS = 5.0
_platform_cache: dict[str, object] = {"expires_at": 0.0, "payload": None}
_platform_cache_lock = threading.Lock()


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://robotek:robotek@database:5432/robotek",
    )


def deployment_release() -> str:
    return os.getenv("DEPLOYMENT_RELEASE", "local")


def prometheus_url() -> str:
    return os.getenv("PROMETHEUS_URL", "").rstrip("/")


def database_is_ready() -> bool:
    try:
        with psycopg.connect(database_url(), connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
    except psycopg.Error:
        return False


def database_status() -> dict[str, object]:
    try:
        with psycopg.connect(database_url(), connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO platform_state (
                        component,
                        status,
                        release,
                        last_checked_at
                    )
                    VALUES ('dashboard-backend', 'CONNECTED', %s, NOW())
                    ON CONFLICT (component)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        release = EXCLUDED.release,
                        last_checked_at = EXCLUDED.last_checked_at
                    RETURNING current_database(), last_checked_at
                    """,
                    (deployment_release(),),
                )
                database_name, checked_at = cursor.fetchone()
            connection.commit()
        return {
            "connected": True,
            "database": database_name,
            "last_checked_at": checked_at.isoformat(),
        }
    except psycopg.Error as error:
        return {
            "connected": False,
            "database": None,
            "last_checked_at": None,
            "error": error.__class__.__name__,
        }


def _prometheus_query(query: str) -> list[dict[str, object]]:
    base_url = prometheus_url()
    if not base_url:
        raise RuntimeError("PROMETHEUS_URL is not configured")

    request_url = (
        f"{base_url}/api/v1/query?"
        f"{urlencode({'query': query})}"
    )
    with urlopen(request_url, timeout=3) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("status") != "success":
        raise RuntimeError("Prometheus query failed")

    result = payload.get("data", {}).get("result", [])
    if not isinstance(result, list):
        raise RuntimeError("Unexpected Prometheus response")

    return result


def _query_safely(query: str) -> list[dict[str, object]] | None:
    try:
        return _prometheus_query(query)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
        return None


def _sample_value(
    samples: list[dict[str, object]] | None,
) -> float | None:
    if not samples:
        return None
    value = samples[0].get("value")
    if not isinstance(value, list) or len(value) != 2:
        return None
    try:
        number = float(value[1])
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _integer(value: float | None) -> int | None:
    return None if value is None else int(round(value))


def _percentage(value: float | None) -> float | None:
    if value is None:
        return None
    return round(max(0.0, min(100.0, value)), 1)


def _sample_label(
    sample: dict[str, object],
    label: str,
) -> str | None:
    metric = sample.get("metric")
    if not isinstance(metric, dict):
        return None
    value = metric.get(label)
    return value if isinstance(value, str) else None


def _node_names(
    samples: list[dict[str, object]] | None,
) -> list[str]:
    if not samples:
        return []
    return sorted(
        {
            node
            for sample in samples
            if (node := _sample_label(sample, "node"))
        }
    )


def _topic_details(
    publishers: list[dict[str, object]] | None,
    subscribers: list[dict[str, object]] | None,
) -> list[dict[str, object]]:
    topics: dict[str, dict[str, object]] = {}

    for key, samples in (
        ("publishers", publishers),
        ("subscribers", subscribers),
    ):
        for sample in samples or []:
            topic = _sample_label(sample, "topic")
            if not topic:
                continue
            value = _sample_value([sample])
            topics.setdefault(
                topic,
                {"topic": topic, "publishers": None, "subscribers": None},
            )[key] = _integer(value)

    return [topics[name] for name in sorted(topics)]


def _alert_details(
    samples: list[dict[str, object]] | None,
) -> list[dict[str, str | None]]:
    alerts: list[dict[str, str | None]] = []
    for sample in samples or []:
        alerts.append(
            {
                "name": _sample_label(sample, "alertname"),
                "severity": _sample_label(sample, "severity"),
                "component": _sample_label(sample, "component"),
            }
        )
    return sorted(
        alerts,
        key=lambda alert: (
            alert.get("severity") or "",
            alert.get("name") or "",
        ),
    )


def _safety_gate(
    critical_alerts: int | None,
    collection_errors: int | None,
    exporter_up: bool | None,
) -> str:
    if (
        critical_alerts is None
        or collection_errors is None
        or exporter_up is None
    ):
        return "UNAVAILABLE"
    if (
        critical_alerts == 0
        and collection_errors == 0
        and exporter_up
    ):
        return "PASS"
    return "FAIL"


def collect_platform() -> dict[str, object]:
    now = time.monotonic()
    with _platform_cache_lock:
        cached_payload = _platform_cache.get("payload")
        if (
            cached_payload is not None
            and now < float(_platform_cache["expires_at"])
        ):
            return cached_payload  # type: ignore[return-value]

    results: dict[str, list[dict[str, object]] | None] = {
        name: None for name in PROMETHEUS_QUERIES
    }
    if prometheus_url():
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(_query_safely, query): name
                for name, query in PROMETHEUS_QUERIES.items()
            }
            for future in as_completed(futures):
                results[futures[future]] = future.result()

    scalar = {
        name: _sample_value(results[name])
        for name in PROMETHEUS_QUERIES
        if name not in {
            "ros_node_details",
            "ros_topic_publishers",
            "ros_topic_subscribers",
            "alert_details",
        }
    }

    targets_up = _integer(scalar["targets_up"])
    targets_total = _integer(scalar["targets_total"])
    prometheus_reachable = results["targets_up"] is not None
    critical_alerts = _integer(scalar["critical_alerts"])
    warning_alerts = _integer(scalar["warning_alerts"])
    collection_errors = _integer(scalar["ros_collection_errors"])
    exporter_up = (
        None
        if scalar["ros_exporter_up"] is None
        else scalar["ros_exporter_up"] >= 1
    )
    safety_gate = _safety_gate(
        critical_alerts,
        collection_errors,
        exporter_up,
    )

    payload: dict[str, object] = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "release": deployment_release(),
        "data_policy": "live-only",
        "robot": {
            "source": "Prometheus / Robotek ROS exporter",
            "available": results["ros_exporter_up"] is not None,
            "exporter_up": exporter_up,
            "nodes": _integer(scalar["ros_nodes"]),
            "topics": _integer(scalar["ros_topics"]),
            "collection_errors": _integer(
                scalar["ros_collection_errors"]
            ),
            "runtime_uptime_seconds": _integer(
                scalar["robot_runtime_uptime_seconds"]
            ),
            "container_restarts": _integer(
                scalar["robot_container_restarts"]
            ),
            "node_names": _node_names(results["ros_node_details"]),
            "topic_details": _topic_details(
                results["ros_topic_publishers"],
                results["ros_topic_subscribers"],
            ),
        },
        "cluster": {
            "source": "Prometheus / kube-state-metrics / node-exporter",
            "nodes_ready": _integer(scalar["cluster_nodes_ready"]),
            "nodes_total": _integer(scalar["cluster_nodes_total"]),
            "pods_ready": _integer(scalar["cluster_pods_ready"]),
            "pods_total": _integer(scalar["cluster_pods_total"]),
            "deployments_available": _integer(
                scalar["deployments_available"]
            ),
            "deployments_desired": _integer(
                scalar["deployments_desired"]
            ),
            "cpu_percent": _percentage(
                scalar["cluster_cpu_percent"]
            ),
            "memory_percent": _percentage(
                scalar["cluster_memory_percent"]
            ),
            "uptime_seconds": _integer(
                scalar["cluster_uptime_seconds"]
            ),
        },
        "observability": {
            "source": "Prometheus HTTP API",
            "prometheus_reachable": prometheus_reachable,
            "targets_up": targets_up,
            "targets_total": targets_total,
            "gitops_synced": _integer(scalar["gitops_synced"]),
            "gitops_healthy": _integer(scalar["gitops_healthy"]),
            "gitops_total": _integer(scalar["gitops_total"]),
            "grafana_url": os.getenv(
                "GRAFANA_PUBLIC_URL",
                "http://localhost:3000",
            ),
            "prometheus_url": os.getenv(
                "PROMETHEUS_PUBLIC_URL",
                "http://localhost:9090",
            ),
        },
        "database": database_status(),
        "alerts": {
            "source": "Prometheus ALERTS",
            "critical_firing": critical_alerts,
            "warning_firing": warning_alerts,
            "items": _alert_details(results["alert_details"]),
        },
        "safety": {
            "source": "Prometheus ALERTS / Robotek ROS exporter",
            "gate": safety_gate,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "ros_collection_errors": collection_errors,
            "exporter_up": exporter_up,
        },
    }

    with _platform_cache_lock:
        _platform_cache["payload"] = payload
        _platform_cache["expires_at"] = now + _CACHE_TTL_SECONDS

    return payload


def clear_platform_cache() -> None:
    with _platform_cache_lock:
        _platform_cache["payload"] = None
        _platform_cache["expires_at"] = 0.0


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(status="ok", component="backend"), 200

    @app.get("/ready")
    def ready():
        if database_is_ready():
            return jsonify(status="ready", database="connected"), 200
        return jsonify(status="not ready", database="unavailable"), 503

    @app.get("/api/platform")
    def platform():
        return jsonify(collect_platform()), 200

    @app.get("/api/robot")
    def robot():
        platform_payload = collect_platform()
        return jsonify(platform_payload["robot"]), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
