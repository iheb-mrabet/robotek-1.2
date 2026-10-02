"""Check Falco scraping without emitting internal metrics or metadata."""
import json
import sys
import urllib.parse
import urllib.request

def check():
    base = "http://robotek-monitoring-prometheus.monitoring.svc.cluster.local:9090"
    def query(expression):
        url = base + "/api/v1/query?" + urllib.parse.urlencode({"query": expression})
        with urllib.request.urlopen(url, timeout=15) as response:
            payload = json.load(response)
        assert payload["status"] == "success"
        return payload["data"]["result"]
    targets = query('up{namespace="runtime-security"}')
    assert targets and all(float(row["value"][1]) == 1 for row in targets)
    metrics = query('{__name__=~"falcosecurity_.*"}')
    assert metrics
    print("PASS Falco metrics are available")

try:
    check()
except Exception:
    print("FAIL Falco metrics availability check")
    sys.exit(1)
