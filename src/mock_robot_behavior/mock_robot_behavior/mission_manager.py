from __future__ import annotations

from math import hypot

import rclpy
from geometry_msgs.msg import PointStamped
from mock_robot_interfaces.action import ExecuteDelivery
from mock_robot_interfaces.msg import MissionStatus
from mock_robot_interfaces.srv import EmergencyStop
from nav_msgs.msg import Odometry
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.task import Future
from std_msgs.msg import Bool

from mock_robot_behavior.mission_state_machine import (
    MissionState,
    MissionStateMachine,
)
from mock_robot_behavior.mission_validation import DestinationValidator


class MissionManager(Node):
    def __init__(self) -> None:
        super().__init__("mission_manager")
        self._mission_timeout = float(self.declare_parameter("mission_timeout", 30.0).value)
        self._goal_tolerance = float(self.declare_parameter("goal_tolerance", 0.15).value)
        self._status_rate_hz = float(self.declare_parameter("status_rate_hz", 2.0).value)
        self._max_abs_coordinate = float(self.declare_parameter("max_abs_coordinate", 4.5).value)

        self._state_machine = MissionStateMachine()
        self._validator = DestinationValidator(max_abs_coordinate=self._max_abs_coordinate)
        self._latest_odom: Odometry | None = None
        self._active_goal = False
        self._emergency_stop_active = False
        self._mission_stopped = False
        self._status_message = "Waiting for delivery request."
        self._remaining_distance = 0.0

        self._target_pub = self.create_publisher(PointStamped, "/mission/target", 10)
        self._status_pub = self.create_publisher(MissionStatus, "/mission/status", 10)
        self._emergency_pub = self.create_publisher(Bool, "/emergency_stop", 10)
        self.create_subscription(Odometry, "/odom", self._on_odom, 20)

        self.create_service(EmergencyStop, "/mission/emergency_stop", self._on_emergency_stop)
        self._action_server = ActionServer(
            self,
            ExecuteDelivery,
            "execute_delivery",
            execute_callback=self._execute_delivery,
            goal_callback=self._on_goal,
            cancel_callback=self._on_cancel,
            callback_group=ReentrantCallbackGroup(),
        )

        period = 1.0 / max(self._status_rate_hz, 0.1)
        self.create_timer(period, self._publish_status)

    def _on_odom(self, msg: Odometry) -> None:
        self._latest_odom = msg

    def _on_goal(self, goal_request: ExecuteDelivery.Goal) -> GoalResponse:
        if (
            self._active_goal
            or self._emergency_stop_active
            or self._state_machine.state
            not in {
                MissionState.IDLE,
                MissionState.COMPLETED,
                MissionState.FAILED,
            }
        ):
            return GoalResponse.REJECT
        current_x, current_y = self._current_position()
        validation = self._validator.validate(
            goal_request.target_x, goal_request.target_y, current_x, current_y
        )
        if not validation.accepted:
            return GoalResponse.REJECT
        # Reserve before returning ACCEPT, so queued goals cannot both be accepted.
        self._active_goal = True
        self._mission_stopped = False
        return GoalResponse.ACCEPT

    def _on_cancel(self, _goal_handle: object) -> CancelResponse:
        return CancelResponse.ACCEPT

    def _on_emergency_stop(
        self,
        request: EmergencyStop.Request,
        response: EmergencyStop.Response,
    ) -> EmergencyStop.Response:
        self._emergency_stop_active = bool(request.activate)
        self._emergency_pub.publish(Bool(data=self._emergency_stop_active))
        if self._emergency_stop_active:
            self._mission_stopped = self._active_goal
            self._state_machine.emergency_stop()
            self._status_message = "Emergency stop is active."
        elif self._state_machine.state == MissionState.EMERGENCY_STOPPED:
            if not self._active_goal:
                self._state_machine.reset()
            self._status_message = "Emergency stop released."
        response.success = True
        response.message = self._status_message
        self._publish_status()
        return response

    async def _execute_delivery(self, goal_handle):
        request = goal_handle.request
        self._active_goal = True
        result = ExecuteDelivery.Result()

        try:
            if self._emergency_stop_active or self._mission_stopped:
                self._state_machine.emergency_stop()
                self._status_message = "Delivery stopped by emergency stop."
                goal_handle.abort()
                return self._populate_result(result, success=False)
            if self._state_machine.state != MissionState.IDLE:
                self._state_machine.reset()
            self._state_machine.begin_validation()

            current_x, current_y = self._current_position()
            validation = self._validator.validate(
                request.target_x,
                request.target_y,
                current_x,
                current_y,
            )
            if not validation.accepted:
                return self._finish_failure(goal_handle, result, validation.message)

            self._state_machine.begin_navigation()
            self._status_message = "Navigating to delivery target."
            self._publish_target(request.target_x, request.target_y)
            started_at = self.get_clock().now()

            while rclpy.ok():
                if self._emergency_stop_active or self._mission_stopped:
                    self._state_machine.emergency_stop()
                    self._status_message = "Delivery stopped by emergency stop."
                    goal_handle.abort()
                    return self._populate_result(result, success=False)

                if goal_handle.is_cancel_requested:
                    self._state_machine.fail()
                    self._status_message = "Delivery mission canceled."
                    goal_handle.canceled()
                    return self._populate_result(result, success=False)

                current_x, current_y = self._current_position()
                self._remaining_distance = hypot(
                    request.target_x - current_x, request.target_y - current_y
                )
                elapsed = (self.get_clock().now() - started_at).nanoseconds / 1_000_000_000.0
                if self._state_machine.fail_if_timed_out(elapsed, self._mission_timeout):
                    self._status_message = "Delivery mission timed out."
                    goal_handle.abort()
                    return self._populate_result(result, success=False)

                if self._remaining_distance <= self._goal_tolerance:
                    self._state_machine.complete()
                    self._status_message = "Delivery target reached."
                    goal_handle.succeed()
                    return self._populate_result(result, success=True)

                feedback = ExecuteDelivery.Feedback()
                feedback.current_x = current_x
                feedback.current_y = current_y
                feedback.remaining_distance = self._remaining_distance
                feedback.state = self._state_machine.state.value
                goal_handle.publish_feedback(feedback)
                self._publish_status()
                await self._wait_for_update()
            return self._finish_failure(goal_handle, result, "ROS shutdown interrupted delivery.")
        finally:
            # Clear the controller target on every unsuccessful exit. This also
            # prevents releasing an emergency stop from resuming an old mission.
            if (
                rclpy.ok()
                and self._latest_odom is not None
                and self._state_machine.state != MissionState.COMPLETED
            ):
                self._publish_target(*self._current_position())
            self._active_goal = False
            if (
                self._state_machine.state == MissionState.EMERGENCY_STOPPED
                and not self._emergency_stop_active
            ):
                self._state_machine.reset()
                self._status_message = "Emergency stop released."
                self._publish_status()

    async def _wait_for_update(self) -> None:
        # rclpy executes coroutines without an asyncio event loop. A ROS Future
        # yields to its executor so odometry, cancel and stop callbacks can run.
        ready: Future = Future()

        def wake() -> None:
            timer.cancel()
            if not ready.done():
                ready.set_result(None)

        timer = self.create_timer(0.2, wake)
        try:
            await ready
        finally:
            self.destroy_timer(timer)

    def _finish_failure(
        self, goal_handle, result: ExecuteDelivery.Result, message: str
    ) -> ExecuteDelivery.Result:
        self._state_machine.fail()
        self._status_message = message
        goal_handle.abort()
        return self._populate_result(result, success=False)

    def _populate_result(
        self, result: ExecuteDelivery.Result, success: bool
    ) -> ExecuteDelivery.Result:
        result.success = success
        result.final_state = self._state_machine.state.value
        result.message = self._status_message
        self._publish_status()
        return result

    def _current_position(self) -> tuple[float, float]:
        if self._latest_odom is None:
            return 0.0, 0.0
        return (
            float(self._latest_odom.pose.pose.position.x),
            float(self._latest_odom.pose.pose.position.y),
        )

    def _publish_target(self, target_x: float, target_y: float) -> None:
        msg = PointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "odom"
        msg.point.x = target_x
        msg.point.y = target_y
        self._target_pub.publish(msg)

    def _publish_status(self) -> None:
        msg = MissionStatus()
        msg.state = self._state_machine.state.value
        msg.message = self._status_message
        msg.remaining_distance = float(self._remaining_distance)
        self._status_pub.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = MissionManager()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
