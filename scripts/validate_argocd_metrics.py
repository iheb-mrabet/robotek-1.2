"""Validate ServiceMonitor discovery against the actual pinned Argo Helm render."""

import sys
from pathlib import Path

import yaml


def validate(argo_path: str, monitoring_path: str) -> None:
    argo = [item for item in yaml.safe_load_all(Path(argo_path).read_text()) if item]
    monitoring = [item for item in yaml.safe_load_all(Path(monitoring_path).read_text()) if item]
    monitors = [
        item
        for item in monitoring
        if item["kind"] == "ServiceMonitor"
        and item["metadata"]["name"].startswith("robotek-argocd-")
    ]
    if len(monitors) != 5:
        raise ValueError(f"Expected five Argo ServiceMonitors, found {len(monitors)}")
    if any(item["kind"] == "ServiceMonitor" for item in argo):
        raise ValueError("Bootstrap must work before Prometheus Operator CRDs exist")
    for monitor in monitors:
        labels = monitor["spec"]["selector"]["matchLabels"]
        namespaces = monitor["spec"]["namespaceSelector"]["matchNames"]
        matches = [
            item
            for item in argo
            if item["kind"] == "Service"
            and item["metadata"]["namespace"] in namespaces
            and all(item["metadata"]["labels"].get(key) == value for key, value in labels.items())
        ]
        if len(matches) != 1:
            raise ValueError(f"{monitor['metadata']['name']} selects {len(matches)} Services")
        ports = {port["name"] for port in matches[0]["spec"]["ports"]}
        if any(endpoint["port"] not in ports for endpoint in monitor["spec"]["endpoints"]):
            raise ValueError(f"{monitor['metadata']['name']} references a missing metrics port")
        print(f"PASS {monitor['metadata']['name']} selects {matches[0]['metadata']['name']}")


if __name__ == "__main__":
    validate(*sys.argv[1:])
