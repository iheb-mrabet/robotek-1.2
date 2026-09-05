#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root on the dedicated Robotek K3s host." >&2
  exit 1
fi

: "${GITHUB_RUNNER_SHA256:?Set the official SHA-256 for the pinned runner archive.}"

if [[ "${1:-}" == "--token-stdin" ]]; then
  IFS= read -r GITHUB_RUNNER_TOKEN
fi
: "${GITHUB_RUNNER_TOKEN:?Provide a fresh one-time token through the environment or --token-stdin.}"

GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-iheb-mrabet/robotek-1.2}"
GITHUB_RUNNER_VERSION="${GITHUB_RUNNER_VERSION:-2.328.0}"
RUNNER_LABELS="${RUNNER_LABELS:-robotek-staging,k3s,staging}"
RUNNER_USER="robotek-runner"
RUNNER_HOME="/opt/actions-runner"

id "${RUNNER_USER}" >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash "${RUNNER_USER}"
install -d -o "${RUNNER_USER}" -g "${RUNNER_USER}" -m 0750 "${RUNNER_HOME}"

archive="actions-runner-linux-x64-${GITHUB_RUNNER_VERSION}.tar.gz"
workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"; unset GITHUB_RUNNER_TOKEN' EXIT
curl --fail --show-error --silent --location \
  "https://github.com/actions/runner/releases/download/v${GITHUB_RUNNER_VERSION}/${archive}" \
  --output "${workdir}/${archive}"
echo "${GITHUB_RUNNER_SHA256}  ${workdir}/${archive}" | sha256sum --check
tar -xzf "${workdir}/${archive}" -C "${RUNNER_HOME}"
chown -R "${RUNNER_USER}:${RUNNER_USER}" "${RUNNER_HOME}"

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl create namespace robotek-staging --dry-run=client -o yaml | kubectl apply -f -
kubectl -n robotek-staging create serviceaccount github-actions-staging \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f - <<'YAML'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: github-actions-staging-validation
  namespace: robotek-staging
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "events"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
  - apiGroups: [""]
    resources: ["pods/exec"]
    verbs: ["create"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: github-actions-staging-validation
  namespace: robotek-staging
subjects:
  - kind: ServiceAccount
    name: github-actions-staging
    namespace: robotek-staging
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: github-actions-staging-validation
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: github-actions-argocd-reader
  namespace: argocd
rules:
  - apiGroups: ["argoproj.io"]
    resources: ["applications"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: github-actions-argocd-reader
  namespace: argocd
subjects:
  - kind: ServiceAccount
    name: github-actions-staging
    namespace: robotek-staging
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: github-actions-argocd-reader
YAML

runner_kubeconfig="/home/${RUNNER_USER}/.kube/config"
install -d -o "${RUNNER_USER}" -g "${RUNNER_USER}" -m 0700 "$(dirname "${runner_kubeconfig}")"
runner_token="$(kubectl -n robotek-staging create token github-actions-staging --duration=8760h)"
kubectl --kubeconfig="${runner_kubeconfig}" config set-cluster robotek-k3s \
  --server=https://127.0.0.1:6443 \
  --certificate-authority=/var/lib/rancher/k3s/server/tls/server-ca.crt \
  --embed-certs=true
kubectl --kubeconfig="${runner_kubeconfig}" config set-credentials github-actions-staging \
  --token="${runner_token}"
kubectl --kubeconfig="${runner_kubeconfig}" config set-context robotek-staging \
  --cluster=robotek-k3s --user=github-actions-staging --namespace=robotek-staging
kubectl --kubeconfig="${runner_kubeconfig}" config use-context robotek-staging
chown -R "${RUNNER_USER}:${RUNNER_USER}" "/home/${RUNNER_USER}/.kube"
chmod 0600 "${runner_kubeconfig}"
unset runner_token

if [[ ! -f "${RUNNER_HOME}/.runner" ]]; then
  sudo -u "${RUNNER_USER}" "${RUNNER_HOME}/config.sh" \
    --url "https://github.com/${GITHUB_REPOSITORY}" \
    --token "${GITHUB_RUNNER_TOKEN}" \
    --name "$(hostname)-robotek" \
    --labels "${RUNNER_LABELS}" \
    --work _work \
    --unattended
fi

"${RUNNER_HOME}/svc.sh" install "${RUNNER_USER}"
"${RUNNER_HOME}/svc.sh" start
unset GITHUB_RUNNER_TOKEN
