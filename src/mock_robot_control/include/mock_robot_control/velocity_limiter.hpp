#pragma once

#include <geometry_msgs/msg/twist.hpp>

namespace mock_robot_control {

struct VelocityLimits {
  double max_linear_velocity{0.5};
  double max_angular_velocity{1.0};
  double max_linear_acceleration{0.0};
  double max_angular_acceleration{0.0};
};

class VelocityLimiter {
 public:
  explicit VelocityLimiter(const VelocityLimits& limits = VelocityLimits{});

  void setLimits(const VelocityLimits& limits);
  const VelocityLimits& limits() const;
  void reset();

  geometry_msgs::msg::Twist limit(const geometry_msgs::msg::Twist& requested,
                                  double dt_seconds = 0.0);

 private:
  VelocityLimits limits_;
  geometry_msgs::msg::Twist previous_;
  bool has_previous_{false};
};

}  // namespace mock_robot_control
