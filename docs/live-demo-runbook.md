# Robotek 15–20 minute live demo

This runbook keeps the presentation short, repeatable, and backed by real deployment evidence.

## Prepared state

- AWS K3s, Argo CD, and the self-hosted GitHub runner are online.
- Docker Hub has public frontend, backend, and database repositories under `ihebmrabet`.
- `Robotek Live Demo` publishes a verified temporary HTTPS URL after a successful deployment.
- The open feature branch `demo-feature/live-safety-gate` contains the pre-written feature and stays unmerged until the meeting.
- The dashboard uses only live ROS 2, Prometheus, Kubernetes, Argo CD, Grafana, and PostgreSQL results. Missing sources display `Unavailable`.

## Open before the call

Open these tabs in order:

1. The HTTPS dashboard URL from the newest successful `Publish temporary HTTPS interface` summary.
2. The prepared safety-gate pull request.
3. GitHub Actions filtered to `Robotek Live Demo`.
4. The three Docker Hub repositories.
5. Argo CD with `robotek-demo` selected.

Run one private rehearsal before the meeting. Confirm the dashboard refreshes, the feature is mergeable, the runner is online, and the latest workflow is green.

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
- If the temporary hostname changes, use the URL in the latest public-interface job summary.
- If the feature branch is behind `main`, update it and rehearse before the meeting; do not improvise a conflict resolution during the call.
