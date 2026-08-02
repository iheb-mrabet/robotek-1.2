#!/usr/bin/env bash

set -Eeuo pipefail

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"
deployment="${3:-robotek-staging}"
expected_digest="${EXPECTED_DIGEST:-${4:-}}"

sync_status="$(
  kubectl -n argocd get application "$application" \
    -o jsonpath='{.status.sync.status}'
)"

health_status="$(
  kubectl -n argocd get application "$application" \
    -o jsonpath='{.status.health.status}'
)"

if [[ "$sync_status" != "Synced" ]]; then
  echo "Argo CD application is not Synced: $sync_status" >&2
  exit 1
fi

if [[ "$health_status" != "Healthy" ]]; then
  echo "Argo CD application is not Healthy: $health_status" >&2
  exit 1
fi

kubectl -n "$namespace" rollout status \
  deployment/"$deployment" \
  --timeout=600s

pod="$(
  kubectl -n "$namespace" get pods \
    -l app.kubernetes.io/instance="$application" \
    --field-selector=status.phase=Running \
    -o jsonpath='{.items[0].metadata.name}'
)"

if [[ -z "$pod" ]]; then
  echo "No running Robotek Pod found." >&2
  exit 1
fi

pod_json="$(
  kubectl -n "$namespace" get pod "$pod" -o json
)"

not_ready="$(
  jq -r '
    [
      .status.containerStatuses[]?
      | select(.ready != true)
      | .name
    ]
    | join(",")
  ' <<<"$pod_json"
)"

if [[ -n "$not_ready" ]]; then
  echo "Containers are not Ready: $not_ready" >&2
  exit 1
fi

mapfile -t images < <(
  jq -r '.spec.containers[].image' <<<"$pod_json"
)

if [[ "${#images[@]}" -eq 0 ]]; then
  echo "No container images found in Pod." >&2
  exit 1
fi

for image in "${images[@]}"; do
  if [[ "$image" != *@sha256:* ]]; then
    echo "Container image is not digest-pinned: $image" >&2
    exit 1
  fi
done

if [[ -n "$expected_digest" ]]; then
  if [[ ! "$expected_digest" =~ ^sha256:[a-f0-9]{64}$ ]]; then
    echo "Invalid expected digest: $expected_digest" >&2
    exit 1
  fi

  for image in "${images[@]}"; do
    if [[ "$image" != *@"$expected_digest" ]]; then
      echo "Unexpected live image: $image" >&2
      echo "Expected digest: $expected_digest" >&2
      exit 1
    fi
  done
fi

ready_summary="$(
  jq -r '
    [
      .status.containerStatuses[]?
      | "\(.name)=\(.ready)"
    ]
    | join(", ")
  ' <<<"$pod_json"
)"

restart_summary="$(
  jq -r '
    [
      .status.containerStatuses[]?
      | "\(.name)=\(.restartCount)"
    ]
    | join(", ")
  ' <<<"$pod_json"
)"

echo "Argo CD sync: $sync_status"
echo "Argo CD health: $health_status"
echo "Pod: $pod"
echo "Containers Ready: $ready_summary"
echo "Container restarts: $restart_summary"

printf 'Images:\n'
printf '  %s\n' "${images[@]}"

echo "Release verification passed."