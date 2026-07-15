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

# 🚧 Phase 2 – CI Workflow (ROS 2)

**Status:** 🚧 **Completed**

## ✅ Completed

### CI Infrastructure
- Build and publish a reusable ROS 2 CI Docker image to GitHub Container Registry (GHCR).
- Execute all CI jobs inside the published container (no ROS installation on every workflow run).

### Code Quality
- Ruff (Python linting)
- Ruff format check
- clang-format
- ShellCheck
- cppcheck

### Pull Request Fast Gate
- Lint validation
- Format validation
- Robot configuration validation

### Unit Testing
- `colcon build`
- GoogleTest (C++)
- pytest (Python)
- Python coverage threshold

### CI Features
- Upload test results and coverage reports as workflow artifacts.
- Tiered CI architecture:
  - **Pull Requests**
    - Fast Gate
    - Unit Tests
  - **Main / Nightly**
    - Integration Tests
    - Headless Gazebo Simulation Tests
- Script parity (`scripts/*.sh` only — no raw commands inside workflows).
- Least-privilege GitHub permissions.
- Concurrency cancellation.



---

# 🚧 Phase 3 – Security Workflow

**Status:** 🚧 **Completed**

## ✅ Completed

### Secret & Code Scanning
- Gitleaks (full Git history)
- Semgrep (Python SAST)
- cppcheck (C++ static analysis)

### Dependency & Container Security
- Trivy filesystem scan
- Trivy CI image scan

### Security Governance
- Security exception policy
- Aggregated Security Gate
- Non-root CI container (Trivy compliant)
- Upload security reports as workflow artifacts



---

# ⏳ Phase 4 – Delivery Image, SBOM & Supply Chain Security

**Status:** ⏳ **Not Started**

## Planned

### Runtime Image
- Create production runtime image (multi-stage Docker build).
- Separate CI image from runtime image.

### Image Quality
- Run Hadolint on Dockerfiles.
- Build/package workflow.
- Semantic version tagging.
- Generate `metadata.json`.
- Generate SHA256 checksums.

### Supply Chain Security
- Generate SBOM (Syft).
- Attach SBOM as build artifact.
- Trivy runtime image scan.
- Configure Trivy exceptions for ROS base image CVEs.
- Cosign keyless signing.
- Cosign verification workflow.
- Publish signed runtime image to GHCR.

---

# ⏳ Phase 5 – Staging Deployment & Rollback

**Status:** ⏳ **Not Started**

## Planned

### Deployment
- Create staging environment.
- Deploy approved runtime image.
- Headless ROS bring-up.

### Validation
- Health checks.
- Smoke tests.

### Continuous Deployment
- CD workflow (`workflow_run`).
- Automatic rollback on failure.
- Store deployment logs.
- Demonstrate rollback scenario.
- Release workflow with evidence package.

---

# ⏳ Phase 6 – Generic Template & Final Demonstration

**Status:** ⏳ **Not Started**

## Planned

### Template Generalization
- Extract reusable workflows (`workflow_call`).
- Parameterize:
  - ROS distribution
  - Package names
  - Coverage thresholds
  - Security thresholds
  - Configuration paths
- Generic Docker image configuration.

### Documentation
- Template usage guide.
- Migration guide.
- Adoption guide for real robot repositories.

### Final Demonstration
- Complete green pipeline.
- Multiple blocked scenarios.
- Final project handover.

---

# 📊 Overall Progress

| Phase | Progress | Status |
|--------|:--------:|--------|
| Phase 1 – Mock Robot Architecture | **100%** | ✅ Completed |
| Phase 2 – CI Workflow | **90%** | 🚧 In Progress |
| Phase 3 – Security Workflow | **90%** | 🚧 In Progress |
| Phase 4 – Delivery Image & Supply Chain Security | **0%** | ⏳ Not Started |
| Phase 5 – Staging Deployment & Rollback | **0%** | ⏳ Not Started |
| Phase 6 – Generic Template & Final Demonstration | **0%** | ⏳ Not Started |

---

## 🎯 Final Objective

Deliver a **production-ready, reusable DevSecOps template for ROS 2 robot software** that provides:

- Containerized CI/CD
- Tiered automated testing
- Security-by-default
- Supply-chain security (SBOM & image signing)
- Automated staging deployment
- Easy adoption by real-world robotics repositories with minimal customization