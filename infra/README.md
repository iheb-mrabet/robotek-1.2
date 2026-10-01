# Robotek AWS Academy rebuild

This directory rebuilds the expired AWS Academy environment without reusing old
instance IDs, IP addresses, credentials, private keys, or Terraform state.

## Ownership boundaries

- Terraform owns the VPC, public subnet, route, security group, key pair, EC2 host,
  and dashboard Elastic IP.
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

The stable dashboard URL is printed by:

```bash
terraform -chdir=infra/terraform output -raw public_dashboard_url
```

When `enable_public_dashboard=true`, ports 80 and 443 are intentionally public.
Caddy is installed from a pinned, SHA-512-verified release and runs as a restricted
systemd service. The hostname is derived from the Elastic IP through `nip.io`, so no
registrar or mutable DNS record is required.

The address is stable only while the Elastic IP remains allocated and
associated. AWS Academy can stop EC2 when the lab session ends, and its account
can be reset or disabled when the course or budget ends. This environment
cannot guarantee 24/7 availability; start the lab and validate the full stack
before every demo. Do not describe the URL as an always-on production service.

For the already-running staging environment, import the existing address before the
first Terraform apply so Terraform does not allocate a second one:

```bash
terraform -chdir=infra/terraform import 'aws_eip.dashboard[0]' eipalloc-02fd54fd6a22fda18
```

Register the runner only after generating a fresh one-time repository token and
copying the official SHA-256 shown for the pinned GitHub Actions runner release:

```bash
export GITHUB_RUNNER_TOKEN='enter privately in your terminal'
export GITHUB_RUNNER_SHA256='official archive checksum'
make runner-register
unset GITHUB_RUNNER_TOKEN GITHUB_RUNNER_SHA256
```

The GitHub deployment job requires an online repository runner labeled
`self-hosted`, `linux`, `x64`, `robotek-staging`, `k3s`, and `staging`. Check
**Settings → Actions → Runners** before triggering or rerunning a deployment.
If no runner is configured, a successful image build or GitOps promotion is
not proof that the live release deployed; the Argo job can remain queued until
GitHub cancels it. Registering a runner requires a fresh one-time GitHub token
and an active lab/EC2 instance. Never paste the token into chat or logs.

The runner's Kubernetes credential is read-only in the Robotek staging and
demo namespaces and expires after eight hours. On each new lab session, after
the instance is running and the current repository revision is installed on
the host, refresh it without creating another GitHub registration token:

```bash
sudo /opt/robotek/repository/infra/scripts/register-runner.sh --refresh-kubeconfig
```

Then confirm the runner is online in GitHub and that `kubectl` can read the
Robotek and Argo CD resources as the `robotek-runner` user. An expired cluster
credential can leave a registered runner online while deployment validation
fails; renewing only the GitHub registration token does not fix that state.

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
