"""Verify a benign terminal-exec detection without exposing event metadata."""
import json
import pty
import subprocess
import sys
import time

def check():
    data = json.loads(subprocess.check_output([
        "kubectl", "-n", "robotek-staging", "get", "pods",
        "-l", "app.kubernetes.io/instance=robotek-staging", "-o", "json"
    ], stderr=subprocess.DEVNULL))
    ready = [p for p in data["items"] if p["status"].get("phase") == "Running"
             and all(c.get("ready") for c in p["status"].get("containerStatuses", []))]
    assert ready
    pod = sorted(ready, key=lambda p:p["metadata"]["creationTimestamp"])[-1]["metadata"]["name"]
    def query(expression):
        code = """import json, urllib.parse, urllib.request
url='http://robotek-monitoring-prometheus.monitoring.svc.cluster.local:9090/api/v1/query?'+urllib.parse.urlencode({'query':EXPRESSION})
with urllib.request.urlopen(url,timeout=15) as r:
 p=json.load(r)
assert p['status']=='success'
rows=p['data']['result']
print(float(rows[0]['value'][1]) if rows else 0.0)
""".replace("EXPRESSION", repr(expression))
        output = subprocess.check_output([
            "kubectl", "-n", "robotek-staging", "exec", "-i", "-c", "robotek", pod,
            "--", "python3", "-"
        ], input=code.encode(), stderr=subprocess.DEVNULL, timeout=25)
        return float(output)
    assert query('min(up{namespace="runtime-security"})') == 1
    assert query("sum(falcosecurity_falco_version_info)") >= 1
    expression = 'sum(falcosecurity_falco_rules_matches_total{rule_name="Terminal shell in container"})'
    before = query(expression)
    # Allocate a local PTY so kubectl requests a real container terminal.
    # The executed shell only prints a marker; no privilege or file changes.
    assert pty.spawn([
        "kubectl", "-n", "robotek-staging", "exec", "-it", "-c", "robotek", pod,
        "--", "/bin/sh", "-c", "printf ROBOTEK_FALCO_ACCEPTANCE"
    ]) == 0
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        time.sleep(5)
        if query(expression) > before:
            print("PASS fresh Falco terminal-shell detection")
            return
    raise AssertionError("No fresh detection counter increase")

try:
    check()
except Exception:
    print("FAIL fresh Falco detection check")
    sys.exit(1)
