#!/usr/bin/env python3
"""Smart test runner — run only tests related to changed files.

Usage:
    .venv/bin/python scripts/test_changed.py              # Test files changed vs main
    .venv/bin/python scripts/test_changed.py --staged      # Test staged files only
    .venv/bin/python scripts/test_changed.py --last-commit  # Test files from last commit
    .venv/bin/python scripts/test_changed.py --verbose      # Show mapping decisions

Maps changed source files to their test files:
    Python/structural_lib/codes/is456/flexure.py  →  tests/test_flexure.py
    Python/structural_lib/services/api.py         →  tests/test_api.py
    fastapi_app/routers/design.py                 →  fastapi_app/tests/test_design*.py
    react_app/src/hooks/useCSVImport.ts           →  (skip — no Python tests)

Falls back to full suite if too many files changed or mapping unclear.
"""

import os
import subprocess
import sys
import glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PYTHON = os.path.join(REPO_ROOT, ".venv", "bin", "python")

# Map source directories/patterns to test directories/patterns
SOURCE_TO_TEST_MAP = [
    # (source_prefix, test_pattern_func)
    ("Python/structural_lib/codes/is456/", lambda f: _is456_test(f)),
    ("Python/structural_lib/services/", lambda f: _services_test(f)),
    ("Python/structural_lib/core/", lambda f: _glob_tests(f, "Python/tests/test_*")),
    (
        "Python/structural_lib/insights/",
        lambda f: _glob_tests(f, "Python/tests/test_insights*"),
    ),
    (
        "Python/structural_lib/visualization/",
        lambda f: _glob_tests(f, "Python/tests/test_geometry*"),
    ),
    (
        "Python/structural_lib/reports/",
        lambda f: _glob_tests(f, "Python/tests/test_report*"),
    ),
    ("fastapi_app/routers/", lambda f: _fastapi_test(f)),
    ("fastapi_app/", lambda f: _glob_tests(f, "fastapi_app/tests/test_*")),
]

VERBOSE = False


def _log(msg: str) -> None:
    if VERBOSE:
        print(f"  \033[2m→ {msg}\033[0m")


def _basename_no_ext(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]


def _is456_test(filepath: str) -> list[str]:
    """Map IS 456 code files to tests."""
    name = _basename_no_ext(filepath)
    patterns = [
        f"Python/tests/test_{name}*",
        "Python/tests/test_is456*",
    ]
    results = []
    for p in patterns:
        results.extend(glob.glob(os.path.join(REPO_ROOT, p)))
    return results


def _services_test(filepath: str) -> list[str]:
    """Map service files to tests."""
    name = _basename_no_ext(filepath)
    patterns = [
        f"Python/tests/test_{name}*",
        "Python/tests/test_api*",
        "Python/tests/test_adapter*",
    ]
    results = []
    for p in patterns:
        results.extend(glob.glob(os.path.join(REPO_ROOT, p)))
    return results


def _fastapi_test(filepath: str) -> list[str]:
    """Map FastAPI router files to tests."""
    name = _basename_no_ext(filepath)
    patterns = [
        f"fastapi_app/tests/test_{name}*",
        "fastapi_app/tests/test_routers*",
    ]
    results = []
    for p in patterns:
        results.extend(glob.glob(os.path.join(REPO_ROOT, p)))
    return results


def _glob_tests(filepath: str, pattern: str) -> list[str]:
    """Generic glob-based test finding."""
    return glob.glob(os.path.join(REPO_ROOT, pattern))


def get_changed_files(mode: str = "diff") -> list[str]:
    """Get list of changed files."""
    if mode == "staged":
        cmd = ["git", "diff", "--cached", "--name-only"]
    elif mode == "last-commit":
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
    else:
        # Changes vs current HEAD (uncommitted)
        cmd = ["git", "diff", "--name-only", "HEAD"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        return []

    return [f for f in result.stdout.strip().split("\n") if f]


def map_to_tests(changed_files: list[str]) -> set[str]:
    """Map changed source files to test files."""
    test_files: set[str] = set()

    for filepath in changed_files:
        mapped = False
        for prefix, finder in SOURCE_TO_TEST_MAP:
            if filepath.startswith(prefix):
                tests = finder(filepath)
                for t in tests:
                    rel = os.path.relpath(t, REPO_ROOT)
                    test_files.add(rel)
                    _log(f"{filepath} → {rel}")
                mapped = True
                break

        if not mapped:
            # Skip non-Python files (React, docs, etc.)
            if filepath.endswith(".py"):
                _log(f"{filepath} → no test mapping (will include in general)")
            else:
                _log(f"{filepath} → skipped (not Python)")

    return test_files


def main() -> None:
    global VERBOSE

    mode = "diff"
    extra_pytest_args = []

    for arg in sys.argv[1:]:
        if arg == "--staged":
            mode = "staged"
        elif arg == "--last-commit":
            mode = "last-commit"
        elif arg == "--verbose" or arg == "-v":
            VERBOSE = True
        else:
            extra_pytest_args.append(arg)

    changed = get_changed_files(mode)

    if not changed:
        print("No changed files detected. Nothing to test.")
        return

    print(f"\033[1mChanged files:\033[0m {len(changed)}")
    for f in changed[:10]:
        print(f"  {f}")
    if len(changed) > 10:
        print(f"  ... and {len(changed) - 10} more")

    # If too many files changed, just run everything
    if len(changed) > 30:
        print("\n\033[33m30+ files changed — running full test suite\033[0m")
        os.chdir(os.path.join(REPO_ROOT, "Python"))
        os.execv(
            VENV_PYTHON,
            [VENV_PYTHON, "-m", "pytest", "tests/", "-v"] + extra_pytest_args,
        )
        return

    test_files = map_to_tests(changed)

    if not test_files:
        print("\nNo matching test files found for changes. Skipping.")
        return

    # Deduplicate and filter to existing files
    existing = sorted(
        t for t in test_files if os.path.exists(os.path.join(REPO_ROOT, t))
    )

    if not existing:
        print("\nMapped test files don't exist. Skipping.")
        return

    print(f"\n\033[1mRunning {len(existing)} test file(s):\033[0m")
    for t in existing:
        print(f"  \033[32m→\033[0m {t}")

    # Run pytest with the specific test files
    cmd = [VENV_PYTHON, "-m", "pytest", "-v"] + extra_pytest_args + existing
    print()
    os.chdir(REPO_ROOT)
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
