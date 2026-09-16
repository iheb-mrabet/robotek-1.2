# Robotek AWS Academy rebuild

This directory rebuilds the expired AWS Academy environment without reusing old
instance IDs, IP addresses, credentials, private keys, or Terraform state.

## Ownership boundaries

- Terraform owns the VPC, public subnet, route, security group, key pair, and EC2 host.
- Cloud-init and `infra/scripts` own K3s, Helm, Argo CD, and bootstrap-time Secrets.
- Argo CD owns Robotek, the demo stack, monitoring, dashboards, alerts, and Falco.

## Before applying

1. Start a fresh AWS Academy Learner Lab and export its temporary credentials only in your local shell.
2. Set `AWS_REGION` and `EXPECTED_AWS_ACCOUNT_ID`; run `make check-aws`.
3. Generate a dedicated SSH key locally. Put only its `.pub` path in Terraform.
4. Copy `infra/terraform/terraform.tfvars.example` to `infra/terraform/terraform.tfvars` and replace every placeholder. The current lab exposes `LabInstanceProfile`; re-check it after every Academy reset.
5. Keep local state for Academy. Use `backend.hcl.example` only for a stable AWS account with a separately created encrypted, versioned state bucket.

The verified Academy session for this rebuild uses `us-east-1`. Keep the
session-specific account ID only in private Terraform variables and evidence;
re-run STS after every lab restart.

## Operator flow

```bash
make check-aws
make infra-init
make infra-plan
make infra-apply
export ROBOTEC_HOST="$(terraform -chdir=infra/terraform output -raw public_ip)"
export ROBOTEC_SSH_KEY=/absolute/path/to/private-key
make platform-bootstrap
make platform-verify
```

Register the runner only after generating a fresh one-time repository token and
copying the official SHA-256 shown for the pinned GitHub Actions runner release:

```bash
export GITHUB_RUNNER_TOKEN='enter privately in your terminal'
export GITHUB_RUNNER_SHA256='official archive checksum'
make runner-register
unset GITHUB_RUNNER_TOKEN GITHUB_RUNNER_SHA256
```

Do not put secrets in this repository, Terraform variables, Terraform state, or
chat. Bootstrap generates PostgreSQL and Grafana credentials directly in K3s.
Telegram routing stays disabled until the exposed historical identifier and bot
token have been rotated and a secret-management design is applied.

## Verification and teardown

`make platform-verify` reports only observed state. A missing source remains
`UNAVAILABLE`; it is never converted to a green default. Run `make
evidence-export` after the platform is healthy.

Teardown is deliberately guarded. It runs only when the current STS account,
`EXPECTED_AWS_ACCOUNT_ID`, and `CONFIRM_DESTROY_ACCOUNT` all match.
