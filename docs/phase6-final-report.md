# Phase 6 Completion Report

**Project:** Robotek 1.2  
**Phase:** Observability and Runtime Security  
**Status:** Completed  
**Completion date:** August 3, 2026  
**Environment:** Ubuntu 24.04, single-node K3s, AWS EC2

---

## 1. Executive summary

Phase 6 transformed the Robotek staging environment from a deployable GitOps workload into an observable, alerting, runtime-aware, and continuously verified platform.

The completed solution provides:

- GitOps-managed Prometheus, Grafana, Alertmanager, kube-state-metrics, and node-exporter.
- Kubernetes, K3s, Robotek, ROS 2, and Argo CD monitoring.
- Git-managed dashboards and alert rules.
- Telegram alert delivery.
- A ROS 2 Prometheus exporter running as a hardened sidecar.
- Falco runtime detection with modern eBPF.
- Automated post-deployment validation on a restricted self-hosted runner.
- Scheduled Trivy rescanning of the promoted runtime image and rendered Kubernetes manifests.
- Evidence artifacts with metadata and SHA-256 checksums.
- Read-only root filesystems for both Robotek containers, with narrowly scoped writable runtime volumes.

All Phase 6 acceptance paths were demonstrated successfully in staging.

---

## 2. Final verified state

### Robotek

```text
Argo CD: Synced / Healthy
Deployment: 1/1 available
Pod: 2/2 Running
Restarts after final rollout: 0
Runtime image: ghcr.io/iheb-mrabet/robotek-1.2-runtime@sha256:9de522ed93c05f218b63334ccdfb4772060d07102ae9f6f781a409a13b126c28
```

Final chart revision validated in staging:

```text
aa17640d099860cc604df27114693e62b3905170
```

The runtime and exporter containers both use:

- Non-root UID/GID `1001`.
- No privilege escalation.
- No privileged mode.
- All Linux capabilities dropped.
- `RuntimeDefault` seccomp.
- Read-only root filesystems.
- Writable `emptyDir` mounts for `/tmp` and `/home/robot`.

The main Robotek container also retains the in-memory `/dev/shm` volume required by Gazebo and ROS middleware.

### ROS validation

The final rollout confirmed:

- `/mission/status` publishes `mock_robot_interfaces/msg/MissionStatus`.
- `/odom` publishes `nav_msgs/msg/Odometry` with best-effort QoS compatibility.
- Startup and readiness probes use explicit message types.
- Mission status and odometry smoke tests pass.
- The ROS exporter is Ready and scraped by Prometheus.

---

## 3. Observability platform

### Components

The `robotek-observability` Argo CD Application manages the monitoring namespace.

Deployed components:

- Prometheus Operator.
- Prometheus.
- Grafana.
- Alertmanager.
- kube-state-metrics.
- node-exporter.

The wrapper chart pins `kube-prometheus-stack` version `88.0.1`.

### Storage

```text
Prometheus: 5 GiB
Grafana: 2 GiB
Alertmanager: 1 GiB
Storage class: local-path
```

### Exposure

All monitoring services use ClusterIP and have no public Ingress. Operator access uses SSH and Kubernetes port forwarding.

### Dashboards

Git-provisioned dashboards:

- **Robotek GitOps Overview** — UID `ad7m2rk`.
- **Robotek ROS Health** — UID `robotek-ros-health`.

The ROS dashboard contains eight panels covering exporter health, topic discovery, collection errors, critical publishers, and safety subscribers.

---

## 4. Metrics and alerting

### Platform and GitOps alerts

- `RobotekDeploymentUnavailable`
- `RobotekPodNotReady`
- `RobotekContainerRestarting`
- `RobotekImagePullFailure`
- `RobotekArgoCDOutOfSync`
- `RobotekArgoCDUnhealthy`

A controlled image-pull failure demonstrated that the configured signal and alert path work.

### ROS alerts

- `RobotekROSExporterDown`
- `RobotekROSCollectionErrors`
- `RobotekMissionStatusPublisherMissing`
- `RobotekOdomPublisherMissing`
- `RobotekLaserScanPublisherMissing`
- `RobotekVelocitySafetySubscriberMissing`
- `RobotekEmergencyStopSubscriberMissing`

