# Phase 6 Operations Runbook

**Status:** Active  
**Environment:** Robotek staging on single-node K3s  
**Owners:** Repository maintainers and staging operators

---

## 1. Purpose

This runbook describes the normal operating, verification, troubleshooting, evidence, and recovery procedures for the Phase 6 observability and runtime-security platform.

The platform contains:

- Robotek and its ROS 2 Prometheus exporter in `robotek-staging`.
- Argo CD in `argocd`.
- Prometheus, Grafana, Alertmanager, kube-state-metrics, and node-exporter in `monitoring`.
- Falco in `runtime-security`.
- A repository-scoped self-hosted GitHub Actions runner on the staging host.
- Automated post-deployment validation and scheduled Trivy rescanning.

All application and platform workloads are managed through Git and Argo CD. Manual cluster changes are for diagnosis or secret bootstrap only and must not replace Git as the source of truth.

---

## 2. Security and access rules

- Do not expose Grafana, Prometheus, Alertmanager, Argo CD, or K3s APIs publicly.
- Access private services through SSH and `kubectl port-forward`.
- Never commit Telegram bot tokens, kubeconfig files, runner registration tokens, private keys, or generated evidence containing secrets.
- Keep the `robotek-telegram` and `robotek-grafana-admin` Secrets outside Git.
- Do not run untrusted pull-request code on the staging self-hosted runner.
- Do not manually edit Argo CD-managed resources as a permanent fix.
- Use Git revert for rollback.

---

## 3. Namespaces and Argo CD applications

| Namespace | Main contents |
|---|---|
| `argocd` | Argo CD control plane and Applications |
| `robotek-staging` | Robotek runtime, ROS exporter, Service, and ServiceMonitor |
| `monitoring` | Prometheus stack, dashboards, alert rules, and Alertmanager secrets |
| `runtime-security` | Falco DaemonSet and ServiceMonitor |

Expected Applications:

```text
robotek-staging
robotek-observability
robotek-runtime-security
```

Check all applications:

```bash
kubectl -n argocd get applications
```

A healthy platform should show every Application as `Synced` and `Healthy`.

---

## 4. Daily health check

Run from the staging host:

```bash
set -Eeuo pipefail

kubectl get nodes -o wide
kubectl -n argocd get applications
kubectl -n robotek-staging get deployment,pods,svc,servicemonitor
kubectl -n monitoring get pods,pvc,svc
kubectl -n runtime-security get daemonset,pods,servicemonitor
kubectl top node
kubectl top pods -A
```

Expected Robotek state:

```text
Deployment available replicas: 1
Pod readiness: 2/2
Pod phase: Running
Container restarts: 0 during a clean rollout
```

Expected runtime image:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime@sha256:9de522ed93c05f218b63334ccdfb4772060d07102ae9f6f781a409a13b126c28
```

Verify the deployed images:

```bash
kubectl -n robotek-staging get deployment robotek-staging \
  -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{"="}{.image}{"\n"}{end}'
```

---

## 5. Release and ROS validation

Run the repository scripts from a checkout configured with the staging kubeconfig:

```bash
./scripts/deployment/verify_release.sh
./scripts/deployment/smoke_test.sh
./scripts/deployment/collect_evidence.sh
```

The scripts verify:

- Argo CD synchronization and health.
- The immutable image digest.
- Deployment and container readiness.
- ROS topic discovery.
- `/mission/status` publication using `mock_robot_interfaces/msg/MissionStatus`.
- `/odom` publication using `nav_msgs/msg/Odometry` and best-effort QoS.
- Deployment logs, events, resource usage, and evidence checksums.

The runtime and exporter containers use read-only root filesystems. Writable runtime data is limited to dedicated `emptyDir` mounts for `/tmp` and `/home/robot`; the main runtime also uses an in-memory `/dev/shm` volume.

Check the live hardening state:

```bash
pod="$(kubectl -n robotek-staging get pods \
  -l app.kubernetes.io/instance=robotek-staging \
  -o jsonpath='{.items[0].metadata.name}')"

kubectl -n robotek-staging get pod "$pod" \
  -o jsonpath='{range .spec.containers[*]}{.name}{" readOnlyRoot="}{.securityContext.readOnlyRootFilesystem}{"\n"}{end}'
