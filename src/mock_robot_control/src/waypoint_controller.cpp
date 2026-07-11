#include "mock_robot_control/waypoint_controller.hpp"

#include <algorithm>
#include <cmath>

namespace mock_robot_control {
namespace {
constexpr double kPi = 3.14159265358979323846;
}

WaypointControllerLogic::WaypointControllerLogic(const WaypointConfig& config,
                                                 const VelocityLimits& velocity_limits)
    : config_(config), limiter_(velocity_limits) {}

void WaypointControllerLogic::setConfig(const WaypointConfig& config) { config_ = config; }

void WaypointControllerLogic::setVelocityLimits(const VelocityLimits& velocity_limits) {
  limiter_.setLimits(velocity_limits);
}

double WaypointControllerLogic::distanceToGoal(const Pose2D& pose, double target_x,
                                               double target_y) const {
  return std::hypot(target_x - pose.x, target_y - pose.y);
}

double WaypointControllerLogic::headingError(const Pose2D& pose, double target_x,
                                             double target_y) const {
  const double target_heading = std::atan2(target_y - pose.y, target_x - pose.x);
  return normalizeAngle(target_heading - pose.yaw);
}

bool WaypointControllerLogic::hasReachedGoal(const Pose2D& pose, double target_x,
                                             double target_y) const {
  return distanceToGoal(pose, target_x, target_y) <= config_.goal_tolerance;
}

geometry_msgs::msg::Twist WaypointControllerLogic::computeCommand(const Pose2D& pose,
                                                                  double target_x, double target_y,
                                                                  double dt_seconds) {
  geometry_msgs::msg::Twist requested;
  const double distance = distanceToGoal(pose, target_x, target_y);
  if (distance <= config_.goal_tolerance) {
    limiter_.reset();
    return requested;
  }

  const double error = headingError(pose, target_x, target_y);
  const double heading_scale = std::clamp(
      1.0 - (std::abs(error) / std::max(0.01, config_.heading_slowdown_angle)), 0.0, 1.0);

  requested.linear.x = config_.linear_gain * distance * heading_scale;
  requested.angular.z = config_.angular_gain * error;
  return limiter_.limit(requested, dt_seconds);
}

double WaypointControllerLogic::normalizeAngle(double angle) {
  while (angle > kPi) {
    angle -= 2.0 * kPi;
  }
  while (angle < -kPi) {
    angle += 2.0 * kPi;
  }
  return angle;
}

}  // namespace mock_robot_control
