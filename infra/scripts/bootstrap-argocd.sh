#!/usr/bin/env bash
set -Eeuo pipefail

source /etc/robotek/bootstrap.env
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
helm repo add argo https://argoproj.github.io/argo-helm --force-update
helm repo update argo
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --version "${ARGOCD_CHART_VERSION}" \
  --set server.service.type=ClusterIP \
  --set configs.params.server\.insecure=false \
  --wait --timeout 10m

install -d -m 0755 /opt/robotek
if [[ ! -d /opt/robotek/repository/.git ]]; then
  git clone --branch "${ROBOTEK_REPOSITORY_REVISION}" --single-branch \
    "${ROBOTEK_REPOSITORY_URL}" /opt/robotek/repository
else
  git -C /opt/robotek/repository fetch origin "${ROBOTEK_REPOSITORY_REVISION}"
  git -C /opt/robotek/repository checkout "${ROBOTEK_REPOSITORY_REVISION}"
  git -C /opt/robotek/repository pull --ff-only origin "${ROBOTEK_REPOSITORY_REVISION}"
fi

# Create namespaces and runtime secrets before Argo CD starts dependent Pods.
kubectl create namespace robotek-demo --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

if ! kubectl -n robotek-demo get secret robotek-demo-database >/dev/null 2>&1; then
  db_password="$(openssl rand -base64 36 | tr -d '\n')"
  kubectl -n robotek-demo create secret generic robotek-demo-database \
    --from-literal=POSTGRES_DB=robotek \
    --from-literal=POSTGRES_USER=robotek \
    --from-literal=POSTGRES_PASSWORD="${db_password}" \
    --from-literal=DATABASE_URL="postgresql://robotek:${db_password}@robotek-demo-database:5432/robotek"
  unset db_password
fi

if ! kubectl -n monitoring get secret robotek-grafana-admin >/dev/null 2>&1; then
  grafana_password="$(openssl rand -base64 36 | tr -d '\n')"
  kubectl -n monitoring create secret generic robotek-grafana-admin \
    --from-literal=admin-user=robotek-admin \
    --from-literal=admin-password="${grafana_password}"
  unset grafana_password
fi

kubectl -n argocd wait --for=condition=Established crd/applications.argoproj.io --timeout=120s
for manifest in \
  robotek-staging.yaml \
  robotek-demo.yaml \
  robotek-observability.yaml \
  robotek-runtime-security.yaml
do
  kubectl apply -f "/opt/robotek/repository/deploy/argocd/${manifest}"
done
touch /var/lib/robotek/argocd-complete
