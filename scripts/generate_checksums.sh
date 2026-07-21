#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="${1:-reports/delivery}"

FILES=(
  candidate-reference.txt
  image-reference.txt
  published-tags.txt
  metadata.json
  sbom.spdx.json
  sbom.cyclonedx.json
  sbom.attestation.cyclonedx.json
  sbom-attestation-info.json
  trivy-runtime.json
  trivy-runtime.txt
  attestations.json
  provenance.attestation.json
  sbom.attestation.json
  cosign-verification.json
  cosign-identity.txt
  github-provenance-verification.json
  github-sbom-verification.json
)

for file in "${FILES[@]}"; do
  if [[ ! -s "${REPORT_DIR}/${file}" ]]; then
    echo "Missing or empty delivery evidence file: ${REPORT_DIR}/${file}" >&2
    exit 1
  fi
done

(
  cd "${REPORT_DIR}"

  sha256sum \
    "${FILES[@]}" \
    > SHA256SUMS
)

echo "Generated ${REPORT_DIR}/SHA256SUMS"