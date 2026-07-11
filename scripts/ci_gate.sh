#!/usr/bin/env bash
set -euo pipefail

for variable in FAST_GATE_RESULT UNIT_TESTS_RESULT; do
  result="${!variable:-missing}"
  if [[ "${result}" != "success" ]]; then
    echo "CI gate failed: ${variable}=${result}" >&2
    exit 1
  fi
done

require_post_merge="${REQUIRE_POST_MERGE:-false}"
for variable in INTEGRATION_RESULT SIMULATION_RESULT; do
  result="${!variable:-missing}"
  if [[ "${require_post_merge}" == "true" ]]; then
    if [[ "${result}" != "success" ]]; then
      echo "CI gate failed: ${variable}=${result}; post-merge tiers are required" >&2
      exit 1
    fi
  elif [[ "${result}" != "success" && "${result}" != "skipped" ]]; then
    echo "CI gate failed: ${variable}=${result}" >&2
    exit 1
  fi
done

echo "CI gate passed."
