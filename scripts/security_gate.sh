#!/usr/bin/env bash
set -eo pipefail

jobs=(
  SECRET_SCAN_RESULT
  SAST_RESULT
  TRIVY_FS_RESULT
  TRIVY_IMAGE_RESULT
  POLICY_RESULT
)

for variable in "${jobs[@]}"; do
  result="${!variable:-missing}"
  if [[ "${result}" != "success" ]]; then
    echo "Security gate failed: ${variable}=${result}" >&2
    exit 1
  fi
done

echo "Aggregated security gate passed."
