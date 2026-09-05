#!/usr/bin/env bash
set -Eeuo pipefail

: "${ROBOTEC_HOST:?Set ROBOTEC_HOST to the new Terraform public_ip.}"
ROBOTEC_SSH_USER="${ROBOTEC_SSH_USER:-ubuntu}"
ROBOTEC_SSH_KEY="${ROBOTEC_SSH_KEY:-}"

ssh_args=(-o BatchMode=yes)
if ssh -G -o StrictHostKeyChecking=accept-new localhost >/dev/null 2>&1; then
  ssh_args+=(-o StrictHostKeyChecking=accept-new)
else
  ssh_args+=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)
fi
[[ -n "${ROBOTEC_SSH_KEY}" ]] && ssh_args+=(-i "${ROBOTEC_SSH_KEY}")
ssh "${ssh_args[@]}" "${ROBOTEC_SSH_USER}@${ROBOTEC_HOST}" \
  'sudo /usr/local/sbin/robotek-verify-platform'
