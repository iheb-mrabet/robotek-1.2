#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root on the dedicated Robotek K3s host." >&2
  exit 1
fi

mode="${1:---token-stdin}"
if [[ "${mode}" == "--token-stdin" ]]; then
  IFS= read -r GITHUB_RUNNER_TOKEN
elif [[ "${mode}" != "--refresh-kubeconfig" ]]; then
  echo "Usage: register-runner.sh --token-stdin | --refresh-kubeconfig" >&2
  exit 2
fi

GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-iheb-mrabet/robotek-1.2}"
GITHUB_RUNNER_VERSION="${GITHUB_RUNNER_VERSION:-2.337.0}"
RUNNER_LABELS="${RUNNER_LABELS:-robotek-staging,k3s,staging}"
RUNNER_USER="robotek-runner"
RUNNER_HOME="/opt/actions-runner"
if [[ "${mode}" == "--refresh-kubeconfig" && ! -f "${RUNNER_HOME}/.runner" ]]; then
  echo "Runner is not registered; use --token-stdin first." >&2
  exit 1
fi
if [[ "${mode}" == "--token-stdin" ]]; then
  : "${GITHUB_RUNNER_TOKEN:?Provide a fresh one-time token on stdin.}"
fi

id "${RUNNER_USER}" >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash "${RUNNER_USER}"
install -d -o "${RUNNER_USER}" -g "${RUNNER_USER}" -m 0750 "${RUNNER_HOME}"

archive="actions-runner-linux-x64-${GITHUB_RUNNER_VERSION}.tar.gz"
if [[ ! -f "${RUNNER_HOME}/.runner" ]]; then
  : "${GITHUB_RUNNER_SHA256:?Set the official SHA-256 for the pinned runner archive.}"
  workdir="$(mktemp -d)"
  trap 'rm -rf "${workdir}"; unset GITHUB_RUNNER_TOKEN' EXIT
  curl --fail --show-error --silent --location \
    "https://github.com/actions/runner/releases/download/v${GITHUB_RUNNER_VERSION}/${archive}" \
    --output "${workdir}/${archive}"
  echo "${GITHUB_RUNNER_SHA256}  ${workdir}/${archive}" | sha256sum --check
  tar -xzf "${workdir}/${archive}" -C "${RUNNER_HOME}"
  chown -R "${RUNNER_USER}:${RUNNER_USER}" "${RUNNER_HOME}"
fi

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
  name: github-actions-demo-validation
  namespace: robotek-demo
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "events"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: github-actions-demo-validation
  namespace: robotek-demo
subjects:
  - kind: ServiceAccount
    name: github-actions-staging
    namespace: robotek-staging
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: github-actions-demo-validation
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

# Keep short-lived validation credentials renewed without granting cluster-admin.
install -d -o root -g root -m 0755 /usr/local/sbin
cat > /usr/local/sbin/robotek-refresh-runner-kubeconfig <<'REFRESH'
#!/usr/bin/env bash
set -Eeuo pipefail
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
runner_user=robotek-runner
config_dir=/home/robotek-runner/.kube
install -d -o "${runner_user}" -g "${runner_user}" -m 0700 "${config_dir}"
umask 077
config_tmp="$(mktemp "${config_dir}/config.XXXXXX")"
trap 'rm -f "${config_tmp}"; unset runner_token' EXIT
runner_token="$(kubectl -n robotek-staging create token github-actions-staging --duration=8h)"
kubectl --kubeconfig="${config_tmp}" config set-cluster robotek-k3s \
  --server=https://127.0.0.1:6443 \
  --certificate-authority=/var/lib/rancher/k3s/server/tls/server-ca.crt \
  --embed-certs=true >/dev/null
kubectl --kubeconfig="${config_tmp}" config set-credentials github-actions-staging \
  --token="${runner_token}" >/dev/null
kubectl --kubeconfig="${config_tmp}" config set-context robotek-staging \
  --cluster=robotek-k3s --user=github-actions-staging --namespace=robotek-staging >/dev/null
kubectl --kubeconfig="${config_tmp}" config use-context robotek-staging >/dev/null
chown "${runner_user}:${runner_user}" "${config_tmp}"
chmod 0600 "${config_tmp}"
mv -f "${config_tmp}" "${config_dir}/config"
REFRESH
chown root:root /usr/local/sbin/robotek-refresh-runner-kubeconfig
chmod 0700 /usr/local/sbin/robotek-refresh-runner-kubeconfig
cat > /etc/systemd/system/robotek-runner-kubeconfig.service <<'SERVICE'
[Unit]
Description=Renew Robotek validation runner Kubernetes credentials
Requires=k3s.service
After=k3s.service
StartLimitIntervalSec=0

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/robotek-refresh-runner-kubeconfig
Restart=on-failure
RestartSec=30s
SERVICE
cat > /etc/systemd/system/robotek-runner-kubeconfig.timer <<'TIMER'
[Unit]
Description=Refresh Robotek validation credentials hourly

[Timer]
OnBootSec=1min
OnUnitActiveSec=1h
Unit=robotek-runner-kubeconfig.service

[Install]
WantedBy=timers.target
TIMER
systemctl daemon-reload
systemctl start robotek-runner-kubeconfig.service
systemctl enable --now robotek-runner-kubeconfig.timer

# GitHub's configuration and service scripts resolve files from the runner root.
cd "${RUNNER_HOME}"

if [[ "${mode}" == "--token-stdin" && ! -f "${RUNNER_HOME}/.runner" ]]; then
  sudo -u "${RUNNER_USER}" "${RUNNER_HOME}/config.sh" \
    --url "https://github.com/${GITHUB_REPOSITORY}" \
    --token "${GITHUB_RUNNER_TOKEN}" \
    --name "$(hostname)-robotek" \
    --labels "${RUNNER_LABELS}" \
    --work _work \
    --unattended
fi

if [[ ! -f "${RUNNER_HOME}/.service" ]]; then
  "${RUNNER_HOME}/svc.sh" install "${RUNNER_USER}"
fi
# K3s kubectl defaults to its admin config unless KUBECONFIG is explicit.
runner_service="$(cat "${RUNNER_HOME}/.service")"
[[ "${runner_service}" == actions.runner.*.service && "${runner_service}" != */* ]]
install -d -o root -g root -m 0755 "/etc/systemd/system/${runner_service}.d"
cat > "/etc/systemd/system/${runner_service}.d/robotek-kubeconfig.conf" <<'ENVIRONMENT'
[Service]
Environment=KUBECONFIG=/home/robotek-runner/.kube/config
ENVIRONMENT
systemctl daemon-reload
systemctl restart "${runner_service}"
unset GITHUB_RUNNER_TOKEN
