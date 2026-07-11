#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "${ROOT_DIR}/.venv/bin" ]]; then
  export PATH="${ROOT_DIR}/.venv/bin:${PATH}"
fi
cd "${ROOT_DIR}"

if ! command -v semgrep >/dev/null 2>&1; then
  echo "Missing required security tool: semgrep" >&2
  exit 1
fi
if ! command -v cppcheck >/dev/null 2>&1; then
  echo "Missing required security tool: cppcheck" >&2
  exit 1
fi

echo "Running deterministic Semgrep rules for Python..."
semgrep scan \
  --config security/semgrep.yml \
  --error \
  --metrics=off \
  --disable-version-check \
  --exclude='build/**' \
  --exclude='install/**' \
  --exclude='log/**' \
  src/mock_robot_behavior src/mock_robot_system_tests

echo "Running cppcheck security-focused C++ analysis..."
cppcheck \
  --enable=warning,style,performance,portability \
  --error-exitcode=1 \
  --inline-suppr \
  --std=c++17 \
  -Isrc/mock_robot_control/include \
  src/mock_robot_control/src \
  src/mock_robot_control/test
