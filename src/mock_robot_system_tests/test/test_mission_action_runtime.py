"""Exercise the real action callback under a single-threaded ROS executor."""

import time
import unittest

import launch
import launch_testing
import pytest
import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PointStamped
from launch_ros.actions import Node
from mock_robot_interfaces.action import ExecuteDelivery
from mock_robot_interfaces.srv import EmergencyStop
from nav_msgs.msg import Odometry
from rclpy.action import ActionClient

pytestmark = pytest.mark.integration


@pytest.mark.launch_test
def generate_test_description():
    mission = Node(
        package="mock_robot_behavior",
        executable="mission_manager",
        parameters=[{"mission_timeout": 3.0}],
        output="screen",
    )
    return launch.LaunchDescription([mission, launch_testing.actions.ReadyToTest()])


class TestMissionActionRuntime(unittest.TestCase):
    def test_completion_cancel_stop_and_timeout(self):
        rclpy.init()
        node = rclpy.create_node("mission_action_runtime_probe")
        try:
            client = ActionClient(node, ExecuteDelivery, "/execute_delivery")
            stop = node.create_client(EmergencyStop, "/mission/emergency_stop")
            odom = node.create_publisher(Odometry, "/odom", 20)
            targets = []
            node.create_subscription(
                PointStamped, "/mission/target", lambda msg: targets.append(msg.point.x), 20
            )
            assert client.wait_for_server(timeout_sec=10.0)
            assert stop.wait_for_service(timeout_sec=10.0)

            def spin_until(predicate, timeout=5.0):
                deadline = time.monotonic() + timeout
                while not predicate() and time.monotonic() < deadline:
                    rclpy.spin_once(node, timeout_sec=0.05)
                assert predicate(), "ROS callback did not complete before deadline"

            def wait(future):
                spin_until(future.done)
                return future.result()

            def send(x):
                return wait(client.send_goal_async(ExecuteDelivery.Goal(target_x=x, target_y=0.0)))

            def move(x):
                message = Odometry()
                message.pose.pose.position.x = x
                # Repeat while spinning so DDS discovery and odom callbacks run.
                deadline = time.monotonic() + 0.5
                while time.monotonic() < deadline:
                    odom.publish(message)
                    rclpy.spin_once(node, timeout_sec=0.05)

            def set_stop(active):
                response = wait(stop.call_async(EmergencyStop.Request(activate=active)))
                assert response.success

            move(0.0)
            goal = send(1.0)
            assert goal.accepted
            result_future = goal.get_result_async()
            # The old asyncio.sleep aborts here before any odom update can arrive.
            move(0.0)
            assert not result_future.done(), "Accepted mission aborted while waiting for odometry"
            assert not send(2.0).accepted, "Concurrent delivery must be rejected"
            move(1.0)
            completed = wait(result_future)
            assert completed.status == GoalStatus.STATUS_SUCCEEDED
            assert completed.result.success
            assert completed.result.final_state == "COMPLETED"
            assert completed.result.message

            # Origin is a valid destination when the robot is away from it.
            goal = send(0.0)
            assert goal.accepted
            move(0.0)
            returned = wait(goal.get_result_async())
            assert returned.status == GoalStatus.STATUS_SUCCEEDED

            goal = send(2.0)
            assert goal.accepted
            move(1.0)
            targets.clear()
            cancellation = wait(goal.cancel_goal_async())
            assert cancellation.goals_canceling
            canceled = wait(goal.get_result_async())
            assert canceled.status == GoalStatus.STATUS_CANCELED
            assert not canceled.result.success
            assert canceled.result.final_state == "FAILED"
            assert "canceled" in canceled.result.message
            spin_until(lambda: bool(targets) and targets[-1] == 1.0)

            goal = send(2.0)
            assert goal.accepted
            move(1.0)
            targets.clear()
            set_stop(True)
            stopped = wait(goal.get_result_async())
            assert stopped.status == GoalStatus.STATUS_ABORTED
            assert not stopped.result.success
            assert stopped.result.final_state == "EMERGENCY_STOPPED"
            assert stopped.result.message
            spin_until(lambda: bool(targets) and targets[-1] == 1.0)
            assert not send(2.0).accepted
            set_stop(False)

            goal = send(2.0)
            assert goal.accepted, "Released stop must permit a new mission"
            timed_out = wait(goal.get_result_async())
            assert timed_out.status == GoalStatus.STATUS_ABORTED
            assert timed_out.result.final_state == "FAILED"
            assert not timed_out.result.success
            assert "timed out" in timed_out.result.message
            assert not send(8.0).accepted
        finally:
            node.destroy_node()
            rclpy.shutdown()
