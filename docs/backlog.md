# 📋 Project Backlog

---

# ✅ Phase 1 – Mock Robot Architecture

**Status:** ✅ **Completed**

### Objectives
- Design a realistic ROS 2 mock delivery robot architecture.
- Create a ROS 2 (`colcon`) workspace.
- Implement C++ and Python robot packages.
- Add launch files and robot configuration.
- Add unit, integration, and simulation test skeletons.
- Create a reusable project structure for CI/CD validation.

---

# ✅ Phase 2 – CI Workflow (ROS 2)

**Status:** ✅ **Completed**

## Completed

### CI Infrastructure
- Build and publish a reusable ROS 2 CI Docker image to GitHub Container Registry (GHCR).
- Execute all CI jobs inside the published container, avoiding repeated ROS installation on every workflow run.

### Code Quality
- Ruff for Python linting.
- Ruff format checks.
- clang-format for C++ formatting.
- ShellCheck for shell scripts.
- cppcheck for C++ static analysis.

### Pull Request Fast Gate
- Lint validation.
- Format validation.
- Robot configuration validation.

### Unit Testing
- ROS 2 workspace build with `colcon build`.
- GoogleTest for C++.
- pytest for Python.
- Enforced Python coverage threshold.

### Integration and Simulation Testing
- ROS 2 integration test tier.
- Headless Gazebo simulation test tier.
- Main-branch and scheduled execution for the complete test suite.

### CI Features
- Upload test results and coverage reports as workflow artifacts.
- Tiered CI architecture:
  - **Pull requests:** fast gate and unit tests.
  - **Main / scheduled runs:** integration and headless Gazebo tests.
- Script parity through `scripts/*.sh` rather than duplicated workflow commands.
- Least-privilege GitHub permissions.
- Concurrency cancellation.
- Aggregated CI gate.

---

# ✅ Phase 3 – Security Workflow

**Status:** ✅ **Completed**

## Completed

### Secret and Code Scanning
- Gitleaks full-history secret scan.
- Semgrep Python SAST.
- cppcheck C++ static analysis.

### Dependency and Container Security
- Trivy repository filesystem scan.
- Trivy CI image vulnerability scan.
- Blocking policy for HIGH and CRITICAL vulnerabilities with available fixes.

### Security Governance
- Security exception policy.
- Aggregated security gate.
- Non-root CI container.
- Upload security reports as workflow artifacts.
- Reusable security workflow through `workflow_call`.

---

# ✅ Phase 4 – Verified Runtime Delivery and Supply Chain Security

**Status:** ✅ **Completed**

## Completed

### Central Release Orchestration
- Created the `Verified Runtime Release` workflow.
- Converted CI, security, and runtime delivery workflows into reusable workflows.
- Run CI and security gates in parallel.
- Block runtime delivery unless both CI and security complete successfully.
- Added a final release gate that fails unless every required stage succeeds.

### Production Runtime Image
- Created a multi-stage runtime Docker image.
- Separated the reusable CI image from the production runtime image.
- Validated the runtime image before registry publication.
- Confirmed ROS 2 package availability and non-root execution.
- Added Hadolint validation for Dockerfiles.

### Secure Candidate and Promotion Flow
- Build the runtime image locally first.
- Scan the image before registry upload.
- Block candidate publication when the runtime vulnerability policy fails.
- Push a temporary candidate image to GHCR.
- Promote the verified digest to final branch, SHA, and semantic-version tags only after all signature and attestation checks pass.
- Verify that every final tag resolves to the expected immutable digest.

### Runtime Vulnerability Security
- Generate Trivy JSON and text reports for the runtime image.
- Enforce a blocking HIGH and CRITICAL vulnerability gate before release.
- Upload pre-publication scan evidence.

### Software Bill of Materials
- Generate package-focused SPDX JSON SBOM.
- Generate package-focused CycloneDX JSON SBOM.
- Exclude unnecessary file components to keep the attestation SBOM within GitHub's supported size limit.
- Validate the CycloneDX format and component count before attestation.

### Image Signing and Attestations
- Sign the immutable runtime image digest using Cosign keyless signing.
- Generate GitHub build-provenance attestation with `actions/attest@v4`.
- Generate GitHub CycloneDX SBOM attestation.
- Push signatures and attestations alongside the OCI image in GHCR.

### Verification and Release Evidence
- Verify the Cosign signature against the GitHub Actions OIDC identity.
- Verify GitHub provenance attestation.
- Verify GitHub CycloneDX SBOM attestation.
- Generate release metadata and immutable image reference evidence.
- Generate and verify SHA256 checksums for the complete evidence set.
- Upload the final signed runtime delivery evidence artifact.
- Upload diagnostic evidence automatically when delivery fails.

