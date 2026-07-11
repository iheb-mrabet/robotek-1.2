#include <chrono>
#include <geometry_msgs/msg/twist.hpp>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <string>

#include "mock_robot_control/velocity_limiter.hpp"

namespace mock_robot_control {

class VelocityLimiterNode : public rclcpp::Node {
 public:
  VelocityLimiterNode() : Node("velocity_limiter") {
    VelocityLimits limits;
    limits.max_linear_velocity = declare_parameter("max_linear_velocity", 0.5);
    limits.max_angular_velocity = declare_parameter("max_angular_velocity", 1.0);
    limits.max_linear_acceleration = declare_parameter("max_linear_acceleration", 0.75);
    limits.max_angular_acceleration = declare_parameter("max_angular_acceleration", 1.5);
    limiter_.setLimits(limits);

    const auto input_topic = declare_parameter<std::string>("input_topic", "/cmd_vel_raw");
    const auto output_topic = declare_parameter<std::string>("output_topic", "/cmd_vel_requested");

    publisher_ = create_publisher<geometry_msgs::msg::Twist>(output_topic, 10);
    subscription_ = create_subscription<geometry_msgs::msg::Twist>(
        input_topic, 10, [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
          const auto now = steady_clock_.now();
          const double dt =
              last_command_time_.nanoseconds() == 0 ? 0.0 : (now - last_command_time_).seconds();
          last_command_time_ = now;
          publisher_->publish(limiter_.limit(*msg, dt));
        });
  }

 private:
  VelocityLimiter limiter_;
  rclcpp::Clock steady_clock_{RCL_STEADY_TIME};
  rclcpp::Time last_command_time_{0, 0, RCL_STEADY_TIME};
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
};

}  // namespace mock_robot_control

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<mock_robot_control::VelocityLimiterNode>());
  rclcpp::shutdown();
  return 0;
}
