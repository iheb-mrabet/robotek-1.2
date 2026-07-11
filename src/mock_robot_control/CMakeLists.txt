cmake_minimum_required(VERSION 3.8)
project(mock_robot_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_library(mock_robot_control_core
  src/velocity_limiter.cpp
  src/safety_controller.cpp
  src/waypoint_controller.cpp
)
target_include_directories(mock_robot_control_core
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_features(mock_robot_control_core PUBLIC cxx_std_17)
ament_target_dependencies(mock_robot_control_core geometry_msgs sensor_msgs)

add_executable(velocity_limiter src/velocity_limiter_node.cpp)
target_compile_features(velocity_limiter PRIVATE cxx_std_17)
target_link_libraries(velocity_limiter mock_robot_control_core)
ament_target_dependencies(velocity_limiter geometry_msgs rclcpp)

add_executable(safety_controller src/safety_controller_node.cpp)
target_compile_features(safety_controller PRIVATE cxx_std_17)
target_link_libraries(safety_controller mock_robot_control_core)
ament_target_dependencies(safety_controller geometry_msgs rclcpp sensor_msgs std_msgs)

add_executable(waypoint_controller src/waypoint_controller_node.cpp)
target_compile_features(waypoint_controller PRIVATE cxx_std_17)
target_link_libraries(waypoint_controller mock_robot_control_core)
ament_target_dependencies(waypoint_controller geometry_msgs nav_msgs rclcpp)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  TARGETS
    mock_robot_control_core
  EXPORT export_mock_robot_control_core
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  INCLUDES DESTINATION include
)

install(
  TARGETS
    velocity_limiter
    safety_controller
    waypoint_controller
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

ament_export_targets(export_mock_robot_control_core HAS_LIBRARY_TARGET)
ament_export_dependencies(geometry_msgs sensor_msgs)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)

  ament_add_gtest(test_velocity_limiter test/test_velocity_limiter.cpp)
  target_link_libraries(test_velocity_limiter mock_robot_control_core)
  ament_target_dependencies(test_velocity_limiter geometry_msgs)

  ament_add_gtest(test_safety_controller test/test_safety_controller.cpp)
  target_link_libraries(test_safety_controller mock_robot_control_core)
  ament_target_dependencies(test_safety_controller geometry_msgs sensor_msgs)

  ament_add_gtest(test_waypoint_controller test/test_waypoint_controller.cpp)
  target_link_libraries(test_waypoint_controller mock_robot_control_core)
  ament_target_dependencies(test_waypoint_controller geometry_msgs)
endif()

ament_package()