### Published Runtime Image
- Publish the verified runtime image to GitHub Container Registry:
  - `ghcr.io/iheb-mrabet/robotek-1.2-runtime`
- Support final tags for:
  - `main`
  - commit SHA
  - semantic versions such as `v1.0.0`

---

# ✅ Phase 5 – Staging Deployment, Runtime Validation and Rollback

**Status:** ✅ **Completed**

## Completed

### Staging Platform
- Provisioned an Ubuntu 24.04 staging host on AWS EC2.
- Installed a pinned K3s Kubernetes cluster with secrets encryption enabled.
- Disabled unnecessary default K3s ingress and load-balancer components.
- Installed Helm and deployed Argo CD into the cluster.
- Kept the Argo CD API private and accessed it through local port forwarding and an SSH tunnel.

### Helm Deployment Package
- Created a reusable Helm application chart under `deploy/helm/robotek`.
- Added a dedicated staging values file.
- Deployed one complete ROS 2 and Gazebo simulation per Pod.
- Used a `Recreate` deployment strategy to prevent duplicate robot simulations during updates.
- Added a dedicated ServiceAccount without an automatically mounted Kubernetes API token.
- Configured CPU and memory requests and limits.
- Added an in-memory `/dev/shm` volume for Gazebo and ROS middleware.

### Kubernetes Security Controls
- Enforced non-root execution with UID and GID `1001`.
- Disabled privilege escalation and privileged mode.
- Dropped all Linux capabilities.
- Enabled the `RuntimeDefault` seccomp profile.
- Scanned the rendered Kubernetes manifests with Trivy.
- Confirmed zero HIGH or CRITICAL Kubernetes misconfiguration findings.

### Runtime Validation
- Added ROS-aware startup and readiness probes.
- Validated `/mission/status` to confirm the mission layer is operational.
- Validated `/odom` with best-effort QoS to confirm Gazebo and the ROS–Gazebo bridge are operational.
- Confirmed expected ROS 2 nodes and topics inside the running Pod.
- Confirmed mission status and odometry messages are published.
- Verified successful deployment with zero container restarts.

### GitOps Continuous Deployment
- Added an Argo CD `Application` manifest under `deploy/argocd`.
- Configured Argo CD to watch the personal repository `main` branch.
- Enabled automated synchronization, pruning, self-healing, retry, and namespace creation.
- Migrated deployment ownership from manual Helm commands to Argo CD.
- Pinned staging to an immutable digest produced by the verified runtime release.
- Added the `promote-staging` job to `.github/workflows/release.yml`.
- Run staging promotion only after CI, security, image signing, attestations, and final digest verification succeed.
- Resolve the verified `ghcr.io/iheb-mrabet/robotek-1.2-runtime:main` digest after runtime delivery.
- Update `deploy/helm/robotek/values-staging.yaml` automatically with the verified immutable digest.
- Validate the promoted configuration with `helm lint`, `helm template`, and `git diff --check` before committing it.
- Commit the desired-state update to `main` with `github-actions[bot]`.
- Ignore digest-only promotion commits in the release trigger to prevent a recursive pipeline loop.
- Let Argo CD detect the Git commit and reconcile the new image into K3s.
- Confirm the automated promotion commit, Argo CD revision, deployed Pod image, and GHCR digest match.
- Confirm the final Argo CD application state is `Synced` and `Healthy`.

### Rollback Demonstration
- Introduced a deliberately invalid image digest through Git.
- Observed the expected `ErrImagePull` and `ImagePullBackOff` failure.
- Restored the last known-good digest with `git revert`.
- Confirmed Argo CD automatically synchronized the reverted desired state.
- Verified the restored Pod became ready with zero restarts.

### Verification and Evidence Tooling
- Added `scripts/deployment/verify_release.sh` for Argo CD, digest, readiness, and restart validation.
- Added `scripts/deployment/smoke_test.sh` for ROS 2 node, topic, mission-status, and odometry validation.
- Added `scripts/deployment/collect_evidence.sh` for deployment status, logs, events, resource usage, and checksums.
- Validated the automatically promoted deployment end to end.
- Confirmed the release verification and ROS 2 smoke test pass against the deployed immutable image.
- Generated local deployment evidence for the completed staging run.

### Follow-up Hardening
- Admission-time signature and attestation enforcement remains a future enhancement.
- Phase 5 rollback is Git-driven and demonstrated through `git revert`; policy-driven automatic rollback can be added later.

