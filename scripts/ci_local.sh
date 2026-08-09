#!/usr/bin/env bash
# Local equivalent of the maintained PR validation lanes.
#
# When to use: Before publishing a broad Python/FastAPI/React change when the
# quick gate is insufficient. This command validates; it does not install or
# replace environments and it does not perform Git/GitHub operations.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
"${REPO_ROOT}/run.sh" check
"${REPO_ROOT}/run.sh" test
"${REPO_ROOT}/run.sh" test --fastapi
"${REPO_ROOT}/run.sh" frontend check

echo "OK: local CI checks passed"
