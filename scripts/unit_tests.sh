#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
else
  echo "ROS 2 Jazzy is not installed at /opt/ros/jazzy." >&2
  exit 1
fi

cd "${ROOT_DIR}"
echo "Running C++ and Python unit tests..."
colcon test --packages-select mock_robot_control mock_robot_behavior --event-handlers console_direct+
colcon test-result --verbose
