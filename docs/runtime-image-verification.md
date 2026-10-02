# Verify a Robotek runtime image

Use the immutable image digest from `deploy/helm/robotek/values-staging.yaml` and the corresponding successful runtime release. The release artifact retains metadata, scan reports, SBOMs, and verification evidence.

## Inspect the release evidence

1. Open the successful **Verified Runtime Release** run.
2. Open **Signed and Attested Runtime Delivery**.
3. Inspect the runtime image scan, generated SPDX and CycloneDX SBOMs, keyless signing, attestations, and verification steps.
4. Download the delivery artifact from that run. Keep its metadata and digest together.
5. Compare the desired digest with the deployed containers, rather than comparing mutable tags.

On the dedicated Robotek host:

```bash
sudo -n k3s kubectl -n robotek-staging get deployment robotek-staging \
  -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{" "}{.image}{"\n"}{end}'
```

## Verify the signature independently

Use the same Cosign version and identity policy as the release workflow. Substitute the exact accepted digest below:

```bash
IMAGE='ghcr.io/iheb-mrabet/robotek-1.2-runtime@sha256:REPLACE_WITH_ACCEPTED_DIGEST'
cosign verify \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp \
  '^https://github.com/iheb-mrabet/robotek-1\.2/\.github/workflows/.*@refs/heads/main$' \
  "$IMAGE"
```

The regular expression above requires this repository, its workflows, and `main`. For tagged releases, use the exact identity recorded in the accepted release instead of loosening the expression.

An SBOM is an inventory. A signature binds an artifact to an identity. Provenance records build context. None alone proves correct robot behavior; combine them with ROS test and live deployment evidence.

## Repeat live acceptance

Use **Staging Post-Deploy Validation** on `main`. Confirm reconciliation, deployed-image verification, ROS smoke testing, and evidence upload all pass. Check current readiness after lab startup before a presentation.
