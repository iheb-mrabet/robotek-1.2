const byId = (id) => document.getElementById(id);

const history = {
  cpu: [],
  memory: [],
};

const isNumber = (value) =>
  typeof value === "number" && Number.isFinite(value);

const displayNumber = (value, suffix = "") =>
  isNumber(value) ? `${value}${suffix}` : "Unavailable";

const displayRatio = (ready, total) =>
  isNumber(ready) && isNumber(total)
    ? `${ready} / ${total}`
    : "Unavailable";

function displayDuration(seconds) {
  if (!isNumber(seconds) || seconds < 0) return "Unavailable";

  const total = Math.floor(seconds);
  const days = Math.floor(total / 86400);
  const hours = Math.floor((total % 86400) / 3600);
  const minutes = Math.floor((total % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m ${total % 60}s`;
}

function setBadge(element, label, state) {
  element.textContent = label;
  element.className = `badge ${state}`;
}

function systemIsReady(payload) {
  const {
    cluster,
    database,
    observability,
    robot,
    safety,
  } = payload;
  return (
    robot.exporter_up === true &&
    database.connected === true &&
    observability.prometheus_reachable === true &&
    isNumber(cluster.pods_ready) &&
    cluster.pods_ready === cluster.pods_total &&
    isNumber(cluster.deployments_available) &&
    cluster.deployments_available === cluster.deployments_desired &&
    isNumber(observability.gitops_healthy) &&
    observability.gitops_healthy === observability.gitops_total &&
    safety?.gate === "PASS"
  );
}

function renderChart(svgId, values, color) {
  const svg = byId(svgId);
  const width = 420;
  const height = 130;
  const padding = 8;

  if (!values.length) {
    svg.innerHTML =
      '<text x="210" y="68" text-anchor="middle" class="chart-empty">Waiting for live readings</text>';
    return;
  }

  const points = values.map((value, index) => {
    const x =
      values.length === 1
        ? width / 2
        : padding + (index / (values.length - 1)) * (width - padding * 2);
    const y = height - padding - (value / 100) * (height - padding * 2);
    return [x, y];
  });

  const line = points
    .map(([x, y], index) => `${index === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(" ");

  const area = `${line} L ${points.at(-1)[0].toFixed(1)} ${height - padding} L ${points[0][0].toFixed(1)} ${height - padding} Z`;
  const gradientId = `${svgId}-gradient`;

  svg.innerHTML = `
    <defs>
      <linearGradient id="${gradientId}" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="${color}" stop-opacity="0.35"></stop>
        <stop offset="100%" stop-color="${color}" stop-opacity="0"></stop>
      </linearGradient>
    </defs>
    <line x1="8" x2="412" y1="32" y2="32" class="chart-gridline"></line>
    <line x1="8" x2="412" y1="65" y2="65" class="chart-gridline"></line>
    <line x1="8" x2="412" y1="98" y2="98" class="chart-gridline"></line>
    <path d="${area}" fill="url(#${gradientId})"></path>
    <path d="${line}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
  `;
}

function addHistory(series, value) {
  if (!isNumber(value)) return;
  series.push(value);
  if (series.length > 36) series.shift();
}

function renderNodes(nodes) {
  const container = byId("node-list");
  container.replaceChildren();
  byId("node-count-label").textContent = nodes.length
    ? `${nodes.length} LIVE`
    : "UNAVAILABLE";

  if (!nodes.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No live node series returned by Prometheus.";
    container.append(empty);
    return;
  }

  nodes.forEach((node) => {
    const row = document.createElement("div");
    row.className = "node-row";

    const status = document.createElement("span");
    status.className = "node-status";

    const name = document.createElement("code");
    name.textContent = node;

    const label = document.createElement("small");
    label.textContent = "DISCOVERED";

    row.append(status, name, label);
    container.append(row);
  });
}

function renderTopics(topics) {
  const body = byId("topic-table");
  body.replaceChildren();
  byId("topic-count-label").textContent = topics.length
    ? `${topics.length} LIVE`
    : "UNAVAILABLE";

  if (!topics.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.className = "empty-state";
    cell.textContent = "No live topic series returned by Prometheus.";
    row.append(cell);
    body.append(row);
    return;
  }

  topics.forEach((topic) => {
    const row = document.createElement("tr");

    const name = document.createElement("td");
    const code = document.createElement("code");
    code.textContent = topic.topic;
    name.append(code);

    const publishers = document.createElement("td");
    publishers.textContent = displayNumber(topic.publishers);

    const subscribers = document.createElement("td");
    subscribers.textContent = displayNumber(topic.subscribers);

    row.append(name, publishers, subscribers);
    body.append(row);
  });
}

function renderSafety(safety, alerts) {
  const panel = byId("safety-gate");
  const gate = safety?.gate || "UNAVAILABLE";
  panel.dataset.gate = gate.toLowerCase();

  byId("safety-gate-value").textContent = gate;
  byId("critical-alerts").textContent = displayNumber(
    safety?.critical_alerts,
  );
  byId("warning-alerts").textContent = displayNumber(
    safety?.warning_alerts,
  );
  byId("collection-errors").textContent = displayNumber(
    safety?.ros_collection_errors,
  );
  byId("safety-exporter").textContent =
    safety?.exporter_up === true
      ? "ONLINE"
      : safety?.exporter_up === false
        ? "OFFLINE"
        : "UNAVAILABLE";

  const messages = {
    PASS: "No critical Robotek alerts or ROS collection errors are present.",
    FAIL: "One or more live safety conditions require attention.",
    UNAVAILABLE: "The gate will not pass without complete live evidence.",
  };
  byId("safety-gate-message").textContent = messages[gate];

  const list = byId("alert-list");
  list.replaceChildren();
  byId("alert-count").textContent = isNumber(alerts?.length)
    ? String(alerts.length)
    : "—";

  if (!alerts?.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent =
      gate === "UNAVAILABLE"
        ? "Alert data is unavailable."
        : "No firing Robotek alerts.";
    list.append(empty);
    return;
  }

  alerts.forEach((alert) => {
    const row = document.createElement("div");
    row.className = `alert-row ${alert.severity || "unknown"}`;

    const indicator = document.createElement("span");
    indicator.className = "alert-indicator";

    const description = document.createElement("div");
    const name = document.createElement("strong");
    name.textContent = alert.name || "Unnamed alert";
    const component = document.createElement("small");
    component.textContent = alert.component || "platform";
    description.append(name, component);

    const severity = document.createElement("code");
    severity.textContent = (alert.severity || "unknown").toUpperCase();

    row.append(indicator, description, severity);
    list.append(row);
  });
}

function renderPlatform(payload) {
  const {
    alerts,
    cluster,
    database,
    observability,
    robot,
    safety,
  } = payload;
  const ready = systemIsReady(payload);

  document.body.dataset.state = ready ? "healthy" : "attention";

  byId("release").textContent = payload.release || "Unavailable";
  byId("release").title = payload.release || "";

  const collected = new Date(payload.collected_at);
  byId("updated-at").textContent = Number.isNaN(collected.getTime())
    ? "Unavailable"
    : collected.toLocaleTimeString();

  if (ready) {
    byId("connection-label").textContent = "Live / Healthy";
    byId("platform-headline").textContent = "All monitored systems are operational";
    byId("platform-summary").textContent =
      "ROS telemetry, cluster workloads, GitOps applications and PostgreSQL are reporting healthy live state.";
  } else if (!observability.prometheus_reachable) {
    byId("connection-label").textContent = "Telemetry unavailable";
    byId("platform-headline").textContent = "Prometheus data is currently unavailable";
    byId("platform-summary").textContent =
      "The interface is online, but live telemetry has not been replaced with fallback data.";
  } else {
    byId("connection-label").textContent = "Attention required";
    byId("platform-headline").textContent = "One or more live checks require attention";
    byId("platform-summary").textContent =
      "Review the live readiness values below and open Grafana for detailed evidence.";
  }

  byId("exporter-status").textContent =
    robot.exporter_up === true
      ? "ONLINE"
      : robot.exporter_up === false
        ? "OFFLINE"
        : "UNAVAILABLE";
  setBadge(
    byId("exporter-badge"),
    robot.exporter_up === true ? "HEALTHY" : "CHECK",
    robot.exporter_up === true ? "good" : "bad",
  );

  byId("ros-nodes").textContent = displayNumber(robot.nodes);
  byId("ros-topics").textContent = displayNumber(robot.topics);
  byId("robot-runtime-uptime").textContent = displayDuration(
    robot.runtime_uptime_seconds,
  );
  byId("robot-restarts").textContent = displayNumber(
    robot.container_restarts,
  );
  byId("targets").textContent = displayRatio(
    observability.targets_up,
    observability.targets_total,
  );
  setBadge(
    byId("targets-badge"),
    observability.prometheus_reachable ? "REACHABLE" : "UNAVAILABLE",
    observability.prometheus_reachable ? "good" : "bad",
  );

  byId("nodes-ready").textContent = displayRatio(
    cluster.nodes_ready,
    cluster.nodes_total,
  );
  byId("pods-ready").textContent = displayRatio(
    cluster.pods_ready,
    cluster.pods_total,
  );
  byId("deployments-ready").textContent = displayRatio(
    cluster.deployments_available,
    cluster.deployments_desired,
  );
  byId("gitops-ready").textContent = displayRatio(
    observability.gitops_healthy,
    observability.gitops_total,
  );
  byId("database-state").textContent = database.connected
    ? "CONNECTED"
    : "UNAVAILABLE";

  byId("cpu-value").textContent = displayNumber(
    cluster.cpu_percent,
    "%",
  );
  byId("memory-value").textContent = displayNumber(
    cluster.memory_percent,
    "%",
  );
  byId("cluster-uptime").textContent = displayDuration(
    cluster.uptime_seconds,
  );

  addHistory(history.cpu, cluster.cpu_percent);
  addHistory(history.memory, cluster.memory_percent);
  renderChart("cpu-chart", history.cpu, "#47e6b1");
  renderChart("memory-chart", history.memory, "#7196ff");

  renderNodes(robot.node_names || []);
  renderTopics(robot.topic_details || []);
  renderSafety(safety, alerts?.items || []);

  if (observability.grafana_url) {
    byId("grafana-link").href = observability.grafana_url;
  }
  if (observability.prometheus_url) {
    byId("prometheus-link").href = observability.prometheus_url;
  }

  byId("refresh-state").textContent =
    "Last refresh completed · next update in 5 seconds";
}

async function refreshPlatform() {
  byId("refresh-state").textContent = "Refreshing live sources…";

  try {
    const response = await fetch("/api/platform", {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Platform API returned ${response.status}`);
    }

    renderPlatform(await response.json());
  } catch (error) {
    document.body.dataset.state = "offline";
    byId("connection-label").textContent = "Dashboard API offline";
    byId("platform-headline").textContent =
      "The live platform API is unreachable";
    byId("platform-summary").textContent =
      "No fallback data is displayed. Check the backend deployment and network path.";
    byId("updated-at").textContent = "Unavailable";
    byId("refresh-state").textContent = error.message;
  }
}

renderChart("cpu-chart", history.cpu, "#47e6b1");
renderChart("memory-chart", history.memory, "#7196ff");
refreshPlatform();
window.setInterval(refreshPlatform, 5000);
