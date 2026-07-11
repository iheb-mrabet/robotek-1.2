#include "mock_robot_control/safety_controller.hpp"

#include <algorithm>
#include <cmath>

namespace mock_robot_control {
namespace {
geometry_msgs::msg::Twist zero_twist() { return geometry_msgs::msg::Twist{}; }
}  // namespace

SafetyControllerLogic::SafetyControllerLogic(const SafetyConfig& config,
                                             const VelocityLimits& velocity_limits)
    : config_(config), limiter_(velocity_limits) {}

void SafetyControllerLogic::setConfig(const SafetyConfig& config) { config_ = config; }

void SafetyControllerLogic::setVelocityLimits(const VelocityLimits& velocity_limits) {
  limiter_.setLimits(velocity_limits);
}

void SafetyControllerLogic::setEmergencyStop(bool active) {
  emergency_stop_active_ = active;
  if (active) {
    limiter_.reset();
  }
}

bool SafetyControllerLogic::emergencyStopActive() const { return emergency_stop_active_; }

void SafetyControllerLogic::setNearestObstacleDistance(std::optional<double> distance) {
  if (distance.has_value() && !std::isfinite(*distance)) {
    nearest_obstacle_distance_.reset();
    return;
  }
  nearest_obstacle_distance_ = distance;
}

std::optional<double> SafetyControllerLogic::nearestObstacleDistance() const {
  return nearest_obstacle_distance_;
}

void SafetyControllerLogic::updateFromScan(const sensor_msgs::msg::LaserScan& scan) {
  std::optional<double> nearest;
  for (const auto range : scan.ranges) {
    if (!std::isfinite(range)) {
      continue;
    }
    if (range < scan.range_min || range > scan.range_max) {
      continue;
    }
    if (!nearest.has_value() || range < *nearest) {
      nearest = range;
    }
  }
  nearest_obstacle_distance_ = nearest;
}

geometry_msgs::msg::Twist SafetyControllerLogic::filterCommand(
    const geometry_msgs::msg::Twist& requested, double dt_seconds) {
  if (emergency_stop_active_) {
    return zero_twist();
  }

  auto limited = limiter_.limit(requested, dt_seconds);
  if (!nearest_obstacle_distance_.has_value()) {
    return limited;
  }

  const double distance = *nearest_obstacle_distance_;
  if (distance <= config_.obstacle_stop_distance) {
    limiter_.reset();
    return zero_twist();
  }

  if (distance < config_.obstacle_warning_distance &&
      config_.obstacle_warning_distance > config_.obstacle_stop_distance) {
    const double scale =
        std::clamp((distance - config_.obstacle_stop_distance) /
                       (config_.obstacle_warning_distance - config_.obstacle_stop_distance),
                   0.0, 1.0);
    if (limited.linear.x > 0.0) {
      limited.linear.x *= scale;
    }
  }

  return limited;
}

}  // namespace mock_robot_control
