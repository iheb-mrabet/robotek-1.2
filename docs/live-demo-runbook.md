# Robotek 15–20 minute live demo

This runbook keeps the presentation short, repeatable, and evidence driven.

## Prepared state

- The AWS K3s server and self-hosted GitHub runner are online.
- Argo CD manages the `robotek-demo` Helm release.
- Docker Hub contains the frontend, backend, and database repositories.
- The `Robotek Live Demo` workflow publishes an HTTPS Cloudflare Quick Tunnel after every successful deployment.
- The separate pull request titled `feat(demo): add live robot safety center` contains the pre-written feature and remains unmerged until the meeting.

## Open before the call

Open these browser tabs and keep them in this order:

1. The live Robotek HTTPS dashboard from the latest successful workflow summary.
2. The prepared feature pull request.
3. GitHub Actions filtered to `Robotek Live Demo`.
4. The three Docker Hub repositories:
   - `ihebmrabet/robotek-demo-frontend`
   - `ihebmrabet/robotek-demo-backend`
   - `ihebmrabet/robotek-demo-database`
5. Argo CD with the `robotek-demo` application selected.

Do one private rehearsal before the call. Confirm the dashboard refreshes, the prepared pull request is mergeable, the runner is online, and the latest pipeline is green.

## Live presentation timeline

### 0:00–2:00 — Explain the starting point

Show the live operations dashboard and state the feature you will add: a Robot Safety Center backed by live ROS and Prometheus data.

### 2:00–3:00 — Integrate the prepared feature

Open the prepared pull request, briefly show its frontend changes and integration-test assertion, then merge it into `main`. This is the live integration and Git push event.

### 3:00–7:00 — Follow CI/CD

Open the new `Robotek Live Demo` run and show:

- unit tests;
- frontend + backend + database integration tests;
- Helm and Docker Compose orchestration validation;
- the three parallel Docker builds and pushes;
- the GitOps image-tag promotion;
- Argo CD automated deployment;
- public HTTPS interface verification.

The last verified full run completed in under three minutes, leaving a generous buffer inside the meeting limit.

### 7:00–10:00 — Prove the artifacts and deployment

Refresh the three Docker Hub repositories and show the new immutable commit tag. In Argo CD, show `Synced` and `Healthy` for `robotek-demo`.

### 10:00–12:00 — Reveal the feature

Refresh the public Robotek dashboard. Show the new Robot Safety Center and explain that its controller, topic, and alert values come from live Prometheus and ROS data; unavailable sources are never replaced with invented values.

### 12:00–15:00 — Close and keep buffer

Summarize the flow: Git push → tests → three Docker images → Helm desired state → Argo CD reconciliation → K3s → public dashboard. Keep the remaining time for questions or a slow image pull.

## Recovery shortcuts

- If a browser tab is stale, refresh it; do not restart the pipeline.
- If Docker Hub takes time to display a tag, use the successful build jobs as proof and refresh once after deployment.
- If the public tunnel URL changed, use the URL in the newest `Publish temporary HTTPS interface` job summary.
- If the prepared feature PR is unexpectedly not mergeable, update it from `main` before the call rather than improvising during the demonstration.
