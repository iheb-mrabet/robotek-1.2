#!/usr/bin/env bash
set -eo pipefail

for variable in FAST_GATE_RESULT UNIT_TESTS_RESULT INTEGRATION_RESULT; do
  result="${!variable:-missing}"
  if [[ "${result}" != "success" ]]; then
    echo "CI gate failed: ${variable}=${result}" >&2
    exit 1
  fi
done

require_post_merge="${REQUIRE_POST_MERGE:-false}"
variable=SIMULATION_RESULT
result="${SIMULATION_RESULT:-missing}"
if [[ "${require_post_merge}" == "true" ]]; then
  if [[ "${result}" != "success" ]]; then
    echo "CI gate failed: ${variable}=${result}; post-merge tiers are required" >&2
    exit 1
  fi
elif [[ "${result}" != "success" && "${result}" != "skipped" ]]; then
  echo "CI gate failed: ${variable}=${result}" >&2
  exit 1
fi

echo "CI gate passed."
