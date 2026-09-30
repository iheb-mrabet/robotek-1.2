#!/usr/bin/env bash
set -Eeuo pipefail

: "${ROBOTEC_HOST:?Set ROBOTEC_HOST to the new Terraform public_ip.}"
: "${GITHUB_RUNNER_TOKEN:?Set a fresh one-time runner token.}"
: "${GITHUB_RUNNER_SHA256:?Set the official runner archive SHA-256.}"
ROBOTEC_SSH_USER="${ROBOTEC_SSH_USER:-ubuntu}"
ROBOTEC_SSH_KEY="${ROBOTEC_SSH_KEY:-}"

ssh_args=(-o BatchMode=yes -o StrictHostKeyChecking=accept-new)
[[ -n "${ROBOTEC_SSH_KEY}" ]] && ssh_args+=(-i "${ROBOTEC_SSH_KEY}")

printf '%s\n' "${GITHUB_RUNNER_TOKEN}" | \
  ssh "${ssh_args[@]}" "${ROBOTEC_SSH_USER}@${ROBOTEC_HOST}" \
    "sudo env GITHUB_RUNNER_SHA256=${GITHUB_RUNNER_SHA256} /opt/robotek/repository/infra/scripts/register-runner.sh --token-stdin"
unset GITHUB_RUNNER_TOKEN
