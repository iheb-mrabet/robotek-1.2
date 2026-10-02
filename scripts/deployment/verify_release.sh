#!/usr/bin/env bash
set -Eeuo pipefail

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"
deployment="${3:-robotek-staging}"
expected_digest="${EXPECTED_DIGEST:-${4:-}}"

if [[ -n "$expected_digest" && ! "$expected_digest" =~ ^sha256:[a-f0-9]{64}$ ]]; then
  echo "Invalid expected digest." >&2
  exit 1
fi

# Reconciliation and rollout are asynchronous. Read each Argo state atomically,
# wait for a completed operation, and require a Ready current Pod plus a second
# consistent Argo snapshot before accepting the deployed artifact.
deadline=$(( $(date +%s) + 600 ))
while (( $(date +%s) < deadline )); do
  if ! application_json="$(kubectl --request-timeout=15s -n argocd get application "$application" -o json 2>/dev/null)"; then
    sleep 3
    continue
  fi
  state="$(jq -r '[.status.sync.status // "Pending", .status.health.status // "Pending", .status.sync.revision // "Pending", (if .operation != null then "Pending" else (.status.operationState.phase // "None") end)] | @tsv' <<< "$application_json")"
  IFS=$'\t' read -r sync_status health_status revision operation_phase <<< "$state"
  if [[ "$sync_status" != Synced || "$health_status" != Healthy ]] || [[ "$operation_phase" != Succeeded && "$operation_phase" != None ]]; then
    sleep 3
    continue
  fi

  if ! kubectl -n "$namespace" rollout status deployment/"$deployment" --timeout=10s >/dev/null 2>&1; then
    sleep 3
    continue
  fi

  if ! pods_json="$(kubectl --request-timeout=15s -n "$namespace" get pods -l app.kubernetes.io/instance="$application" -o json 2>/dev/null)"; then
    sleep 3
    continue
  fi
  pod_json="$(jq -c --arg expected "$expected_digest" '
    [.items[]
      | select(.metadata.deletionTimestamp == null)
      | select(.status.phase == "Running")
      | select((.status.containerStatuses | length) == (.spec.containers | length))
      | select(all(.status.containerStatuses[]; .ready == true))
      | select((.spec.containers | length) > 0)
      | select(all(.spec.containers[];
          (.image | test("@sha256:[a-f0-9]{64}$")) and
          ($expected == "" or (.image | endswith("@" + $expected)))))
    ] | sort_by(.metadata.creationTimestamp) | last // null
  ' <<< "$pods_json")"
  if [[ "$pod_json" == null ]]; then
    sleep 3
    continue
  fi

  sleep 2
  if ! confirmed_json="$(kubectl --request-timeout=15s -n argocd get application "$application" -o json 2>/dev/null)"; then
    sleep 3
    continue
  fi
  confirmed="$(jq -r '[.status.sync.status // "Pending", .status.health.status // "Pending", .status.sync.revision // "Pending", (if .operation != null then "Pending" else (.status.operationState.phase // "None") end)] | @tsv' <<< "$confirmed_json")"
  if [[ "$confirmed" != "$state" ]]; then
    sleep 3
    continue
  fi

  pod="$(jq -r '.metadata.name' <<< "$pod_json")"
  ready_summary="$(jq -r '[.status.containerStatuses[] | "\(.name)=\(.ready)"] | join(", ")' <<< "$pod_json")"
  restart_summary="$(jq -r '[.status.containerStatuses[] | "\(.name)=\(.restartCount)"] | join(", ")' <<< "$pod_json")"
  echo "Argo CD sync: $sync_status"
  echo "Argo CD health: $health_status"
  echo "Pod: $pod"
  echo "Containers Ready: $ready_summary"
  echo "Container restarts: $restart_summary"
  printf 'Images:\n'
  jq -r '.spec.containers[].image | "  " + .' <<< "$pod_json"
  echo "Release verification passed."
  exit 0
done

echo "Release verification failed: no stable healthy deployment with the expected digest within 600s." >&2
exit 1
