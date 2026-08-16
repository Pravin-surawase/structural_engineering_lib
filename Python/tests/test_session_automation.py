"""Regression tests for maintenance session automation."""

from __future__ import annotations

import copy
import importlib
import json
import os
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

session = importlib.import_module("scripts.session")
check_api = importlib.import_module("scripts.check_api")
validate_script_refs = importlib.import_module("scripts.validate_script_refs")
prompt_router = importlib.import_module("scripts.prompt_router")


def test_run_sh_routes_receipt_bound_handoff_help():
    result = subprocess.run(
        [str(REPO_ROOT / "run.sh"), "session", "handoff", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--git-receipt" in result.stdout


def test_handoff_replaces_maintained_legacy_heading(monkeypatch, tmp_path):
    brief = tmp_path / "next-session-brief.md"
    brief.write_text(
        "# Brief\n\n## Latest Handoff\n\n"
        f"{session.HANDOFF_START}\n- Date: old\n{session.HANDOFF_END}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "NEXT_BRIEF", brief)

    session._update_next_brief(["- Date: 2026-08-15", "- Git receipt: exact"])

    updated = brief.read_text(encoding="utf-8")
    assert "## Latest Handoff (auto)" in updated
    assert "- Git receipt: exact" in updated
    assert "- Date: old" not in updated


git_state = importlib.import_module("scripts.git_state")
git_handoff_receipt = importlib.import_module("scripts.git_handoff_receipt")


def _closeout_state(
    *,
    clean: bool,
    paths: list[str] | None = None,
    failures: list | None = None,
    schema_version: int = 1,
):
    modified = list(paths or [])
    query_failures = list(failures or [])
    if query_failures:
        derived_action = "HOLD_UNKNOWN"
        hold_reasons = ["required Git evidence is unknown"]
        if modified:
            hold_reasons.append(f"changed paths: {len(modified)}")
    elif clean:
        derived_action = "READY_LOCAL"
        hold_reasons = []
    else:
        derived_action = "HOLD_DIRTY"
        hold_reasons = [f"changed paths: {len(modified)}"]
    return git_state.RepositoryState(
        schema_version=schema_version,
        observed_at_utc=datetime.now(UTC).isoformat(),
        repository_root="/tmp/repo",
        worktree_root="/tmp/repo",
        git_dir="/tmp/repo/.git",
        git_common_dir="/tmp/repo/.git",
        linked_worktree=False,
        branch="codex/git-7e",
        head_sha="a" * 40,
        default_base=git_state.Relation("origin/main", "b" * 40, 1, 0, "ahead"),
        upstream=git_state.Relation("origin/codex/git-7e", "a" * 40, 0, 0, "equal"),
        tree=git_state.TreeState(modified_paths=modified, clean=clean),
        operation="none",
        operation_markers=[],
        locks=[],
        remote_freshness="NOT_CHECKED",
        derived_action=derived_action,
        hold_reasons=hold_reasons,
        query_failures=query_failures,
        duration_ms=1.0,
    )


def _malformed_clean_state(case: str):
    state = copy.deepcopy(_closeout_state(clean=True))
    if case == "head_sha":
        state.head_sha = "not-a-sha"
    elif case == "empty_branch":
        state.branch = ""
    elif case == "head_branch":
        state.branch = "HEAD"
    elif case == "banana_relation":
        state.default_base.status = "BANANA"
    elif case == "uppercase_unknown_relation":
        state.default_base.status = "UNKNOWN"
    elif case == "schema":
        state.schema_version = 999
    elif case == "remote_freshness":
        state.remote_freshness = "CURRENT"
    elif case == "default_none_observed":
        state.default_base.ref = "NONE"
    elif case == "default_bad_ref":
        state.default_base.ref = "bad ref"
    elif case == "upstream_none_observed":
        state.upstream.ref = "NONE"
    elif case == "double_slash_branch":
        state.branch = "codex//x"
    elif case == "leading_dash_branch":
        state.branch = "-bad"
    elif case == "worktree_identity":
        state.worktree_root = "/tmp/other"
    elif case == "nan_duration":
        state.duration_ms = float("nan")
    elif case == "infinite_duration":
        state.duration_ms = float("inf")
    elif case == "future_timestamp":
        state.observed_at_utc = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    elif case == "stale_timestamp":
        state.observed_at_utc = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    return state


def test_session_closeout_uses_canonical_clean_evidence_without_subprocess(
    monkeypatch: pytest.MonkeyPatch,
):
    state = _closeout_state(clean=True)
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)
    monkeypatch.setattr(
        session.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("closeout evidence must not invoke a second subprocess")
        ),
    )

    assert session.get_closeout_git_evidence() == (
        "CLEAN",
        [],
        "Canonical Git-state tree is clean",
    )


def test_session_closeout_reports_canonical_dirty_paths(
    monkeypatch: pytest.MonkeyPatch,
):
    state = _closeout_state(clean=False, paths=["docs/SESSION_LOG.md"])
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)

    status, paths, _reason = session.get_closeout_git_evidence()

    assert status == "DIRTY"
    assert paths == ["docs/SESSION_LOG.md"]


