#!/usr/bin/env bash
set -Eeuo pipefail

export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"
failed=0

check() {
  local label="$1"
  shift
  if "$@"; then
    printf 'PASS  %s\n' "${label}"
  else
    printf 'FAIL  %s\n' "${label}" >&2
    failed=1
  fi
}

check "K3s node Ready" kubectl wait --for=condition=Ready node --all --timeout=30s
check "Argo CD server available" kubectl -n argocd rollout status deployment/argocd-server --timeout=60s

application_healthy() {
  local app="$1"
  local sync health
  sync="$(kubectl -n argocd get application "${app}" -o jsonpath='{.status.sync.status}')"
  health="$(kubectl -n argocd get application "${app}" -o jsonpath='{.status.health.status}')"
  [[ "${sync}" == "Synced" && "${health}" == "Healthy" ]]
}

for app in robotek-staging robotek-demo robotek-observability robotek-runtime-security; do
  check "Argo CD application ${app} Synced/Healthy" application_healthy "${app}"
done

for namespace in robotek-staging robotek-demo monitoring runtime-security; do
  check "Namespace ${namespace} exists" kubectl get namespace "${namespace}"
done

kubectl -n argocd get applications \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status,REVISION:.status.sync.revision
kubectl get pods -A -o wide

if [[ "${failed}" -ne 0 ]]; then
  echo "Platform verification is incomplete. Missing evidence remains UNAVAILABLE." >&2
  exit 1
fi

echo "Base platform and Argo CD application checks passed. Endpoint-level proof is still required."
