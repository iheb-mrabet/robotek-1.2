#include "mock_robot_control/velocity_limiter.hpp"

#include <algorithm>
#include <cmath>

namespace mock_robot_control {
namespace {
double finite_or_zero(double value) { return std::isfinite(value) ? value : 0.0; }

double clamp_abs(double value, double max_abs) {
  const double limit = std::max(0.0, max_abs);
  return std::clamp(value, -limit, limit);
}

double limit_rate(double requested, double previous, double max_rate, double dt_seconds) {
  if (max_rate <= 0.0 || dt_seconds <= 0.0) {
    return requested;
  }
  const double max_delta = max_rate * dt_seconds;
  return previous + std::clamp(requested - previous, -max_delta, max_delta);
}
}  // namespace

VelocityLimiter::VelocityLimiter(const VelocityLimits& limits) : limits_(limits) {}

void VelocityLimiter::setLimits(const VelocityLimits& limits) { limits_ = limits; }

const VelocityLimits& VelocityLimiter::limits() const { return limits_; }

void VelocityLimiter::reset() {
  previous_ = geometry_msgs::msg::Twist{};
  has_previous_ = false;
}

geometry_msgs::msg::Twist VelocityLimiter::limit(const geometry_msgs::msg::Twist& requested,
                                                 double dt_seconds) {
  geometry_msgs::msg::Twist output;
  output.linear.x = clamp_abs(finite_or_zero(requested.linear.x), limits_.max_linear_velocity);
  output.angular.z = clamp_abs(finite_or_zero(requested.angular.z), limits_.max_angular_velocity);

  if (has_previous_) {
    output.linear.x = limit_rate(output.linear.x, previous_.linear.x,
                                 limits_.max_linear_acceleration, dt_seconds);
    output.angular.z = limit_rate(output.angular.z, previous_.angular.z,
                                  limits_.max_angular_acceleration, dt_seconds);
  }

  previous_ = output;
  has_previous_ = true;
  return output;
}

}  // namespace mock_robot_control
