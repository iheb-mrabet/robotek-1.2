#!/usr/bin/env bash
set -Eeuo pipefail

source /etc/robotek/bootstrap.env
install -d -m 0700 /var/lib/robotek

if ! command -v k3s >/dev/null 2>&1; then
  curl --fail --show-error --silent --location https://get.k3s.io \
    | INSTALL_K3S_VERSION="${K3S_VERSION}" sh -s - server \
      --disable traefik \
      --disable servicelb \
      --secrets-encryption \
      --write-kubeconfig-mode 0640
fi

systemctl enable --now k3s
for _ in $(seq 1 90); do
  k3s kubectl get node >/dev/null 2>&1 && break
  sleep 2
done
k3s kubectl wait --for=condition=Ready node --all --timeout=180s

install -d -m 0750 /root/.kube
install -m 0600 /etc/rancher/k3s/k3s.yaml /root/.kube/config
ln -sf /usr/local/bin/k3s /usr/local/bin/kubectl

if ! command -v helm >/dev/null 2>&1 || [[ "$(helm version --template '{{.Version}}' 2>/dev/null || true)" != "${HELM_VERSION}" ]]; then
  archive="helm-${HELM_VERSION}-linux-amd64.tar.gz"
  workdir="$(mktemp -d)"
  trap 'rm -rf "${workdir}"' EXIT
  curl --fail --show-error --silent --location "https://get.helm.sh/${archive}" --output "${workdir}/${archive}"
  curl --fail --show-error --silent --location "https://get.helm.sh/${archive}.sha256sum" --output "${workdir}/${archive}.sha256sum"
  (cd "${workdir}" && sha256sum --check "${archive}.sha256sum")
  tar -xzf "${workdir}/${archive}" -C "${workdir}"
  install -m 0755 "${workdir}/linux-amd64/helm" /usr/local/bin/helm
fi

KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl get nodes -o wide
touch /var/lib/robotek/k3s-complete
