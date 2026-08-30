import os
import time
from dataclasses import asdict, dataclass

import psycopg
from flask import Flask, jsonify


@dataclass(frozen=True)
class Robot:
    name: str
    status: str
    battery: int
    mission: str
    destination: str
    completed_deliveries: int
    release: str


def normalize_battery(value: int) -> int:
    return max(0, min(100, int(value)))


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://robotek:robotek@database:5432/robotek",
    )


def load_robot() -> Robot:
    query = """
        SELECT name, status, battery, mission, destination,
               completed_deliveries, release
        FROM robot_status
        ORDER BY id
        LIMIT 1
    """
    with psycopg.connect(database_url(), connect_timeout=3) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
    if row is None:
        raise RuntimeError("robot_status contains no rows")
    return Robot(
        name=row[0],
        status=row[1],
        battery=normalize_battery(row[2]),
        mission=row[3],
        destination=row[4],
        completed_deliveries=row[5],
        release=row[6],
    )


def wait_for_database(attempts: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, attempts + 1):
        try:
            load_robot()
            return
        except (psycopg.Error, RuntimeError):
            if attempt == attempts:
                raise
            time.sleep(delay)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        try:
            load_robot()
            return jsonify(status="ok"), 200
        except (psycopg.Error, RuntimeError):
            return jsonify(status="database unavailable"), 503

    @app.get("/api/robot")
    def robot_status():
        return jsonify(asdict(load_robot())), 200

    return app


app = create_app()


if __name__ == "__main__":
    wait_for_database()
    app.run(host="0.0.0.0", port=8000)
