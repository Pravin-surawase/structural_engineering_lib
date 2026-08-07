"""Regression tests for maintenance session automation."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

session = importlib.import_module("scripts.session")


@pytest.mark.parametrize(
    "heading",
    [
        "## 2026-08-07 — Session 101",
        "## 2026-08-07 — Session — Maintenance",
        "## 2026-08-07 — Maintenance Recovery Session",
    ],
)
def test_session_heading_marker_accepts_descriptive_titles(heading: str):
    match = session.DATE_RE.match(heading)
    assert match is not None
    assert match.group(1) == "2026-08-07"


def test_latest_session_block_does_not_rewind_descriptive_heading():
    lines = [
        "# Session Log",
        "## 2026-08-07 — Maintenance Recovery Session",
        "**Focus:** current recovery",
        "## 2026-04-07 — Session — Old work",
        "**Focus:** old release",
    ]

    entry_date, block = session._latest_session_block(lines)

    assert entry_date == "2026-08-07"
    assert "**Focus:** current recovery" in block
    assert "old release" not in "\n".join(block)


def test_last_session_date_reads_multiline_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    session_log = tmp_path / "SESSION_LOG.md"
    session_log.write_text(
        """# Session Log

## 2026-08-07 — Maintenance Recovery Session
**Focus:** current recovery

## 2026-04-07 — Session — Old work
**Focus:** old release
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "SESSION_LOG", session_log)

    assert session._get_last_session_date() == "2026-04-07"


@pytest.mark.parametrize("heading", ["## Active", "## 🔴 Active"])
@pytest.mark.parametrize("task_id", ["MAINT-005", "**MAINT-005**"])
def test_active_task_reader_accepts_current_and_legacy_headings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, heading: str, task_id: str
):
    tasks = tmp_path / "TASKS.md"
    tasks.write_text(
        f"""# Tasks

{heading}

| ID | Task | Owner | Status |
|----|------|-------|--------|
| {task_id} | Finish maintenance | Main Agent | 🚧 IN PROGRESS |

## Up Next
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "TASKS_MD", tasks)

    assert session.get_active_tasks() == [("MAINT-005", "Finish maintenance", "")]


def test_commit_summary_uses_exclusive_previous_day_boundary(
    monkeypatch: pytest.MonkeyPatch,
):
    seen: list[list[str]] = []

    def fake_run(args, **kwargs):
        seen.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(session.subprocess, "run", fake_run)

    assert session._get_commits_since("2026-04-07") == []
    assert "--after=2026-04-07 23:59:59" in seen[0]


def test_launcher_port_discovery_is_listener_only():
    launcher = (REPO_ROOT / "scripts" / "launch_stack.sh").read_text(encoding="utf-8")
    function_body = launcher.split("get_process_on_port()", 1)[1].split(
        "kill_port()", 1
    )[0]
    commands = "\n".join(
        line for line in function_body.splitlines() if not line.lstrip().startswith("#")
    )

    assert 'lsof -nP -tiTCP:"$port" -sTCP:LISTEN' in commands
    assert "lsof -ti :" not in commands
