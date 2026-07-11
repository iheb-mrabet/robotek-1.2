#include <gtest/gtest.h>

#include <limits>

#include "mock_robot_control/safety_controller.hpp"

namespace {
geometry_msgs::msg::Twist forward_command() {
  geometry_msgs::msg::Twist msg;
  msg.linear.x = 0.5;
  msg.angular.z = 0.2;
  return msg;
}
}  // namespace

TEST(SafetyController, StopsInsideObstacleStopDistance) {
  mock_robot_control::SafetyControllerLogic safety({0.35, 0.7}, {0.5, 1.0, 0.0, 0.0});
  safety.setNearestObstacleDistance(0.2);
  const auto output = safety.filterCommand(forward_command());
  EXPECT_DOUBLE_EQ(output.linear.x, 0.0);
  EXPECT_DOUBLE_EQ(output.angular.z, 0.0);
}

TEST(SafetyController, SlowsInsideWarningDistance) {
  mock_robot_control::SafetyControllerLogic safety({0.35, 0.7}, {0.5, 1.0, 0.0, 0.0});
  safety.setNearestObstacleDistance(0.525);
  const auto output = safety.filterCommand(forward_command());
  EXPECT_GT(output.linear.x, 0.0);
  EXPECT_LT(output.linear.x, 0.5);
}

TEST(SafetyController, EmergencyStopAlwaysProducesZeroVelocity) {
  mock_robot_control::SafetyControllerLogic safety({0.35, 0.7}, {0.5, 1.0, 0.0, 0.0});
  safety.setNearestObstacleDistance(2.0);
  safety.setEmergencyStop(true);
  const auto output = safety.filterCommand(forward_command());
  EXPECT_DOUBLE_EQ(output.linear.x, 0.0);
  EXPECT_DOUBLE_EQ(output.angular.z, 0.0);
}

TEST(SafetyController, ReadsNearestFiniteLaserScanRange) {
  mock_robot_control::SafetyControllerLogic safety({0.35, 0.7}, {0.5, 1.0, 0.0, 0.0});
  sensor_msgs::msg::LaserScan scan;
  scan.range_min = 0.05;
  scan.range_max = 8.0;
  scan.ranges = {std::numeric_limits<float>::infinity(), 2.0F, 0.42F,
                 std::numeric_limits<float>::quiet_NaN()};
  safety.updateFromScan(scan);
  ASSERT_TRUE(safety.nearestObstacleDistance().has_value());
  EXPECT_NEAR(*safety.nearestObstacleDistance(), 0.42, 1e-6);
}
