const byId = (id) => document.getElementById(id);

function renderRobot(robot) {
  byId("status").textContent = robot.status;
  byId("battery").textContent = robot.battery;
  byId("battery-meter").style.width = `${robot.battery}%`;
  byId("mission").textContent = robot.mission;
  byId("destination").textContent = `Destination: ${robot.destination}`;
  byId("deliveries").textContent = robot.completed_deliveries;
  byId("release").textContent = robot.release;
  byId("connection").textContent = "Robot online";
  byId("updated").textContent = `Updated ${new Date().toLocaleTimeString()}`;
  document.body.dataset.state = "online";
}

async function refreshRobot() {
  try {
    const response = await fetch("/api/robot", { cache: "no-store" });
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    renderRobot(await response.json());
  } catch (error) {
    byId("connection").textContent = "Telemetry temporarily unavailable";
    byId("updated").textContent = error.message;
    document.body.dataset.state = "offline";
  }
}

refreshRobot();
window.setInterval(refreshRobot, 10000);
