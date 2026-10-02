"""Exercise the real test dispatcher with isolated, deterministic runtimes.

The copied run.sh retains its complete entry point and usage-event wrapper.
Only its external Python/Node/usage commands are stubbed; no product suite,
dependency installation or shared session store is reached by these tests.
"""

from __future__ import annotations

import itertools
import os
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only
REPO_ROOT = Path(__file__).resolve().parents[2]
BASH = shutil.which("bash")

_RUNTIME_STUB = r"""#!/usr/bin/env bash
set -uo pipefail
fixture_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" == "-m" && "${2:-}" == "pytest" ]]; then
    if [[ "${3:-}" == "$fixture_root/fastapi_app/tests" ]]; then
        phase=fastapi
        result="${STUB_FASTAPI_STATUS:-0}"
    else
        phase=python
        result="${STUB_PYTHON_STATUS:-0}"
    fi
elif [[ "${1:-}" == "$fixture_root/scripts/node_runtime.py" ]]; then
    phase=react
    result="${STUB_REACT_STATUS:-0}"
elif [[ "${1:-}" == "$fixture_root/scripts/session.py" ]]; then
    phase=usage
    result="${STUB_USAGE_STATUS:-0}"
else
    printf 'Unexpected isolated runtime invocation\n' >&2
    exit 97
fi
printf '%s\0' "$phase" "$PWD" "$@" >> "$fixture_root/runtime-trace.bin"
printf '\0' >> "$fixture_root/runtime-trace.bin"
exit "$result"
"""


def _make_cli_fixture(tmp_path: Path, *, source: str | None = None) -> Path:
    if BASH is None:
        pytest.skip("Bash is unavailable; the repository shell entry point cannot run.")
    root = tmp_path / "isolated test repo"
    (root / "scripts").mkdir(parents=True)
    (root / "Python").mkdir()
    (root / "fastapi_app" / "tests").mkdir(parents=True)
    (root / "run.sh").write_text(
        source if source is not None else (REPO_ROOT / "run.sh").read_text(),
        encoding="utf-8",
    )
    runtime = root / "scripts" / "python_runtime.sh"
    runtime.write_text(_RUNTIME_STUB, encoding="utf-8")
    runtime.chmod(0o755)
    tools = root / "react_app" / "node_modules" / ".bin"
    tools.mkdir(parents=True)
    for tool in ("eslint", "tsc", "vite", "vitest"):
        (tools / tool).touch()
    return root


