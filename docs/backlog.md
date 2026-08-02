# 📋 Project Backlog

---

## ✅ Phase 1 – Mock Robot Architecture

**Status:** Completed

Delivered:

- ROS 2 Jazzy workspace.
- Python and C++ robot packages.
- Robot description, Gazebo world, bridges, controllers, mission manager, and bringup.
- Custom action, service, and message interfaces.
- Unit, integration, launch, and simulation test structure.
- Reusable repository layout for CI/CD validation.

---

## ✅ Phase 2 – ROS 2 CI Workflow

**Status:** Completed

Delivered:

- Reusable ROS 2 CI image in GHCR.
- Ruff linting and formatting.
- clang-format, ShellCheck, and cppcheck.
- Robot configuration validation.
- colcon build.
- GoogleTest and pytest.
- Python coverage enforcement.
- Integration and headless Gazebo simulation tests.
- Pull-request fast gate and complete main/scheduled tier.
- Test and coverage artifacts.
- Least-privilege permissions, concurrency control, and aggregate CI gate.

---

## ✅ Phase 3 – Security Workflow

**Status:** Completed

Delivered:

- Gitleaks full-history secret scanning.
- Semgrep Python SAST.
- cppcheck C++ analysis.
- Trivy filesystem and CI-image scanning.
- Blocking HIGH and CRITICAL vulnerability policy.
- Security exception governance.
- Security artifacts and aggregate security gate.
- Reusable workflow through `workflow_call`.

---

## ✅ Phase 4 – Verified Runtime Delivery and Supply-Chain Security

**Status:** Completed

Delivered:

- Central `Verified Runtime Release` workflow.
- Parallel CI and security gates.
- Multi-stage production runtime image.
- Runtime package and non-root validation.
- Blocking pre-publication Trivy gate.
- Candidate image flow before final promotion.
- SPDX and CycloneDX SBOMs.
- Cosign keyless signing.
- GitHub provenance and SBOM attestations.
- Signature and attestation verification before promotion.
- Immutable digest verification for final tags.
- Release evidence, metadata, and SHA-256 checksums.
- Published runtime image:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime
```

---

## ✅ Phase 5 – GitOps Staging Deployment, Validation, and Rollback

**Status:** Completed

Delivered:

- Ubuntu 24.04 staging host on AWS EC2.
- Pinned single-node K3s cluster.
- Helm and private Argo CD deployment.
- Reusable Robotek Helm chart.
- Dedicated staging values.
- One complete ROS 2/Gazebo simulation per Pod.
- `Recreate` strategy.
- Dedicated ServiceAccount with no automatic API token mount.
- CPU and memory requests and limits.
- In-memory `/dev/shm`.
- Non-root UID/GID `1001`.
- No privilege escalation or privileged mode.
- All Linux capabilities dropped.
- `RuntimeDefault` seccomp.
- ROS-aware startup and readiness probes.
- Argo CD automated sync, pruning, self-healing, retry, and namespace creation.
- Automated immutable-digest promotion from verified GHCR `main`.
- Helm lint/render and Git validation before promotion commit.
- Demonstrated Git-driven rollback from an invalid digest.
- Release verification, ROS smoke test, and deployment evidence scripts.

---

## ✅ Phase 6 – Observability and Runtime Security

**Status:** Completed

### Observability foundation

Delivered:

- Approved architecture in `docs/phase6-design.md`.
- GitOps wrapper chart under `deploy/helm/observability`.
- Pinned `kube-prometheus-stack` version `88.0.1`.
- Dedicated Argo CD Application `robotek-observability`.
- Private Prometheus, Grafana, and Alertmanager services.
- kube-state-metrics and node-exporter.
- Conservative single-node CPU and memory limits.
- Persistent local-path storage:
  - Prometheus: 5 GiB.
  - Grafana: 2 GiB.
  - Alertmanager: 1 GiB.

### Kubernetes and GitOps monitoring

Delivered:

- Robotek Deployment and Pod availability metrics.
- Pod readiness and restart monitoring.
- Image-pull failure monitoring.
- Node CPU, memory, storage, and readiness metrics.
- Argo CD sync and health metrics.
- Controlled image-pull failure demonstration.

Platform and GitOps alerts:

- `RobotekDeploymentUnavailable`
- `RobotekPodNotReady`
- `RobotekContainerRestarting`
- `RobotekImagePullFailure`
- `RobotekArgoCDOutOfSync`
- `RobotekArgoCDUnhealthy`

### ROS 2 metrics exporter

Delivered:

- `src/mock_robot_observability` package.
- Sidecar deployment named `ros-exporter`.
- Internal metrics Service and ServiceMonitor.
- Port `9108`.
- `/metrics`, `/-/ready`, and `/healthz` endpoints.
- Metrics for exporter state, ROS topics, topic publishers, topic subscribers, node discovery, and collection errors.
- Prometheus scrape validation.
- Runtime and exporter image pinned to the same verified digest.

Operational alerting uses topic publisher and subscriber metrics because ROS node-name metadata was not consistently discoverable in the staging DDS environment.

### ROS dashboards and alerts

Delivered:

- Git-provisioned **Robotek GitOps Overview** dashboard.
- Git-provisioned **Robotek ROS Health** dashboard.
- Eight ROS health panels.
- Seven ROS Prometheus alerts:
  - `RobotekROSExporterDown`
  - `RobotekROSCollectionErrors`
  - `RobotekMissionStatusPublisherMissing`
  - `RobotekOdomPublisherMissing`
  - `RobotekLaserScanPublisherMissing`
  - `RobotekVelocitySafetySubscriberMissing`
  - `RobotekEmergencyStopSubscriberMissing`

### Alertmanager and Telegram

Delivered:

- Alert grouping, routing, repeat intervals, and inhibition.
- Robotek alert route selected through `service="robotek"`.
- Telegram notification receiver.
- Bot token mounted from the non-Git `robotek-telegram` Secret.
- Controlled notification delivery test.

### Falco runtime security

Delivered:

- Wrapper chart under `deploy/helm/runtime-security`.
- Dedicated Argo CD Application `robotek-runtime-security`.
- Falco chart `9.1.0` and Falco `0.44.1`.
- Modern eBPF driver.
- K3s containerd integration.
- Least-privileged capabilities.
- No privileged mode and no host PID namespace.
- Prometheus ServiceMonitor and successful scrape.
- Controlled terminal-shell detection demonstration.
- Verified zero observed Falco buffer drops during validation.

### Automated post-deployment validation

Delivered:

- Dedicated repository-scoped self-hosted GitHub Actions runner.
- Restricted Kubernetes ServiceAccount, Roles, and RoleBindings.
- Runner cannot read Secrets or delete Deployments.
- `.github/workflows/post-deploy-validation.yml`.
- Exact revision checkout and desired-state compatibility check.
- Live digest verification.
- Release verification and ROS smoke tests.
- Evidence collection on success or failure.
- Timestamped artifact upload.

Verified successful run:

```text
Run ID: 30771625827
Job ID: 91559654636
Artifact: robotek-staging-evidence-30771625827-1
```

### Scheduled staging security rescans

Delivered:

- `.github/workflows/scheduled-staging-security.yml`.
- Thursday 03:37 UTC schedule and manual dispatch.
- Exact promoted-image resolution from staging values.
- Runtime image HIGH/CRITICAL vulnerability scan.
- Helm lint and staging manifest render.
- Rendered-manifest HIGH/CRITICAL misconfiguration scan.
- Metadata, report checksums, and 30-day evidence artifact.
- Aggregate final security gate.

The first controlled run found two valid `KSV-0014` findings. They were fixed rather than ignored.

Final hardening:

- `readOnlyRootFilesystem: true` for `robotek` and `ros-exporter`.
- Separate writable `/tmp` and `/home/robot` `emptyDir` mounts.
- Preserved in-memory `/dev/shm` for Robotek.
- Explicit `mock_robot_interfaces/msg/MissionStatus` health-probe type.
- Explicit `nav_msgs/msg/Odometry` health-probe type.
- Final Pod `2/2 Running` with zero restarts.
- Mission status and odometry verified after hardening.

Verified successful security run:

```text
Run ID: 30772842488
Job ID: 91562893672
Commit: aa17640d099860cc604df27114693e62b3905170
Artifact: robotek-scheduled-security-30772842488-1
Artifact SHA-256: 054b51184da7365fb4d0e51dd77b8b7ce44a7f396d0c28bb23dc5b499bf1662e
Result: success
```

### Operations and handover

Delivered:

- `docs/phase6-operations.md`.
- `docs/phase6-final-report.md`.
- Updated README and backlog.
- Daily, weekly, incident, rollback, evidence, and maintenance procedures.

---

## ⏳ Phase 7 – Generic Multi-Robot Template and Final Demonstration

**Status:** Planned

### Template extraction

Planned:

- Extract reusable workflows and shared delivery logic.
- Parameterize:
  - ROS distribution.
  - Package names.
  - Coverage thresholds.
  - Security thresholds.
  - Configuration paths.
  - Runtime image names.
  - Deployment targets.
  - Observability settings.
  - Robot-specific topic expectations.
- Generalize CI and runtime container configuration.
- Separate shared platform code from Robotek-specific behavior.

### Multi-robot adoption

Planned:

- Apply the reusable platform to delivery, reception, security, and robot-arm repositories.
- Preserve robot-specific tests and behavior.
- Share the same CI, security, delivery, GitOps, monitoring, and runtime-security controls.

### Documentation

Planned:

- Template usage guide.
- Migration guide.
- Adoption guide for real robot repositories.
- Final platform architecture guide.
- Final operations and troubleshooting handover.

### Final demonstration

Planned:

- Complete green end-to-end pipeline.
- Demonstrate blocked CI and security scenarios.
- Demonstrate blocked release and deployment scenarios.
- Demonstrate observability alerts.
- Demonstrate Falco runtime detection.
- Demonstrate Git-driven rollback.
- Present evidence artifacts and final platform handover.

---

## Future hardening outside the current phase plan

- Admission-time Cosign signature and attestation enforcement.
- Policy-driven automatic rollback.
- Highly available multi-node Kubernetes.
- Long-term centralized metrics and logs.
- Additional notification channels.
- Terraform ownership of AWS and K3s infrastructure.
- Secret-management integration.
- Production-grade disaster recovery.

---

## 📊 Overall progress

| Phase | Progress | Status |
|---|:---:|---|
| Phase 1 – Mock Robot Architecture | 100% | ✅ Completed |
| Phase 2 – CI Workflow | 100% | ✅ Completed |
| Phase 3 – Security Workflow | 100% | ✅ Completed |
| Phase 4 – Verified Runtime Delivery | 100% | ✅ Completed |
| Phase 5 – GitOps Staging Deployment | 100% | ✅ Completed |
| Phase 6 – Observability and Runtime Security | 100% | ✅ Completed |
| Phase 7 – Multi-Robot Template and Final Demonstration | 0% | ⏳ Planned |

---

## 🎯 Final objective

Deliver a reusable, production-oriented DevSecOps platform for ROS 2 robot software that provides:

- Containerized CI and delivery.
- Tiered automated testing.
- Security-by-default.
- Runtime vulnerability and configuration gates.
- SBOM generation and verification.
- Keyless image signing.
- Provenance and SBOM attestations.
- Immutable evidence-backed releases.
- Automated GitOps staging deployment.
- Runtime observability and alerting.
- Runtime security detection.
- Automated deployment validation.
- Scheduled security rescanning.
- Git-driven rollback.
- Easy adoption across multiple robot repositories.
