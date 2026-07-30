#!/usr/bin/env bash

set -Eeuo pipefail

namespace="${1:-robotek-staging}"
application="${2:-robotek-staging}"

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

echo "Testing Pod: $pod"

expected_nodes=(
  /mission_manager
  /robot_state_publisher
  /ros_gz_bridge
  /safety_controller
  /waypoint_controller
)

nodes=""
nodes_valid=false

for attempt in 1 2 3 4 5; do
  nodes="$(
    kubectl -n "$namespace" exec "$pod" -- bash -lc '
      source /opt/ros/${ROS_DISTRO}/setup.bash
      source /opt/robot/setup.bash
      ros2 node list --no-daemon --spin-time 5
    ' 2>/dev/null || true
  )"

  nodes_valid=true

  for expected_node in "${expected_nodes[@]}"; do
    if ! grep -Fxq "$expected_node" <<<"$nodes"; then
      nodes_valid=false
      break
    fi
  done

  [[ "$nodes_valid" == true ]] && break
  sleep 3
done

if [[ "$nodes_valid" != true ]]; then
  echo "Missing expected ROS 2 nodes." >&2
  printf '%s\n' "$nodes"
  exit 1
fi

echo "Expected ROS 2 nodes found."

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
    kubectl -n "$namespace" exec "$pod" -- bash -lc '
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

  [[ "$topics_valid" == true ]] && break
  sleep 3
done

if [[ "$topics_valid" != true ]]; then
  echo "Missing expected ROS 2 topics." >&2
  printf '%s\n' "$topics"
  exit 1
fi

echo "Expected ROS 2 topics found."

kubectl -n "$namespace" exec "$pod" -- bash -lc '
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

kubectl -n "$namespace" exec "$pod" -- bash -lc '
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
