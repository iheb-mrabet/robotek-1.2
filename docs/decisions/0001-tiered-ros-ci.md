# ADR 0001: Tiered ROS 2 CI execution

- Status: Accepted
- Date: 2026-07-11

## Context

The repository contains cheap deterministic checks, ROS graph integration tests, and Gazebo simulation tests with a 180-second process timeout. Running every tier on every pull request makes feedback slow and increases flaky failures that are unrelated to the change under review.

## Decision

Use four tiers:

1. Fast gate: Ruff, clang-format, ShellCheck, cppcheck, and safety-config validation.
2. Unit gate: full `colcon build`, C++ gtests, Python pytest, and Python coverage.
3. Integration: ROS graph tests without Gazebo, after merge to `main`, nightly, or manually.
4. Simulation: headless Gazebo tests, after integration on `main`, nightly, or manually.

Every shell command executed by the CI workflow calls a version-controlled script under `scripts/`. The same scripts are used locally through the Makefile.

## Consequences

Pull requests receive fast deterministic feedback. Heavy system tests still protect `main` and run nightly. A defect visible only in simulation can reach `main` before the post-merge tier runs, so rollback or a follow-up fix may be required; Phase 5 will add deployment rollback controls.
