import time

import launch
import launch_testing
import pytest
import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from mock_robot_interfaces.msg import MissionStatus
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

pytestmark = pytest.mark.simulation


@pytest.mark.launch_test
def generate_test_description():
    _ = get_package_share_directory("mock_robot_bringup")
    full_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("mock_robot_bringup"), "launch", "full_simulation.launch.py"]
            )
        ),
        launch_arguments={"gui": "false"}.items(),
    )
    return launch.LaunchDescription([full_simulation, launch_testing.actions.ReadyToTest()])


class TestSimulationTopics:
    def test_core_simulation_topics_receive_messages(self) -> None:
        rclpy.init()
        node = rclpy.create_node("simulation_topic_probe")
        odom_msgs: list[Odometry] = []
        scan_msgs: list[LaserScan] = []
        cmd_msgs: list[Twist] = []
        status_msgs: list[MissionStatus] = []
        try:
            node.create_subscription(Odometry, "/odom", lambda msg: odom_msgs.append(msg), 10)
            node.create_subscription(LaserScan, "/scan", lambda msg: scan_msgs.append(msg), 10)
            node.create_subscription(Twist, "/cmd_vel", lambda msg: cmd_msgs.append(msg), 10)
            node.create_subscription(
                MissionStatus, "/mission/status", lambda msg: status_msgs.append(msg), 10
            )
            publisher = node.create_publisher(Twist, "/cmd_vel_requested", 10)

            command = Twist()
            command.linear.x = 0.1
            deadline = time.time() + 25.0
            while time.time() < deadline:
                publisher.publish(command)
                rclpy.spin_once(node, timeout_sec=0.1)
                if odom_msgs and scan_msgs and cmd_msgs and status_msgs:
                    return

            assert odom_msgs, "No /odom message received."
            assert scan_msgs, "No /scan message received."
            assert cmd_msgs, "No /cmd_vel message received."
            assert status_msgs, "No /mission/status message received."
        finally:
            node.destroy_node()
            rclpy.shutdown()
