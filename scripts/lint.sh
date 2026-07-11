#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "${ROOT_DIR}/.venv/bin" ]]; then
  export PATH="${ROOT_DIR}/.venv/bin:${PATH}"
fi
cd "${ROOT_DIR}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required lint tool: $1" >&2
    exit 1
  fi
}

for tool in python3 clang-format cppcheck shellcheck; do
  require_command "${tool}"
done

if ! python3 -m ruff --version >/dev/null 2>&1; then
  echo "Missing required Python module: ruff" >&2
  exit 1
fi

echo "Running Ruff lint checks..."
python3 -m ruff check src scripts

echo "Checking Python formatting with Ruff..."
python3 -m ruff format --check src scripts

mapfile -d '' CPP_FILES < <(
  find src/mock_robot_control -type f \
    \( -name '*.cpp' -o -name '*.hpp' -o -name '*.cc' -o -name '*.h' \) -print0
)
if (( ${#CPP_FILES[@]} == 0 )); then
  echo "No C++ files found for clang-format." >&2
  exit 1
fi

echo "Checking C++ formatting with clang-format..."
clang-format --dry-run --Werror "${CPP_FILES[@]}"

echo "Running ShellCheck on repository scripts..."
shellcheck scripts/*.sh

echo "Running cppcheck..."
cppcheck \
  --enable=warning,performance,portability \
  --error-exitcode=1 \
  --inline-suppr \
  --std=c++17 \
  -Isrc/mock_robot_control/include \
  src/mock_robot_control/src \
  src/mock_robot_control/test

echo "Lint and static checks completed."
