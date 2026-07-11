#pragma once

#include <geometry_msgs/msg/twist.hpp>
#include <optional>
#include <sensor_msgs/msg/laser_scan.hpp>

#include "mock_robot_control/velocity_limiter.hpp"

namespace mock_robot_control {

struct SafetyConfig {
  double obstacle_stop_distance{0.35};
  double obstacle_warning_distance{0.7};
};

class SafetyControllerLogic {
 public:
  explicit SafetyControllerLogic(const SafetyConfig& config = SafetyConfig{},
                                 const VelocityLimits& velocity_limits = VelocityLimits{});

  void setConfig(const SafetyConfig& config);
  void setVelocityLimits(const VelocityLimits& velocity_limits);
  void setEmergencyStop(bool active);
  bool emergencyStopActive() const;

  void setNearestObstacleDistance(std::optional<double> distance);
  std::optional<double> nearestObstacleDistance() const;
  void updateFromScan(const sensor_msgs::msg::LaserScan& scan);

  geometry_msgs::msg::Twist filterCommand(const geometry_msgs::msg::Twist& requested,
                                          double dt_seconds = 0.0);

 private:
  SafetyConfig config_;
  VelocityLimiter limiter_;
  bool emergency_stop_active_{false};
  std::optional<double> nearest_obstacle_distance_;
};

}  // namespace mock_robot_control
