# Security controls

## Dependency model

This ROS 2 repository does not use a single Python lockfile for all runtime dependencies. ROS dependencies are declared in each `package.xml`; `rosdep` resolves them primarily to Ubuntu/ROS Debian packages installed with apt. Therefore Phase 3 uses two Trivy views:

- filesystem scan of repository manifests and configuration;
- image scan of the published dev/CI image, which contains the resolved apt and ROS packages.

## SAST

- Python: deterministic local Semgrep rules in `security/semgrep.yml`.
- C++: cppcheck. Its limits and the future CodeQL option are documented in ADR 0002.

## Exceptions

Every accepted finding must be recorded in `security/exceptions.yaml`. Exceptions require an owner, a different approver, a tracking ticket, a technical reason, and an expiration no later than 90 days after creation. An expired or malformed exception fails the security workflow.

An entry in `exceptions.yaml` documents governance; it does not automatically suppress a scanner. Any tool-specific suppression must be reviewed in the same PR and reference the matching exception ID.
