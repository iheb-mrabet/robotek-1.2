# Robotek 15–20 minute live demo

This runbook keeps the presentation short, repeatable, and backed by real deployment evidence.

## Prepared state

- AWS K3s, Argo CD, and the self-hosted GitHub runner are online.
- Docker Hub has public frontend, backend, and database repositories under `ihebmrabet`.
- `Robotek Live Demo` verifies the stable HTTPS address after a successful deployment.
- The open feature branch `demo-feature/live-safety-gate` contains the pre-written feature and stays unmerged until the meeting.
- The dashboard uses only live ROS 2, Prometheus, Kubernetes, Argo CD, Grafana, and PostgreSQL results. Missing sources display `Unavailable`.

## Open before the call

Open these tabs in order:

1. The dashboard's stable address: <https://18-211-80-86.nip.io>.
2. The prepared safety-gate pull request.
3. GitHub Actions filtered to `Robotek Live Demo`.
4. The three Docker Hub repositories.
5. Argo CD with `robotek-demo` selected.

At least one hour before the meeting, start the AWS Academy Learner Lab and
wait for `AWS Status: Ready`. Confirm the Robotek EC2 instance is running,
its Elastic IP remains associated, the HTTPS dashboard and `/health` and
`/ready` endpoints respond, and the repository has an **online** runner with
the required `robotek-staging`, `k3s`, and `staging` labels. Run one private
rehearsal. Do not start the live merge if any of these gates is red.

The Elastic IP preserves the address across instance stop/start cycles; it
does **not** keep the service online while the instance is stopped. AWS Academy
sessions expire and may stop EC2. The URL is stable, but this student-lab
deployment is not a continuously available production service. Keep the lab
session active throughout the presentation. If the account is reset or deleted,
rebuild with Terraform and update this runbook and the workflow URL to the new
`public_dashboard_url` output.

## Live timeline

### 0:00–2:00 — Starting platform

Show the live Robotek operations dashboard. Point out the immutable release, live ROS graph, robot and K3s uptime, resource use, Prometheus targets, Grafana health, Argo CD state, and PostgreSQL status.

### 2:00–3:00 — Integrate the prepared feature

Open the prepared safety-gate pull request, show its code and tests briefly, and merge it into `main`. The merge is the live source integration and Git push event.

### 3:00–7:00 — Follow CI/CD

Open the triggered `Robotek Live Demo` run and show:

- unit tests;
- frontend + backend + database integration tests;
- Docker Compose and Helm orchestration validation;
- three parallel Docker image builds and pushes;
- immutable GitOps tag promotion;
- Argo CD automated K3s deployment;
- external HTTPS verification.

### 7:00–10:00 — Prove delivery

Show the new immutable tag in each Docker Hub repository. In Argo CD, show `Synced` and `Healthy` for `robotek-demo`.

### 10:00–12:00 — Reveal the feature

Refresh the HTTPS dashboard and show the new live safety gate. Explain that it is derived from real ROS controller/topic and Prometheus alert evidence, never seeded values.

### 12:00–15:00 — Close with buffer

Summarize: Git push → tests → three Docker images → Helm desired state → Argo CD reconciliation → K3s → public dashboard. Keep the remaining time for questions or a slow network pull.

## Recovery

- Refresh a stale page instead of restarting a successful pipeline.
- If Docker Hub is slow to list a tag, show the successful build job and refresh once after deployment.
- If the public endpoint fails, verify the Elastic IP association, `caddy.service`, and
  the latest `Verify permanent HTTPS interface` job before the meeting. First
  check whether the AWS Academy lab session expired and EC2 stopped.
- If GitHub shows no configured or online self-hosted runner, do not rerun the
  workflow yet: its Argo deployment job will wait in the queue and eventually
  be cancelled. Restore or register the runner using `infra/README.md`, verify
  its labels, then rerun the failed/cancelled workflow and wait for the external
  HTTPS verification job to succeed.
- If the feature branch is behind `main`, update it and rehearse before the meeting; do not improvise a conflict resolution during the call.
