#include <chrono>
#include <geometry_msgs/msg/twist.hpp>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <std_msgs/msg/bool.hpp>
#include <string>

#include "mock_robot_control/safety_controller.hpp"

namespace mock_robot_control {

class SafetyControllerNode : public rclcpp::Node {
 public:
  SafetyControllerNode() : Node("safety_controller") {
    SafetyConfig safety_config;
    safety_config.obstacle_stop_distance = declare_parameter("obstacle_stop_distance", 0.35);
    safety_config.obstacle_warning_distance = declare_parameter("obstacle_warning_distance", 0.7);

    VelocityLimits limits;
    limits.max_linear_velocity = declare_parameter("max_linear_velocity", 0.5);
    limits.max_angular_velocity = declare_parameter("max_angular_velocity", 1.0);
    limits.max_linear_acceleration = declare_parameter("max_linear_acceleration", 0.75);
    limits.max_angular_acceleration = declare_parameter("max_angular_acceleration", 1.5);

    logic_.setConfig(safety_config);
    logic_.setVelocityLimits(limits);

    const auto input_topic = declare_parameter<std::string>("input_topic", "/cmd_vel_requested");
    const auto output_topic = declare_parameter<std::string>("output_topic", "/cmd_vel");
    const auto scan_topic = declare_parameter<std::string>("scan_topic", "/scan");
    const auto emergency_stop_topic =
        declare_parameter<std::string>("emergency_stop_topic", "/emergency_stop");

    publisher_ = create_publisher<geometry_msgs::msg::Twist>(output_topic, 10);
    command_subscription_ = create_subscription<geometry_msgs::msg::Twist>(
        input_topic, 10, [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
          const auto now = steady_clock_.now();
          const double dt =
              last_command_time_.nanoseconds() == 0 ? 0.0 : (now - last_command_time_).seconds();
          last_command_time_ = now;
          publisher_->publish(logic_.filterCommand(*msg, dt));
        });
    scan_subscription_ = create_subscription<sensor_msgs::msg::LaserScan>(
        scan_topic, rclcpp::SensorDataQoS(),
        [this](const sensor_msgs::msg::LaserScan::SharedPtr msg) { logic_.updateFromScan(*msg); });
    emergency_subscription_ = create_subscription<std_msgs::msg::Bool>(
        emergency_stop_topic, 10, [this](const std_msgs::msg::Bool::SharedPtr msg) {
          logic_.setEmergencyStop(msg->data);
          if (msg->data) {
            publisher_->publish(geometry_msgs::msg::Twist{});
          }
        });
  }

 private:
  SafetyControllerLogic logic_;
  rclcpp::Clock steady_clock_{RCL_STEADY_TIME};
  rclcpp::Time last_command_time_{0, 0, RCL_STEADY_TIME};
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr command_subscription_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_subscription_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr emergency_subscription_;
};

}  // namespace mock_robot_control

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<mock_robot_control::SafetyControllerNode>());
  rclcpp::shutdown();
  return 0;
}
