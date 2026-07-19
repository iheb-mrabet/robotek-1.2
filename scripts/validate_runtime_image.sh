#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:-robotek-runtime:local}"

echo "Validating runtime image: ${IMAGE}"

echo "1. Checking runtime user..."
USER_ID="$(docker run --rm "${IMAGE}" id -u)"

if [[ "${USER_ID}" == "0" ]]; then
  echo "Runtime image is running as root." >&2
  exit 1
fi

echo "Runtime user is non-root: UID ${USER_ID}"

echo "2. Checking compiled ROS workspace..."
docker run --rm "${IMAGE}" \
  test -f /opt/robot/setup.bash

echo "3. Checking ROS 2..."
docker run --rm "${IMAGE}" \
  ros2 --help >/dev/null

echo "4. Checking required robot packages..."

REQUIRED_PACKAGES=(
  mock_robot_behavior
  mock_robot_bringup
  mock_robot_control
  mock_robot_description
  mock_robot_gazebo
  mock_robot_interfaces
)

PACKAGE_LIST="$(docker run --rm "${IMAGE}" ros2 pkg list)"

for package in "${REQUIRED_PACKAGES[@]}"; do
  if ! grep -qx "${package}" <<< "${PACKAGE_LIST}"; then
    echo "Missing ROS package: ${package}" >&2
    exit 1
  fi

  echo "Found: ${package}"
done

echo "Runtime image validation passed."