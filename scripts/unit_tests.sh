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
colcon test --packages-select mock_robot_control --event-handlers console_direct+
colcon test-result --verbose

mkdir -p reports/unit
export PYTHONPATH="${ROOT_DIR}/src/mock_robot_behavior:${PYTHONPATH:-}"
python3 -m pytest \
  src/mock_robot_behavior/test \
  --junitxml=reports/unit/mock_robot_behavior.xml
