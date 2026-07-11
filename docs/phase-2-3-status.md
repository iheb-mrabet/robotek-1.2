# Phase 2 and Phase 3 implementation status

## Phase 2: implemented

- Dev/CI image built from `docker/Dockerfile` and published to GHCR by `ci-image.yml`.
- ROS CI jobs run inside the published image; they do not install ROS per run.
- Fast PR gate: Ruff, Ruff format check, clang-format check, ShellCheck, cppcheck, and robot safety-config validation.
- Unit PR gate: complete colcon build, C++ gtests, Python pytest, test-result artifacts, and an 85% Python coverage threshold.
- Current pure behavior-core coverage: 100% branch coverage.
- Integration and 180-second headless Gazebo tiers run only after merge to `main`, nightly, or manually.
- All workflow `run` steps call `scripts/*.sh`.
- Read-only workflow permissions, GHCR read access where required, and concurrency cancellation.
- ADR and branch-protection/demo runbooks included.

## Phase 2: intentionally deferred

- C++ gcovr/lcov reporting is a stretch item. The image contains gcovr/lcov so it can be added without redesigning the image.
- GitHub branch rules and screenshots require manual configuration in the real repository.

## Phase 3: implemented

- Gitleaks on pull requests with full Git history.
- Semgrep for Python and cppcheck for C++.
- Trivy filesystem scan for repository manifests/configuration.
- Trivy image scan for resolved Ubuntu and ROS Debian packages in the dev/CI image.
- Dated, owned, separately approved, expiring security exceptions.
- One aggregated security gate suitable for branch protection.
- Blocked-PR demo instructions for secret and vulnerable dependency/image cases.

## Phase 3: documented limitation

- C++ CodeQL is not enabled in this phase. ADR 0002 documents why cppcheck is the current gate and what it cannot detect.
