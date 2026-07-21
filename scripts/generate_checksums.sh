#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="${1:-reports/delivery}"

FILES=(
  metadata.json
  sbom.spdx.json
  sbom.cyclonedx.json
  trivy-runtime.json
  trivy-runtime.txt
)

for file in "${FILES[@]}"; do
  if [[ ! -f "${REPORT_DIR}/${file}" ]]; then
    echo "Missing delivery evidence file: ${REPORT_DIR}/${file}" >&2
    exit 1
  fi
done

(
  cd "${REPORT_DIR}"
  sha256sum "${FILES[@]}" > SHA256SUMS
)

echo "Generated ${REPORT_DIR}/SHA256SUMS"
