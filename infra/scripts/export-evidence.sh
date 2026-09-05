#!/usr/bin/env bash
set -Eeuo pipefail

command -v terraform >/dev/null 2>&1 || { echo "terraform is required" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }

output_dir="${EVIDENCE_DIR:-rebuild-evidence}"
mkdir -p "${output_dir}"

terraform -chdir=infra/terraform output -json > "${output_dir}/terraform-outputs.json"
jq '{
  generated_at: (now | todateiso8601),
  account_id: .account_id.value,
  region: .region.value,
  instance_id: .instance_id.value,
  public_ip: .public_ip.value,
  private_ip: .private_ip.value
}' "${output_dir}/terraform-outputs.json" > "${output_dir}/rebuild-report.json"

git rev-parse HEAD > "${output_dir}/repository-commit.txt"
echo "Evidence written to ${output_dir}; no secret values were exported."
