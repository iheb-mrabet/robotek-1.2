import time
import unittest

import launch
import launch_testing
import pytest
import rclpy
from action_msgs.msg import GoalStatus
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from mock_robot_interfaces.action import ExecuteDelivery
from nav_msgs.msg import Odometry
from rclpy.action import ActionClient
from sensor_msgs.msg import LaserScan

pytestmark = pytest.mark.simulation


@pytest.mark.launch_test
def generate_test_description():
    full_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("mock_robot_bringup"), "launch", "full_simulation.launch.py"]
            )
        ),
        launch_arguments={"gui": "false"}.items(),
    )
    return launch.LaunchDescription([full_simulation, launch_testing.actions.ReadyToTest()])


class TestDeliveryMission(unittest.TestCase):
    def test_nearby_delivery_mission_completes_successfully(self) -> None:
        rclpy.init()
        node = rclpy.create_node("delivery_mission_probe")
        odometry: list[Odometry] = []
        scans: list[LaserScan] = []
        try:
            node.create_subscription(Odometry, "/odom", odometry.append, 20)
            node.create_subscription(LaserScan, "/scan", scans.append, 10)
            client = ActionClient(node, ExecuteDelivery, "execute_delivery")
            assert client.wait_for_server(timeout_sec=15.0)

            # The action server starts before Gazebo has spawned the robot and
            # the bridge has delivered its first sensor messages. A goal sent
            # during that gap spends its mission timeout waiting for physics.
            ready_deadline = time.monotonic() + 25.0
            while time.monotonic() < ready_deadline and (len(odometry) < 2 or not scans):
                rclpy.spin_once(node, timeout_sec=0.1)
            assert len(odometry) >= 2, "Gazebo odometry did not become ready."
            assert scans, "Gazebo laser scan did not become ready."

            goal = ExecuteDelivery.Goal()
            goal.target_x = 0.6
            goal.target_y = 0.0
            send_future = client.send_goal_async(goal)
            rclpy.spin_until_future_complete(node, send_future, timeout_sec=10.0)
            goal_handle = send_future.result()
            assert goal_handle is not None
            assert goal_handle.accepted

            result_future = goal_handle.get_result_async()
            deadline = time.time() + 35.0
            while time.time() < deadline and not result_future.done():
                rclpy.spin_once(node, timeout_sec=0.2)

            assert result_future.done(), "Delivery action did not finish before timeout."
            response = result_future.result()
            result = response.result
            assert response.status == GoalStatus.STATUS_SUCCEEDED, (
                f"{result.message} Last odometry: "
                f"({odometry[-1].pose.pose.position.x:.2f}, "
                f"{odometry[-1].pose.pose.position.y:.2f}); "
                f"received {len(odometry)} samples."
            )
            assert result.success, result.message
            assert result.final_state == "COMPLETED", result.message
            assert result.message
        finally:
            node.destroy_node()
            rclpy.shutdown()
