cmake_minimum_required(VERSION 3.8)
project(mock_robot_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MissionStatus.msg"
  "srv/EmergencyStop.srv"
  "action/ExecuteDelivery.action"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
