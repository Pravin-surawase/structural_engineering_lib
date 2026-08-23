#!/usr/bin/env bash
# Compatibility bridge for the retired all-folder index generator.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "DEPRECATED: generated folder indexes are retired; validating live context."
exec "$PROJECT_ROOT/scripts/python_runtime.sh" \
    "$PROJECT_ROOT/scripts/repo_context.py" validate
