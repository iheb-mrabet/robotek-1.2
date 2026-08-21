#!/usr/bin/env bash
# The single-quoted commands below are intentionally expanded inside the Pod.
# shellcheck disable=SC2016

set -Eeuo pipefail

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"
container="${3:-robotek}"

pod="$(
  kubectl -n "$namespace" get pods \
    -l app.kubernetes.io/instance="$application" \
    -o json |
    jq -r --arg container "$container" '
      [
        .items[]
        | select(.status.phase == "Running")
        | select(
            any(.spec.containers[]?; .name == $container)
          )
        | select(
            all(.status.containerStatuses[]?; .ready == true)
          )
      ]
      | sort_by(.metadata.creationTimestamp)
      | last
      | .metadata.name // empty
    '
)"

if [[ -z "$pod" ]]; then
  echo \
    "No Ready Robotek Pod with container '$container' found." \
    >&2
  exit 1
fi

echo "Testing Pod: $pod"
echo "Testing container: $container"

expected_topics=(
  /clock
  /cmd_vel
  /mission/status
  /odom
  /scan
  /tf
)

topics=""
topics_valid=false

for attempt in 1 2 3 4 5; do
  topics="$(
    kubectl -n "$namespace" exec \
      -c "$container" \
      "$pod" \
      -- bash -lc '
        source /opt/ros/${ROS_DISTRO}/setup.bash
        source /opt/robot/setup.bash
        ros2 daemon stop >/dev/null 2>&1 || true
        sleep 2
        ros2 topic list
      ' 2>/dev/null || true
  )"

  topics_valid=true

  for expected_topic in "${expected_topics[@]}"; do
    if ! grep -Fxq "$expected_topic" <<<"$topics"; then
      topics_valid=false
      break
    fi
  done

  if [[ "$topics_valid" == true ]]; then
    break
  fi

  echo "Topic discovery attempt $attempt did not find every expected topic."
  sleep 3
done

if [[ "$topics_valid" != true ]]; then
  echo "Missing expected ROS 2 topics." >&2
  printf '%s\n' "$topics"
  exit 1
fi

echo "Expected ROS 2 topics found."

kubectl -n "$namespace" exec \
  -c "$container" \
  "$pod" \
  -- bash -lc '
    source /opt/ros/${ROS_DISTRO}/setup.bash
    source /opt/robot/setup.bash

    for attempt in 1 2 3; do
      timeout 20 ros2 topic echo \
        /mission/status \
        mock_robot_interfaces/msg/MissionStatus \
        --once \
        --no-daemon \
        >/dev/null 2>&1 && exit 0

      sleep 3
    done

    exit 1
  '

echo "Mission status is publishing."

kubectl -n "$namespace" exec \
  -c "$container" \
  "$pod" \
  -- bash -lc '
    source /opt/ros/${ROS_DISTRO}/setup.bash
    source /opt/robot/setup.bash

    for attempt in 1 2 3; do
      timeout 20 ros2 topic echo \
        /odom \
        nav_msgs/msg/Odometry \
        --once \
        --no-daemon \
        --qos-reliability best_effort \
        >/dev/null 2>&1 && exit 0

      sleep 3
    done

    exit 1
  '

echo "Odometry is publishing."
echo "Robotek smoke test passed."
