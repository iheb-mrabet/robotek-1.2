#pragma once

#include <geometry_msgs/msg/twist.hpp>

#include "mock_robot_control/velocity_limiter.hpp"

namespace mock_robot_control {

struct Pose2D {
  double x{0.0};
  double y{0.0};
  double yaw{0.0};
};

struct WaypointConfig {
  double goal_tolerance{0.15};
  double linear_gain{0.8};
  double angular_gain{1.8};
  double heading_slowdown_angle{0.8};
};

class WaypointControllerLogic {
 public:
  explicit WaypointControllerLogic(const WaypointConfig& config = WaypointConfig{},
                                   const VelocityLimits& velocity_limits = VelocityLimits{});

  void setConfig(const WaypointConfig& config);
  void setVelocityLimits(const VelocityLimits& velocity_limits);

  double distanceToGoal(const Pose2D& pose, double target_x, double target_y) const;
  double headingError(const Pose2D& pose, double target_x, double target_y) const;
  bool hasReachedGoal(const Pose2D& pose, double target_x, double target_y) const;

  geometry_msgs::msg::Twist computeCommand(const Pose2D& pose, double target_x, double target_y,
                                           double dt_seconds = 0.0);

  static double normalizeAngle(double angle);

 private:
  WaypointConfig config_;
  VelocityLimiter limiter_;
};

}  // namespace mock_robot_control
