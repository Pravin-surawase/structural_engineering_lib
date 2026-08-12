"""Regression tests for maintenance session automation."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

session = importlib.import_module("scripts.session")
check_api = importlib.import_module("scripts.check_api")
validate_script_refs = importlib.import_module("scripts.validate_script_refs")
prompt_router = importlib.import_module("scripts.prompt_router")


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


def test_task_brief_reports_lane_route_and_safe_workflow(
    monkeypatch: pytest.MonkeyPatch,
):
    lane = {
        "branch": "codex/intake",
        "head": "abc12345",
        "dirty_files": 0,
        "base": "def67890",
        "base_ref": "origin/main",
        "upstream": "none",
        "worktrees": [],
        "attention": [],
        "root": "/tmp/intake",
    }
    monkeypatch.setattr(prompt_router, "collect_lane_state", lambda: lane)
    brief = prompt_router.build_task_brief("fix CSV import")

    assert brief["lane"] is lane
    assert brief["route"]["agent"]
    assert brief["workflow"]["start"][0].startswith("./run.sh session brief")
    assert "inspection-only" in brief["workflow"]["git_rule"]


def test_run_task_brief_and_index_help_are_read_only():
    before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    brief = subprocess.run(
        [str(REPO_ROOT / "run.sh"), "task", "brief", "fix CSV import"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    help_result = subprocess.run(
        [str(REPO_ROOT / "run.sh"), "generate", "indexes", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    task_help = subprocess.run(
        [str(REPO_ROOT / "run.sh"), "task", "brief", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    after = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    assert brief.returncode == 0, brief.stderr
    assert "Lane:" in brief.stdout
    assert "Route:" in brief.stdout
    assert "Safe start:" in brief.stdout
    assert help_result.returncode == 0, help_result.stderr
    assert "Usage: ./run.sh generate indexes" in help_result.stdout
    assert task_help.returncode == 0, task_help.stderr
    assert "Usage: ./run.sh task brief" in task_help.stdout
    assert before == after


def test_index_generator_uses_worktree_runtime_in_temp_project(tmp_path: Path):
    """The index launcher must resolve its runtime from its own worktree."""
    project = tmp_path / "linked-worktree"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    (project / "docs").mkdir()
    generator = REPO_ROOT / "scripts" / "generate_all_indexes.sh"
    launcher = scripts / "generate_all_indexes.sh"
    launcher.write_text(generator.read_text(encoding="utf-8"), encoding="utf-8")
    launcher.chmod(0o755)
    calls = tmp_path / "runtime-calls.txt"
    runtime = scripts / "python_runtime.sh"
    runtime.write_text(
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "${RUNTIME_ARGS:?}"\n',
        encoding="utf-8",
    )
    runtime.chmod(0o755)

    result = subprocess.run(
        [str(launcher)],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=10,
        env={**os.environ, "RUNTIME_ARGS": str(calls)},
    )

    assert result.returncode == 0, result.stderr
    recorded = calls.read_text(encoding="utf-8")
    assert "scripts/generate_enhanced_index.py --json-only docs" in recorded
    assert "scripts/generate_enhanced_index.py scripts" in recorded


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
    class SessionDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2026, 8, 7)

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
    monkeypatch.setattr(session, "date", SessionDate)

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


@pytest.mark.parametrize(
    ("branch", "git_state", "trusted"),
    [
        ("codex/task", "Clean working tree", True),
        ("codex/task", "2 uncommitted change(s)", False),
        ("codex/task", "Unable to check", False),
        ("main", "Clean working tree", False),
        ("unknown", "Clean working tree", False),
        ("", "Clean working tree", False),
    ],
)
def test_session_trust_fails_closed_on_dirty_or_unknown_git_state(
    branch: str, git_state: str, trusted: bool
):
    result, _reason = session._evaluate_trust(branch, git_state)

    assert result is trusted


def test_git_identity_helpers_reject_failed_commands(monkeypatch: pytest.MonkeyPatch):
    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args, 128, "", "fatal: not a repository")

    monkeypatch.setattr(session.subprocess, "run", fake_run)

    assert session.get_branch() == "unknown"
    assert session.get_uncommitted_status() == "Unable to check"


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


def test_run_sh_does_not_own_git_or_github_lifecycle():
    run_sh = (REPO_ROOT / "run.sh").read_text(encoding="utf-8")
    assert "_cmd_commit" not in run_sh
    assert "_cmd_pr" not in run_sh
    assert "scripts/ai_commit.sh" not in run_sh
    assert "scripts/create_task_pr.sh" not in run_sh


def test_retired_git_lifecycle_paths_stay_absent():
    retired = (
        "scripts/ai_commit.sh",
        "scripts/safe_push.sh",
        "scripts/recover_git_state.sh",
        "scripts/finish_task_pr.sh",
        "scripts/create_task_pr.sh",
        "scripts/should_use_pr.sh",
        "scripts/install_git_hooks.sh",
        "scripts/git-hooks/pre-commit",
        "scripts/git-hooks/pre-push",
        "scripts/git-hooks/commit-msg",
    )
    assert not [path for path in retired if (REPO_ROOT / path).exists()]


def test_p0_missing_script_control_paths_stay_removed():
    run_sh = (REPO_ROOT / "run.sh").read_text(encoding="utf-8")
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "--vba" not in run_sh
    assert "run_vba_smoke_tests.py" not in run_sh
    assert "test_vba_adapter.py" not in run_sh
    assert "scripts/check_cost_optimizer_issues.py" not in pre_commit
    assert "scripts/check_streamlit.py" not in pre_commit
    assert "scripts/check_performance_issues.py" not in pre_commit


def test_script_reference_validator_fails_missing_control_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "existing.py").write_text("", encoding="utf-8")
    run_sh = tmp_path / "run.sh"
    run_sh.write_text(
        '"$SCRIPTS/existing.py"\n"$SCRIPTS/missing.py"\n', encoding="utf-8"
    )

    monkeypatch.setattr(validate_script_refs, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(validate_script_refs, "SCRIPTS_DIR", scripts_dir)
    monkeypatch.setattr(validate_script_refs, "CONTROL_FILES", {run_sh})

    issues = validate_script_refs.check_missing_targets(run_sh)

    assert [(issue["target"], issue["severity"]) for issue in issues] == [
        ("missing.py", "error")
    ]


def test_api_endpoint_extraction_stops_before_query_template():
    expression = (
        "`${API_BASE_URL}/api/v1/import/dual-csv${queryStr ? `?${queryStr}` : ''}`"
    )
    assert check_api._extract_endpoint(expression) == "/api/v1/import/dual-csv"


def test_api_call_method_extraction_stops_at_each_fetch(tmp_path: Path):
    client = tmp_path / "client.ts"
    client.write_text(
        """export async function load() {
  return fetch(`${API_BASE_URL}/api/v1/workflows/beam-template`, {
    headers: { Accept: 'application/json' },
  });
}
export async function run() {
  return fetch(`${API_BASE_URL}/api/v1/workflows/run`, {
    method: 'POST',
  });
}
""",
        encoding="utf-8",
    )

    calls, unresolved = check_api._extract_call_sites(client)

    assert unresolved == []
    assert [(call.endpoint, call.method) for call in calls] == [
        ("/api/v1/workflows/beam-template", "GET"),
        ("/api/v1/workflows/run", "POST"),
    ]


def test_api_route_shape_matches_dynamic_segments():
    assert check_api._same_route_shape(
        "/api/v1/export/{dynamic}", "/api/v1/export/{format}"
    )
    assert not check_api._same_route_shape(
        "/api/v1/export/{dynamic}", "/api/v1/export/archive/{format}"
    )


def test_api_contract_scan_fails_closed_without_typescript(tmp_path: Path):
    assert check_api.check_signatures(pages_dir=str(tmp_path)) == 1


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


def test_generated_json_indexes_end_with_newline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    generator = importlib.import_module("scripts.generate_enhanced_index")
    output = tmp_path / "scripts"
    output.mkdir()
    monkeypatch.setattr(generator, "PROJECT_ROOT", tmp_path)

    generator.generate_json({"folder": "scripts"}, output)

    assert (output / "index.json").read_bytes().endswith(b"\n")


def test_generated_index_hash_tracks_subfolder_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    generator = importlib.import_module("scripts.generate_enhanced_index")
    parent = tmp_path / "parent"
    child = parent / "child"
    child.mkdir(parents=True)
    (child / "first.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(generator, "PROJECT_ROOT", tmp_path)

    initial = generator.scan_folder_enhanced(parent)
    (child / "second.py").write_text("VALUE = 2\n", encoding="utf-8")
    updated = generator.scan_folder_enhanced(parent)

    assert initial["subfolders"][0]["file_count"] == 1
    assert updated["subfolders"][0]["file_count"] == 2
    assert initial["content_hash"] != updated["content_hash"]


def test_session_end_preserves_current_same_day_handoff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    session_log = tmp_path / "SESSION_LOG.md"
    next_brief = tmp_path / "next-session-brief.md"
    session_log.write_text(
        """# Log

