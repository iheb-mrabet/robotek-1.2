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

# ⏳ Phase 5 – Staging Deployment, Runtime Validation and Rollback

**Status:** ⏳ **Not Started**

## Planned

### Staging Environment
- Define a reproducible staging environment for the verified runtime image.
- Deploy only an immutable, signed, and attested image digest.
- Add controlled ROS 2 headless bring-up.

### Deployment Validation
- Add container and ROS 2 health checks.
- Add deployment smoke tests.
- Confirm required nodes, topics, services, and parameters after deployment.
- Store deployment logs and validation evidence.

### Continuous Deployment
- Trigger staging deployment only after a successful verified runtime release.
- Add deployment concurrency protection.
- Track deployed image digest and release metadata.
- Prevent deployment of unsigned or unverified images.

### Rollback
- Automatically roll back when health checks or smoke tests fail.
- Preserve the last known-good runtime digest.
- Demonstrate and document a controlled rollback scenario.
- Produce deployment and rollback evidence artifacts.

---

# ⏳ Phase 6 – Observability and Runtime Security

**Status:** ⏳ **Not Started**

## Planned

### Observability
- Add structured application and ROS 2 logs.
- Add runtime metrics and resource monitoring.
- Add health dashboards and alerting.
- Track node availability, topic activity, CPU, memory, and container health.

### Runtime Security
- Detect unexpected processes or runtime behavior.
- Monitor container events and security-relevant failures.
- Define alerting and incident-response evidence.

---

# ⏳ Phase 7 – Generic Multi-Robot Template and Final Demonstration

**Status:** ⏳ **Not Started**

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
| Phase 5 – Staging Deployment, Runtime Validation and Rollback | **0%** | ⏳ Not Started |
| Phase 6 – Observability and Runtime Security | **0%** | ⏳ Not Started |
| Phase 7 – Generic Multi-Robot Template and Final Demonstration | **0%** | ⏳ Not Started |

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
- Automated staging deployment and rollback.
- Runtime observability and security monitoring.
- Easy adoption by multiple real-world robot repositories with minimal customization.
