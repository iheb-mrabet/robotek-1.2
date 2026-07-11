#include <chrono>
#include <cmath>
#include <geometry_msgs/msg/point_stamped.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <memory>
#include <nav_msgs/msg/odometry.hpp>
#include <optional>
#include <rclcpp/rclcpp.hpp>
#include <string>

#include "mock_robot_control/waypoint_controller.hpp"

namespace mock_robot_control {
namespace {
double yaw_from_quaternion(const geometry_msgs::msg::Quaternion& q) {
  const double siny_cosp = 2.0 * (q.w * q.z + q.x * q.y);
  const double cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z);
  return std::atan2(siny_cosp, cosy_cosp);
}
}  // namespace

class WaypointControllerNode : public rclcpp::Node {
 public:
  WaypointControllerNode() : Node("waypoint_controller") {
    WaypointConfig waypoint_config;
    waypoint_config.goal_tolerance = declare_parameter("goal_tolerance", 0.15);
    waypoint_config.linear_gain = declare_parameter("linear_gain", 0.8);
    waypoint_config.angular_gain = declare_parameter("angular_gain", 1.8);
    waypoint_config.heading_slowdown_angle = declare_parameter("heading_slowdown_angle", 0.8);

    VelocityLimits limits;
    limits.max_linear_velocity = declare_parameter("max_linear_velocity", 0.5);
    limits.max_angular_velocity = declare_parameter("max_angular_velocity", 1.0);
    limits.max_linear_acceleration = declare_parameter("max_linear_acceleration", 0.75);
    limits.max_angular_acceleration = declare_parameter("max_angular_acceleration", 1.5);

    logic_.setConfig(waypoint_config);
    logic_.setVelocityLimits(limits);

    const auto target_topic = declare_parameter<std::string>("target_topic", "/mission/target");
    const auto odom_topic = declare_parameter<std::string>("odom_topic", "/odom");
    const auto output_topic = declare_parameter<std::string>("output_topic", "/cmd_vel_requested");
    const auto control_rate_hz = declare_parameter("control_rate_hz", 20.0);

    publisher_ = create_publisher<geometry_msgs::msg::Twist>(output_topic, 10);
    target_subscription_ = create_subscription<geometry_msgs::msg::PointStamped>(
        target_topic, 10, [this](const geometry_msgs::msg::PointStamped::SharedPtr msg) {
          target_x_ = msg->point.x;
          target_y_ = msg->point.y;
          RCLCPP_INFO(get_logger(), "Received waypoint target (%.2f, %.2f)", *target_x_,
                      *target_y_);
        });
    odom_subscription_ = create_subscription<nav_msgs::msg::Odometry>(
        odom_topic, 20, [this](const nav_msgs::msg::Odometry::SharedPtr msg) {
          pose_.x = msg->pose.pose.position.x;
          pose_.y = msg->pose.pose.position.y;
          pose_.yaw = yaw_from_quaternion(msg->pose.pose.orientation);
          has_pose_ = true;
        });

    const auto period = std::chrono::duration<double>(1.0 / std::max(1.0, control_rate_hz));
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period),
                               [this]() { update(); });
  }

 private:
  void update() {
    if (!has_pose_ || !target_x_.has_value() || !target_y_.has_value()) {
      return;
    }

    const auto now = steady_clock_.now();
    const double dt =
        last_update_time_.nanoseconds() == 0 ? 0.0 : (now - last_update_time_).seconds();
    last_update_time_ = now;

    const auto command = logic_.computeCommand(pose_, *target_x_, *target_y_, dt);
    publisher_->publish(command);

    if (logic_.hasReachedGoal(pose_, *target_x_, *target_y_)) {
      target_x_.reset();
      target_y_.reset();
      publisher_->publish(geometry_msgs::msg::Twist{});
    }
  }

  WaypointControllerLogic logic_;
  Pose2D pose_;
  bool has_pose_{false};
  std::optional<double> target_x_;
  std::optional<double> target_y_;
  rclcpp::Clock steady_clock_{RCL_STEADY_TIME};
  rclcpp::Time last_update_time_{0, 0, RCL_STEADY_TIME};
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::Subscription<geometry_msgs::msg::PointStamped>::SharedPtr target_subscription_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_subscription_;
  rclcpp::TimerBase::SharedPtr timer_;
};

}  // namespace mock_robot_control

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<mock_robot_control::WaypointControllerNode>());
  rclcpp::shutdown();
  return 0;
}
