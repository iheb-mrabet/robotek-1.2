# Phase 6 - Observability and Runtime Security Design

**Status:** Approved for implementation  
**Started:** August 1, 2026  
**Depends on:** Completed Phase 5 GitOps staging deployment  
**Infrastructure as Code:** Terraform is intentionally deferred until after Phase 6.

---

## 1. Purpose

Phase 5 proved that Robotek can be built, verified, promoted by immutable digest, deployed through Argo CD, validated in K3s, and recovered through Git.

Phase 6 adds the ability to answer operational questions continuously:

- Is the Kubernetes platform healthy?
- Is the Robotek Pod ready and stable?
- Are the required ROS 2 nodes and topics available?
- Are `/mission/status` and `/odom` still publishing fresh data?
- Is the emergency-stop state visible?
- Is Argo CD synchronized and healthy?
- Is suspicious runtime behavior occurring?
- Can every deployment be validated automatically and preserved as evidence?

The objective is not only to collect metrics. The objective is to create an observable and security-aware staging system with repeatable dashboards, alerts, runtime detections, and post-deployment evidence.

---

## 2. Scope

### Included

1. Prometheus, Grafana, Alertmanager, kube-state-metrics, and node-exporter.
2. Kubernetes, K3s node, Pod, Deployment, container, and Argo CD monitoring.
3. A Robotek ROS 2 Prometheus exporter.
4. Git-managed Grafana dashboards.
5. Git-managed Prometheus alert rules.
6. Falco-based runtime detection.
7. Scheduled Trivy image and Kubernetes configuration scans.
8. Automated post-deployment verification and evidence upload.
9. Controlled failure demonstrations for monitoring and runtime security.

### Not included

- Terraform provisioning or importing existing AWS resources.
- Production multi-node Kubernetes.
- Public Grafana or Prometheus exposure.
- Long-term enterprise telemetry storage.
- Automatic production rollback.
- Generalization to the other robot repositories; that remains Phase 7.

---

## 3. Current Phase 5 Baseline

Phase 6 builds on the following verified state:

- Robotek runs in the `robotek-staging` namespace on K3s.
- Argo CD owns the Helm deployment.
- The runtime image is pinned by immutable GHCR digest.
- The application has ROS-aware startup and readiness probes.
- `verify_release.sh`, `smoke_test.sh`, and `collect_evidence.sh` already exist.
- Argo CD finishes in `Synced` and `Healthy` state.
- The Robotek Pod becomes Ready with zero restarts.

Phase 6 must preserve these guarantees.

---

## 4. Target Architecture

```text
GitHub repository
├── Robotek Helm chart
├── Observability Helm chart
├── Runtime-security Helm chart
├── Grafana dashboards
├── Prometheus alert rules
├── Falco rules
└── Post-deployment validation workflow
            |
            v
         Argo CD
        /       \
       v         v
robotek-staging  monitoring
├── Robotek Pod ├── Prometheus
│   ├── runtime ├── Grafana
│   └── exporter├── Alertmanager
│               ├── kube-state-metrics
│               └── node-exporter
│
└──────── Prometheus scrapes Robotek exporter

runtime-security
└── Falco DaemonSet

Prometheus
├── Kubernetes metrics
├── node metrics
├── Argo CD metrics
└── Robotek ROS 2 metrics
        |
        v
Grafana dashboards + Alertmanager alerts
```

---

## 5. Ownership Boundaries

| Component | Owner | Responsibility |
|---|---|---|
| GitHub Actions | CI/CD | Build, test, scan, sign, attest, promote, and validate deployments. |
| Argo CD | GitOps | Reconcile Robotek, observability, dashboards, alerts, and runtime-security resources. |
| Prometheus | Metrics | Scrape, store, and evaluate platform and Robotek metrics. |
| Grafana | Visualization | Display provisioned dashboards from Git. |
| Alertmanager | Notification routing | Group and route Prometheus alerts. Initial phase may use a local receiver until a final channel is selected. |
| Robotek metrics exporter | Application observability | Convert ROS 2 graph and topic health into Prometheus metrics. |
| Falco | Runtime security | Detect suspicious process, file, privilege, and container behavior. |
| Terraform | Deferred | Future AWS and K3s infrastructure provisioning after Phase 6. |

