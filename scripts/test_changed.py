#!/usr/bin/env python3
"""Smart test runner — run only tests related to changed files.

When to use: After a bounded change when mapped Python/FastAPI tests provide a
faster feedback loop than the complete suite.

Usage:
    ./scripts/python_runtime.sh scripts/test_changed.py               # Uncommitted files
    ./scripts/python_runtime.sh scripts/test_changed.py --staged      # Staged files only
    ./scripts/python_runtime.sh scripts/test_changed.py --last-commit # Last commit
    ./scripts/python_runtime.sh scripts/test_changed.py --verbose     # Mapping decisions

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
from pathlib import Path

import verification as verification_control

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PYTHON = os.path.join(REPO_ROOT, "scripts", "python_runtime.sh")

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
        return list(verification_control.changed_paths(root=Path(REPO_ROOT)))

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        raise verification_control.VerificationError(
            f"changed-file Git query failed: {' '.join(cmd)}"
        )

    return [f for f in result.stdout.strip().split("\n") if f]


def map_to_tests(changed_files: list[str]) -> set[str]:
    """Map changed source files to test files."""
    test_files: set[str] = set()

    for filepath in changed_files:
        mapped = False
        if filepath.endswith(".py") and (
            filepath.startswith("Python/tests/")
            or filepath.startswith("fastapi_app/tests/")
        ):
            test_files.add(filepath)
            _log(f"{filepath} → exact changed test")
            continue
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


def _run(cmd: list[str]) -> int:
    _log("running: " + " ".join(cmd))
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


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

    try:
        manifest = verification_control.load_manifest(require_coverage=False)
        if mode == "diff":
            plan = verification_control.plan_changes(manifest)
        else:
            try:
                discovered = get_changed_files(mode)
            except verification_control.VerificationError as exc:
                plan = verification_control.classify_paths(
                    (), manifest, failure_reasons=(str(exc),)
                )
            else:
                plan = verification_control.classify_paths(discovered, manifest)
    except verification_control.VerificationError as exc:
        print(f"ERROR: verification control is invalid: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    changed = list(plan.changed_paths)

    if not changed and not plan.fail_closed:
        print("No changed files detected. Nothing to test.")
        return

    print(f"\033[1mChanged files:\033[0m {len(changed)}")
    for f in changed[:10]:
        print(f"  {f}")
    if len(changed) > 10:
        print(f"  ... and {len(changed) - 10} more")

    print(f"\n\033[1mImpacted domains:\033[0m {', '.join(plan.domains)}")
    if plan.fail_closed:
        reasons = [*plan.unknown_paths, *plan.failure_reasons]
        print(
            "\033[33mUnknown impact — every product test domain is required: "
            + "; ".join(reasons)
            + "\033[0m"
        )

    test_files = map_to_tests(changed)
    existing = sorted(
        t for t in test_files if os.path.exists(os.path.join(REPO_ROOT, t))
    )
    domains = set(plan.domains)
    full_python = "python" in domains and (
        len(changed) > 30
        or not existing
        or any(
            path.startswith("Python/")
            and not path.startswith("Python/tests/")
            and not any(
                path.startswith(prefix) for prefix, _finder in SOURCE_TO_TEST_MAP
            )
            for path in changed
        )
    )
    full_fastapi = "fastapi" in domains and (
        len(changed) > 30
        or not any(
            path.startswith("fastapi_app/") or path.startswith("Python/structural_lib/")
            for path in changed
        )
        or not any(path.startswith("fastapi_app/tests/") for path in existing)
    )

    commands: list[list[str]] = []
    if full_python:
        commands.append(
            [VENV_PYTHON, "-m", "pytest", "Python/tests/", "-v", *extra_pytest_args]
        )
    if full_fastapi:
        commands.append(
            [
                VENV_PYTHON,
                "-m",
                "pytest",
                "fastapi_app/tests/",
                "-v",
                *extra_pytest_args,
            ]
        )

    focused = [
        path
        for path in existing
        if not (full_python and path.startswith("Python/tests/"))
        and not (full_fastapi and path.startswith("fastapi_app/tests/"))
    ]
    focused_python = [path for path in focused if path.startswith("Python/tests/")]
    focused_fastapi = [
        path for path in focused if path.startswith("fastapi_app/tests/")
    ]
    if focused_python:
        commands.append(
            [
                VENV_PYTHON,
                "-m",
                "pytest",
                "-v",
                *extra_pytest_args,
                *focused_python,
            ]
        )
    if focused_fastapi:
        commands.append(
            [
                VENV_PYTHON,
                "-m",
                "pytest",
                "-v",
                *extra_pytest_args,
                *focused_fastapi,
            ]
        )
    if "react" in domains:
        commands.append([os.path.join(REPO_ROOT, "run.sh"), "test", "--react"])
    if "excel" in domains:
        commands.append(
            [
                VENV_PYTHON,
                os.path.join(REPO_ROOT, "scripts", "node_runtime.py"),
                "--",
                "npm",
                "--prefix",
                "excel_addin",
                "test",
            ]
        )

    if not commands:
        print("\nNo product test suite is owned by the impacted non-product domains.")
        return

    failed = 0
    for command in commands:
        print("\n\033[1mRunning:\033[0m " + " ".join(command))
        if _run(command) != 0:
            failed += 1
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
