#!/usr/bin/env bash
# Compatibility entrypoint. Fails closed on main, detached, or unknown state.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/python_runtime.sh" "$SCRIPT_DIR/git_state.py" --guard branch "$@"
