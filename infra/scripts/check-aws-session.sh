#!/usr/bin/env bash
set -Eeuo pipefail

for command in aws jq; do
  command -v "${command}" >/dev/null 2>&1 || {
    echo "Required command not found: ${command}" >&2
    exit 1
  }
done

region="${AWS_REGION:-${AWS_DEFAULT_REGION:-}}"
if [[ -z "${region}" ]]; then
  echo "Set AWS_REGION to the Academy region before continuing." >&2
  exit 1
fi

identity="$(aws sts get-caller-identity --output json)"
account_id="$(jq -r '.Account' <<<"${identity}")"
arn="$(jq -r '.Arn' <<<"${identity}")"

if [[ -n "${EXPECTED_AWS_ACCOUNT_ID:-}" && "${account_id}" != "${EXPECTED_AWS_ACCOUNT_ID}" ]]; then
  echo "AWS account mismatch: expected ${EXPECTED_AWS_ACCOUNT_ID}, received ${account_id}." >&2
  exit 1
fi

printf 'AWS session verified\nAccount: %s\nRegion: %s\nPrincipal: %s\n' \
  "${account_id}" "${region}" "${arn}"
