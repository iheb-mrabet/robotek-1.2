#!/usr/bin/env bash

set -euo pipefail

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"
deployment="${3:-robotek-staging}"

sync_status="$(
  kubectl -n argocd get application "$application" \
    -o jsonpath='{.status.sync.status}'
)"

health_status="$(
  kubectl -n argocd get application "$application" \
    -o jsonpath='{.status.health.status}'
)"

kubectl -n "$namespace" rollout status \
  deployment/"$deployment" \
  --timeout=600s >/dev/null

pod="$(
  kubectl -n "$namespace" get pods \
    -l app.kubernetes.io/instance="$application" \
    -o jsonpath='{.items[0].metadata.name}'
)"

image="$(
  kubectl -n "$namespace" get pod "$pod" \
    -o jsonpath='{.spec.containers[0].image}'
)"

ready="$(
  kubectl -n "$namespace" get pod "$pod" \
    -o jsonpath='{.status.containerStatuses[0].ready}'
)"

restarts="$(
  kubectl -n "$namespace" get pod "$pod" \
    -o jsonpath='{.status.containerStatuses[0].restartCount}'
)"

[[ "$sync_status" == "Synced" ]]
[[ "$health_status" == "Healthy" ]]
[[ "$ready" == "true" ]]
[[ "$restarts" == "0" ]]
[[ "$image" == *@sha256:* ]]

echo "Argo CD sync: $sync_status"
echo "Argo CD health: $health_status"
echo "Pod: $pod"
echo "Image: $image"
echo "Ready: $ready"
echo "Restarts: $restarts"
echo "Release verification passed."
