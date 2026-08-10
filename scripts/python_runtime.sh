#!/usr/bin/env bash
# Resolve the repository Python interpreter across primary and linked worktrees.
#
# When to use: internal launcher for run.sh, pre-commit, and Python subprocess
# orchestration. Callers pass normal Python arguments after this script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

run_python_candidate() {
    local candidate="$1"
    local bound_pythonpath="$REPO_ROOT/Python:$REPO_ROOT"
    shift
    if [[ -n "$candidate" && -x "$candidate" ]]; then
        if [[ -n "${PYTHONPATH:-}" ]]; then
            bound_pythonpath="$bound_pythonpath:$PYTHONPATH"
        fi
        PYTHONPATH="$bound_pythonpath" exec "$candidate" "$@"
    fi
}

if [[ -n "${STRUCTURAL_LIB_PYTHON:-}" ]]; then
    if [[ ! -x "$STRUCTURAL_LIB_PYTHON" ]]; then
        echo "ERROR: STRUCTURAL_LIB_PYTHON is not executable: $STRUCTURAL_LIB_PYTHON" >&2
        exit 1
    fi
    run_python_candidate "$STRUCTURAL_LIB_PYTHON" "$@"
fi

run_python_candidate "$REPO_ROOT/.venv/bin/python" "$@"

git_common_dir="$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
if [[ -n "$git_common_dir" ]]; then
    primary_worktree="$(dirname "$git_common_dir")"
    if [[ "$primary_worktree" != "$REPO_ROOT" ]]; then
        run_python_candidate "$primary_worktree/.venv/bin/python" "$@"
    fi
fi

if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    run_python_candidate "$VIRTUAL_ENV/bin/python" "$@"
fi

echo "ERROR: No project Python interpreter found." >&2
echo "Checked STRUCTURAL_LIB_PYTHON, this worktree's .venv, the primary worktree's .venv, and VIRTUAL_ENV." >&2
echo "Create .venv in the primary checkout or set STRUCTURAL_LIB_PYTHON to an executable interpreter." >&2
exit 1
