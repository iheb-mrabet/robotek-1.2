#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "Removing generated workspace files..."
rm -rf build install log
rm -rf .pytest_cache .ruff_cache reports
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
find . -type f \( -name ".coverage" -o -name "coverage.xml" -o -name "*.gcda" -o -name "*.gcno" \) -delete
