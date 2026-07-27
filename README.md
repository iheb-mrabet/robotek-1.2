# 🤖 Robotek 1.2

[![ROS 2 CI](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci.yml)
[![ROS 2 Security](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/security.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/security.yml)
[![Verified Runtime Release](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/release.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/release.yml)
[![Build CI Image](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci-image.yml/badge.svg)](https://github.com/iheb-mrabet/robotek-1.2/actions/workflows/ci-image.yml)
![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros)
![Ubuntu 24.04](https://img.shields.io/badge/Ubuntu-24.04-E95420?logo=ubuntu)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![C++17](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=cplusplus)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)

> A ROS 2 DevSecOps reference project demonstrating automated testing, security gates, verified container delivery, SBOM generation, keyless image signing, provenance attestations, and evidence-backed releases.

Robotek 1.2 is a compact but realistic mock indoor delivery robot built for learning and demonstrating a professional robotics DevSecOps lifecycle. The repository combines ROS 2 application development with CI, security automation, container hardening, software supply-chain protection, and verified runtime image delivery.

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

The project is intentionally small enough to understand end to end, while still including the packages, tests, workflows, security controls, and release logic expected from a professional robot software repository.

---

## Current project status

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Mock robot architecture | ✅ Completed |
| Phase 2 | ROS 2 CI workflow | ✅ Completed |
| Phase 3 | Security workflow | ✅ Completed |
| Phase 4 | Verified runtime delivery and supply-chain security | ✅ Completed |
| Phase 5 | Staging deployment, validation, and rollback | ⏳ Next sprint |
| Phase 6 | Observability and runtime security | ⏳ Planned |
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

---

## Robot architecture

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
└── release.yml                 Central verified release orchestrator

docker/
├── Dockerfile                  Development and CI image
├── Dockerfile.runtime          Production runtime image
└── compose.yaml                Local container workflow

scripts/                        Local and CI execution scripts
security/                       Semgrep and security-policy configuration
docs/                           Backlog, verification, and project documentation
reports/                        Generated coverage and delivery evidence
```

---

## DevSecOps architecture

The central `Verified Runtime Release` workflow coordinates the complete release path.

```text
                         ┌──────────────────────┐
Developer push or tag ──▶│ Verified Runtime     │
                         │ Release orchestrator │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           ┌────────────────┐              ┌─────────────────┐
           │ ROS 2 CI Gate  │              │ Security Gate   │
           └───────┬────────┘              └────────┬────────┘
                   │                                │
                   └───────────────┬────────────────┘
                                   │ both must pass
                                   ▼
                      ┌─────────────────────────┐
                      │ Runtime image delivery  │
                      └────────────┬────────────┘
                                   ▼
                          Local runtime build
                                   ▼
                          Runtime validation
                                   ▼
                       Blocking Trivy image gate
                                   ▼
                       Temporary candidate image
                                   ▼
                         SPDX + CycloneDX SBOMs
                                   ▼
                         Cosign keyless signature
                                   ▼
                    Provenance + SBOM attestations
                                   ▼
                  Signature and attestation verification
                                   ▼
                     Promotion to final GHCR tags
                                   ▼
                     Digest and checksum verification
                                   ▼
                         Final release evidence
```

The runtime delivery job cannot begin unless both the CI gate and security gate return success.

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

The SBOM records the packages, libraries, versions, and dependencies contained in the runtime image.

### 6. Keyless signing

Cosign signs the immutable runtime image digest using the GitHub Actions OIDC identity. No long-lived private signing key is stored in the repository.

### 7. GitHub attestations

The workflow creates:

- A signed build-provenance attestation.
- A signed CycloneDX SBOM attestation.

The provenance connects the image digest to the repository, workflow, commit, and build process that produced it.

### 8. Verification before promotion

The workflow verifies:

- The Cosign signature.
- The signer identity and OIDC issuer.
- The GitHub build-provenance attestation.
- The GitHub CycloneDX SBOM attestation.

Final tags are created only after these verifications succeed.

### 9. Evidence-backed release

The workflow produces and validates:

- Immutable image reference.
- Candidate image reference.
- Published final tags.
- Runtime metadata.
- Trivy reports.
- SPDX and CycloneDX SBOMs.
- Cosign verification output.
- Provenance attestation bundle.
- SBOM attestation bundle.
- GitHub attestation-verification reports.
- SHA256 checksums for the complete evidence package.

The evidence is uploaded as a GitHub Actions artifact for later review and audit.

---

## Published runtime image

The released product is the runtime container image stored in GitHub Container Registry:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime
```

Supported final tags include:

- `main`
- `sha-<commit>`
- Semantic versions such as `v1.0.0`, `1.0`, and `latest` when a matching release tag is pushed.

For security-sensitive use, deploy the immutable digest rather than a movable tag:

```text
ghcr.io/iheb-mrabet/robotek-1.2-runtime@sha256:<digest>
```

See [`docs/runtime-image-verification.md`](docs/runtime-image-verification.md) for independent signature, provenance, SBOM, checksum, and runtime verification instructions.

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

## Build

```bash
bash scripts/build.sh
```

Then source the workspace:

```bash
source install/setup.bash
```

---

## Test locally

Run lint and formatting checks:

```bash
bash scripts/lint.sh
```

Run unit tests and coverage:

```bash
bash scripts/unit_tests.sh
bash scripts/python_coverage.sh
```

Run ROS 2 integration tests:

```bash
bash scripts/integration_tests.sh
```

Run headless Gazebo tests:

```bash
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
| `release.yml` | Orchestrate CI, security, delivery, and the final release gate |

---

## Documentation

- [`docs/backlog.md`](docs/backlog.md) — completed phases and remaining roadmap.
- [`docs/branch-protection.md`](docs/branch-protection.md) — recommended required checks and merge protection.
- [`docs/runtime-image-verification.md`](docs/runtime-image-verification.md) — independent verification of released runtime images.
- [`security/`](security/) — Semgrep and security-policy configuration.
- [`scripts/`](scripts/) — reproducible local and CI commands.

---

## Next sprint: Phase 5

The next phase focuses on controlled staging deployment and rollback:

- Deploy the verified image by immutable digest.
- Perform headless ROS 2 bring-up in staging.
- Add health checks and deployment smoke tests.
- Preserve deployment logs and evidence.
- Prevent unsigned or unverified image deployment.
- Roll back automatically to the last known-good digest when validation fails.

---

## Final objective

The long-term objective is to deliver a reusable, production-ready DevSecOps platform for ROS 2 robot software that supports automated testing, security-by-default, verified software supply chains, controlled deployment, runtime observability, rollback, and easy adoption across multiple robot repositories.
