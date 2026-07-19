#!/usr/bin/env bash
set -eo pipefail

# ROS setup scripts may reference variables that are initially undefined.
set +u

# shellcheck source=/dev/null
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# shellcheck source=/dev/null
source "/opt/robot/setup.bash"

set -u

exec "$@"