## 2026-08-07 — Maintenance Session
**Focus:** broad session-start scope

**Completed:**
- old completion
""",
        encoding="utf-8",
    )
    expected = """# Brief

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-07
- Focus: obtain approval for the focused CI fixes
<!-- HANDOFF:END -->
"""
    next_brief.write_text(expected, encoding="utf-8")
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "NEXT_BRIEF", next_brief)

    ok, message = session._do_handoff(preserve_current_same_day=True)

    assert ok is True
    assert "Preserved" in message
    assert next_brief.read_text(encoding="utf-8") == expected


def test_session_log_completeness_uses_only_newest_same_day_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    class SessionDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2026, 8, 10)

    session_log = tmp_path / "SESSION_LOG.md"
    session_log.write_text(
        """# Log

## 2026-08-10 — Session 2
**Focus:** finish the capability platform

### Summary
- Completed the owned packet.

## 2026-08-10 — Session 1
**Focus:** prior work

**Completed:**
- Prior completion

### Issues encountered
- None encountered.

### Root causes and resolutions
- None encountered.
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "date", SessionDate)

    complete, issues = session.check_session_log_complete()

    assert complete is False
    assert "SESSION_LOG: Missing 'Issues encountered' section" in issues
    assert "SESSION_LOG: Missing 'Root causes and resolutions' section" in issues


def test_session_log_completeness_accepts_explicit_issue_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    class SessionDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2026, 8, 10)

    session_log = tmp_path / "SESSION_LOG.md"
    session_log.write_text(
        """# Log

## 2026-08-10 — Session 2
**Focus:** finish the capability platform

### Summary
- Completed the owned packet.

### Issues encountered
- Catalogue validation initially accepted a duplicate ID.

### Root causes and resolutions
- Registry construction skipped uniqueness validation; validation now fails closed and the duplicate regression passes.
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "date", SessionDate)

    complete, issues = session.check_session_log_complete()

    assert complete is True
    assert issues == []


def test_legacy_activity_log_uses_local_midnight_and_no_billing_estimate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    cost_log = tmp_path / "agent_costs.jsonl"
    monkeypatch.setattr(session, "COST_LOG", cost_log)
    monkeypatch.setattr(session.subprocess, "run", fake_run)
    monkeypatch.setattr(session, "_get_session_number", lambda: 1)

    session._log_session_cost("orchestrator")

    assert all("--since=midnight" in command for command in calls)
    entry = json.loads(cost_log.read_text(encoding="utf-8"))
    assert entry["duration_min"] is None
    assert entry["billing_tokens"] is None
    assert entry["billing_cost"] is None
