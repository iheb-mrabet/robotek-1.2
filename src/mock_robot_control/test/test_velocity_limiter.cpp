#include <gtest/gtest.h>

#include <cmath>
#include <limits>

#include "mock_robot_control/velocity_limiter.hpp"

namespace {
geometry_msgs::msg::Twist twist(double linear, double angular) {
  geometry_msgs::msg::Twist msg;
  msg.linear.x = linear;
  msg.angular.z = angular;
  return msg;
}
}  // namespace

TEST(VelocityLimiter, LimitsLinearVelocity) {
  mock_robot_control::VelocityLimiter limiter({0.5, 1.0, 0.0, 0.0});
  const auto output = limiter.limit(twist(2.0, 0.0));
  EXPECT_DOUBLE_EQ(output.linear.x, 0.5);
}

TEST(VelocityLimiter, LimitsAngularVelocity) {
  mock_robot_control::VelocityLimiter limiter({0.5, 1.0, 0.0, 0.0});
  const auto output = limiter.limit(twist(0.0, -5.0));
  EXPECT_DOUBLE_EQ(output.angular.z, -1.0);
}

TEST(VelocityLimiter, ReplacesNonFiniteValuesWithZero) {
  mock_robot_control::VelocityLimiter limiter({0.5, 1.0, 0.0, 0.0});
  auto requested =
      twist(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::infinity());
  const auto output = limiter.limit(requested);
  EXPECT_DOUBLE_EQ(output.linear.x, 0.0);
  EXPECT_DOUBLE_EQ(output.angular.z, 0.0);
}

TEST(VelocityLimiter, LimitsAccelerationWhenConfigured) {
  mock_robot_control::VelocityLimiter limiter({1.0, 2.0, 0.4, 0.8});
  limiter.limit(twist(0.0, 0.0));
  const auto output = limiter.limit(twist(1.0, 2.0), 0.5);
  EXPECT_NEAR(output.linear.x, 0.2, 1e-9);
  EXPECT_NEAR(output.angular.z, 0.4, 1e-9);
}
