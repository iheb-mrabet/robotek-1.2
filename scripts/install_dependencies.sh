#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SUDO=""
if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
fi

if command -v apt-get >/dev/null 2>&1; then
  echo "Installing ROS build, test, and lint tools..."
  ${SUDO} apt-get update
  ${SUDO} apt-get install -y \
    clang-format \
    cppcheck \
    gcovr \
    lcov \
    python3-colcon-common-extensions \
    python3-pip \
    python3-pytest \
    python3-rosdep \
    python3-venv \
    shellcheck
fi

VENV_DIR="${ROOT_DIR}/.venv"
python3 -m venv --system-site-packages "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install \
  pytest-cov==7.1.0 \
  PyYAML==6.0.3 \
  ruff==0.15.21 \
  semgrep==1.169.0

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
else
  echo "ROS 2 Jazzy is not installed at /opt/ros/jazzy." >&2
  exit 1
fi

if ! command -v rosdep >/dev/null 2>&1; then
  echo "rosdep is required. Install python3-rosdep first." >&2
  exit 1
fi

if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  echo "Initializing rosdep..."
  ${SUDO} rosdep init || true
fi

echo "Updating rosdep database..."
rosdep update

echo "Installing ROS package dependencies..."
rosdep install --from-paths "${ROOT_DIR}/src" --ignore-src --rosdistro jazzy -r -y
