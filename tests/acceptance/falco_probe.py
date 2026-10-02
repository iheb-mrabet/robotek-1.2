"""Inspect existing Falco metrics through the in-cluster Prometheus API."""
import json
import urllib.parse
import urllib.request

base = 'http://robotek-monitoring-prometheus.monitoring.svc.cluster.local:9090'

def query(expression):
    url = base + '/api/v1/query?' + urllib.parse.urlencode({'query': expression})
    with urllib.request.urlopen(url, timeout=15) as response:
        payload = json.load(response)
    assert payload['status'] == 'success', payload
    return payload['data']['result']

targets = query('up{namespace="runtime-security"}')
print('FALCO_TARGETS', json.dumps(targets), flush=True)
assert targets and all(float(row['value'][1]) == 1 for row in targets), 'Falco metrics target is unavailable'
metrics = query('{__name__=~"falcosecurity_.*"}')
names = sorted({row['metric']['__name__'] for row in metrics})
print('FALCO_METRIC_NAMES', json.dumps(names), flush=True)
for row in metrics:
    if any(word in row['metric']['__name__'] for word in ['version', 'engine', 'rules_matches', 'drops']):
        print('FALCO_METRIC', json.dumps(row), flush=True)
assert names, 'No native Falco metrics found'
print('PASS Falco native metrics are being scraped', flush=True)
