# Blocked pull-request demonstrations

Create each demo on a temporary branch. Never merge the intentionally broken change.

## 1. Broken C++ gtest

Edit one assertion in `src/mock_robot_control/test/test_velocity_limiter.cpp` so the expected value is intentionally wrong. Push the branch and open a PR. `Unit tests` must fail and branch protection must disable merge.

## 2. Unsafe robot configuration

Change this value in `src/mock_robot_bringup/config/robot.yaml`:

```yaml
use_sim_time: false
```

Push and open a PR. `Fast gate` must fail in `scripts/validate_config.sh`.

## 3. Secret detection

Add a temporary file containing a clearly fake token that matches a Gitleaks rule, commit it on the demo branch, and open a PR. `Gitleaks full-history scan` and the aggregated security gate must fail. Delete the branch after capturing evidence.

## 4. Vulnerable dependency

On a temporary branch, add a manifest that pins a dependency version with a known HIGH or CRITICAL advisory. The Trivy repository scan must fail. Use a package/version confirmed by the current Trivy database at demo time because vulnerability data changes.

## 5. Vulnerable image layer

Temporarily modify `docker/Dockerfile` to install a package version currently reported by Trivy as HIGH or CRITICAL, publish a temporary CI-image tag, and scan it. Do not replace the protected `jazzy` tag with the intentionally vulnerable image.
