#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "src" / "mock_robot_bringup" / "config"


def load_parameters(filename: str, node_name: str) -> dict[str, Any]:
    path = CONFIG_DIR / filename
    if not path.is_file():
        raise ValueError(f"missing configuration file: {path.relative_to(ROOT)}")

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path.relative_to(ROOT)}: {exc}") from exc

    try:
        parameters = document[node_name]["ros__parameters"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            f"{path.relative_to(ROOT)} must contain {node_name}.ros__parameters"
        ) from exc

    if not isinstance(parameters, dict):
        raise ValueError(f"{node_name}.ros__parameters must be a mapping")
    return parameters


def number(parameters: dict[str, Any], key: str, context: str) -> float:
    value = parameters.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context}.{key} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{context}.{key} must be finite")
    return value


def require_between(value: float, minimum: float, maximum: float, label: str) -> None:
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}; got {value}")


def require_absolute_topic(parameters: dict[str, Any], key: str, context: str) -> None:
    value = parameters.get(key)
    if not isinstance(value, str) or not value.startswith("/") or " " in value:
        raise ValueError(f"{context}.{key} must be an absolute ROS topic without spaces")


def main() -> int:
    try:
        waypoint = load_parameters("control.yaml", "waypoint_controller")
        safety = load_parameters("control.yaml", "safety_controller")
        mission = load_parameters("mission.yaml", "mission_manager")
        robot = load_parameters("robot.yaml", "robot_state_publisher")

        for context, parameters in (
            ("waypoint_controller", waypoint),
            ("safety_controller", safety),
            ("mission_manager", mission),
            ("robot_state_publisher", robot),
        ):
            if parameters.get("use_sim_time") is not True:
                raise ValueError(f"{context}.use_sim_time must be true for the mock simulation")

        require_between(
            number(waypoint, "max_linear_velocity", "waypoint_controller"),
            0.01,
            0.75,
            "waypoint_controller.max_linear_velocity",
        )
        require_between(
            number(waypoint, "max_angular_velocity", "waypoint_controller"),
            0.01,
            1.5,
            "waypoint_controller.max_angular_velocity",
        )
        require_between(
            number(waypoint, "max_linear_acceleration", "waypoint_controller"),
            0.01,
            1.5,
            "waypoint_controller.max_linear_acceleration",
        )
        require_between(
            number(waypoint, "max_angular_acceleration", "waypoint_controller"),
            0.01,
            3.0,
            "waypoint_controller.max_angular_acceleration",
        )

        for key in (
            "max_linear_velocity",
            "max_angular_velocity",
            "max_linear_acceleration",
            "max_angular_acceleration",
        ):
            if number(waypoint, key, "waypoint_controller") != number(
                safety, key, "safety_controller"
            ):
                raise ValueError(
                    f"{key} must match between waypoint_controller and safety_controller"
                )

        stop_distance = number(safety, "obstacle_stop_distance", "safety_controller")
        warning_distance = number(safety, "obstacle_warning_distance", "safety_controller")
        require_between(stop_distance, 0.1, 1.0, "safety_controller.obstacle_stop_distance")
        require_between(warning_distance, 0.2, 2.0, "safety_controller.obstacle_warning_distance")
        if warning_distance <= stop_distance:
            raise ValueError(
                "obstacle_warning_distance must be greater than obstacle_stop_distance"
            )

        goal_tolerance = number(waypoint, "goal_tolerance", "waypoint_controller")
        require_between(goal_tolerance, 0.05, 0.5, "waypoint_controller.goal_tolerance")
        if goal_tolerance != number(mission, "goal_tolerance", "mission_manager"):
            raise ValueError("goal_tolerance must match in control.yaml and mission.yaml")

        require_between(
            number(mission, "mission_timeout", "mission_manager"),
            5.0,
            300.0,
            "mission_manager.mission_timeout",
        )
        require_between(
            number(mission, "max_abs_coordinate", "mission_manager"),
            0.5,
            10.0,
            "mission_manager.max_abs_coordinate",
        )

        for context, parameters, keys in (
            (
                "waypoint_controller",
                waypoint,
                ("target_topic", "odom_topic", "output_topic"),
            ),
            (
                "safety_controller",
                safety,
                ("input_topic", "output_topic", "scan_topic", "emergency_stop_topic"),
            ),
        ):
            for key in keys:
                require_absolute_topic(parameters, key, context)

    except ValueError as exc:
        print(f"Configuration safety validation failed: {exc}", file=sys.stderr)
        return 1

    print("Configuration safety validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