@pytest.mark.parametrize(
    "case",
    [
        "head_sha",
        "empty_branch",
        "head_branch",
        "banana_relation",
        "uppercase_unknown_relation",
        "schema",
        "remote_freshness",
        "default_none_observed",
        "default_bad_ref",
        "upstream_none_observed",
        "double_slash_branch",
        "leading_dash_branch",
        "worktree_identity",
        "nan_duration",
        "infinite_duration",
        "future_timestamp",
        "stale_timestamp",
    ],
)
def test_session_closeout_holds_malformed_canonical_contract_without_subprocess(
    case: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    state = _malformed_clean_state(case)
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)
    monkeypatch.setattr(
        session.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("closeout validation must not invoke a subprocess")
        ),
    )

    evidence = session.get_closeout_git_evidence()

    assert evidence[0] == "UNKNOWN"
    assert session.report_closeout_git_evidence(evidence) is False
    assert "Working tree clean" not in capsys.readouterr().out


def test_session_closeout_holds_clean_action_hold_contradiction(
    monkeypatch: pytest.MonkeyPatch,
):
    state = _closeout_state(clean=True)
    state.derived_action = "HOLD_DIRTY"
    state.hold_reasons = ["WORKTREE_DIRTY"]
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)

    status, paths, reason = session.get_closeout_git_evidence()

    assert status == "UNKNOWN"
    assert paths == []
    assert "contradicts" in reason


def test_session_closeout_holds_dirty_ready_contradiction(
    monkeypatch: pytest.MonkeyPatch,
):
    state = _closeout_state(clean=False, paths=["docs/SESSION_LOG.md"])
    state.derived_action = "READY_LOCAL"
    state.hold_reasons = []
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)

    status, paths, reason = session.get_closeout_git_evidence()

    assert status == "UNKNOWN"
    assert paths == []
    assert "contradicts" in reason


def test_changed_doc_folders_uses_only_canonical_dirty_paths():
    status, folders, reason = session.get_changed_doc_folders(
        (
            "DIRTY",
            ["docs/SESSION_LOG.md", "docs/git-automation/index.json", "source.py"],
            "canonical dirty paths",
        )
    )

    assert status == "OBSERVED"
    assert folders == [session.REPO_ROOT / "docs"]
    assert reason == "canonical dirty paths inspected"


def test_session_closeout_holds_nonzero_git_state_query(
    monkeypatch: pytest.MonkeyPatch,
):
    state = _closeout_state(
        clean=False,
        failures=[git_state.QueryFailure("git status --porcelain=v2", "exit 128")],
    )
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)

    status, paths, reason = session.get_closeout_git_evidence()

    assert status == "UNKNOWN"
    assert paths == []
    assert "exit 128" in reason


def test_session_closeout_holds_git_state_exception(
    monkeypatch: pytest.MonkeyPatch,
):
    def raise_query(_repo):
        raise OSError("authority unavailable")

    monkeypatch.setattr(session, "collect_repository_state", raise_query)

    status, paths, reason = session.get_closeout_git_evidence()

    assert status == "UNKNOWN"
    assert paths == []
    assert "authority unavailable" in reason


@pytest.mark.parametrize(
    "evidence",
    [
        {"tree": {"clean": True}},
        _closeout_state(clean=True, schema_version=999),
        _closeout_state(clean=True, paths=["contradiction.md"]),
        _closeout_state(clean=False),
    ],
)
def test_session_closeout_holds_malformed_or_unknown_evidence(
    evidence, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: evidence)

    status, paths, _reason = session.get_closeout_git_evidence()

    assert status == "UNKNOWN"
    assert paths == []