Terraform and Argo CD must never manage the same application resources. When Terraform is introduced later, it will own cloud infrastructure and cluster bootstrap; Argo CD will continue owning Kubernetes workloads.

---

## 6. Namespaces

| Namespace | Purpose |
|---|---|
| `argocd` | Existing GitOps control plane. |
| `robotek-staging` | Existing Robotek runtime and ROS metrics exporter. |
| `monitoring` | Prometheus, Grafana, Alertmanager, kube-state-metrics, node-exporter integration, dashboards, and rules. |
| `runtime-security` | Falco and security-event forwarding components. |

No monitoring UI will be exposed publicly. Access will initially use Kubernetes port-forwarding through the existing SSH tunnel.

---

## 7. Proposed Repository Structure

```text
deploy/
├── argocd/
│   ├── robotek-staging.yaml
│   ├── robotek-observability.yaml
│   └── robotek-runtime-security.yaml
│
└── helm/
    ├── robotek/
    │   └── existing application chart
    │
    ├── observability/
    │   ├── Chart.yaml
    │   ├── Chart.lock
    │   ├── values.yaml
    │   ├── values-staging.yaml
    │   ├── dashboards/
    │   │   ├── robotek-overview.json
    │   │   ├── robotek-runtime.json
    │   │   ├── k3s-cluster.json
    │   │   └── argocd-gitops.json
    │   └── templates/
    │       ├── prometheus-rules.yaml
    │       ├── robotek-service-monitor.yaml
    │       ├── argocd-service-monitors.yaml
    │       └── dashboard-configmaps.yaml
    │
    └── runtime-security/
        ├── Chart.yaml
        ├── Chart.lock
        ├── values.yaml
        ├── values-staging.yaml
        └── rules/
            └── robotek-falco-rules.yaml

src/
└── robotek_metrics_exporter/
    ├── package.xml
    ├── setup.py
    ├── resource/
    ├── robotek_metrics_exporter/
    │   ├── __init__.py
    │   └── exporter_node.py
    └── test/

.github/workflows/
├── release.yml
├── post-deploy-validation.yml
└── scheduled-runtime-scan.yml

docs/
├── phase6-design.md
└── phase6-operations.md
```

The exact package and chart layout may be adjusted during implementation, but the ownership boundaries must remain unchanged.

---

## 8. Workstream 1 - Observability Foundation

### Tool choice

Use one GitOps-managed observability chart based on `kube-prometheus-stack`. It provides the central components needed by this phase:

- Prometheus Operator and Prometheus.
- Grafana.
- Alertmanager.
- kube-state-metrics.
- node-exporter.
- ServiceMonitor and PrometheusRule custom resources.

The chart dependency must be pinned rather than using an unbounded latest version.

### Initial staging configuration

Because the environment is a single K3s node, the first deployment will use conservative resource settings:

- One Prometheus replica.
- One Grafana replica.
- One Alertmanager replica.
- Short initial Prometheus retention.
- Small persistent volumes using the K3s local-path storage class.
- No public Ingress or LoadBalancer.
- ClusterIP services only.
- Port-forward access for Prometheus, Grafana, and Alertmanager.
- Resource requests and limits for every monitoring component.

Before installation, record node allocatable CPU, memory, storage, and current usage. The monitoring stack must not make the Robotek simulation unstable.

### Acceptance criteria

- Argo CD Application is `Synced` and `Healthy`.
- Prometheus, Grafana, Alertmanager, kube-state-metrics, and node-exporter are Running.
- All expected Prometheus targets are Up.
- Monitoring survives a normal Pod restart.
- No monitoring service is publicly exposed.

---

## 9. Workstream 2 - Kubernetes and GitOps Metrics

### Required platform signals

