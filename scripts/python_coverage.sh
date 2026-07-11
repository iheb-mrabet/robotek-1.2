#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "${ROOT_DIR}/.venv/bin" ]]; then
  export PATH="${ROOT_DIR}/.venv/bin:${PATH}"
fi
COVERAGE_MIN="${PYTHON_COVERAGE_MIN:-85}"

cd "${ROOT_DIR}"
mkdir -p reports/coverage/html
export PYTHONPATH="${ROOT_DIR}/src/mock_robot_behavior:${PYTHONPATH:-}"

echo "Running mock_robot_behavior coverage with minimum ${COVERAGE_MIN}%..."
python3 -m pytest src/mock_robot_behavior/test \
  --cov=mock_robot_behavior.mission_state_machine \
  --cov=mock_robot_behavior.mission_validation \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml:reports/coverage/python-coverage.xml \
  --cov-report=html:reports/coverage/html \
  --cov-fail-under="${COVERAGE_MIN}"
