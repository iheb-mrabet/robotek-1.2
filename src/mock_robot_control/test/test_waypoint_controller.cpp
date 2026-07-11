#include <gtest/gtest.h>

#include <cmath>

#include "mock_robot_control/waypoint_controller.hpp"

TEST(WaypointController, DetectsGoalTolerance) {
  mock_robot_control::WaypointControllerLogic controller({0.15, 0.8, 1.8, 0.8},
                                                         {0.5, 1.0, 0.0, 0.0});
  const mock_robot_control::Pose2D pose{1.0, 1.0, 0.0};
  EXPECT_TRUE(controller.hasReachedGoal(pose, 1.05, 1.05));
  EXPECT_FALSE(controller.hasReachedGoal(pose, 1.3, 1.0));
}

TEST(WaypointController, CalculatesDistanceToGoal) {
  mock_robot_control::WaypointControllerLogic controller;
  const mock_robot_control::Pose2D pose{0.0, 0.0, 0.0};
  EXPECT_NEAR(controller.distanceToGoal(pose, 3.0, 4.0), 5.0, 1e-9);
}

TEST(WaypointController, CalculatesHeadingError) {
  mock_robot_control::WaypointControllerLogic controller;
  const mock_robot_control::Pose2D pose{0.0, 0.0, 0.0};
  EXPECT_NEAR(controller.headingError(pose, 0.0, 1.0), 1.5707963267948966, 1e-9);
}

TEST(WaypointController, ProducesBoundedCommandTowardGoal) {
  mock_robot_control::WaypointControllerLogic controller({0.15, 1.0, 2.0, 1.0},
                                                         {0.5, 1.0, 0.0, 0.0});
  const mock_robot_control::Pose2D pose{0.0, 0.0, 0.0};
  const auto output = controller.computeCommand(pose, 2.0, 0.0);
  EXPECT_GT(output.linear.x, 0.0);
  EXPECT_LE(output.linear.x, 0.5);
  EXPECT_NEAR(output.angular.z, 0.0, 1e-9);
}

TEST(WaypointController, StopsAtGoal) {
  mock_robot_control::WaypointControllerLogic controller({0.15, 1.0, 2.0, 1.0},
                                                         {0.5, 1.0, 0.0, 0.0});
  const mock_robot_control::Pose2D pose{0.0, 0.0, 0.0};
  const auto output = controller.computeCommand(pose, 0.05, 0.0);
  EXPECT_DOUBLE_EQ(output.linear.x, 0.0);
  EXPECT_DOUBLE_EQ(output.angular.z, 0.0);
}
