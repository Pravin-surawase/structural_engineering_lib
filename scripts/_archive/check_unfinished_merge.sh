#!/usr/bin/env bash
# Compatibility entrypoint. The shared kernel detects every operation from the
# invoking worktree's real Git administration path. Standalone use fails on an
# operation; the existing pre-commit caller passes the explicit completion flag.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/python_runtime.sh" "$SCRIPT_DIR/git_state.py" \
  --guard operation "$@"