@pytest.mark.parametrize("status", ["DIRTY", "UNKNOWN"])
def test_session_closeout_never_prints_clean_for_hold(
    status: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    monkeypatch.setattr(
        session,
        "get_closeout_git_evidence",
        lambda: (status, ["dirty.md"] if status == "DIRTY" else [], "held"),
    )

    assert session.report_closeout_git_evidence() is False
    assert "Working tree clean" not in capsys.readouterr().out


def _patch_cmd_end_dependencies(
    monkeypatch: pytest.MonkeyPatch, state
) -> tuple[list[list[str]], SimpleNamespace]:
    authority_calls = []

    def collect(_repo):
        authority_calls.append(["collect_repository_state"])
        return state

    subprocess_calls: list[list[str]] = []

    def run(args, **_kwargs):
        command = [str(part) for part in args]
        subprocess_calls.append(command)
        assert not (
            command[:1] == ["git"]
            and len(command) > 1
            and command[1] in {"diff", "status"}
        ), f"session end invoked a second Git-state reader: {command}"
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(session, "collect_repository_state", collect)
    monkeypatch.setattr(session.subprocess, "run", run)
    monkeypatch.setattr(
        session, "run_handoff_check", lambda: (True, "All checks passed")
    )
    monkeypatch.setattr(session, "check_session_log_complete", lambda: (True, []))
    monkeypatch.setattr(
        session, "_latest_session_block", lambda _lines: ("2026-08-15", [])
    )
    monkeypatch.setattr(
        session,
        "_resolve_git_receipt",
        lambda _block, _path: (
            {
                "local_state_receipt_hash": "sha256:" + "a" * 64,
                "receipt_status": "HOLD",
            },
            "docs/research/git-governance/receipt.json",
            [],
        ),
    )
    monkeypatch.setattr(session, "check_doc_links", lambda: (True, "All links valid"))
    monkeypatch.setattr(session, "archive_completed_tasks", lambda fix=False: (0, 0))
    monkeypatch.setattr(session, "get_today_prs", list)
    args = SimpleNamespace(fix=False, git_receipt=None, log_cost=False, agent="ops")
    return authority_calls, args


def test_session_end_reuses_one_clean_authority_query_and_skips_unknown_doc_set(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    authority_calls, args = _patch_cmd_end_dependencies(
        monkeypatch, _closeout_state(clean=True)
    )

    assert session.cmd_end(args) == 0
    output = capsys.readouterr().out
    assert authority_calls == [["collect_repository_state"]]
    assert "Working tree clean (scripts/git_state.py)" in output
    assert "Doc-folder set UNKNOWN" in output
    assert "no committed-diff path evidence" in output
    assert "No doc folder changes detected" not in output


def test_session_end_query_failure_cannot_pass_or_print_clean(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    state = _closeout_state(
        clean=False,
        failures=[git_state.QueryFailure("git status --porcelain=v2", "exit 128")],
    )
    authority_calls, args = _patch_cmd_end_dependencies(monkeypatch, state)

    assert session.cmd_end(args) == 1
    output = capsys.readouterr().out
    assert authority_calls == [["collect_repository_state"]]
    assert "Git state UNKNOWN/hold" in output
    assert "Doc-folder set UNKNOWN" in output
    assert "Working tree clean" not in output


@pytest.mark.parametrize(
    "case",
    [
        "head_sha",
        "empty_branch",
        "head_branch",
        "banana_relation",
        "uppercase_unknown_relation",
        "schema",
        "remote_freshness",
        "default_none_observed",
        "default_bad_ref",
        "upstream_none_observed",
        "double_slash_branch",
        "leading_dash_branch",
        "worktree_identity",
        "nan_duration",
        "infinite_duration",
        "future_timestamp",
        "stale_timestamp",
    ],
)
def test_session_end_malformed_canonical_contract_fails_closed(
    case: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    authority_calls, args = _patch_cmd_end_dependencies(
        monkeypatch, _malformed_clean_state(case)
    )

    assert session.cmd_end(args) == 1
    output = capsys.readouterr().out
    assert authority_calls == [["collect_repository_state"]]
    assert "Git state UNKNOWN/hold" in output
    assert "Working tree clean" not in output


@pytest.mark.parametrize(
    ("case", "expected_return", "expected_text"),
    [
        ("clean", 0, "Working tree: \x1b[2mclean"),
        ("dirty", 1, "Uncommitted changes: 1 file(s)"),
        ("detached", 1, "Branch: \x1b[32mDETACHED"),
        ("held", 1, "UNKNOWN/hold (HOLD_BEHIND)"),
        ("query_failed", 1, "Branch: \x1b[33mUNKNOWN"),
        ("malformed", 1, "Branch: \x1b[33mUNKNOWN"),
    ],
)
def test_session_context_uses_only_canonical_git_state_and_fails_closed(
    case: str,
    expected_return: int,
    expected_text: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    state = _closeout_state(clean=True)
    if case == "dirty":
        state = _closeout_state(clean=False, paths=["docs/SESSION_LOG.md"])
    elif case == "detached":
        state.branch = "DETACHED"
        state.derived_action = "HOLD_DETACHED"
        state.hold_reasons = ["HEAD is detached"]
    elif case == "held":
        state.default_base = git_state.Relation("origin/main", "b" * 40, 0, 1, "behind")
        state.derived_action = "HOLD_BEHIND"
        state.hold_reasons = ["HEAD is behind a required ref"]
    elif case == "query_failed":
        state = _closeout_state(
            clean=True,
            failures=[git_state.QueryFailure("git status --porcelain=v2", "exit 128")],
        )
    elif case == "malformed":
        state.branch = "HEAD"

    monkeypatch.setattr(session, "collect_repository_state", lambda _repo: state)
    monkeypatch.setattr(
        session.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("session context must not invoke a Git subprocess")
        ),
    )

    assert session.cmd_context(SimpleNamespace()) == expected_return
    output = capsys.readouterr().out
    assert expected_text in output
    assert "Branch: \x1b[32m\x1b[0m" not in output
    if case != "clean":
        assert "Working tree: \x1b[2mclean" not in output


def test_session_context_holds_authority_exception_without_subprocess_fallback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    def raise_authority(_repo):
        raise OSError("canonical authority unavailable")

    monkeypatch.setattr(session, "collect_repository_state", raise_authority)
    monkeypatch.setattr(
        session.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("session context must not invoke a Git subprocess")
        ),
    )

    assert session.cmd_context(SimpleNamespace()) == 1
    output = capsys.readouterr().out
    assert "Branch: \x1b[33mUNKNOWN" in output
    assert "canonical authority unavailable" in output
    assert "Working tree: \x1b[2mclean" not in output


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
    no_args_result = subprocess.run(
        [str(REPO_ROOT / "run.sh"), "generate", "indexes"],
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
    assert "./run.sh generate indexes <owned-folder> [options]" in help_result.stdout
    assert no_args_result.returncode == 0, no_args_result.stderr
    assert "No arguments or --help shows this non-writing help" in no_args_result.stdout
    assert task_help.returncode == 0, task_help.stderr
    assert "Usage: ./run.sh task brief" in task_help.stdout
    assert before == after


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (
            ["docs/research/git-governance", "--dry-run"],
            "Would generate: docs/research/git-governance/index.json + "
            "docs/research/git-governance/index.md",
        ),
        (["--all", "--dry-run"], "Folders to process:"),
    ],
)
def test_run_index_generator_dry_run_routes_scope_without_writes(
    arguments: list[str], expected: str
):
    before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    result = subprocess.run(
        [str(REPO_ROOT / "run.sh"), "generate", "indexes", *arguments],
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

    assert result.returncode == 0, result.stderr
    assert "Mode: DRY RUN" in result.stdout
    assert expected in result.stdout
    if arguments[0] != "--all":
        assert "Folders to process: 1" in result.stdout
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
    ("action", "trusted"),
    [
        ("READY_LOCAL", True),
        ("HOLD_DIRTY", False),
        ("HOLD_MAIN", False),
        ("HOLD_DETACHED", False),
        ("HOLD_BEHIND", False),
        ("HOLD_DIVERGED", False),
        ("HOLD_OPERATION", False),
        ("HOLD_LOCKED", False),
        ("HOLD_UNKNOWN", False),
    ],
)
def test_session_trust_accepts_only_kernel_ready_local(action: str, trusted: bool):
    state = git_state.RepositoryState(
        schema_version=1,
        observed_at_utc="2026-08-13T00:00:00+00:00",
        repository_root="/tmp/repo",
        worktree_root="/tmp/repo",
        git_dir="/tmp/repo/.git",
        git_common_dir="/tmp/repo/.git",
        linked_worktree=False,
        branch="codex/task",
        head_sha="a" * 40,
        default_base=git_state.Relation("main", "b" * 40, 1, 0, "ahead"),
        upstream=git_state.Relation("NONE", None, None, None, "none"),
        tree=git_state.TreeState(clean=action != "HOLD_DIRTY"),
        operation="merge" if action == "HOLD_OPERATION" else "none",
        operation_markers=[],
        locks=["index.lock"] if action == "HOLD_LOCKED" else [],
        remote_freshness="NOT_CHECKED",
        derived_action=action,
        hold_reasons=[] if action == "READY_LOCAL" else [action],
        query_failures=(
            [git_state.QueryFailure("git status", "failed")]
            if action == "HOLD_UNKNOWN"
            else []
        ),
        duration_ms=1.0,
    )

    result, _reason = session._evaluate_trust(state)

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


def test_index_generator_requires_opt_in_for_new_index_folder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    generator = importlib.import_module("scripts.generate_enhanced_index")
    unmaintained = tmp_path / "tests" / "new-area"
    unmaintained.mkdir(parents=True)
    (unmaintained / "sample.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(generator, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(generator, "KEY_FOLDERS", [])
    monkeypatch.setattr(sys, "argv", ["generate_enhanced_index.py", str(unmaintained)])

    with pytest.raises(SystemExit, match="2"):
        generator.main()

    output = capsys.readouterr().out
    assert "Refusing to create indexes in unmaintained folder" in output
    assert not (unmaintained / "index.json").exists()
    assert not (unmaintained / "index.md").exists()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_enhanced_index.py",
            str(unmaintained),
            "--allow-new-index",
        ],
    )
    generator.main()

    assert (unmaintained / "index.json").is_file()
    assert (unmaintained / "index.md").is_file()


def test_index_generator_owned_folder_write_changes_only_expected_indexes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    generator = importlib.import_module("scripts.generate_enhanced_index")
    owned = tmp_path / "owned"
    owned.mkdir()
    (owned / "sample.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(generator, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(generator, "KEY_FOLDERS", ["owned"])
    monkeypatch.setattr(sys, "argv", ["generate_enhanced_index.py", "owned"])

    generator.main()

    generated = {
        path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("index.*")
    }
    assert generated == {"owned/index.json", "owned/index.md"}


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
- Git receipt: docs/receipt.json | sha256:test-hash | READY
<!-- HANDOFF:END -->
"""
    next_brief.write_text(expected, encoding="utf-8")
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "NEXT_BRIEF", next_brief)
    monkeypatch.setattr(
        session,
        "_resolve_git_receipt",
        lambda block, explicit_path=None: (
            {"local_state_receipt_hash": "sha256:test-hash"},
            "docs/receipt.json",
            [],
        ),
    )

    ok, message = session._do_handoff(preserve_current_same_day=True)

    assert ok is True
    assert "Preserved" in message
    assert next_brief.read_text(encoding="utf-8") == expected


def test_handoff_round_trip_embeds_valid_receipt_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    now = datetime(2026, 8, 15, 9, 30, tzinfo=UTC)
    head = "a" * 40
    base = "b" * 40
    state = git_state.RepositoryState(
        schema_version=1,
        observed_at_utc=now.isoformat(),
        repository_root=str(tmp_path),
        worktree_root=str(tmp_path),
        git_dir=str(tmp_path / ".git"),
        git_common_dir=str(tmp_path / ".git"),
        linked_worktree=False,
        branch="codex/git-7e",
        head_sha=head,
        default_base=git_state.Relation("origin/main", base, 1, 0, "ahead"),
        upstream=git_state.Relation("origin/codex/git-7e", head, 0, 0, "equal"),
        tree=git_state.TreeState(clean=True),
        operation="none",
        operation_markers=[],
        locks=[],
        remote_freshness="NOT_CHECKED",
        derived_action="READY_LOCAL",
        hold_reasons=[],
        query_failures=[],
        duration_ms=1.0,
    )
    not_applicable = {
        "status": "NOT_APPLICABLE",
        "reason_code": "LOCAL_ONLY_TASK_AT_HANDOFF",
    }
    receipt = git_handoff_receipt.build_receipt(
        task_id="GIT-7E",
        integration_owner="Main Agent",
        local_state=state,
        evidence={
            "remote": not_applicable,
            "pull_request": not_applicable,
            "review": not_applicable,
            "integration": not_applicable,
            "retention": {
                "status": "NOT_APPLICABLE",
                "reason_code": "NO_RETENTION_ACTION_IN_SCOPE",
            },
            "authorization": {
                "status": "OBSERVED",
                "authorized_actions": ["CONTINUE_LOCAL_WORK"],
                "prohibited_actions": ["DELETE_BRANCH"],
                "next_action": "CONTINUE_LOCAL_VALIDATION",
            },
        },
        now=now,
    )
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    receipt_path = docs / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    session_log = docs / "SESSION_LOG.md"
    session_log.write_text(
        """# Log

## 2026-08-15 — GIT-7E Session
**Focus:** durable handoff

**Completed:**
- receipt contract
""",
        encoding="utf-8",
    )
    next_brief = docs / "next-session-brief.md"
    next_brief.write_text("# Brief\n", encoding="utf-8")
    monkeypatch.setattr(session, "REPO_ROOT", repo)
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "NEXT_BRIEF", next_brief)

    ok, message = session._do_handoff(git_receipt=receipt_path)

    handoff = next_brief.read_text(encoding="utf-8")
    assert ok is True, message
    assert receipt["local_state_receipt_hash"] in handoff
    assert f"codex/git-7e@{head}" in handoff
    assert "remote=NOT_APPLICABLE" in handoff
    assert "Next action: CONTINUE_LOCAL_VALIDATION" in handoff


def test_handoff_missing_receipt_is_an_explicit_hold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    session_log = tmp_path / "SESSION_LOG.md"
    next_brief = tmp_path / "next-session-brief.md"
    session_log.write_text(
        """# Log

## 2026-08-15 — GIT-7E Session
**Focus:** missing receipt
""",
        encoding="utf-8",
    )
    next_brief.write_text("# Brief\n", encoding="utf-8")
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "NEXT_BRIEF", next_brief)

    ok, message = session._do_handoff()

    assert ok is False
    assert "Missing task-to-Git handoff receipt" in message


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


def test_repeated_session_compaction_indexes_existing_archives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    session_log = tmp_path / "SESSION_LOG.md"
    archive_dir = tmp_path / "session-logs"
    archive_dir.mkdir()
    session_index = tmp_path / "session_index.json"
    session_log.write_text(
        """# Session Log

## 2026-08-16 — Session: Current
**Focus:** current work

## 2026-08-15 — Session: Prior
**Focus:** prior work

## 2026-08-14 — Session: Earlier
**Focus:** earlier work
""",
        encoding="utf-8",
    )
    (archive_dir / "2026-03.md").write_text(
        """# SESSION_LOG Archive — 2026-03

## 2026-03-31 — Session 106: Historical
**Focus:** historical work
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "SESSION_ARCHIVE_DIR", archive_dir)
    monkeypatch.setattr(session, "SESSION_ARCHIVE_MAX_BYTES", 140)
    monkeypatch.setattr(session, "SESSION_INDEX", session_index)

    assert session.cmd_compact(SimpleNamespace(keep_last=1, dry_run=False)) == 0

    index = json.loads(session_index.read_text(encoding="utf-8"))
    assert index["_meta"] == {
        "total_sessions": 4,
        "main_log_entries": 1,
        "archived_entries": 3,
        "last_compacted": date.today().strftime("%Y-%m-%d"),
    }
    assert {item["date"] for item in index["sessions"]} == {
        "2026-03-31",
        "2026-08-14",
        "2026-08-15",
        "2026-08-16",
    }
    august_archives = sorted(archive_dir.glob("2026-08*.md"))
    assert [path.name for path in august_archives] == [
        "2026-08-part-2.md",
        "2026-08.md",
    ]
    assert all(path.stat().st_size <= 140 for path in august_archives)
    august_index_paths = {
        item["archive_file"]
        for item in index["sessions"]
        if item["date"].startswith("2026-08") and not item["in_main_log"]
    }
    assert august_index_paths == {
        "session-logs/2026-08.md",
        "session-logs/2026-08-part-2.md",
    }


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
