#!/usr/bin/env bash
set -Eeuo pipefail

command -v terraform >/dev/null 2>&1 || { echo "terraform is required" >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "aws is required" >&2; exit 1; }

current_account="$(aws sts get-caller-identity --query Account --output text)"
: "${EXPECTED_AWS_ACCOUNT_ID:?Set EXPECTED_AWS_ACCOUNT_ID to the verified Academy account.}"
: "${CONFIRM_DESTROY_ACCOUNT:?Set CONFIRM_DESTROY_ACCOUNT to the same account ID.}"

if [[ "${current_account}" != "${EXPECTED_AWS_ACCOUNT_ID}" || "${current_account}" != "${CONFIRM_DESTROY_ACCOUNT}" ]]; then
  echo "Destroy refused: current, expected and confirmation account IDs must match." >&2
  exit 1
fi

terraform -chdir=infra/terraform destroy -var-file="${TFVARS:-terraform.tfvars}"
