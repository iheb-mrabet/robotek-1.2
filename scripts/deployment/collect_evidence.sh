#!/usr/bin/env bash

set -u

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
evidence_root="${EVIDENCE_ROOT:-reports/deployment}"
output_directory="${evidence_root}/${timestamp}"

mkdir -p "$output_directory"

capture() {
  local output_file="$1"
  shift

  "$@" >"$output_directory/$output_file" 2>&1 || true
}

capture \
  argocd-status.txt \
  kubectl -n argocd get application "$application" \
    -o jsonpath='Application: {.metadata.name}{"\n"}Sync: {.status.sync.status}{"\n"}Health: {.status.health.status}{"\n"}Revision: {.status.sync.revision}{"\n"}'

capture \
  kubernetes-resources.txt \
  kubectl -n "$namespace" get deployment,replicaset,pods -o wide

capture \
  events.txt \
  kubectl -n "$namespace" get events \
    --sort-by=.metadata.creationTimestamp

pod="$(
  kubectl -n "$namespace" get pods \
    -l app.kubernetes.io/instance="$application" \
    --field-selector=status.phase=Running \
    -o jsonpath='{.items[0].metadata.name}' \
    2>/dev/null || true
)"

if [[ -n "$pod" ]]; then
  kubectl -n "$namespace" get pod "$pod" -o json |
    jq '
      {
        pod: .metadata.name,
        namespace: .metadata.namespace,
        node: .spec.nodeName,
        phase: .status.phase,
        containers: [
          .spec.containers[] as $container
          | {
              name: $container.name,
              image: $container.image,
              status: (
                [
                  .status.containerStatuses[]?
                  | select(.name == $container.name)
                  | {
                      ready,
                      started,
                      restartCount,
                      imageID,
                      state,
                      lastState
                    }
                ][0] // null
              )
            }
        ]
      }
    ' >"$output_directory/pod-status.json" 2>&1 || true

  mapfile -t containers < <(
    kubectl -n "$namespace" get pod "$pod" \
      -o jsonpath='{range .spec.containers[*]}{.name}{"\n"}{end}' \
      2>/dev/null || true
  )

  for container in "${containers[@]}"; do
    safe_container="$(
      printf '%s' "$container" |
      tr -c 'A-Za-z0-9._-' '_'
    )"

    capture \
      "logs-${safe_container}.txt" \
      kubectl -n "$namespace" logs "$pod" \
        -c "$container" \
        --tail=300
  done

  capture \
    resources.txt \
    kubectl -n "$namespace" top pod "$pod" --containers
else
  printf '%s\n' \
    "No running Robotek Pod was available during evidence collection." \
    >"$output_directory/pod-status.txt"
fi

capture \
  runner-permissions.txt \
  kubectl auth can-i --list --namespace="$namespace"

checksum_tmp="$(mktemp)"
trap 'rm -f "$checksum_tmp"' EXIT

(
  cd "$output_directory" || exit 1

  find . \
    -maxdepth 1 \
    -type f \
    ! -name checksums.sha256 \
    -print0 |
    sort -z |
    xargs -0 -r sha256sum \
      >"$checksum_tmp"
)

mv "$checksum_tmp" "$output_directory/checksums.sha256"
trap - EXIT

echo "Evidence collected in: $output_directory"