All seven ROS rules were loaded by Prometheus with healthy evaluation state after deployment.

### Notification channel

Alertmanager routes Robotek alerts to Telegram. The bot token is mounted from the manually managed `robotek-telegram` Secret and is never stored in Git.

A direct controlled alert confirmed successful Telegram delivery.

---

## 5. ROS 2 Prometheus exporter

Package:

```text
src/mock_robot_observability
```

Deployment model:

```text
Robotek Pod
├── robotek
└── ros-exporter
```

HTTP port:

```text
9108
```

Endpoints:

```text
/metrics
/-/ready
/healthz
```

Exported metrics include:

- `robotek_ros_exporter_up`
- `robotek_ros_nodes`
- `robotek_ros_topics`
- `robotek_ros_node_up{node="..."}`
- `robotek_ros_topic_publishers{topic="..."}`
- `robotek_ros_topic_subscribers{topic="..."}`
- `robotek_ros_collection_errors_total`

ROS node-name metadata was not consistently discoverable in the selected DDS/K3s environment even though endpoint discovery worked. Final operational alerting therefore uses publisher and subscriber metrics instead of assuming reliable graph node names.

A diagnostic ROS CLI process previously exceeded the exporter's normal memory limit and was OOM-killed. Normal exporter operation remained healthy, so the resource limit was not increased. The operations runbook explicitly prohibits heavy ROS CLI diagnostics inside the exporter container.

---

## 6. Runtime security with Falco

Argo CD Application:

```text
robotek-runtime-security
```

Namespace:

```text
runtime-security
```

Versions:

```text
Falco Helm chart: 9.1.0
Falco application: 0.44.1
```

Driver and runtime integration:

- Modern eBPF probe.
- K3s containerd socket at `/host/run/k3s/containerd/containerd.sock`.
- BPF filesystem and kernel tracing support verified.
- No privileged container.
- No host PID namespace.
- Capabilities limited to `BPF`, `PERFMON`, `SYS_RESOURCE`, and `SYS_PTRACE`.

The message indicating disabled BPF iterators is expected because Falco is not running in the root PID namespace.

Prometheus successfully scraped the Falco ServiceMonitor, including version and event metrics, with no observed buffer drops during validation.

### Controlled detection

A hardened Alpine test Pod launched an attached terminal shell. Falco detected:

```text
A shell was spawned in a container with an attached terminal
```

The event included the namespace, Pod, container, user, UID, and command. The test Pod was removed after validation.

---

## 7. Automated post-deployment validation

Workflow:

```text
.github/workflows/post-deploy-validation.yml
```

Execution platform:

- Dedicated repository-scoped self-hosted GitHub Actions runner.
- Runner host: the staging K3s node.
- Service user: `github-runner`.
- Runner labels: `robotek-staging`, `k3s`, and `staging`.

Kubernetes permissions are restricted to the minimum required staging and Argo CD reads plus controlled Pod execution. The runner cannot read Kubernetes Secrets or delete Deployments.

The workflow:

1. Checks out the exact expected commit.
2. Resolves the promoted staging digest.
3. Waits for a compatible Argo CD desired state.
4. Verifies the live release and immutable image.
5. Runs ROS smoke tests.
6. Collects deployment evidence.
7. Uploads evidence even when a validation stage fails.
8. Enforces a final aggregate result.

Verified successful run:

```text
Run ID: 30771625827
Job ID: 91559654636
Result: success
```

Evidence artifact:

```text
Name: robotek-staging-evidence-30771625827-1
Artifact ID: 8840711468
Files: 15
SHA-256: fe47f7eb75c1a7c48c06dec6fea08f77b8d5a14d4efaab85383aa103707a5ece
```

---

## 8. Scheduled security rescan

Workflow:

```text
.github/workflows/scheduled-staging-security.yml
```

Schedule:

```text
Thursday at 03:37 UTC
```

The workflow scans:

1. The exact promoted staging runtime image by immutable digest.
2. The exact rendered staging Kubernetes manifests.

