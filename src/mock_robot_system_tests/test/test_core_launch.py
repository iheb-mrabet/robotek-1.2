from __future__ import annotations

import time

import launch
import launch_testing
import pytest
import rclpy
from launch_ros.actions import Node

pytestmark = pytest.mark.integration


def _wait_for_topics(node: rclpy.node.Node, expected_topics: set[str], timeout: float) -> set[str]:
    deadline = time.time() + timeout
    seen: set[str] = set()
    while time.time() < deadline and seen != expected_topics:
        topics = {name for name, _types in node.get_topic_names_and_types()}
        seen = expected_topics.intersection(topics)
        rclpy.spin_once(node, timeout_sec=0.1)
    return seen


@pytest.mark.launch_test
def generate_test_description():
    waypoint = Node(package="mock_robot_control", executable="waypoint_controller", output="screen")
    safety = Node(package="mock_robot_control", executable="safety_controller", output="screen")
    mission = Node(package="mock_robot_behavior", executable="mission_manager", output="screen")

    return (
        launch.LaunchDescription(
            [
                waypoint,
                safety,
                mission,
                launch_testing.actions.ReadyToTest(),
            ]
        ),
        {"waypoint": waypoint, "safety": safety, "mission": mission},
    )


class TestCoreLaunch:
    def test_main_nodes_expose_expected_topics(self) -> None:
        rclpy.init()
        node = rclpy.create_node("core_launch_topic_probe")
        try:
            expected = {"/cmd_vel", "/cmd_vel_requested", "/mission/status", "/mission/target"}
            seen = _wait_for_topics(node, expected, timeout=8.0)
            assert seen == expected
        finally:
            node.destroy_node()
            rclpy.shutdown()


@launch_testing.post_shutdown_test()
class TestProcessExit:
    def test_processes_exit_cleanly(self, proc_info, waypoint, safety, mission) -> None:
        proc_info.assertWaitForShutdown(process=waypoint, timeout=5)
        proc_info.assertWaitForShutdown(process=safety, timeout=5)
        proc_info.assertWaitForShutdown(process=mission, timeout=5)
