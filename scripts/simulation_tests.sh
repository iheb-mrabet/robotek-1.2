#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/build.sh"

# shellcheck source=/dev/null
source "${ROOT_DIR}/install/setup.bash"

cd "${ROOT_DIR}"
echo "Running headless Gazebo simulation tests..."
mkdir -p reports/simulation
# Each scenario owns a fresh DDS domain and Gazebo transport partition.
# Launch shutdown may leave Gazebo descendants alive briefly; they must never
# provide sensor data or consume commands for the next robot world.
export ROBOTEK_SIMULATION_PARTITION
ROBOTEK_SIMULATION_PARTITION="robotek-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
timeout 180s bash -c '
  status=0
  scenario=0
  for test_file in "$@"; do
    scenario=$((scenario + 1))
    test_name="$(basename "$test_file" .py)"
    echo "Simulation scenario: $test_name (isolated domain/partition)"
    if ROS_DOMAIN_ID=$((70 + scenario)) \\
      GZ_PARTITION="${ROBOTEK_SIMULATION_PARTITION}-${scenario}" \\
      python3 -m pytest \\
        -c src/mock_robot_system_tests/pytest.ini \\
        "$test_file" \\
        --junitxml="reports/simulation/${test_name}.xml"; then
      :
    else
      status=1
    fi
  done
  exit "$status"
' simulation-tier \\
  src/mock_robot_system_tests/test/test_basic_movement.py \\
  src/mock_robot_system_tests/test/test_delivery_mission.py \\
  src/mock_robot_system_tests/test/test_simulation_topics.py
