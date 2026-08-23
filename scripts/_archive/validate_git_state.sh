#!/usr/bin/env bash
# Compatibility entrypoint. scripts/git_state.py owns all Git-state semantics.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/python_runtime.sh" "$SCRIPT_DIR/git_state.py" "$@"
