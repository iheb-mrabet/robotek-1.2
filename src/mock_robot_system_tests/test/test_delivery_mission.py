import time

import launch
import launch_testing
import pytest
import rclpy
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from mock_robot_interfaces.action import ExecuteDelivery
from rclpy.action import ActionClient

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


class TestDeliveryMission:
    def test_nearby_delivery_mission_reaches_reported_final_state(self) -> None:
        rclpy.init()
        node = rclpy.create_node("delivery_mission_probe")
        try:
            client = ActionClient(node, ExecuteDelivery, "execute_delivery")
            assert client.wait_for_server(timeout_sec=15.0)

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
            result = result_future.result().result
            assert result.final_state in {"COMPLETED", "FAILED", "EMERGENCY_STOPPED"}
            assert result.message
        finally:
            node.destroy_node()
            rclpy.shutdown()
