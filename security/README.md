# Robotek 1.2

A containerized **DevSecOps pipeline for ROS 2 robotic software**, validated using a mock autonomous delivery robot built with ROS 2 Jazzy, C++, Python, colcon and Gazebo.

[GitHub Repository](https://github.com/iheb-mrabet/robotek-1.2)

---

## Project Overview

The project provides:

- A realistic ROS 2 mock delivery robot.
- C++ and Python robot packages.
- Unit, integration and Gazebo simulation tests.
- A reusable ROS 2 CI Docker image.
- Automated CI and security workflows.
- Configuration safety validation.
- Test, coverage and security reports.

The mock robot is used to validate the pipeline before adapting it to real robot repositories.

---

## Repository Structure

```text
robotek-1.2/
├── .github/workflows/       GitHub Actions workflows
├── docker/                  ROS 2 CI Docker image
├── docs/                    Architecture decisions and CI documentation
├── scripts/                 Commands used locally and in GitHub Actions
├── security/                Security rules and exception policy
├── src/                     ROS 2 robot software and automated tests
├── Makefile                 Shortcuts for local CI commands
├── pyproject.toml           Python, Ruff, pytest and coverage configuration
└── README.md                Project documentation
```

### Main folders

| Folder | Purpose |
|---|---|
| `.github/workflows/` | Contains the CI image, robot CI and security pipelines. |
| `docker/` | Defines the reusable ROS 2 Jazzy CI environment. |
| `scripts/` | Contains build, lint, test, simulation and security commands. |
| `security/` | Contains Semgrep rules and temporary security exceptions. |
| `docs/` | Contains architecture decisions, branch protection and demo guides. |
| `src/` | Contains the mock robot source code and automated tests. |

---

## ROS 2 Packages

```text
src/
├── mock_robot_interfaces/
├── mock_robot_control/
├── mock_robot_behavior/
├── mock_robot_description/
├── mock_robot_gazebo/
├── mock_robot_bringup/
└── mock_robot_system_tests/
```

| Package | Purpose |
|---|---|
| `mock_robot_interfaces` | Custom ROS messages, services and actions. |
| `mock_robot_control` | C++ control, velocity limiting and emergency-stop logic. |
| `mock_robot_behavior` | Python mission management and state-machine logic. |
| `mock_robot_description` | Robot URDF/Xacro model. |
| `mock_robot_gazebo` | Warehouse world and Gazebo simulation configuration. |
| `mock_robot_bringup` | Launch files and robot YAML configuration. |
| `mock_robot_system_tests` | Integration and simulation autotests. |

---

## Testing Strategy

### Unit Tests

Unit tests validate individual functions and classes.

- **GoogleTest** for C++ control logic.
- **pytest** for Python mission behavior.
- **pytest-cov** for Python coverage.

### Integration Tests

Integration tests verify that ROS nodes work together correctly through:

- Topics
- Services
- Actions
- Mission state updates
- Emergency-stop behavior

### Simulation Tests

Simulation tests launch the complete robot in headless Gazebo and verify:

- Robot startup
- Required ROS topics
- Movement behavior
- Delivery missions
- Emergency-stop scenarios

---

## GitHub Actions Workflows

### 1. CI Image — `ci-image.yml`

Builds the reusable ROS 2 CI image and publishes it to GitHub Container Registry:

```text
ghcr.io/iheb-mrabet/robotek-1.2-ci:jazzy
```

The image contains ROS 2 Jazzy, Gazebo, colcon, test tools, linters and security scanners.

This prevents ROS and system dependencies from being reinstalled during every workflow run.

---

### 2. ROS 2 CI — `ci.yml`

Validates the robot software.

#### On Pull Requests

```text
Fast Gate
    ↓
Build and Unit Tests
    ↓
Python Coverage
    ↓
Final CI Gate
```

The Fast Gate runs:

```text
scripts/lint.sh
scripts/validate_config.sh
```

It checks:

- Python linting and formatting
- C++ formatting
- Bash scripts
- C++ static analysis
- Robot safety configuration

The Unit Test job runs:

```text
scripts/build.sh
scripts/unit_tests.sh
scripts/python_coverage.sh
```

It performs:

- `colcon build`
- C++ GoogleTests
- Python pytest tests
- Coverage validation
- Test artifact generation

#### On Main or Nightly

The pipeline additionally runs:

```text
scripts/integration_tests.sh
scripts/simulation_tests.sh
```

These validate ROS communication and the complete headless Gazebo simulation.

---

### 3. Security — `security.yml`

Runs security checks in parallel:

- **Gitleaks** — detects committed secrets.
- **Semgrep** — analyzes Python security issues.
- **cppcheck** — analyzes C++ code.
- **Trivy filesystem scan** — scans repository files and Docker configuration.
- **Trivy image scan** — scans Ubuntu, ROS and Python packages in the CI image.
- **Exception policy** — validates documented and expiring security exceptions.

The results are combined into one:

```text
Aggregated Security Gate
```

A failed required security check can block a pull request.

---

## Pipeline Logic

```text
Developer opens Pull Request
            │
            ▼
        Fast Gate
            │
            ▼
    Build and Unit Tests
            │
            ▼
       Security Gate
            │
            ▼
       Merge to main
            │
            ▼
     Integration Tests
            │
            ▼
  Headless Gazebo Tests
```

Fast and deterministic checks run before merge. More expensive integration and simulation tests run after merge or during scheduled executions.

---

## Script-First CI

GitHub Actions calls scripts from `scripts/` instead of placing complex commands directly inside YAML.

Examples:

```text
scripts/lint.sh
scripts/build.sh
scripts/unit_tests.sh
scripts/integration_tests.sh
scripts/simulation_tests.sh
scripts/security_sast.sh
scripts/ci_gate.sh
scripts/security_gate.sh
```

This keeps local execution and GitHub Actions consistent.

---

## Local Commands

Run the pull-request checks:

```bash
make ci-pr
```

Run the full post-merge test suite:

```bash
make ci-post-merge
```

Run local security checks:

```bash
make security-local
```

Clean generated ROS files:

```bash
make clean
```

---

## Required Pull Request Checks

The recommended required checks for `main` are:

```text
Fast Gate
Unit Tests
Aggregated Security Gate
```

Integration and Gazebo tests remain post-merge and nightly checks because they are slower and more environment-dependent.

---

## Future Work

- C++ coverage with gcovr/lcov.
- Minimal runtime robot image.
- SBOM generation.
- Trivy runtime-image scanning.
- Cosign image signing.
- Staging deployment and automated rollback.
- Reusable workflows for other robot repositories.

---

## Reusing the Pipeline

For a real robot repository, keep:

```text
.github/workflows/
docker/
scripts/
security/
Makefile
.clang-format
```

Replace the mock packages, configuration, tests and simulation assets with those of the real robot.

The pipeline structure remains the same, while package names, dependency files, launch files, test commands and safety rules are adapted to the target robot.