---

# 🚧 Phase 6 – Observability and Runtime Security

**Status:** 🚧 **In Progress**

## Design completed

- Added `docs/phase6-design.md` as the implementation blueprint.
- Defined the Prometheus, Grafana, Alertmanager, kube-state-metrics, and node-exporter architecture.
- Defined Kubernetes, K3s, and Argo CD metrics to collect.
- Defined a ROS 2 Prometheus exporter for mission status, odometry freshness, node/topic availability, emergency-stop state, mission state, and startup duration.
- Defined Git-provisioned Grafana dashboards and Prometheus alert rules.
- Selected Falco for initial runtime detection.
- Defined scheduled Trivy image and rendered-manifest scanning.
- Designed automated post-deployment validation using the existing verification, smoke-test, and evidence scripts.
- Deferred Terraform infrastructure automation until after Phase 6.

## Current implementation task

### Observability foundation
- Capture the existing K3s node, Pod, storage, CPU, memory, and disk baseline.
- Create a pinned `kube-prometheus-stack` Helm dependency.
- Configure Prometheus, Grafana, Alertmanager, kube-state-metrics, and node-exporter for the single-node staging environment.
- Keep all monitoring services private and access them through port forwarding.
- Deploy the observability stack through a dedicated Argo CD Application.
- Confirm all monitoring targets are available without destabilizing Robotek.

## Planned next

### Kubernetes and GitOps monitoring
- Monitor Pod readiness, restart count, Deployment availability, Pending Pods, image-pull failures, CPU, memory, node readiness, and Argo CD synchronization/health.

### Robotek-specific monitoring
- Add a ROS 2 Prometheus exporter.
- Monitor `/mission/status`, `/odom`, expected nodes/topics, emergency-stop state, mission state, and simulation startup duration.

### Dashboards and alerts
- Provision Grafana dashboards from Git.
- Add and deliberately test platform, GitOps, and Robotek alert rules.

### Runtime security
- Deploy Falco and Robotek-specific detection rules.
- Add scheduled Trivy runtime-image and rendered-manifest scans.

### Automated post-deployment validation
- Trigger verification after staging digest promotion.
- Run `verify_release.sh`, `smoke_test.sh`, and `collect_evidence.sh`.
- Upload timestamped evidence as a workflow artifact.

---

# ⏳ Phase 7 – Generic Multi-Robot Template and Final Demonstration

**Status:** ⏳ **Planned**

## Planned

### Template Generalization
- Extract reusable workflows and shared delivery logic.
- Parameterize:
  - ROS distribution.
  - Package names.
  - Coverage thresholds.
  - Security thresholds.
  - Configuration paths.
  - Runtime image names.
  - Deployment targets.
- Generalize CI and runtime Docker configuration.

### Multi-Robot Adoption
- Apply the reusable platform to delivery, reception, security, and robot-arm repositories.
- Keep robot-specific tests and behavior while sharing the same DevSecOps controls.

### Documentation
- Template usage guide.
- Migration guide.
- Adoption guide for real robot repositories.
- Operations and troubleshooting guide.

### Final Demonstration
- Complete green end-to-end pipeline.
- Demonstrate blocked CI, security, release, deployment, and runtime scenarios.
- Demonstrate successful rollback.
- Complete final project handover.

---

# 📊 Overall Progress

| Phase | Progress | Status |
|--------|:--------:|--------|
| Phase 1 – Mock Robot Architecture | **100%** | ✅ Completed |
| Phase 2 – CI Workflow | **100%** | ✅ Completed |
| Phase 3 – Security Workflow | **100%** | ✅ Completed |
| Phase 4 – Verified Runtime Delivery and Supply Chain Security | **100%** | ✅ Completed |
| Phase 5 – Staging Deployment, Runtime Validation and Rollback | **100%** | ✅ Completed |
| Phase 6 – Observability and Runtime Security | **5%** | 🚧 In Progress |
| Phase 7 – Generic Multi-Robot Template and Final Demonstration | **0%** | ⏳ Planned |

---

## 🎯 Final Objective

Deliver a **production-ready, reusable DevSecOps platform for ROS 2 robot software** that provides:

- Containerized CI and delivery.
- Tiered automated testing.
- Security-by-default.
- Runtime image vulnerability gates.
- SBOM generation and verification.
- Keyless image signing.
- Build provenance and SBOM attestations.
- Immutable and evidence-backed releases.
- Automated GitOps staging deployment and Git-driven rollback.
- Runtime observability and security monitoring.
- Easy adoption by multiple real-world robot repositories with minimal customization.
