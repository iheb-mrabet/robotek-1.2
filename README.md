# 🤖 Robotek 1.2

[![ROS 2 CI](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci.yml)
[![ROS 2 Security](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/security.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/security.yml)
[![Verified Runtime Release](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/release.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/release.yml)
[![Post-Deploy Validation](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/post-deploy-validation.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/post-deploy-validation.yml)
[![Scheduled Staging Security](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/scheduled-staging-security.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/scheduled-staging-security.yml)
![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros)
![Ubuntu 24.04](https://img.shields.io/badge/Ubuntu-24.04-E95420?logo=ubuntu)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-326CE5?logo=kubernetes)
![GitOps](https://img.shields.io/badge/GitOps-Argo%20CD-EF7B4D?logo=argo)
![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-E6522C?logo=prometheus)
![Grafana](https://img.shields.io/badge/Dashboards-Grafana-F46800?logo=grafana)
![Falco](https://img.shields.io/badge/Runtime%20Security-Falco-00AEC7)

> A complete ROS 2 DevSecOps reference project covering automated testing, security gates, verified container delivery, SBOMs, keyless signing, attestations, GitOps deployment, runtime validation, observability, alerting, runtime detection, and evidence-backed operations.

Robotek 1.2 is a compact but realistic mock indoor delivery robot built to demonstrate a professional robotics software lifecycle end to end. It combines ROS 2 Jazzy, Gazebo Harmonic, GitHub Actions, GHCR, Helm, Argo CD, K3s, Prometheus, Grafana, Alertmanager, Trivy, Cosign, and Falco.

---

## Project status

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Mock robot architecture | ✅ Completed |
| Phase 2 | ROS 2 CI workflow | ✅ Completed |
| Phase 3 | Security workflow | ✅ Completed |
| Phase 4 | Verified runtime delivery and supply-chain security | ✅ Completed |
| Phase 5 | GitOps staging deployment, validation, and rollback | ✅ Completed |
| Phase 6 | Observability and runtime security | ✅ Completed |
| Phase 7 | Generic multi-robot template and final demonstration | ⏳ Planned |

See [`docs/backlog.md`](docs/backlog.md) for the detailed roadmap.

---

## Robot capabilities

The simulated differential-drive robot can:

- Spawn in a warehouse environment.
- Publish odometry, transforms, and LiDAR data.
- Accept delivery goals through a ROS 2 action.
- Navigate toward a waypoint.
- Apply velocity and obstacle-safety limits.
- Activate and release emergency stop.
- Publish mission state and execution results.

---

## Technology stack

| Area | Technologies |
|---|---|
| Robotics | ROS 2 Jazzy, Gazebo Harmonic |
| Languages | C++17, Python 3.12 |
| Build and test | colcon, CMake, ament, GoogleTest, pytest, launch testing |
| CI/CD | GitHub Actions, reusable workflows, self-hosted staging runner |
| Static analysis | Ruff, clang-format, ShellCheck, cppcheck, Semgrep |
| Security | Gitleaks, Trivy, Cosign, Syft, GitHub attestations, Falco |
| Containers | Docker, multi-stage runtime build, GHCR |
| Deployment | Helm, K3s, Argo CD |
| Observability | Prometheus, Grafana, Alertmanager, kube-state-metrics, node-exporter |
| Staging | Ubuntu 24.04 on AWS EC2 |

---

## Repository architecture

```text
src/
├── mock_robot_interfaces/
├── mock_robot_description/
├── mock_robot_gazebo/
├── mock_robot_control/
├── mock_robot_behavior/
├── mock_robot_bringup/
├── mock_robot_observability/
└── mock_robot_system_tests/

.github/workflows/
├── ci-image.yml
├── ci.yml
├── security.yml
├── build-package.yml
├── release.yml
├── post-deploy-validation.yml
└── scheduled-staging-security.yml

deploy/
├── argocd/
│   ├── robotek-staging.yaml
│   ├── robotek-observability.yaml
│   └── robotek-runtime-security.yaml
└── helm/
    ├── robotek/
    ├── observability/
    └── runtime-security/

scripts/deployment/
├── verify_release.sh
├── smoke_test.sh
└── collect_evidence.sh

docs/
├── backlog.md
├── phase6-design.md
├── phase6-operations.md
└── phase6-final-report.md
```

---

## End-to-end DevSecOps flow

```text
Developer push
   │
   ├── ROS 2 CI gate
   ├── Security gate
   │
   ▼
Runtime image build and validation
   │
   ├── Trivy vulnerability gate
   ├── SPDX and CycloneDX SBOMs
   ├── Cosign keyless signing
   ├── Provenance and SBOM attestations
   └── Signature and attestation verification
   │
   ▼
Promote verified digest to GHCR
   │
   ▼
Update staging desired state in Git
   │
   ▼
Argo CD reconciles K3s
   │
   ├── Hardened Robotek runtime
   ├── ROS Prometheus exporter
   ├── Prometheus/Grafana/Alertmanager
   └── Falco runtime security
   │
   ▼
Automated post-deploy validation
   │
   ├── Release verification
   ├── ROS smoke test
   ├── Evidence collection
   └── Artifact upload
   │
   ▼
Scheduled image and manifest security rescans
```

Runtime delivery cannot start unless CI and security pass. Staging promotion cannot occur until the image is built, scanned, signed, attested, verified, and promoted by immutable digest.

---

## Continuous integration

The reusable CI workflow includes:

- Ruff linting and formatting.
- clang-format.
- ShellCheck.
- cppcheck.
- Robot configuration validation.
- ROS 2 workspace build.
- C++ and Python unit tests.
- Python coverage enforcement.
- Integration tests.
- Headless Gazebo simulation tests.
- Aggregated CI gate.
- Test and coverage artifacts.

CI jobs use:

```text
ghcr.io/iheb-mrabet/robotek-1.2-ci:jazzy
```

---

## Security workflow

The security workflow includes:

- Gitleaks full-history secret scanning.
- Semgrep Python SAST.
- cppcheck C++ analysis.
- Trivy filesystem and image scanning.
- Security exception-policy validation.
- Blocking HIGH and CRITICAL vulnerability policy.
- Aggregated security gate.

---

## Verified runtime delivery

The production runtime image is built with a multi-stage Dockerfile and published to:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime
```

The delivery workflow performs:

1. Runtime build and startup validation.
2. Non-root and package validation.
3. Blocking Trivy image scan.
4. Candidate publication.
5. SPDX and CycloneDX SBOM generation.
6. Cosign keyless signing.
7. GitHub build-provenance and SBOM attestations.
8. Signature and attestation verification.
9. Promotion to final tags only after verification.
10. Evidence generation and SHA-256 checksums.

Security-sensitive deployments use immutable references:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime@sha256:<digest>
```

The current verified staging digest is:

```text
sha256:9de522ed93c05f218b63334ccdfb4772060d07102ae9f6f781a409a13b126c28
```

---

## GitOps staging deployment

The release workflow updates `deploy/helm/robotek/values-staging.yaml` with the verified digest. Argo CD then reconciles the Helm release into K3s.

Validated staging state:

```text
Argo CD: Synced / Healthy
Deployment: 1/1 available
Pod: 2/2 Running
Restarts after final rollout: 0
```

The staging workload enforces:

- Non-root UID/GID `1001`.
- Privilege escalation disabled.
- Privileged mode disabled.
- All Linux capabilities dropped.
- `RuntimeDefault` seccomp.
- Dedicated ServiceAccount with no automatic token mount.
- CPU and memory requests and limits.
- Read-only root filesystems for `robotek` and `ros-exporter`.
- Separate writable `emptyDir` mounts for `/tmp` and `/home/robot`.
- In-memory `/dev/shm` for Gazebo and ROS middleware.
- ROS-aware startup and readiness probes.
- `Recreate` strategy to avoid duplicate simulations.

Rollback is Git-driven through `git revert`, with Argo CD restoring the last known-good desired state.

---

## Phase 6 observability

The GitOps-managed observability stack contains:

- Prometheus Operator.
- Prometheus.
- Grafana.
- Alertmanager.
- kube-state-metrics.
- node-exporter.

The stack is private, uses ClusterIP services, and is accessed through port forwarding.

Persistent storage:

```text
Prometheus: 5 GiB
Grafana: 2 GiB
Alertmanager: 1 GiB
```

Provisioned dashboards:

- **Robotek GitOps Overview** — UID `ad7m2rk`.
- **Robotek ROS Health** — UID `robotek-ros-health`.

---

## ROS 2 Prometheus exporter

The `mock_robot_observability` package runs as the `ros-exporter` sidecar and exposes port `9108`.

Endpoints:

```text
/metrics
/-/ready
/healthz
```

Key metrics:

- `robotek_ros_exporter_up`
- `robotek_ros_nodes`
- `robotek_ros_topics`
- `robotek_ros_node_up{node="..."}`
- `robotek_ros_topic_publishers{topic="..."}`
- `robotek_ros_topic_subscribers{topic="..."}`
- `robotek_ros_collection_errors_total`

Operational alerts use publisher and subscriber metrics because ROS node-name metadata was not consistently discoverable in the staging DDS environment.

---

## Alerts and Telegram notifications

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

Alertmanager routes Robotek alerts to Telegram using a Kubernetes Secret that is not stored in Git.

---

## Falco runtime security

Falco is deployed through the `robotek-runtime-security` Argo CD Application.

Configuration:

```text
Falco chart: 9.1.0
Falco version: 0.44.1
Driver: modern eBPF
Container runtime: K3s containerd
```

The DaemonSet is not privileged and uses only the capabilities required by the selected modern eBPF mode.

A controlled terminal-shell test was detected successfully, proving runtime event collection and rule evaluation.

---

## Automated post-deployment validation

The dedicated self-hosted staging runner executes:

```text
.github/workflows/post-deploy-validation.yml
```

The workflow:

- Checks out the exact expected revision.
- Waits for a compatible Argo CD state.
- Verifies the immutable digest and live deployment.
- Runs ROS smoke tests.
- Collects evidence on success or failure.
- Uploads a timestamped artifact.

Verified successful run:

```text
Run ID: 30771625827
Artifact: robotek-staging-evidence-30771625827-1
```

---

## Scheduled staging security rescan

The scheduled workflow scans the exact promoted image and the rendered Kubernetes manifests:

```text
.github/workflows/scheduled-staging-security.yml
```

Schedule:

```text
Thursday at 03:37 UTC
```

The first controlled run identified missing read-only root filesystems. The issue was corrected without suppressing the Trivy rule.

Verified successful run:

```text
Run ID: 30772842488
Job ID: 91562893672
Result: success
Artifact: robotek-scheduled-security-30772842488-1
Artifact SHA-256: 054b51184da7365fb4d0e51dd77b8b7ce44a7f396d0c28bb23dc5b499bf1662e
```

---

## Verify staging

From the configured staging host or self-hosted runner:

```bash
./scripts/deployment/verify_release.sh
./scripts/deployment/smoke_test.sh
./scripts/deployment/collect_evidence.sh
```

These scripts verify Argo CD, the immutable image, Pod readiness, ROS topic discovery, mission status, odometry, and evidence checksums.

---

## Local build and test

```bash
bash scripts/install_dependencies.sh
bash scripts/build.sh
source install/setup.bash
bash scripts/lint.sh
bash scripts/unit_tests.sh
bash scripts/python_coverage.sh
bash scripts/integration_tests.sh
bash scripts/simulation_tests.sh
```

Development container:

```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm mock-delivery-robot
```

Run the simulation:

```bash
source install/setup.bash
ros2 launch mock_robot_bringup full_simulation.launch.py gui:=false
```

---

## Execute a delivery mission

```bash
source install/setup.bash
ros2 action send_goal \
  /execute_delivery \
  mock_robot_interfaces/action/ExecuteDelivery \
  "{target_x: 0.8, target_y: 0.0}"
```

Emergency stop:

```bash
ros2 service call \
  /mission/emergency_stop \
  mock_robot_interfaces/srv/EmergencyStop \
  "{activate: true}"
```

Release emergency stop:

```bash
ros2 service call \
  /mission/emergency_stop \
  mock_robot_interfaces/srv/EmergencyStop \
  "{activate: false}"
```

---

## Workflow responsibilities

| Workflow | Responsibility |
|---|---|
| `ci-image.yml` | Build, scan, and publish the reusable ROS 2 CI image |
| `ci.yml` | Lint, build, tests, simulation, and aggregated CI gate |
| `security.yml` | Secret scanning, SAST, vulnerability scanning, and security gate |
| `build-package.yml` | Runtime build, scan, SBOM, signing, attestations, verification, and GHCR promotion |
| `release.yml` | Orchestrate CI, security, verified delivery, staging promotion, and release gate |
| `post-deploy-validation.yml` | Verify the live staging release and upload deployment evidence |
| `scheduled-staging-security.yml` | Rescan the promoted runtime image and rendered staging configuration |

---

## Documentation

- [`docs/backlog.md`](docs/backlog.md) — phase status and future roadmap.
- [`docs/phase6-design.md`](docs/phase6-design.md) — approved Phase 6 architecture and acceptance criteria.
- [`docs/phase6-operations.md`](docs/phase6-operations.md) — operations, incident response, recovery, and maintenance runbook.
- [`docs/phase6-final-report.md`](docs/phase6-final-report.md) — completed implementation, validation evidence, and final acceptance report.
- [`docs/runtime-image-verification.md`](docs/runtime-image-verification.md) — independent image, signature, attestation, and SBOM verification.
- [`docs/branch-protection.md`](docs/branch-protection.md) — recommended repository protection rules.

---

## Next phase

Phase 7 will extract the reusable platform into a generic multi-robot template, document adoption and migration, apply the shared controls to additional robot repositories, and prepare the final demonstration and handover.