| Area | Signal | Purpose |
|---|---|---|
| Pod health | Ready condition | Detect an unhealthy or initializing Robotek Pod. |
| Stability | Container restart count | Detect crashes and repeated restarts. |
| Deployment | Desired, available, and unavailable replicas | Detect incomplete rollout. |
| Scheduling | Pending Pod phase | Detect capacity and scheduling problems. |
| Image delivery | Waiting reason such as `ImagePullBackOff` | Detect registry, image, or digest failures. |
| CPU | Container and node CPU usage | Detect saturation. |
| Memory | Working-set and node memory usage | Detect pressure or limit risk. |
| Storage | Node and Prometheus storage consumption | Detect disk pressure. |
| K3s node | Ready condition | Detect cluster host failure. |
| Argo CD | Sync and health status | Detect drift, failed reconciliation, or degraded applications. |

### Initial recording and dashboard queries

The implementation should use stable metrics from kube-state-metrics, cAdvisor/Kubelet, node-exporter, and Argo CD. Examples include:

- `kube_pod_status_ready`
- `kube_pod_container_status_restarts_total`
- `kube_deployment_status_replicas_available`
- `kube_deployment_status_replicas_unavailable`
- `kube_pod_status_phase`
- `kube_pod_container_status_waiting_reason`
- `container_cpu_usage_seconds_total`
- `container_memory_working_set_bytes`
- `kube_node_status_condition`
- `argocd_app_info`

Metric names and labels must be confirmed against the installed versions before dashboards and alerts are finalized.

### Argo CD monitoring

Prometheus will scrape the available Argo CD metrics services through ServiceMonitor resources. The implementation must verify the actual service names, ports, and labels installed in the existing `argocd` namespace rather than assuming defaults.

### Acceptance criteria

- Kubernetes resource metrics are visible in Prometheus.
- K3s node CPU, memory, disk, and readiness are visible.
- Robotek Deployment availability and Pod state are visible.
- Argo CD sync and health state are visible.
- A deliberately Pending or image-pull-failing test workload produces the expected metric and alert signal.

---

## 10. Workstream 3 - Robotek ROS 2 Metrics Exporter

### Deployment model

The initial design uses a metrics-exporter sidecar in the Robotek Pod.

Reasons:

- It shares the Pod network namespace with the Robotek runtime.
- It uses the same `ROS_DOMAIN_ID`.
- It avoids depending on cross-Pod multicast behavior for initial ROS discovery.
- It is deployed and versioned with the Robotek Helm release.
- Prometheus can scrape it through a dedicated ClusterIP Service and ServiceMonitor.

The exporter must only observe ROS 2 state. It must not publish control commands or change robot behavior.

### Exporter responsibilities

1. Create an `rclpy` monitoring node.
2. Subscribe to `/mission/status`.
3. Subscribe to `/odom` with compatible best-effort QoS.
4. Discover expected ROS nodes.
5. Discover expected ROS topics.
6. Track emergency-stop state from the appropriate Robotek message or service state.
7. Record time until the first valid mission-status and odometry messages are both observed.
8. Expose an HTTP `/metrics` endpoint for Prometheus.
9. Continue exporting negative or stale values when a ROS dependency disappears.

### Required custom metrics

| Metric | Type | Meaning |
|---|---|---|
| `robotek_mission_status_available` | Gauge | `1` when mission-status data has been received recently, otherwise `0`. |
| `robotek_mission_status_age_seconds` | Gauge | Age of the most recently received mission-status message. |
| `robotek_odom_available` | Gauge | `1` when odometry has been received recently, otherwise `0`. |
| `robotek_odom_age_seconds` | Gauge | Age of the most recently received odometry message. |
| `robotek_expected_node_available{node="..."}` | Gauge | Availability of each required ROS node. |
| `robotek_expected_topic_available{topic="..."}` | Gauge | Availability of each required ROS topic. |
| `robotek_expected_nodes_available_total` | Gauge | Count of currently available expected nodes. |
| `robotek_expected_topics_available_total` | Gauge | Count of currently available expected topics. |
| `robotek_mission_state` | Gauge or state-set | Current normalized mission state without unbounded labels. |
| `robotek_emergency_stop_active` | Gauge | `1` when the emergency stop is active. |
| `robotek_simulation_startup_duration_seconds` | Gauge | Time from exporter startup until mission status and odometry are both healthy. |
| `robotek_exporter_ros_ok` | Gauge | Overall exporter view of the ROS graph and critical topics. |

