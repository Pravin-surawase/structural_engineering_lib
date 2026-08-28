#!/usr/bin/env bash
# Resolve the repository Python interpreter across primary and linked worktrees.
#
# When to use: internal launcher for run.sh, pre-commit, and Python subprocess
# orchestration. Callers pass normal Python arguments after this script. In a
# linked worktree, use --diagnose before evidence-producing tests and require
# source_bound=true; the selected interpreter may live in the primary checkout
# while imports must come from the invoking worktree.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "${1:-}" == "--diagnose" ]]; then
    export STRUCTURAL_LIB_RUNTIME_REPO_ROOT="$REPO_ROOT"
    set -- -c '
import json
import os
import sys
from pathlib import Path

import structural_lib

repo_root = Path(os.environ["STRUCTURAL_LIB_RUNTIME_REPO_ROOT"]).resolve()
module_path = Path(structural_lib.__file__).resolve()
source_root = (repo_root / "Python" / "structural_lib").resolve()
print(json.dumps({
    "interpreter": str(Path(sys.executable).resolve()),
    "repository": str(repo_root),
    "module": str(module_path),
    "source_bound": module_path.is_relative_to(source_root),
}))
'
fi

run_python_candidate() {
    local candidate="$1"
    local bound_pythonpath="$REPO_ROOT/Python:$REPO_ROOT"
    local caller_pythonpath="${PYTHONPATH:-}"
    shift
    if [[ -n "$candidate" && -x "$candidate" ]]; then
        case "$(uname -s)" in
            MINGW*|MSYS*|CYGWIN*)
                local native_root
                local native_caller_pythonpath="$caller_pythonpath"
                native_root="$(cygpath -w "$REPO_ROOT")"
                bound_pythonpath="${native_root}\\Python;${native_root}"
                if [[ -n "$native_caller_pythonpath" ]]; then
                    if [[ ! "$native_caller_pythonpath" =~ ^[A-Za-z]:[\\/].* && "$native_caller_pythonpath" != *";"* ]]; then
                        native_caller_pythonpath="$(cygpath -wp "$native_caller_pythonpath")"
                    fi
                    bound_pythonpath="$bound_pythonpath;$native_caller_pythonpath"
                fi
                MSYS2_ENV_CONV_EXCL="${MSYS2_ENV_CONV_EXCL:+$MSYS2_ENV_CONV_EXCL;}PYTHONPATH" \
                    PYTHONPATH="$bound_pythonpath" exec "$candidate" "$@"
                ;;
        esac
        if [[ -n "$caller_pythonpath" ]]; then
            bound_pythonpath="$bound_pythonpath:$caller_pythonpath"
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
