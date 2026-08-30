from unittest.mock import patch

from app import Robot, create_app, normalize_battery


SAMPLE_ROBOT = Robot(
    name="Robotek-01",
    status="ONLINE",
    battery=87,
    mission="Warehouse delivery",
    destination="Dock B",
    completed_deliveries=12,
    release="base-v1",
)


def test_normalize_battery_keeps_values_in_range():
    assert normalize_battery(-4) == 0
    assert normalize_battery(71) == 71
    assert normalize_battery(109) == 100


def test_robot_endpoint_returns_dashboard_payload():
    application = create_app()
    with patch("app.load_robot", return_value=SAMPLE_ROBOT):
        response = application.test_client().get("/api/robot")

    assert response.status_code == 200
    assert response.get_json() == {
        "name": "Robotek-01",
        "status": "ONLINE",
        "battery": 87,
        "mission": "Warehouse delivery",
        "destination": "Dock B",
        "completed_deliveries": 12,
        "release": "base-v1",
    }


def test_health_reports_healthy_database():
    application = create_app()
    with patch("app.load_robot", return_value=SAMPLE_ROBOT):
        response = application.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