### Expected nodes

The initial expected-node set is:

- `/mission_manager`
- `/robot_state_publisher`
- `/ros_gz_bridge`
- `/safety_controller`
- `/waypoint_controller`

The exporter configuration must allow this list to be overridden through Helm values for future robots.

### Expected topics

The initial expected-topic set is:

- `/mission/status`
- `/odom`
- `/scan`
- `/tf`
- `/cmd_vel`

The exporter configuration must allow this list to be overridden through Helm values.

### Freshness defaults

Initial staging thresholds:

- Mission-status data is stale after 15 seconds.
- Odometry data is stale after 15 seconds.
- Node/topic discovery is evaluated repeatedly rather than only during startup.

These values are starting points and must be validated against real simulation behavior.

### Security requirements

- Run as non-root.
- Disable privilege escalation.
- Drop all Linux capabilities.
- Use `RuntimeDefault` seccomp.
- Use a read-only root filesystem when compatible with ROS runtime needs.
- Do not mount the Kubernetes ServiceAccount token.
- Apply CPU and memory requests and limits.
- Expose only the metrics port through an internal Service.

### Tests

- Unit tests for freshness and state conversion logic.
- Unit tests for expected-node and expected-topic evaluation.
- Integration test with synthetic ROS messages.
- Container validation confirming the metrics endpoint starts as non-root.
- Helm render tests for Service, sidecar, and ServiceMonitor resources.

### Acceptance criteria

- Prometheus successfully scrapes the exporter.
- All expected nodes and topics appear as metrics.
- Mission-status and odometry freshness values change in real time.
- Stopping a required publisher changes the corresponding metric and triggers an alert.
- Exporter failure does not directly control or modify the robot.

---

## 11. Workstream 4 - Grafana Dashboards

Dashboards will be stored in Git and provisioned automatically. Manual dashboard creation in the Grafana UI is not the source of truth.

### Dashboard 1 - Robotek Staging Overview

Panels:

- Argo CD sync status.
- Argo CD health status.
- Robotek Deployment available replicas.
- Robotek Pod Ready state.
- Restarts in the selected period.
- Current immutable image digest.
- Mission-status availability and age.
- Odometry availability and age.
- Emergency-stop state.
- Expected ROS nodes available.
- Expected ROS topics available.
- Active alerts.

### Dashboard 2 - Robotek Runtime

Panels:

- Mission state timeline.
- Mission-status freshness.
- Odometry freshness.
- Expected-node availability by node.
- Expected-topic availability by topic.
- Simulation startup duration.
- Robotek runtime and exporter CPU.
- Robotek runtime and exporter memory.
- Container restart history.
- Pod events or linked troubleshooting guidance.

### Dashboard 3 - K3s Cluster

Panels:

- Node Ready status.
- CPU usage and allocatable capacity.
- Memory usage and allocatable capacity.
- Disk usage and pressure.
- Pod count by phase.
- Pending Pods.
- Container restarts.
- Deployment availability by namespace.
- Prometheus target health.

### Dashboard 4 - Argo CD GitOps

Panels:

- Application sync status.
- Application health status.
- Last observed revision.
- Reconciliation duration and failures when available.
- Out-of-sync duration.
- Degraded applications.
- Robotek and observability Application state.

### Dashboard design rules

- Use clear green, amber, and red state semantics.
- Avoid displaying high-cardinality labels.
- Keep the overview dashboard useful at a glance.
- Add descriptions and troubleshooting links to important panels.
- Store dashboard JSON in the repository and load it through labeled ConfigMaps.

### Acceptance criteria

- Dashboards appear automatically after Argo CD synchronization.
- No manual Grafana configuration is required after a clean deployment.
- Dashboard data sources are provisioned automatically.
- Deliberate failures visibly change the relevant panels.

