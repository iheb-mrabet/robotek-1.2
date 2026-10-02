"""Verify the public platform contract without emitting private telemetry."""
import json
import sys
import urllib.request

def check():
    base = 'https://18-211-80-86.nip.io'
    def get(path):
        with urllib.request.urlopen(base + path, timeout=30) as response:
            assert response.status == 200
            return response.read().decode()
    assert 'Operations Control' in get('/')
    assert json.loads(get('/health')) == {'component':'backend', 'status':'ok'}
    assert json.loads(get('/ready')) == {'database':'connected', 'status':'ready'}
    p = json.loads(get('/api/platform'))
    assert p['data_policy'] == 'live-only'
    assert p['database']['connected'] is True
    robot, cluster, o = p['robot'], p['cluster'], p['observability']
    assert robot['exporter_up'] is True and robot['collection_errors'] == 0
    assert robot['nodes'] > 0 and robot['topics'] > 0 and robot['runtime_uptime_seconds'] > 0
    assert cluster['nodes_ready'] == cluster['nodes_total'] > 0
    assert cluster['pods_ready'] == cluster['pods_total'] > 0
    assert cluster['deployments_available'] == cluster['deployments_desired'] > 0
    assert o['prometheus_reachable'] is True
    assert o['targets_up'] == o['targets_total'] > 0
    assert o['gitops_synced'] == o['gitops_healthy'] == o['gitops_total'] > 0
    assert o['grafana']['reachable'] is True and o['grafana']['database'] == 'ok'
    assert p['alerts']['critical_firing'] == 0
    print('PASS public HTTPS and complete platform contract')

try:
    check()
except Exception:
    print('FAIL public platform contract')
    sys.exit(1)
