# 🤖 Robotek 1.2

[![ROS 2 CI](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci.yml)
[![ROS 2 Security](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/security.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/security.yml)
[![Verified Runtime Release](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/release.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/release.yml)
[![Build CI Image](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci-image.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci-image.yml)
![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros)
![Ubuntu 24.04](https://img.shields.io/badge/Ubuntu-24.04-E95420?logo=ubuntu)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-326CE5?logo=kubernetes)
![Argo CD](https://img.shields.io/badge/GitOps-Argo%20CD-EF7B4D?logo=argo)
![C++17](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=cplusplus)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)

> A ROS 2 DevSecOps reference project demonstrating automated testing, security gates, verified container delivery, SBOM generation, keyless image signing, provenance attestations, automatic GitOps staging promotion, Kubernetes deployment, runtime validation, and evidence-backed releases.

Robotek 1.2 is a compact but realistic mock indoor delivery robot built for learning and demonstrating a professional robotics DevSecOps lifecycle. The repository combines ROS 2 application development with CI, security automation, container hardening, software supply-chain protection, verified runtime image delivery, and automated deployment to a K3s staging cluster through Argo CD.

---

## Project overview

The robot is a differential-drive platform simulated with ROS 2 Jazzy and Gazebo Harmonic. It can:

- Spawn inside a simulated warehouse.
- Publish odometry and LiDAR data.
- Accept a delivery destination through a ROS 2 action.
- Move toward the requested waypoint.
- Apply velocity and obstacle-safety limits.
- Support emergency-stop activation and release.
- Publish mission state and execution results.

The project is intentionally small enough to understand end to end, while still including the packages, tests, workflows, security controls, release logic, GitOps configuration, deployment validation, and rollback procedures expected from a professional robot software repository.

---

## Current project status

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Mock robot architecture | ✅ Completed |
| Phase 2 | ROS 2 CI workflow | ✅ Completed |
| Phase 3 | Security workflow | ✅ Completed |
| Phase 4 | Verified runtime delivery and supply-chain security | ✅ Completed |
| Phase 5 | Staging deployment, runtime validation, GitOps promotion, and rollback | ✅ Completed |
| Phase 6 | Observability and runtime security | ⏳ Next |
| Phase 7 | Generic multi-robot template and final demonstration | ⏳ Planned |

See the complete roadmap in [`docs/backlog.md`](docs/backlog.md).

---

## Technology stack

| Area | Technologies |
|---|---|
| Robotics | ROS 2 Jazzy |
| Simulation | Gazebo Harmonic |
| Languages | C++17, Python 3.12 |
| Build system | colcon, CMake, ament |
| Testing | GoogleTest, pytest, ROS 2 launch testing |
| Containers | Docker, multi-stage builds |
| CI/CD | GitHub Actions, reusable workflows |
| Static analysis | Ruff, clang-format, ShellCheck, cppcheck, Semgrep |
| Secret detection | Gitleaks |
| Vulnerability scanning | Trivy |
| SBOM | Syft, SPDX JSON, CycloneDX JSON |
| Signing | Cosign keyless signing |
| Attestations | GitHub `actions/attest@v4` |
| Registry | GitHub Container Registry (GHCR) |
| Kubernetes | K3s |
| Packaging | Helm |
| GitOps | Argo CD |
| Staging platform | Ubuntu 24.04 on AWS EC2 |

---

## Repository architecture

```text
src/
├── mock_robot_interfaces/      Custom message, service, and action types
├── mock_robot_description/     Xacro model and robot-state publisher launch
├── mock_robot_gazebo/          Warehouse world, bridge config, simulation launch
├── mock_robot_control/         C++17 limiter, safety, and waypoint controllers
├── mock_robot_behavior/        Python mission manager and state machine
├── mock_robot_bringup/         Full-system launch and YAML configuration
└── mock_robot_system_tests/    Unit, integration, launch, and simulation tests

.github/workflows/
├── ci-image.yml                Build and publish the reusable CI image
├── ci.yml                      Reusable ROS 2 CI workflow
├── security.yml                Reusable security workflow
├── build-package.yml           Reusable signed runtime delivery workflow
└── release.yml                 Release orchestration and staging GitOps promotion

deploy/
├── helm/robotek/               Reusable Kubernetes Helm chart
└── argocd/                     Argo CD staging Application manifest

docker/
├── Dockerfile                  Development and CI image
├── Dockerfile.runtime          Production runtime image
└── compose.yaml                Local container workflow

scripts/
└── deployment/
    ├── verify_release.sh       Argo CD, digest, readiness, and restart validation
    ├── smoke_test.sh           ROS 2 node, topic, mission, and odometry validation
    └── collect_evidence.sh     Deployment evidence and checksums

security/                       Semgrep and security-policy configuration
docs/                           Backlog, verification, and project documentation
reports/                        Generated coverage, delivery, and deployment evidence
```

---

## End-to-end DevSecOps architecture

The central `Verified Runtime Release` workflow coordinates the complete release and staging deployment path.

```text
Developer push to main
        │
        ├──────────────────────────────┐
        ▼                              ▼
  ROS 2 CI Gate                 Security Gate
        │                              │
        └──────────────┬───────────────┘
                       │ both must pass
                       ▼
              Runtime image build
                       ▼
              Runtime validation
                       ▼
             Blocking Trivy gate
                       ▼
            Candidate image in GHCR
                       ▼
            SPDX + CycloneDX SBOMs
                       ▼
             Cosign keyless signing
                       ▼
        Provenance + SBOM attestations
                       ▼
       Signature and attestation checks
                       ▼
          Promotion to final GHCR tags
                       ▼
         Final-tag digest verification
                       ▼
        Resolve verified `main` digest
                       ▼
     Update `values-staging.yaml` in Git
                       ▼
          Helm lint and render checks
                       ▼
   Commit desired state with Actions bot
                       ▼
          Argo CD detects Git change
                       ▼
       K3s deploys immutable image digest
                       ▼
        Startup and readiness probes
                       ▼
         ROS 2 release and smoke tests
                       ▼
        Synced, Healthy staging release
```

Runtime delivery cannot begin unless both the CI gate and security gate succeed. Staging promotion cannot begin unless the runtime image has been built, scanned, signed, attested, verified, and promoted successfully.

---

## Continuous integration

The reusable ROS 2 CI workflow uses tiered validation.

### Pull-request tier

- Python linting and formatting with Ruff.
- C++ formatting with clang-format.
- Shell validation with ShellCheck.
- Robot configuration validation.
- ROS 2 workspace build.
- C++ unit tests with GoogleTest.
- Python unit tests with pytest.
- Python coverage-threshold enforcement.

### Main, scheduled, and release tier

- All pull-request checks.
- ROS 2 integration tests.
- Headless Gazebo simulation tests.
- Aggregated CI gate.
- Uploaded test results and coverage evidence.

CI jobs run inside the reusable image:

```text
ghcr.io/iheb-mrabet/robotek-1.2-ci:jazzy
```

This avoids reinstalling ROS 2 and the complete toolchain during every workflow job.

---

## Security workflow

The reusable security workflow runs in parallel with CI and contains:

- **Gitleaks:** full Git-history secret scanning.
- **Semgrep:** Python static application security testing.
- **cppcheck:** C++ static analysis.
- **Trivy filesystem scan:** dependency and repository misconfiguration scanning.
- **Trivy CI image scan:** vulnerability scanning of the current CI image candidate.
- **Security exception policy:** validation of owned and time-bounded exceptions.
- **Aggregated security gate:** blocks delivery when any required security job fails.

HIGH and CRITICAL vulnerabilities with available fixes are treated as blocking findings according to the configured policy.

---

## Verified runtime delivery

Phase 4 introduced a complete software supply-chain security flow.

### 1. Runtime image build

The production image is built from [`docker/Dockerfile.runtime`](docker/Dockerfile.runtime) using a multi-stage build. Build tools remain in the builder stage while the final runtime image contains only what is required to execute the robot software.

### 2. Runtime validation

Before publication, the workflow checks that:

- The image starts correctly.
- The ROS 2 environment is available.
- The expected robot packages are installed.
- The runtime image uses a non-root user.
- The packaged application is usable.

### 3. Pre-publication vulnerability gate

Trivy generates JSON and text reports and enforces a blocking runtime-image policy. A failing security gate prevents release progression.

### 4. Candidate image

The validated image is first pushed under a temporary candidate tag. Final branch, SHA, or semantic-version tags are not promoted yet.

### 5. Software Bill of Materials

Syft generates:

- SPDX JSON SBOM.
- CycloneDX JSON SBOM.
- A package-focused CycloneDX document suitable for GitHub attestation.

### 6. Keyless signing and attestations

Cosign signs the immutable runtime image digest using the GitHub Actions OIDC identity. The workflow also creates signed build-provenance and CycloneDX SBOM attestations.

### 7. Verification before promotion

The workflow verifies:

- The Cosign signature.
- The signer identity and OIDC issuer.
- The GitHub build-provenance attestation.
- The GitHub CycloneDX SBOM attestation.

Final tags are created only after these verifications succeed.

### 8. Evidence-backed release

The workflow produces and validates:

- Immutable and candidate image references.
- Published final tags.
- Runtime metadata.
- Trivy reports.
- SPDX and CycloneDX SBOMs.
- Cosign verification output.
- Provenance and SBOM attestation bundles.
- GitHub attestation-verification reports.
- SHA256 checksums for the complete evidence package.

The evidence is uploaded as a GitHub Actions artifact for later review and audit.

---

## Published runtime image

The released product is stored in GitHub Container Registry:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime
```

Supported final tags include:

- `main`
- `sha-<commit>`
- Semantic versions such as `v1.0.0`, `1.0`, and `latest` when a matching release tag is pushed.

Security-sensitive deployments use the immutable digest rather than a movable tag:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime@sha256:<digest>
```

See [`docs/runtime-image-verification.md`](docs/runtime-image-verification.md) for independent signature, provenance, SBOM, checksum, and runtime verification instructions.

---

## Automated GitOps staging deployment

Phase 5 connects verified runtime delivery to the K3s staging cluster without giving GitHub Actions direct Kubernetes credentials.

After the image-delivery job succeeds, the `promote-staging` job in [`release.yml`](.github/workflows/release.yml):

1. Resolves the digest currently referenced by the verified GHCR `main` image.
2. Validates that the value is a correctly formatted SHA-256 digest.
3. Updates `deploy/helm/robotek/values-staging.yaml` with that immutable digest.
4. Runs `helm lint`, `helm template`, and `git diff --check`.
5. Commits the desired-state change to `main` using `github-actions[bot]`.
6. Avoids a recursive release loop by ignoring digest-only promotion commits.
7. Lets Argo CD detect the Git revision and reconcile the Helm release into K3s.

The validated staging deployment reached:

```text
Argo CD sync: Synced
Argo CD health: Healthy
Deployment rollout: successful
Pod readiness: 1/1
Container restarts: 0
Release verification: passed
ROS 2 smoke test: passed
```

### Kubernetes controls

The staging workload includes:

- Non-root execution with UID and GID `1001`.
- Privilege escalation disabled.
- All Linux capabilities dropped.
- `RuntimeDefault` seccomp profile.
- Dedicated ServiceAccount without an automatically mounted API token.
- CPU and memory requests and limits.
- In-memory `/dev/shm` for Gazebo and ROS middleware.
- ROS-aware startup and readiness probes for `/mission/status` and `/odom`.
- `Recreate` deployment strategy to prevent simultaneous robot simulations.

### Git-driven rollback

Rollback was demonstrated by committing an invalid digest, observing `ErrImagePull` and `ImagePullBackOff`, and reverting the Git commit. Argo CD restored the last known-good desired state automatically.

Admission-time signature and attestation enforcement, plus policy-driven automatic rollback, remain future hardening opportunities.

---

## Verify the staging release

From a host configured to access the K3s cluster:

```bash
./scripts/deployment/verify_release.sh
./scripts/deployment/smoke_test.sh
./scripts/deployment/collect_evidence.sh
```

The verification scripts confirm:

- Argo CD synchronization and health.
- Deployed immutable image reference.
- Pod readiness and restart count.
- Expected ROS 2 nodes and topics.
- Mission-status publication.
- Odometry publication.
- Deployment logs, events, resource data, and evidence checksums.

---

## Local installation

Recommended local environment:

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Docker

Install project dependencies:

```bash
bash scripts/install_dependencies.sh
```

Or use the development container:

```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm mock-delivery-robot
```

---

## Build and test locally

```bash
bash scripts/build.sh
source install/setup.bash
bash scripts/lint.sh
bash scripts/unit_tests.sh
bash scripts/python_coverage.sh
bash scripts/integration_tests.sh
bash scripts/simulation_tests.sh
```

Convenience Make targets are also available:

```bash
make ci-pr
make integration-tests
make simulation-tests
make security-sast
make security-policy
```

---

## Run the simulation

```bash
source install/setup.bash
ros2 launch mock_robot_bringup full_simulation.launch.py gui:=false
```

Use `gui:=true` to open the Gazebo graphical interface.

---

## Execute a delivery mission

In another terminal:

```bash
source install/setup.bash
ros2 action send_goal \
  /execute_delivery \
  mock_robot_interfaces/action/ExecuteDelivery \
  "{target_x: 0.8, target_y: 0.0}"
```

Activate emergency stop:

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

## Clean the workspace

```bash
bash scripts/clean.sh
```

---

## Workflow responsibilities

| Workflow | Responsibility |
|---|---|
| `ci-image.yml` | Build, scan, and publish the reusable ROS 2 CI image |
| `ci.yml` | Lint, build, unit tests, integration tests, Gazebo tests, aggregated CI gate |
| `security.yml` | Secret scanning, SAST, vulnerability scanning, exception policy, aggregated security gate |
| `build-package.yml` | Runtime build, validation, scanning, SBOM, signing, attestations, verification, GHCR promotion |
| `release.yml` | Orchestrate CI, security, verified delivery, automatic staging digest promotion, and the final release gate |

---

## Documentation

- [`docs/backlog.md`](docs/backlog.md) — completed phases and remaining roadmap.
- [`docs/branch-protection.md`](docs/branch-protection.md) — recommended required checks and merge protection.
- [`docs/runtime-image-verification.md`](docs/runtime-image-verification.md) — independent verification of released runtime images.
- [`security/`](security/) — Semgrep and security-policy configuration.
- [`scripts/deployment/`](scripts/deployment/) — staging verification, smoke testing, and evidence collection.

---

## Next sprint: Phase 6

Phase 6 focuses on observability and runtime security:

- Add structured application and ROS 2 logs.
- Collect runtime and Kubernetes resource metrics.
- Build health and operational dashboards.
- Add alerts for node availability, topic activity, CPU, memory, and container health.
- Detect unexpected processes and runtime behavior.
- Monitor security-relevant container and Kubernetes events.
- Preserve incident-response and alert evidence.

---

## Final objective

The long-term objective is to deliver a reusable, production-ready DevSecOps platform for ROS 2 robot software that supports automated testing, security-by-default, verified software supply chains, automatic controlled GitOps deployment, runtime observability, rollback, and easy adoption across multiple robot repositories.