---

## 12. Workstream 5 - Alert Rules

### Initial alerts

| Alert | Starting condition | Severity |
|---|---|---|
| `RobotekPodNotReady` | Robotek Pod not Ready for 5 minutes. | Critical |
| `RobotekDeploymentUnavailable` | Available replicas below desired replicas for 5 minutes. | Critical |
| `RobotekContainerRestarted` | Restart count increases during a 15-minute window. | Warning |
| `RobotekImagePullFailure` | `ErrImagePull` or `ImagePullBackOff` exists for 2 minutes. | Critical |
| `RobotekMissionStatusMissing` | Mission status unavailable or older than 15 seconds for 2 minutes. | Critical |
| `RobotekOdometryMissing` | Odometry unavailable or older than 15 seconds for 2 minutes. | Critical |
| `RobotekExpectedNodeMissing` | Any required ROS node is missing for 2 minutes. | Critical |
| `RobotekExpectedTopicMissing` | Any required ROS topic is missing for 2 minutes. | Critical |
| `RobotekEmergencyStopActive` | Emergency stop remains active for 1 minute. | Warning |
| `RobotekHighCPU` | Sustained CPU above 85 percent of the configured limit for 10 minutes. | Warning |
| `RobotekHighMemory` | Sustained memory above 85 percent of the configured limit for 10 minutes. | Warning |
| `RobotekPodPending` | Robotek Pod remains Pending for 10 minutes. | Critical |
| `K3sNodeNotReady` | K3s node not Ready for 2 minutes. | Critical |
| `ArgoCDApplicationOutOfSync` | An owned Application remains OutOfSync for 10 minutes. | Warning |
| `ArgoCDApplicationDegraded` | An owned Application is Degraded for 5 minutes. | Critical |
| `PrometheusTargetDown` | A required scrape target is down for 5 minutes. | Warning |

### Alert quality rules

- Every alert must include a clear summary and description.
- Every alert must identify the affected namespace, Pod, application, node, topic, or component.
- Alert thresholds must be validated against real Robotek startup and workload behavior.
- Alerts must avoid firing continuously during normal Gazebo startup.
- A runbook reference must be added before the alert set is considered complete.

### Alert testing

At least these demonstrations are required:

1. Scale or stop Robotek to trigger NotReady or DeploymentUnavailable.
2. Use an invalid digest to trigger ImagePullBackOff detection.
3. Stop or isolate `/mission/status` publishing.
4. Stop or isolate `/odom` publishing.
5. Force an Argo CD OutOfSync state in a controlled test.
6. Restore the system through Git and confirm alerts resolve.

### Acceptance criteria

- Every critical alert has a tested firing and recovery path.
- Resolved alerts clear automatically after recovery.
- Alertmanager receives the alerts.
- Alert evidence is included in the Phase 6 report.

---

## 13. Workstream 6 - Runtime Security

### Tool choice

Use Falco as the initial runtime detection engine, deployed through Argo CD as a DaemonSet in the `runtime-security` namespace.

Falco will begin with upstream default rules and a small Robotek-specific rule set. Custom rules must be added gradually to avoid excessive noise on the single-node staging cluster.

### Detection priorities

- Shell started inside the Robotek container.
- Package manager or compiler executed in the runtime container.
- Write activity in sensitive filesystem locations.
- Unexpected process execution.
- Privileged container creation.
- Linux capability or privilege-escalation activity.
- Sensitive host path access.
- Kubernetes credential or ServiceAccount token access.
- Unexpected outbound network activity when a reliable baseline is available.

### Kubernetes events and audit visibility

- Collect Kubernetes warning events through metrics and dashboard panels.
- Review K3s audit-log configuration as a controlled infrastructure change.
- Do not enable verbose audit logging without disk-usage limits and rotation.
- Preserve runtime-security evidence outside the application container.

### Scheduled Trivy scans

Add a scheduled GitHub Actions workflow that:

