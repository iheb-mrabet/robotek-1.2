import time

import launch
import launch_testing
import pytest
import rclpy
from geometry_msgs.msg import Twist
from launch_ros.actions import Node
from mock_robot_interfaces.srv import EmergencyStop

pytestmark = pytest.mark.integration


@pytest.mark.launch_test
def generate_test_description():
    safety = Node(package="mock_robot_control", executable="safety_controller", output="screen")
    mission = Node(package="mock_robot_behavior", executable="mission_manager", output="screen")

    return (
        launch.LaunchDescription([safety, mission, launch_testing.actions.ReadyToTest()]),
        {"safety": safety, "mission": mission},
    )


class TestEmergencyStop:
    def test_emergency_stop_forces_zero_command(self) -> None:
        rclpy.init()
        node = rclpy.create_node("emergency_stop_probe")
        received: list[Twist] = []
        try:
            publisher = node.create_publisher(Twist, "/cmd_vel_requested", 10)
            node.create_subscription(Twist, "/cmd_vel", lambda msg: received.append(msg), 10)
            client = node.create_client(EmergencyStop, "/mission/emergency_stop")
            assert client.wait_for_service(timeout_sec=8.0)

            request = EmergencyStop.Request()
            request.activate = True
            future = client.call_async(request)
            rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
            assert future.done()
            assert future.result().success

            command = Twist()
            command.linear.x = 0.4
            deadline = time.time() + 5.0
            while time.time() < deadline:
                publisher.publish(command)
                rclpy.spin_once(node, timeout_sec=0.1)
                if received and received[-1].linear.x == 0.0 and received[-1].angular.z == 0.0:
                    return

            assert received, "No /cmd_vel messages were observed."
            assert received[-1].linear.x == 0.0
            assert received[-1].angular.z == 0.0
        finally:
            node.destroy_node()
            rclpy.shutdown()


@launch_testing.post_shutdown_test()
class TestEmergencyStopShutdown:
    def test_processes_exit_cleanly(self, proc_info, safety, mission) -> None:
        proc_info.assertWaitForShutdown(process=safety, timeout=5)
        proc_info.assertWaitForShutdown(process=mission, timeout=5)
