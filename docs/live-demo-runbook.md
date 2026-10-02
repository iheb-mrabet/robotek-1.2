# Robotek demonstration runbook

The full presenter deliverable provides a one-hour preparation checklist and a detailed twenty-minute script. This repository runbook contains the commands needed for rehearsal.

## Entry points

- Public dashboard: https://18-211-80-86.nip.io/
- Repository: https://github.com/iheb-mrabet/robotek-1.2
- Robotek instance: `i-0e137aba90ebc359d`, `us-east-1`.
- Run commands in the Ubuntu Robotek EC2 terminal, reached through EC2 Instance Connect or existing authorized SSH access.

Start the Learner Lab early. Keep it running for the entire meeting. Administrative dashboards remain private; the public operations dashboard and terminal evidence are enough for the core demonstration.

## One hour before the meeting

1. Start the lab, connect to Robotek, and verify node, pods, services, applications, runner, and public readiness.
2. Open the public dashboard, the repository, successful release evidence, successful staging acceptance, and two EC2 terminal windows.
3. Define the helper below in both terminal windows.
4. Rehearse a delivery to `(0.8, 0.0)` and a return to `(0.0, 0.0)`. Use only a reachable coordinate verified in that same session.
5. Rehearse emergency stop and release in separate terminals. Restore the safe baseline.
6. If presenting Falco detection, rehearse a controlled disposable pod and confirm its event before the meeting.
7. At five minutes before the start, refresh the dashboard and check readiness again. Stop editing, deploying, or rebuilding during the presentation.

## ROS terminal helper

Select a Ready runtime pod rather than assuming a pod name survives deployment:

```bash
ROBOT_POD=$(sudo -n k3s kubectl -n robotek-staging get pods \
  -l app.kubernetes.io/instance=robotek-staging -o json |
  python3 -c 'import json,sys; p=json.load(sys.stdin); a=[x for x in p["items"] if x["status"].get("phase")=="Running" and any(c.get("type")=="Ready" and c.get("status")=="True" for c in x["status"].get("conditions",[]))]; a.sort(key=lambda x:x["metadata"]["creationTimestamp"]); print(a[-1]["metadata"]["name"] if a else "")')
test -n "$ROBOT_POD" && printf 'Runtime pod %s\n' "$ROBOT_POD"

rr() {
  sudo -n k3s kubectl -n robotek-staging exec -c robotek "$ROBOT_POD" \
    -- bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash; source /opt/robot/setup.bash; exec "$@"' robotek-shell "$@"
}
```

If a rollout replaces the pod, select it again and redefine the helper in each terminal.

## Show ROS state

```bash
rr ros2 node list
rr ros2 topic list
rr timeout 12 ros2 topic echo /mission/status \
  mock_robot_interfaces/msg/MissionStatus --once --no-daemon
rr timeout 12 ros2 topic echo /odom nav_msgs/msg/Odometry \
  --once --no-daemon --qos-reliability best_effort
```

## Show a completed delivery

```bash
rr timeout 45 ros2 action send_goal /execute_delivery \
  mock_robot_interfaces/action/ExecuteDelivery \
  '{target_x: 0.8, target_y: 0.0}' --feedback
```

Show goal acceptance, progress feedback, and a final `SUCCEEDED` result with `success: true` and `COMPLETED`. Return to origin during rehearsal so the meeting starts from a known position:

```bash
rr timeout 45 ros2 action send_goal /execute_delivery \
  mock_robot_interfaces/action/ExecuteDelivery \
  '{target_x: 0.0, target_y: 0.0}' --feedback
```

## Show emergency stop and recovery

Start a new rehearsed delivery in terminal A. While it is navigating, run in terminal B:

```bash
rr timeout 10 ros2 service call /mission/emergency_stop \
  mock_robot_interfaces/srv/EmergencyStop '{activate: true}'
rr timeout 12 ros2 topic echo /mission/status \
  mock_robot_interfaces/msg/MissionStatus --once --no-daemon
```

Inspect the interrupted action result. Release before leaving the segment:

```bash
rr timeout 10 ros2 service call /mission/emergency_stop \
  mock_robot_interfaces/srv/EmergencyStop '{activate: false}'
```

Release permits a new goal; it does not resume the old one. Do not use Ctrl+C on the action client as a substitute for emergency stop.

## Twenty minute route

| Time | Demonstration |
|---|---|
| 00:00 to 02:00 | Public dashboard and robotics DevSecOps objective |
| 02:00 to 04:00 | Repository, architecture, and AWS deployment |
| 04:00 to 07:00 | ROS graph, mission feedback, and completed delivery |
| 07:00 to 09:00 | Emergency stop and safe recovery |
| 09:00 to 12:00 | CI, simulation, security, and release evidence |
| 12:00 to 14:00 | Immutable digest, signature, SBOM, and provenance |
| 14:00 to 16:00 | GitOps desired state, live rollout, and acceptance |
| 16:00 to 18:00 | Live monitoring and controlled Falco evidence |
| 18:00 to 20:00 | Reboot recovery, operating conditions, and closing |

Use completed workflow evidence during the meeting. A full release may take longer than twenty minutes. Do not trigger a build merely to fill the slot.

## Finish safely

Release emergency stop, complete or stop any test mission deliberately, remove only the disposable demonstration pod, and close any local tunnels. Leave Robotek workloads and services running. Never display tokens, passwords, Secrets, or kubeconfig contents in a recording.