1. Resolves the currently promoted runtime digest.
2. Scans the runtime image for HIGH and CRITICAL vulnerabilities.
3. Renders the staging Helm chart.
4. Scans the rendered Kubernetes configuration.
5. Uploads JSON and text reports.
6. Fails according to the existing vulnerability and misconfiguration policies.

This scheduled scan complements release-time scanning by detecting newly disclosed vulnerabilities after an image has already been deployed.

### Falco demonstration scenarios

- Start a shell in a controlled test container.
- Attempt to write to a sensitive path in a controlled test container.
- Start an unexpected executable in a dedicated test Pod.
- Confirm Falco records the event and identifies the Pod, namespace, container, and rule.

Do not weaken the Robotek production security context merely to generate a demonstration.

### Acceptance criteria

- Falco is Running on the K3s node.
- Default and Robotek-specific rules load without errors.
- Controlled suspicious activity generates an event.
- Normal Robotek operation does not generate unmanageable alert noise.
- Scheduled Trivy reports are uploaded as GitHub Actions artifacts.

---

## 14. Workstream 7 - Automated Post-Deployment Validation

### Current limitation

The K3s API and Argo CD API are private. A normal GitHub-hosted runner cannot directly execute the existing cluster verification scripts without a secure connectivity mechanism.

### Initial execution model

Use a dedicated, repository-restricted self-hosted GitHub Actions runner associated with the staging environment.

Security restrictions:

- The runner must not execute pull-request code from forks.
- The workflow must run only for protected `main` deployment events or manual dispatch.
- The runner group must be restricted to this repository.
- The runner must use minimum filesystem and Kubernetes permissions required by the validation scripts.
- Secrets must not be printed into logs or collected into evidence artifacts.
- Long-term improvement: replace the persistent runner with an ephemeral runner or a controlled remote-execution mechanism.

### Trigger

Create `.github/workflows/post-deploy-validation.yml` with these triggers:

- Push to `main` affecting `deploy/helm/robotek/values-staging.yaml`.
- Manual `workflow_dispatch` for recovery and testing.

The digest-promotion commit already changes this values file, so it becomes the natural deployment-validation trigger without retriggering the release workflow.

### Validation sequence

```text
Verified digest promotion commit
        |
        v
Argo CD detects the desired-state change
        |
        v
Post-deploy workflow starts on staging runner
        |
        v
Wait until Argo CD is Synced/Healthy at the expected revision
        |
        v
Wait for Kubernetes rollout
        |
        v
scripts/deployment/verify_release.sh
        |
        v
scripts/deployment/smoke_test.sh
        |
        v
scripts/deployment/collect_evidence.sh
        |
        v
Upload timestamped evidence artifact
```

### Required workflow behavior

- Checkout the exact promotion commit.
- Determine the expected image digest from `values-staging.yaml`.
- Wait with a bounded timeout for Argo CD reconciliation.
- Confirm Argo CD revision corresponds to the expected Git state.
- Confirm the live Deployment and Pod use the expected digest.
- Run release verification.
- Run ROS 2 smoke tests.
- Collect evidence even when validation fails.
- Upload evidence with a retention period.
- Fail the workflow if release verification or smoke testing fails.
- Avoid committing generated evidence to Git.

### Acceptance criteria

- Every automatic digest promotion triggers one post-deployment validation run.
- A healthy deployment produces a successful workflow and evidence artifact.
- A deliberately broken deployment produces a failed workflow and diagnostic evidence.
- The validation workflow does not create a release or deployment loop.

---

## 15. GitOps Application Order

The recommended Argo CD synchronization order is:

1. Observability custom resources and monitoring stack.
2. Robotek application and metrics exporter.
3. Runtime-security stack.

Argo CD sync waves may be used where required so that CustomResourceDefinitions exist before ServiceMonitor and PrometheusRule resources are applied.

The existing Robotek application must remain independently deployable if the monitoring stack is temporarily unavailable.

---

## 16. Security and Privacy Requirements

