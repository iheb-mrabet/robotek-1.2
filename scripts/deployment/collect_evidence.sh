#!/usr/bin/env bash

set -euo pipefail

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output_directory="reports/deployment/${timestamp}"

mkdir -p "$output_directory"

kubectl -n argocd get application "$application" \
  -o jsonpath='Application: {.metadata.name}{"\n"}Sync: {.status.sync.status}{"\n"}Health: {.status.health.status}{"\n"}Revision: {.status.sync.revision}{"\n"}' \
  > "$output_directory/argocd-status.txt"

kubectl -n "$namespace" get deployment,pods \
  > "$output_directory/kubernetes-resources.txt"

pod="$(
  kubectl -n "$namespace" get pods \
    -l app.kubernetes.io/instance="$application" \
    -o jsonpath='{.items[0].metadata.name}'
)"

kubectl -n "$namespace" get pod "$pod" \
  -o jsonpath='Pod: {.metadata.name}{"\n"}Image: {.spec.containers[0].image}{"\n"}Image ID: {.status.containerStatuses[0].imageID}{"\n"}Ready: {.status.containerStatuses[0].ready}{"\n"}Started: {.status.containerStatuses[0].started}{"\n"}Restarts: {.status.containerStatuses[0].restartCount}{"\n"}' \
  > "$output_directory/pod-status.txt"

kubectl -n "$namespace" logs "$pod" \
  --tail=300 \
  > "$output_directory/robotek.log"

kubectl -n "$namespace" top pod "$pod" \
  > "$output_directory/resources.txt" 2>&1 || true

kubectl -n "$namespace" get events \
  --sort-by=.metadata.creationTimestamp \
  > "$output_directory/events.txt"

helm list --namespace "$namespace" \
  > "$output_directory/helm-list.txt"

(
  cd "$output_directory"
  sha256sum ./* > checksums.sha256
)

echo "Evidence collected in: $output_directory"
