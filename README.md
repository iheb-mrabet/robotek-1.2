# Mock Delivery Robot

A compact ROS 2 Jazzy workspace for a simulated indoor delivery robot. It is meant to be small enough for CI/CD demonstrations while still looking like a realistic robot repository.

The robot is a differential-drive platform that spawns in Gazebo Harmonic, publishes odometry and LiDAR, accepts a delivery destination, moves toward it with a simple waypoint controller, applies velocity and obstacle safety limits, supports emergency stop, and publishes mission state.

## Architecture

```text
src/
  mock_robot_interfaces/      custom message, service, and action types
  mock_robot_description/     Xacro robot model and robot_state_publisher launch
  mock_robot_gazebo/          warehouse world, bridge config, simulation launch
  mock_robot_control/         C++17 limiter, safety, and waypoint controllers
  mock_robot_behavior/        Python mission manager and state machine
  mock_robot_bringup/         full-system launch and YAML configuration
  mock_robot_system_tests/    launch, integration, and simulation tests
scripts/                     local developer commands
docker/                      Jazzy development/test container
```

## Install

Use Ubuntu 24.04 with ROS 2 Jazzy and Gazebo Harmonic. Then run:

```bash
bash scripts/install_dependencies.sh
```

The Docker image includes the expected ROS, Gazebo, colcon, pytest, GoogleTest, clang-format, and cppcheck tooling:

```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm mock-delivery-robot
```

## Build

```bash
bash scripts/build.sh
```

## Test

Fast unit tests:

```bash
bash scripts/unit_tests.sh
```

ROS integration tests without Gazebo:

```bash
bash scripts/integration_tests.sh
```

Headless Gazebo smoke and mission tests:

```bash
bash scripts/simulation_tests.sh
```

Lint checks:

```bash
bash scripts/lint.sh
```

## Run Simulation

```bash
source install/setup.bash
ros2 launch mock_robot_bringup full_simulation.launch.py gui:=false
```

Use `gui:=true` to open the Gazebo interface.

## Run A Delivery Mission

In another terminal:

```bash
source install/setup.bash
ros2 action send_goal /execute_delivery mock_robot_interfaces/action/ExecuteDelivery "{target_x: 0.8, target_y: 0.0}"
```

Emergency stop:

```bash
ros2 service call /mission/emergency_stop mock_robot_interfaces/srv/EmergencyStop "{activate: true}"
```

Release emergency stop:

```bash
ros2 service call /mission/emergency_stop mock_robot_interfaces/srv/EmergencyStop "{activate: false}"
```

## Clean

```bash
bash scripts/clean.sh
```

## CI and security

The repository uses a published ROS 2 Jazzy dev/CI image from GHCR so pull-request jobs do not reinstall ROS on every run.

Python coverage is enforced on the pure mission state-machine and destination-validation core; the ROS node adapter is exercised by the integration tier.

Local PR-equivalent checks inside that image:

```bash
make ci-pr
```

Post-merge test tiers:

```bash
make integration-tests
make simulation-tests
```

Local SAST and exception-policy checks:

```bash
make security-sast
make security-policy
```

Workflow responsibilities:

- `ci-image.yml`: builds and publishes `ghcr.io/<owner>/<repo>-ci:jazzy`.
- `ci.yml`: fast gate and unit tests on PR; integration and Gazebo tiers on `main`, nightly, or manual runs.
- `security.yml`: Gitleaks, Semgrep/cppcheck, Trivy filesystem/image scans, and one aggregated security gate.

Before opening the first PR, run **Build CI image** manually once and ensure the GHCR package is accessible to repository workflows. See `docs/branch-protection.md` for required checks.