- Keep Grafana, Prometheus, Alertmanager, and Argo CD private.
- Rotate generated or default passwords.
- Store credentials in Kubernetes Secrets, never in Git.
- Disable anonymous Grafana access.
- Avoid collecting secrets, tokens, message payloads, or unnecessary personal data in metrics.
- Do not use mission identifiers or unbounded strings as Prometheus labels.
- Set retention limits for metrics and workflow artifacts.
- Apply non-root and least-privilege controls where supported.
- Review all monitoring and Falco container images through the existing security process.
- Pin Helm chart versions and review upgrades.

---

## 17. Capacity and Reliability Plan

The cluster is a single K3s node that also runs Gazebo. Monitoring must be introduced gradually.

Before each major installation:

1. Record baseline CPU and memory usage.
2. Record free disk space.
3. Confirm Robotek smoke tests pass.
4. Deploy one workstream.
5. Re-run Robotek verification and smoke tests.
6. Compare resource usage against the baseline.
7. Adjust retention, scrape frequency, or component resources when necessary.

Initial reliability priorities:

- Robotek runtime remains stable.
- Prometheus storage is bounded.
- Monitoring failures do not block Robotek startup.
- Alert rules tolerate normal simulation startup time.
- Dashboards continue functioning after Pod recreation.

---

## 18. Implementation Sequence

### Step 0 - Design and baseline

- Commit this design.
- Mark Phase 6 In Progress.
- Capture current node and Robotek resource baselines.

### Step 1 - Observability foundation

- Create the observability Helm chart.
- Pin the monitoring dependency.
- Add staging values and private access settings.
- Add the Argo CD Application.
- Deploy and verify all monitoring targets.

### Step 2 - Kubernetes and Argo CD monitoring

- Add Argo CD ServiceMonitors.
- Verify kube-state-metrics and node-exporter data.
- Create initial platform dashboard and alerts.

### Step 3 - Robotek metrics exporter

- Implement the exporter package.
- Add tests and container integration.
- Add sidecar, Service, and ServiceMonitor support to the Robotek chart.
- Validate live metrics.

### Step 4 - Dashboards and alert rules

- Add all four dashboards.
- Add and test alert rules.
- Add runbook links.

### Step 5 - Runtime security

- Deploy Falco.
- Add Robotek-specific rules.
- Add scheduled Trivy scans.
- Run controlled detection demonstrations.

### Step 6 - Automated post-deployment validation

- Configure the restricted staging runner.
- Add the validation workflow.
- Upload evidence artifacts.
- Test successful and failed deployments.

### Step 7 - Documentation and phase closure

- Write the operations and troubleshooting guide.
- Update README and backlog.
- Produce the Phase 6 implementation report, learning guide, and presentation.
- Capture final dashboards, alerts, security events, and automated evidence.

---

## 19. Definition of Done

Phase 6 is complete only when all of the following are true:

- [ ] Observability stack is GitOps-managed and Healthy.
- [ ] Prometheus collects node, Kubernetes, Argo CD, and Robotek metrics.
- [ ] Grafana dashboards are provisioned entirely from Git.
- [ ] Robotek exporter exposes ROS node, topic, mission, odometry, e-stop, and startup metrics.
- [ ] Critical alerts have been tested through firing and recovery.
- [ ] Falco detects controlled suspicious runtime activity.
- [ ] Scheduled Trivy scans publish evidence.
- [ ] Every staging digest promotion triggers automated post-deployment validation.
- [ ] Validation runs release verification, ROS smoke testing, and evidence collection.
- [ ] A failed validation preserves diagnostic artifacts.
- [ ] Robotek remains stable on the single-node K3s cluster.
- [ ] Documentation and demonstration evidence are complete.

---

## 20. First Implementation Task

The first code task is **Workstream 1: deploy the observability foundation through Helm and Argo CD**.

Before creating the chart, capture this baseline from the staging host:

```bash
kubectl get nodes -o wide
kubectl top nodes
kubectl top pods -A
kubectl get storageclass
kubectl get pvc -A
kubectl get pods -A
free -h
df -h
```

This baseline determines safe Prometheus retention, storage, and resource limits for the current K3s node.