def _run_cli(
    root: Path,
    args: tuple[str, ...],
    *,
    statuses: tuple[int, int, int] = (0, 0, 0),
    usage_status: int = 0,
) -> tuple[subprocess.CompletedProcess[str], list[dict]]:
    env = os.environ.copy()
    env.update(
        STUB_PYTHON_STATUS=str(statuses[0]),
        STUB_FASTAPI_STATUS=str(statuses[1]),
        STUB_REACT_STATUS=str(statuses[2]),
        STUB_USAGE_STATUS=str(usage_status),
    )
    result = subprocess.run(
        [BASH, str(root / "run.sh"), "test", *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    trace = root / "runtime-trace.bin"
    calls = []
    if trace.exists():
        for record in trace.read_bytes().split(b"\0\0"):
            if record:
                phase, cwd, *argv = record.decode().split("\0")
                calls.append({"phase": phase, "cwd": cwd, "argv": argv})
    return result, calls


def _assert_usage(calls: list[dict], expected_status: int) -> None:
    usage = [c for c in calls if c["phase"] == "usage"]
    assert len(usage) == 1
    argv = usage[0]["argv"]
    assert argv[1:4] == ["usage", "--event", "test"]
    assert argv[argv.index("--result-code") + 1] == str(expected_status)
    assert int(argv[argv.index("--duration-sec") + 1]) >= 0


@pytest.mark.parametrize("statuses", itertools.product((0, 17), (0, 23), (0, 31)))
def test_all_runs_every_suite_and_retains_first_failure(tmp_path, statuses):
    root = _make_cli_fixture(tmp_path)
    result, calls = _run_cli(root, ("--all",), statuses=statuses)
    expected = next((status for status in statuses if status), 0)

    assert result.returncode == expected, result.stderr
    assert [c["phase"] for c in calls] == ["python", "fastapi", "react", "usage"]
    assert Path(calls[0]["cwd"]).name == "Python"
    assert calls[0]["argv"] == ["-m", "pytest", "tests/"]
    assert calls[1]["argv"][:2] == ["-m", "pytest"]
    assert calls[1]["argv"][2].endswith("/fastapi_app/tests")
    assert calls[2]["argv"][1:] == ["--", "npm", "--prefix", "react_app", "test"]
    _assert_usage(calls, expected)


@pytest.mark.parametrize(
    "option,phase,index",
    [("--python", "python", 0), ("--fastapi", "fastapi", 1), ("--react", "react", 2)],
)
@pytest.mark.parametrize("status", [0, 19])
def test_single_suite_retains_selection_arguments_and_status(
    tmp_path, option, phase, index, status
):
    root = _make_cli_fixture(tmp_path)
    statuses = [0, 0, 0]
    statuses[index] = status
    result, calls = _run_cli(root, (option, "-q"), statuses=tuple(statuses))

    assert result.returncode == status, result.stderr
    assert [c["phase"] for c in calls] == [phase, "usage"]
    assert calls[0]["argv"][-1] == "-q"
    if phase == "react":
        assert calls[0]["argv"][-2] == "--"
    _assert_usage(calls, status)


@pytest.mark.parametrize(
    "args,expected_argv",
    [
        ((), ["-m", "pytest", "tests/", "-v"]),
        (
            ("Python/tests/test_sample.py", "-q"),
            ["-m", "pytest", "tests/test_sample.py", "-q"],
        ),
    ],
)
def test_default_and_explicit_python_paths_keep_failure_and_forwarding(
    tmp_path, args, expected_argv
):
    root = _make_cli_fixture(tmp_path)
    result, calls = _run_cli(root, args, statuses=(29, 0, 0))

    assert result.returncode == 29, result.stderr
    assert [c["phase"] for c in calls] == ["python", "usage"]
    assert calls[0]["argv"] == expected_argv
    assert Path(calls[0]["cwd"]).name == "Python"
    _assert_usage(calls, 29)


@pytest.mark.parametrize("statuses", [(0, 0, 0), (17, 0, 0)])
def test_usage_recorder_failure_does_not_replace_test_result(tmp_path, statuses):
    root = _make_cli_fixture(tmp_path)
    result, calls = _run_cli(root, ("--all",), statuses=statuses, usage_status=61)

    assert result.returncode == statuses[0], result.stderr
    assert [c["phase"] for c in calls] == ["python", "fastapi", "react", "usage"]
    _assert_usage(calls, statuses[0])


@pytest.mark.parametrize(
    "option,expected_phases",
    [("--all", ["python", "fastapi", "usage"]), ("--react", ["usage"])],
)
def test_react_readiness_failure_cannot_be_replaced_by_runtime_success(
    tmp_path, option, expected_phases
):
    root = _make_cli_fixture(tmp_path)
    (root / "react_app" / "node_modules" / ".bin" / "eslint").unlink()
    result, calls = _run_cli(root, (option,))

    assert result.returncode == 1, result.stderr
    assert [c["phase"] for c in calls] == expected_phases
    assert "React dependencies are not ready" in result.stderr
    _assert_usage(calls, 1)


@pytest.mark.parametrize(
    "args", [("--all",), ("--python",), (), ("Python/tests/test_sample.py",)]
)
def test_missing_python_directory_prevents_wrong_directory_success(tmp_path, args):
    root = _make_cli_fixture(tmp_path)
    (root / "Python").rmdir()
    result, calls = _run_cli(root, args)

    assert result.returncode == 1, result.stderr
    expected_phases = ["fastapi", "react", "usage"] if args == ("--all",) else ["usage"]
    assert [c["phase"] for c in calls] == expected_phases
    _assert_usage(calls, 1)


@pytest.mark.parametrize("option", ["--all", "--react"])
def test_missing_python_launcher_fails_without_running_any_suite(tmp_path, option):
    root = _make_cli_fixture(tmp_path)
    (root / "scripts" / "python_runtime.sh").unlink()
    result, calls = _run_cli(root, (option,))

    assert result.returncode == 1, result.stderr
    assert calls == []
    assert "Python runtime launcher not found" in result.stderr
