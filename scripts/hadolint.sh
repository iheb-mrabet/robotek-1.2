#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DOCKERFILES=(
  "docker/Dockerfile"
  "docker/Dockerfile.runtime"
)

for dockerfile in "${DOCKERFILES[@]}"; do
  echo "Checking ${dockerfile}..."

  docker run --rm -i \
    ghcr.io/hadolint/hadolint:v2.14.0 \
    hadolint \
    --failure-threshold error \
    - < "${ROOT_DIR}/${dockerfile}"
done

echo "Both Dockerfiles passed the blocking Hadolint checks."
