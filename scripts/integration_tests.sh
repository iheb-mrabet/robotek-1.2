#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/build.sh"

# shellcheck source=/dev/null
source "${ROOT_DIR}/install/setup.bash"

cd "${ROOT_DIR}"
echo "Running ROS 2 integration tests..."
colcon test \
  --packages-select mock_robot_system_tests \
  --event-handlers console_direct+ \
  --pytest-args -m integration
colcon test-result --verbose
