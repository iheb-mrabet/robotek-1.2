import time
from math import hypot

import launch
import launch_testing
import pytest
import rclpy
from geometry_msgs.msg import Twist
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from nav_msgs.msg import Odometry

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


class TestBasicMovement:
    def test_robot_odometry_changes_after_command(self) -> None:
        rclpy.init()
        node = rclpy.create_node("basic_movement_probe")
        odom_msgs: list[Odometry] = []
        try:
            node.create_subscription(Odometry, "/odom", lambda msg: odom_msgs.append(msg), 10)
            publisher = node.create_publisher(Twist, "/cmd_vel_requested", 10)

            deadline = time.time() + 15.0
            while time.time() < deadline and not odom_msgs:
                rclpy.spin_once(node, timeout_sec=0.1)
            assert odom_msgs, "No starting odometry received."

            start = odom_msgs[-1].pose.pose.position
            command = Twist()
            command.linear.x = 0.25
            deadline = time.time() + 10.0
            while time.time() < deadline:
                publisher.publish(command)
                rclpy.spin_once(node, timeout_sec=0.1)
                current = odom_msgs[-1].pose.pose.position
                if hypot(current.x - start.x, current.y - start.y) > 0.05:
                    return

            current = odom_msgs[-1].pose.pose.position
            assert hypot(current.x - start.x, current.y - start.y) > 0.05
        finally:
            node.destroy_node()
            rclpy.shutdown()
