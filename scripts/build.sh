#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # ROS setup scripts may reference unset variables.
  set +u
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
  set -u
else
  echo "ROS 2 Jazzy is not installed at /opt/ros/jazzy." >&2
  exit 1
fi

cd "${ROOT_DIR}"

echo "Building mock delivery robot workspace..."
colcon build --symlink-install