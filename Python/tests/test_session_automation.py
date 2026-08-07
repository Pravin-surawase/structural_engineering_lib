"""Regression tests for maintenance session automation."""

from __future__ import annotations

import importlib
import json
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


def test_pr_status_is_terminal_first_and_browser_is_explicit():
    run_sh = (REPO_ROOT / "run.sh").read_text(encoding="utf-8")
    status_body = run_sh.split("        status)", 1)[1].split("        *)", 1)[0]

    assert 'if [[ "${1:-}" == "--web" ]]' in status_body
    assert status_body.count("gh pr view --web") == 1
    assert "--json number,title,state,url" in status_body


def test_usage_checkpoint_records_observable_fields_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    monkeypatch.setattr(
        session,
        "_git_checkpoint_state",
        lambda: {"branch": "task/TEST", "head": "abc1234", "working_tree_files": 2},
    )
    args = session.build_parser().parse_args(
        [
            "usage",
            "--checkpoint",
            "milestone",
            "--task-id",
            "MAINT-001",
            "--model",
            "gpt-5.6-sol",
            "--reasoning",
            "high",
            "--elapsed-min",
            "45",
            "--verification",
            "targeted tests pass",
        ]
    )

    assert session.cmd_usage(args) == 0
    entry = json.loads(usage_log.read_text(encoding="utf-8"))
    assert entry["task_id"] == "MAINT-001"
    assert entry["model"] == "gpt-5.6-sol"
    assert entry["elapsed_min"] == 45
    assert entry["billing_tokens"] is None
    assert entry["billing_cost"] is None
    assert entry["verification"] == ["targeted tests pass"]


def test_tool_registry_discovers_all_copilot_skills():
    tool_registry = importlib.import_module("scripts.tool_registry")
    registry = tool_registry.load_registry()
    skill_names = {name for name in registry if name.startswith("skill:")}

    assert len(skill_names) == 14
    assert "skill:quality-gate" in skill_names
    assert "skill:release-preflight" in skill_names
    assert "skill:user-acceptance-test" in skill_names
    assert "check streamlit code" not in registry


def test_generated_indexes_do_not_emit_trailing_space_hard_breaks():
    generator = (REPO_ROOT / "scripts" / "generate_enhanced_index.py").read_text(
        encoding="utf-8"
    )

    assert 'f"**Type:** {type_label}  "' not in generator
    assert "f\"**Last Updated:** {index['last_updated']}  \"" not in generator
