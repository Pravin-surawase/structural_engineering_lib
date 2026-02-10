"""Shared utility functions for scripts/.

Common patterns extracted from 90+ scripts to eliminate duplication:
- Repository root / Python path resolution
- Subprocess execution helpers
- AST file parsing helpers

Usage from any script in scripts/:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _lib.utils import REPO_ROOT, PYTHON_DIR, add_python_path, run_command
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def get_repo_root() -> Path:
    """Resolve repository root from any script location.

    Works regardless of current working directory by using
    this file's location as an anchor.
    """
    return Path(__file__).resolve().parent.parent.parent


# Pre-computed constants for convenience
REPO_ROOT: Path = get_repo_root()
PYTHON_DIR: Path = REPO_ROOT / "Python"
STRUCTURAL_LIB: Path = PYTHON_DIR / "structural_lib"
SCRIPTS_DIR: Path = REPO_ROOT / "scripts"
DOCS_DIR: Path = REPO_ROOT / "docs"


def add_python_path() -> None:
    """Add Python/structural_lib to sys.path if not already present.

    Call this before importing from structural_lib in scripts.
    """
    python_str = str(PYTHON_DIR)
    if python_str not in sys.path:
        sys.path.insert(0, python_str)


def run_command(
    cmd: list[str] | str,
    *,
    cwd: Path | str | None = None,
    capture: bool = True,
    check: bool = False,
    timeout: int | None = 30,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command with sensible defaults.

    Args:
        cmd: Command and arguments (list or string).
        cwd: Working directory (defaults to REPO_ROOT).
        capture: Capture stdout/stderr (default True).
        check: Raise on non-zero exit (default False).
        timeout: Timeout in seconds (default 30, None for no timeout).

    Returns:
        CompletedProcess with stdout/stderr as strings.
    """
    if cwd is None:
        cwd = REPO_ROOT

    kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "text": True,
    }
    if capture:
        kwargs["capture_output"] = True
    if timeout is not None:
        kwargs["timeout"] = timeout
    if isinstance(cmd, str):
        kwargs["shell"] = True

    return subprocess.run(cmd, check=check, **kwargs)


def find_python_files(
    directory: Path,
    *,
    exclude_dirs: set[str] | None = None,
) -> list[Path]:
    """Find all .py files in a directory, excluding common non-source dirs.

    Args:
        directory: Root directory to search.
        exclude_dirs: Directory names to skip (defaults include __pycache__,
            .venv, node_modules, _archive).

    Returns:
        Sorted list of .py file paths.
    """
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".venv", "node_modules", "_archive", ".git"}

    files = []
    for py_file in directory.rglob("*.py"):
        if not any(part in exclude_dirs for part in py_file.parts):
            files.append(py_file)

    return sorted(files)
