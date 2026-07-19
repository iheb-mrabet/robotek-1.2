#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:?Usage: generate_delivery_metadata.sh IMAGE DIGEST [VERSION]}"
DIGEST="${2:?Usage: generate_delivery_metadata.sh IMAGE DIGEST [VERSION]}"
VERSION="${3:-${GITHUB_REF_NAME:-development}}"

OUTPUT_DIR="reports/delivery"
OUTPUT_FILE="${OUTPUT_DIR}/metadata.json"

mkdir -p "${OUTPUT_DIR}"

python3 - \
  "${IMAGE}" \
  "${DIGEST}" \
  "${VERSION}" \
  "${OUTPUT_FILE}" <<'PY'
import datetime
import json
import os
import sys

image = sys.argv[1]
digest = sys.argv[2]
version = sys.argv[3]
output_file = sys.argv[4]

metadata = {
    "repository": os.environ.get(
        "GITHUB_REPOSITORY",
        "iheb-mrabet/robotek-1.2",
    ),
    "commit_sha": os.environ.get("GITHUB_SHA", "local"),
    "workflow_name": os.environ.get(
        "GITHUB_WORKFLOW",
        "local",
    ),
    "workflow_run_id": os.environ.get(
        "GITHUB_RUN_ID",
        "local",
    ),
    "workflow_run_number": os.environ.get(
        "GITHUB_RUN_NUMBER",
        "local",
    ),
    "ros_distribution": "jazzy",
    "image": image,
    "image_digest": digest,
    "immutable_reference": f"{image}@{digest}",
    "version": version,
    "build_timestamp": datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat(),
}

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(metadata, file, indent=2)
    file.write("\n")

print(f"Generated {output_file}")
PY
