#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/build.sh"

# shellcheck source=/dev/null
source "${ROOT_DIR}/install/setup.bash"

cd "${ROOT_DIR}"
echo "Running ROS 2 integration tests..."
mkdir -p reports/integration
python3 -m pytest \
  -c src/mock_robot_system_tests/pytest.ini \
  src/mock_robot_system_tests/test \
  -m integration \
  --junitxml=reports/integration/pytest.xml
