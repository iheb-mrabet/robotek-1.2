#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/build.sh"

# shellcheck source=/dev/null
source "${ROOT_DIR}/install/setup.bash"

cd "${ROOT_DIR}"
echo "Running headless Gazebo simulation tests..."
mkdir -p reports/simulation
timeout 180s python3 -m pytest \
  -c src/mock_robot_system_tests/pytest.ini \
  src/mock_robot_system_tests/test \
  -m simulation \
  --junitxml=reports/simulation/pytest.xml