```

---

## 6. Private dashboard access

List services before forwarding:

```bash
kubectl -n monitoring get services
```

Prometheus:

```bash
kubectl -n monitoring port-forward \
  service/robotek-monitoring-prometheus \
  9090:9090
```

Open `http://127.0.0.1:9090` from the machine running the port forward.

Grafana:

```bash
kubectl -n monitoring port-forward \
  service/robotek-observability-grafana \
  3000:80
```

Open `http://127.0.0.1:3000`.

Retrieve the Git-managed Grafana administrator credentials without printing them into logs or chat transcripts:

```bash
kubectl -n monitoring get secret robotek-grafana-admin \
  -o jsonpath='{.data.admin-user}' | base64 -d
echo

kubectl -n monitoring get secret robotek-grafana-admin \
  -o jsonpath='{.data.admin-password}' | base64 -d
echo
```

Alertmanager:

```bash
kubectl -n monitoring port-forward \
  service/robotek-monitoring-alertmanager \
  9093:9093
```

Open `http://127.0.0.1:9093`.

Provisioned dashboards:

- **Robotek GitOps Overview** — UID `ad7m2rk`.
- **Robotek ROS Health** — UID `robotek-ros-health`.

---

## 7. Prometheus checks

Check target health through the API:

```bash
kubectl -n monitoring port-forward \
  service/robotek-monitoring-prometheus \
  9090:9090
```

Useful PromQL queries:

```promql
up
```

```promql
kube_deployment_status_replicas_available{namespace="robotek-staging",deployment="robotek-staging"}
```

```promql
kube_pod_container_status_restarts_total{namespace="robotek-staging"}
```

```promql
robotek_ros_exporter_up
```

```promql
robotek_ros_topic_publishers{topic=~"/mission/status|/odom|/scan"}
```

```promql
robotek_ros_topic_subscribers{topic=~"/cmd_vel|/emergency_stop"}
```

```promql
argocd_app_info{name=~"robotek-staging|robotek-observability|robotek-runtime-security"}
```

```promql
falco_version_info
```

The ROS exporter intentionally bases operational checks on topic publishers and subscribers. ROS node metadata was not reliable in this environment even though DDS endpoint discovery was working.

---

## 8. Alert inventory

Platform and GitOps alerts:

- `RobotekDeploymentUnavailable`
- `RobotekPodNotReady`
- `RobotekContainerRestarting`
- `RobotekImagePullFailure`
- `RobotekArgoCDOutOfSync`
- `RobotekArgoCDUnhealthy`

ROS alerts:

- `RobotekROSExporterDown`
- `RobotekROSCollectionErrors`
- `RobotekMissionStatusPublisherMissing`
- `RobotekOdomPublisherMissing`
- `RobotekLaserScanPublisherMissing`
- `RobotekVelocitySafetySubscriberMissing`
- `RobotekEmergencyStopSubscriberMissing`

Inspect rule state:

```bash
kubectl -n monitoring get prometheusrules
```

Through Prometheus, use:

```promql
ALERTS{alertstate="firing",service="robotek"}
```

Alertmanager routes Robotek alerts to Telegram. The bot token is read from the manually created `robotek-telegram` Secret and is never stored in Git.

---

## 9. Telegram secret rotation

Create or rotate the token interactively. Do not paste the token into shell history shared with other users.

```bash
read -rsp "Telegram bot token: " TELEGRAM_BOT_TOKEN
echo

kubectl -n monitoring create secret generic robotek-telegram \
  --from-literal=bot-token="$TELEGRAM_BOT_TOKEN" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

unset TELEGRAM_BOT_TOKEN
```

Restart the Alertmanager Pod so it remounts the Secret:

```bash
kubectl -n monitoring delete pod \
  -l app.kubernetes.io/name=alertmanager
```

Then verify Alertmanager returns to Ready and send only a controlled test alert.

---

## 10. Falco runtime security

Check Falco:

```bash
kubectl -n runtime-security get daemonset,pods
kubectl -n runtime-security logs \
  daemonset/robotek-runtime-security-falco \
  --tail=200
```

Expected characteristics:

- Falco `0.44.1`.
- Modern eBPF probe.
- K3s containerd socket at `/host/run/k3s/containerd/containerd.sock`.
- No privileged Falco container.
- Capabilities limited to `BPF`, `PERFMON`, `SYS_RESOURCE`, and `SYS_PTRACE`.
- BPF iterators may be disabled because Falco does not use the host PID namespace; this is expected for the selected least-privileged configuration.

### Controlled detection test

Run only during a maintenance or demonstration window:

```bash
kubectl run falco-terminal-shell-test \
  --image=alpine:3.20 \
  --restart=Never \
  --rm -it \
  -- sh
```

Exit immediately, then inspect Falco logs for a terminal shell detection. Remove any test Pod that remains.

Never generate uncontrolled privilege-escalation, host-write, or destructive test activity on the staging node.

---

## 11. Automated post-deployment validation

Workflow:

```text
.github/workflows/post-deploy-validation.yml
```

Runner labels:

```text
self-hosted
Linux
X64
robotek-staging
k3s
staging
```

Check the runner service on the staging host:

```bash
sudo systemctl status \
  actions.runner.iheb-mrabet-robotek-1.2.robotek-staging-k3s.service
```

The runner Kubernetes identity is intentionally restricted. It can inspect staging Pods, logs, events, Deployments, ReplicaSets, metrics, and Argo CD Applications, and can execute the smoke test inside the Robotek Pod. It cannot read Secrets or delete Deployments.

The workflow:

1. Checks out the exact Git revision.
2. Resolves the expected promoted digest.
3. Waits for a compatible Argo CD desired state.
4. Runs release verification and the ROS smoke test.
5. Collects evidence even when validation fails.
6. Uploads a timestamped artifact.

Manually dispatch this workflow after chart or probe changes that do not modify `values-staging.yaml`.

---

## 12. Scheduled security rescan

Workflow:

```text
.github/workflows/scheduled-staging-security.yml
```

Schedule:

```text
Thursday at 03:37 UTC
```

The workflow:

- Resolves the exact runtime image repository and digest from staging values.
- Scans the promoted runtime image for fixable HIGH and CRITICAL vulnerabilities.
- Lints and renders the staging Helm chart.
- Scans the rendered Kubernetes manifests for HIGH and CRITICAL misconfigurations.
- Records metadata and SHA-256 checksums.
- Uploads all reports for 30 days.
- Fails the final aggregate gate when any required check fails.

The first controlled policy failure identified missing read-only root filesystems. The configuration was corrected without suppressing the rule, and the successful rescan confirmed both image and Kubernetes policies.

---

## 13. Incident runbooks

### 13.1 Robotek Application is not Healthy

```bash
kubectl -n argocd get application robotek-staging -o wide
kubectl -n argocd get application robotek-staging \
  -o jsonpath='{range .status.conditions[*]}{.type}{": "}{.message}{"\n"}{end}'

kubectl -n robotek-staging get deployment,replicaset,pods -o wide
kubectl -n robotek-staging describe deployment robotek-staging
kubectl -n robotek-staging get events --sort-by=.metadata.creationTimestamp | tail -40
```

Do not treat `Healthy` at an old revision as proof that the latest Git commit is deployed. Always compare `.status.sync.revision` with the expected commit SHA.

### 13.2 Robotek Pod is not Ready

```bash
pod="$(kubectl -n robotek-staging get pods \
  -l app.kubernetes.io/instance=robotek-staging \
  --sort-by=.metadata.creationTimestamp \
  -o jsonpath='{.items[-1].metadata.name}')"

kubectl -n robotek-staging describe pod "$pod"
kubectl -n robotek-staging logs "$pod" -c robotek --tail=200
kubectl -n robotek-staging logs "$pod" -c ros-exporter --tail=200
```

Check:

- Startup and readiness probe messages.
- `/mission/status` with its explicit custom message type.
- `/odom` with best-effort QoS.
- Writable `/tmp` and `/home/robot` mounts.
- OOMKilled or restart history.

### 13.3 Image pull failure

```bash
kubectl -n robotek-staging describe pod "$pod"
kubectl -n robotek-staging get events \
  --sort-by=.metadata.creationTimestamp | tail -40
```

