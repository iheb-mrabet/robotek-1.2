"""Verify a benign terminal-shell event without exposing event metadata."""
import json
import pty
import sys
import time
import urllib.parse
import urllib.request

def check():
    base = 'http://robotek-monitoring-prometheus.monitoring.svc.cluster.local:9090'
    def query(expression):
        url = base + '/api/v1/query?' + urllib.parse.urlencode({'query': expression})
        with urllib.request.urlopen(url, timeout=15) as response:
            payload = json.load(response)
        assert payload['status'] == 'success'
        return payload['data']['result']
    targets = query('up{namespace="runtime-security"}')
    assert targets and all(float(row['value'][1]) == 1 for row in targets)
    native = query('falcosecurity_falco_version_info')
    assert native
    expression = 'sum(falcosecurity_falco_rules_matches_total{rule_name="Terminal shell in container"})'
    def count():
        rows = query(expression)
        return float(rows[0]['value'][1]) if rows else 0.0
    before = count()
    # A short shell on an allocated PTY exercises Falco's terminal-shell rule.
    # The command only prints a marker: no mounts, privileges or file writes.
    assert pty.spawn(['/bin/sh', '-c', 'printf ROBOTEK_FALCO_ACCEPTANCE']) == 0
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        time.sleep(5)
        if count() > before:
            print('PASS fresh Falco terminal-shell detection counter increased')
            return
    raise AssertionError('No fresh detection counter increase')

try:
    check()
except Exception:
    print('FAIL fresh Falco detection check')
    sys.exit(1)
