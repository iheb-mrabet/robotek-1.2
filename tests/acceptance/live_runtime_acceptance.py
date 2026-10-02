"""Accept the deployed Robotek runtime using actual Gazebo odometry."""

import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Twist
from mock_robot_interfaces.action import ExecuteDelivery
from mock_robot_interfaces.srv import EmergencyStop
from nav_msgs.msg import Odometry
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data

rclpy.init()
node = rclpy.create_node("robotek_live_acceptance")
positions = []
commands = []
feedback = []
node.create_subscription(
    Odometry,
    "/odom",
    lambda msg: positions.append((msg.pose.pose.position.x, msg.pose.pose.position.y)),
    qos_profile_sensor_data,
)
node.create_subscription(
    Twist, "/cmd_vel", lambda msg: commands.append((msg.linear.x, msg.angular.z)), 20
)
client = ActionClient(node, ExecuteDelivery, "/execute_delivery")
stop = node.create_client(EmergencyStop, "/mission/emergency_stop")


def until(predicate, timeout=80):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
    assert predicate(), "Live ROS acceptance deadline exceeded"


def wait(future, timeout=80):
    until(future.done, timeout)
    return future.result()


def spin_for(seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)


def set_stop(active):
    response = wait(stop.call_async(EmergencyStop.Request(activate=active)), 12)
    assert response.success, response.message
    print("STOP", active, response.message, flush=True)


def goal(x, y=0):
    return wait(
        client.send_goal_async(
            ExecuteDelivery.Goal(target_x=float(x), target_y=float(y)),
            feedback_callback=lambda msg: feedback.append(
                msg.feedback.remaining_distance
            ),
        ),
        15,
    )


def complete(x, y=0):
    feedback.clear()
    handle = goal(x, y)
    assert handle.accepted, "Reachable delivery rejected"
    response = wait(handle.get_result_async())
    print("DELIVERY", x, y, "STATUS", response.status, response.result, flush=True)
    assert response.status == GoalStatus.STATUS_SUCCEEDED, response.result.message
    assert response.result.success and response.result.final_state == "COMPLETED"
    assert feedback, "No live navigation feedback"
    assert math.hypot(positions[-1][0] - x, positions[-1][1] - y) < 0.18
    print(
        "PASS simulated delivery with actual odometry",
        "position",
        positions[-1],
        "feedback",
        len(feedback),
        flush=True,
    )


def stationary():
    # Gazebo models physical braking rather than teleporting velocity to zero.
    # Require the robot to reach a stable position within a bounded interval,
    # then prove that it remains stopped and receives no non-zero command.
    stop_origin = positions[-1]
    previous = stop_origin
    stable_samples = 0
    settle_deadline = time.monotonic() + 5.0
    while stable_samples < 2 and time.monotonic() < settle_deadline:
        sample_count = len(positions)
        spin_for(0.4)
        assert len(positions) > sample_count, "Odometry stopped publishing during stop verification"
        current = positions[-1]
        segment_drift = math.hypot(
            current[0] - previous[0], current[1] - previous[1]
        )
        stable_samples = stable_samples + 1 if segment_drift < 0.01 else 0
        previous = current
    assert stable_samples >= 2, "Interrupted robot did not settle in simulation within 5s"
    stopping_distance = math.hypot(
        positions[-1][0] - stop_origin[0], positions[-1][1] - stop_origin[1]
    )
    commands.clear()
    start = positions[-1]
    sample_count = len(positions)
    spin_for(1.5)
    assert len(positions) > sample_count, "No fresh odometry during stationary observation"
    assert commands, "No velocity heartbeat during stationary observation"
    drift = math.hypot(positions[-1][0] - start[0], positions[-1][1] - start[1])
    assert drift < 0.03, f"Interrupted robot still moving: {drift}"
    assert max(
        max(abs(linear), abs(angular)) for linear, angular in commands
    ) < 0.001, f"Non-zero command published after interruption: {commands[-1]}"
    print(
        "PASS interrupted motion stopped",
        "post-stop commands",
        commands,
        "stopping distance",
        stopping_distance,
        "drift",
        drift,
        flush=True,
    )


try:
    assert client.wait_for_server(timeout_sec=15)
    assert stop.wait_for_service(timeout_sec=15)
    until(lambda: bool(positions), 20)
    set_stop(False)
    spin_for(1)
    print("START actual odometry", positions[-1], flush=True)
    if math.hypot(*positions[-1]) > 0.2:
        complete(0)
    complete(0.8)

    feedback.clear()
    commands.clear()
    handle = goal(1.8)
    assert handle.accepted
    until(lambda: bool(feedback), 15)
    until(lambda: commands and abs(commands[-1][0]) > 0.02, 15)
    assert not goal(2.0).accepted, "Concurrent mission was accepted"
    cancel = wait(handle.cancel_goal_async(), 15)
    assert cancel.goals_canceling
    response = wait(handle.get_result_async(), 15)
    assert response.status == GoalStatus.STATUS_CANCELED
    assert not response.result.success and "canceled" in response.result.message
    print("PASS cancellation", response.result, flush=True)
    stationary()

    feedback.clear()
    commands.clear()
    handle = goal(0)
    assert handle.accepted
    until(lambda: bool(feedback), 15)
    until(lambda: commands and max(abs(v) for v in commands[-1]) > 0.02, 15)
    set_stop(True)
    response = wait(handle.get_result_async(), 15)
    assert response.status == GoalStatus.STATUS_ABORTED
    assert response.result.final_state == "EMERGENCY_STOPPED"
    assert not response.result.success and response.result.message
    assert not goal(0).accepted
    print("PASS active emergency-stop interruption", response.result, flush=True)
    stationary()
    set_stop(False)
    stationary()
    complete(0)
    assert not goal(8, 8).accepted
    assert not goal(float("nan")).accepted
    print("PASS invalid and non-finite destinations rejected", flush=True)
    print("PASS DEPLOYED ROBOTEK LIVE ACCEPTANCE", flush=True)
except BaseException:
    if stop.service_is_ready():
        set_stop(True)
        spin_for(1)
        set_stop(False)
    raise
finally:
    node.destroy_node()
    rclpy.try_shutdown()