Policy:

- HIGH and CRITICAL image vulnerabilities with available fixes are blocking.
- HIGH and CRITICAL Kubernetes misconfigurations are blocking.
- Reports, metadata, and checksums are preserved as an artifact.

### Controlled policy failure and remediation

The first run correctly failed with two `KSV-0014` findings because `robotek` and `ros-exporter` did not use read-only root filesystems.

The remediation:

- Enabled `readOnlyRootFilesystem: true` for both containers.
- Added separate writable `/tmp` and `/home/robot` `emptyDir` volumes.
- Preserved `/dev/shm` for the main runtime.
- Corrected health probes to use explicit ROS message types.
- Verified the final Pod as `2/2 Running` with zero restarts.
- Verified mission status and odometry after hardening.

No Trivy policy rule was ignored or weakened.

### Final successful run

```text
Run ID: 30772842488
Job ID: 91562893672
Commit: aa17640d099860cc604df27114693e62b3905170
Result: success
```

All required steps succeeded:

- Runtime vulnerability JSON report.
- Runtime vulnerability policy.
- Helm setup, lint, and render.
- Kubernetes configuration JSON report.
- Kubernetes configuration policy.
- Metadata and checksum generation.
- Artifact upload.
- Final aggregate evaluation.

Evidence artifact:

```text
Name: robotek-scheduled-security-30772842488-1
Artifact ID: 8841080194
Files: 9
Size: 605999 bytes
SHA-256: 054b51184da7365fb4d0e51dd77b8b7ce44a7f396d0c28bb23dc5b499bf1662e
Expiry: September 1, 2026
```

Final workflow result:

```text
Scheduled staging security rescan passed.
```

---

## 9. Acceptance criteria result

| Acceptance criterion | Result |
|---|---|
| Prometheus stack deployed through Argo CD | Passed |
| Monitoring components Running and private | Passed |
| Kubernetes and node metrics available | Passed |
| Argo CD metrics available | Passed |
| ROS exporter scraped by Prometheus | Passed |
| Git-provisioned Grafana dashboards available | Passed |
| Platform and GitOps alerts deployed | Passed |
| ROS health alerts deployed | Passed |
| Telegram notification path tested | Passed |
| Falco deployed with modern eBPF | Passed |
| Controlled Falco event detected | Passed |
| Automated post-deployment workflow successful | Passed |
| Scheduled image and manifest security scan successful | Passed |
| Final Pod hardened and healthy | Passed |
| Evidence artifacts generated with checksums | Passed |

---

## 10. Operational documentation

Phase 6 operational guidance is maintained in:

```text
docs/phase6-operations.md
```

The runbook includes:

- Daily and weekly checks.
- Private dashboard access.
- Prometheus queries.
- Alert inventory.
- Secret rotation.
- Falco operation and controlled testing.
- Runner and workflow operation.
- Incident diagnostics.
- Git-driven rollback.
- Evidence handling.
- Known limitations.

---

## 11. Remaining limitations and deferred work

The following are intentionally outside Phase 6:

- Highly available or multi-node Kubernetes.
- Long-term enterprise metrics retention.
- Public monitoring endpoints.
- Admission-time Cosign signature and attestation enforcement.
- Policy-driven automatic rollback.
- Terraform ownership of AWS and K3s infrastructure.
- Centralized long-term log storage.
- Multi-robot generalization.

These items are future hardening or Phase 7 work and do not invalidate the completed Phase 6 acceptance criteria.

---

## 12. Final conclusion

Phase 6 is complete.

Robotek now has an end-to-end staging platform that can:

- Observe Kubernetes, GitOps, runtime, and ROS health.
- Notify operators when critical conditions occur.
- Detect suspicious container runtime behavior.
- Revalidate every deployment from inside the staging environment.
- Rescan the exact promoted image and rendered configuration on a schedule.
- Enforce container and Kubernetes security policy without suppressing valid findings.
- Preserve reproducible evidence for release, deployment, and security review.

The repository is ready to proceed to Phase 7: generic multi-robot template extraction, adoption guidance, and the final demonstration.