Verify the digest in Git and GHCR. Do not replace an immutable digest with a movable tag as a shortcut.

### 13.4 ROS exporter down

```bash
kubectl -n robotek-staging get pod "$pod" \
  -o jsonpath='{range .status.containerStatuses[*]}{.name}{" ready="}{.ready}{" restarts="}{.restartCount}{" last="}{.lastState}{"\n"}{end}'

kubectl -n robotek-staging logs "$pod" \
  -c ros-exporter \
  --tail=200
```

Do not run memory-heavy ROS CLI diagnostics inside the exporter container. A prior extra CLI diagnostic caused an OOM at the exporter limit even though normal exporter operation was healthy.

### 13.5 Telegram notifications missing

Check:

```bash
kubectl -n monitoring get secret robotek-telegram
kubectl -n monitoring get pods -l app.kubernetes.io/name=alertmanager
kubectl -n monitoring logs \
  -l app.kubernetes.io/name=alertmanager \
  --tail=200
```

Confirm the alert carries `service="robotek"`, because that label selects the Telegram route.

### 13.6 Falco event

1. Record timestamp, rule, priority, namespace, Pod, container, user, command, and image.
2. Determine whether the event corresponds to an approved test or operator action.
3. Inspect the Pod specification, events, and logs.
4. Preserve relevant Falco and Kubernetes output.
5. Remove unauthorized workloads through the Git or workload owner process.
6. Rotate credentials only when evidence indicates possible exposure.

### 13.7 Monitoring storage or node pressure

```bash
kubectl -n monitoring get pvc
kubectl -n monitoring describe pvc
kubectl describe node
kubectl top node
kubectl top pods -A
sudo df -h
```

Prometheus retention is intentionally short for the single-node staging environment. Do not increase retention or PVC size without checking node memory and disk capacity.

---

## 14. Git-driven rollback

For an application or chart regression:

```bash
git log --oneline --max-count=10
git revert <bad-commit-sha>
git push origin main
```

Then verify:

```bash
kubectl -n argocd get application robotek-staging -w
kubectl -n robotek-staging rollout status deployment/robotek-staging --timeout=10m
```

Rollback must restore a known-good Git state. Do not use `kubectl edit`, direct image replacement, or unmanaged Helm upgrades as the final recovery mechanism.

---

## 15. Evidence handling

Expected workflow evidence includes:

- Image reference and digest.
- Helm lint output.
- Rendered staging manifests.
- Trivy JSON and text reports.
- Release verification output.
- ROS smoke-test output.
- Kubernetes status, logs, events, and metrics.
- Workflow metadata.
- SHA-256 checksums.

Artifacts are retained for 30 days unless the workflow is intentionally changed. Download important evidence before expiry and store it in an approved audit location. Generated evidence is not committed to the repository.

---

## 16. Maintenance checklist

Weekly:

- Confirm all Argo CD Applications are `Synced` and `Healthy`.
- Confirm Prometheus targets are Up.
- Review firing or recently resolved alerts.
- Review Falco detections for unexpected events.
- Confirm the scheduled security workflow completed successfully.
- Check node CPU, memory, and disk pressure.
- Check Prometheus, Grafana, and Alertmanager PVC usage.

After every staging change:

- Confirm the exact Argo CD revision.
- Confirm the immutable runtime digest.
- Confirm the Robotek Pod is `2/2 Running`.
- Confirm both root filesystems remain read-only.
- Run or dispatch post-deployment validation.
- Preserve the resulting evidence artifact.

Monthly:

- Review pinned chart and action versions.
- Review Trivy database and scanner-version changes.
- Rotate secrets according to the project policy.
- Review runner updates and repository access.
- Test one controlled alert and one controlled Falco detection.

---

## 17. Known limitations

- The staging cluster has one K3s node and is not highly available.
- Metrics retention is short and uses local-path storage.
- UIs are private and require port forwarding.
- Telegram is the only configured external alert channel.
- The Telegram and Grafana administrator Secrets are bootstrapped manually.
- Admission-time verification of Cosign signatures and attestations is not yet enforced.
- Rollback is Git-driven, not policy-driven automatic rollback.
- Terraform infrastructure ownership is deferred.
- Multi-robot generalization belongs to Phase 7.
