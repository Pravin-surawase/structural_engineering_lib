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


def test_agent_brief_filters_multiline_closed_task_ids_without_awk_failure(tmp_path):
    tasks = tmp_path / "TASKS.md"
    tasks.write_text(
        "# Tasks\n\n"
        "## Active\n\n"
        "| ID | Task | Owner | Status |\n"
        "|---|---|---|---|\n"
        "| CLOSED-1 | completed packet | Main | done |\n"
        "| LIVE-1 | active packet | Main | ready |\n\n"
        "## Next\n",
        encoding="utf-8",
    )
    brief = tmp_path / "brief.md"
    brief.write_text(
        "# Brief\n"
        "- Focus: prepare the next bounded task\n"
        "- Completed: repaired the prior candidate\n"
        "- Recurrence controls: normalize evidence before freezing hashes\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update(
        {
            "AGENT_BRIEF_TASKS": str(tasks),
            "AGENT_BRIEF_BRIEF": str(brief),
            "AGENT_BRIEF_CLOSED_TASKS": "CLOSED-1\nCLOSED-2",
        }
    )

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / "agent_brief.sh")],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert "awk:" not in result.stderr
    assert "LIVE-1: active packet [ready]" in result.stdout
    assert "CLOSED-1: completed packet" not in result.stdout
    assert "Repeat control: normalize evidence before freezing hashes" in result.stdout
    assert "Full index: ./run.sh session recurrence" in result.stdout


def test_run_sh_routes_receipt_bound_handoff_help():
    result = subprocess.run(
        ["bash", str(REPO_ROOT / "run.sh"), "session", "handoff", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--git-receipt" in result.stdout


def test_run_sh_routes_compact_recurrence_index():
    result = subprocess.run(
        [
            "bash",
            str(REPO_ROOT / "run.sh"),
            "session",
            "recurrence",
            "--id",
            "RR-003",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert "RR-003 | 4x | unknown" in result.stdout
    assert "Candidate or evidence frozen before normalization" in result.stdout
    assert "corrected-candidate-sequence" in result.stdout


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
        repository_root=str(Path("/tmp/repo").resolve()),
        worktree_root=str(Path("/tmp/repo").resolve()),
        git_dir=str(Path("/tmp/repo/.git").resolve()),
        git_common_dir=str(Path("/tmp/repo/.git").resolve()),
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
    monkeypatch.setattr(session, "_brief_receipt_identity_errors", lambda *_args: [])
    monkeypatch.setattr(session, "check_doc_links", lambda: (True, "All links valid"))
    monkeypatch.setattr(session, "archive_completed_tasks", lambda fix=False: (0, 0))
    monkeypatch.setattr(session, "get_today_prs", list)
    args = SimpleNamespace(fix=False, git_receipt=None, log_cost=False, agent="ops")
    args._subprocess_calls = subprocess_calls
    return authority_calls, args


def test_session_end_reuses_one_clean_authority_query_and_validates_context(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    authority_calls, args = _patch_cmd_end_dependencies(
        monkeypatch, _closeout_state(clean=True)
    )

    assert session.cmd_end(args) == 0
    output = capsys.readouterr().out
    assert authority_calls == [["collect_repository_state"]]
    assert "Working tree clean (scripts/git_state.py)" in output
    assert "Repository Context" in output
    assert "context validator produced no output" in output
    assert "session end is read-only and does not close timed task usage" in output


def test_session_end_has_no_mutating_fix_or_activity_logging_modes():
    parser = session.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["end", "--fix"])
    with pytest.raises(SystemExit):
        parser.parse_args(["end", "--log-cost"])


def test_session_end_dirty_state_is_always_a_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    authority_calls, args = _patch_cmd_end_dependencies(
        monkeypatch, _closeout_state(clean=False, paths=["docs/SESSION_LOG.md"])
    )

    assert session.cmd_end(args) == 1
    output = capsys.readouterr().out
    assert authority_calls == [["collect_repository_state"]]
    assert "Safe to end session" not in output


def test_session_end_allows_same_checkout_without_a_git_receipt(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    _authority_calls, args = _patch_cmd_end_dependencies(
        monkeypatch, _closeout_state(clean=True)
    )

    assert session.cmd_end(args) == 0
    assert "same-checkout delivery needs no Git receipt" in capsys.readouterr().out


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
    assert "Repository Context" in output
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
    assert brief["workflow"]["start"] == [
        "./run.sh session begin --task-id <TASK-ID> --agent " + brief["route"]["agent"]
    ]
    assert "inspection-only" in brief["workflow"]["git_rule"]


def test_run_task_brief_and_context_help_are_read_only():
    before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    brief = subprocess.run(
        ["bash", str(REPO_ROOT / "run.sh"), "task", "brief", "fix CSV import"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    help_result = subprocess.run(
        ["bash", str(REPO_ROOT / "run.sh"), "context", "summary", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    task_help = subprocess.run(
        ["bash", str(REPO_ROOT / "run.sh"), "task", "brief", "--help"],
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
    assert "usage: repo_context.py summary" in help_result.stdout
    assert task_help.returncode == 0, task_help.stderr
    assert "Usage: ./run.sh task brief" in task_help.stdout
    assert before == after


def test_context_summary_replaces_index_routes_without_writes():
    before = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    result = subprocess.run(
        [
            "bash",
            str(REPO_ROOT / "run.sh"),
            "context",
            "summary",
            "docs/research/git-governance",
        ],
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
    assert "docs/research/git-governance:" in result.stdout
    assert before == after


def test_retired_index_generate_routes_are_rejected():
    for subcommand in ("indexes", "docs-index"):
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "run.sh"), "generate", subcommand],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )

        assert result.returncode == 1
        assert f"Unknown generate subcommand: {subcommand}" in result.stderr


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


def test_active_tasks_hide_exact_external_closeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    tasks = tmp_path / "TASKS.md"
    tasks.write_text(
        """# Tasks

## Active

| ID | Task | Owner | Status |
|----|------|-------|--------|
| MAINT-0131 | Already merged | Main Agent | CANDIDATE |
| MAINT-0132 | Current work | Main Agent | ACTIVE |

## Up Next
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "TASKS_MD", tasks)
    monkeypatch.setattr(session, "_externally_closed_task_ids", lambda: {"MAINT-0131"})

    assert session.get_active_tasks() == [("MAINT-0132", "Current work", "")]


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
        repository_root=str(Path("/tmp/repo").resolve()),
        worktree_root=str(Path("/tmp/repo").resolve()),
        git_dir=str(Path("/tmp/repo/.git").resolve()),
        git_common_dir=str(Path("/tmp/repo/.git").resolve()),
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


def test_launcher_uses_worktree_bound_python_runtime():
    launcher = (REPO_ROOT / "scripts" / "launch_stack.sh").read_text(encoding="utf-8")

    assert 'PYTHON_LAUNCHER="$REPO_ROOT/scripts/python_runtime.sh"' in launcher
    assert '"$PYTHON_LAUNCHER" -m uvicorn' in launcher
    assert ".venv/bin/python" not in launcher
    assert ".venv/bin/uvicorn" not in launcher


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
    assert check_api.check_react_openapi(pages_dir=str(tmp_path)) == 1


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


USAGE_NOW = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)


def _write_usage_start(
    path: Path, *, task_id: str = "MAINT-0132", minutes_ago: float = 31
) -> None:
    started = USAGE_NOW - timedelta(minutes=minutes_ago)
    path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "timestamp": started.isoformat(timespec="seconds"),
                "checkpoint": "start",
                "task_id": task_id,
                "model": "unknown",
                "reasoning": "unknown",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_new_usage_start_explains_how_to_close_the_active_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log, task_id="WP09-STANDALONE-EXCEL")
    args = session.build_parser().parse_args(
        ["usage", "--checkpoint", "start", "--task-id", "WP10-01"]
    )

    assert session.cmd_usage(args) == 1
    output = capsys.readouterr().err
    assert "WP09-STANDALONE-EXCEL" in output
    assert (
        "session end validates repository state but does not close task timing"
        in output
    )
    assert "./run.sh session usage --active --json" in output
    assert len(usage_log.read_text(encoding="utf-8").splitlines()) == 1


def _complete_efficiency_closeout_args() -> list[str]:
    arguments = [
        "usage",
        "--checkpoint",
        "closeout",
        "--task-id",
        "MAINT-0132",
        "--candidate-head",
        "a" * 40,
        "--audit-rejections",
        "1",
        "--repair-batches",
        "1",
        "--focused-gate-retries",
        "2",
        "--full-gate-runs",
        "1",
        "--hosted-validation-runs",
        "0",
    ]
    minutes = (2, 10, 3, 4, 5, 6, 1)
    for label, value in zip(session.EFFICIENCY_PHASES, minutes, strict=True):
        arguments.extend(["--phase", f"{label}={value}"])
    return arguments


def test_closeout_usage_requires_complete_efficiency_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    args = session.build_parser().parse_args(
        [
            "usage",
            "--checkpoint",
            "closeout",
            "--task-id",
            "MAINT-0132",
            "--candidate-head",
            "a" * 40,
        ]
    )

    assert session.cmd_usage(args) == 1
    assert len(usage_log.read_text(encoding="utf-8").splitlines()) == 1
    assert "closeout efficiency evidence incomplete" in capsys.readouterr().err


def test_closeout_usage_records_non_overlapping_timing_and_retry_metrics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    monkeypatch.setattr(
        session, "_resolve_commit_tree", lambda value, **_kwargs: (value, "b" * 40)
    )
    monkeypatch.setattr(
        session,
        "_git_checkpoint_state",
        lambda: {"branch": "task/TEST", "head": "abc1234", "working_tree_files": 0},
    )
    args = session.build_parser().parse_args(_complete_efficiency_closeout_args())

    assert session.cmd_usage(args) == 0
    entry = json.loads(usage_log.read_text(encoding="utf-8").splitlines()[-1])
    efficiency = entry["efficiency"]
    assert entry["elapsed_min"] == 31
    assert efficiency["total_wall_time_min"] == 31
    assert efficiency["candidate_heads"] == ["a" * 40]
    assert efficiency["audit_rejections"] == 1
    assert efficiency["repair_batches"] == 1
    assert efficiency["focused_gate_retries"] == 2
    assert efficiency["full_gate_runs"] == 1
    assert efficiency["hosted_validation_runs"] == 0
    assert efficiency["rework_minutes"] == 4
    assert efficiency["network_wait_minutes"] == 6


def test_closeout_usage_rejects_elapsed_total_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    arguments = _complete_efficiency_closeout_args() + ["--elapsed-min", "99"]

    assert session.cmd_usage(session.build_parser().parse_args(arguments)) == 1
    assert len(usage_log.read_text(encoding="utf-8").splitlines()) == 1
    assert "do not match derived elapsed" in capsys.readouterr().err


def test_closeout_usage_rejects_unallocated_app_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log, minutes_ago=20.25)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    arguments = _complete_efficiency_closeout_args()
    values = (2, 7.5, 1.5, 0.5, 4, 1.3, 1.717)
    arguments = [
        item
        for item in arguments
        if not item.startswith(tuple(session.EFFICIENCY_PHASES))
    ]
    # Remove the value tokens paired with the original seven --phase flags.
    rebuilt = arguments[: arguments.index("--phase")]
    for label, value in zip(session.EFFICIENCY_PHASES, values, strict=True):
        rebuilt.extend(["--phase", f"{label}={value}"])

    assert session.cmd_usage(session.build_parser().parse_args(rebuilt)) == 1
    assert "unallocated time 1.733m" in capsys.readouterr().err


def test_usage_defaults_never_infer_model_or_reasoning() -> None:
    args = session.build_parser().parse_args(
        ["usage", "--checkpoint", "milestone", "--task-id", "MAINT-0132"]
    )

    assert args.model == "unknown"
    assert args.reasoning == "unknown"
    assert (
        session._usage_profile(
            {"schema_version": 1, "model": "gpt-5.6-sol", "reasoning": "high"}
        )
        == "legacy-unverified"
    )


def test_superseded_usage_closes_only_the_exact_active_task_without_timing_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log, task_id="STALE-PILOT")
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    monkeypatch.setattr(
        session,
        "_git_checkpoint_state",
        lambda: {"branch": "task/TEST", "head": "abc1234", "working_tree_files": 0},
    )
    args = session.build_parser().parse_args(
        [
            "usage",
            "--checkpoint",
            "superseded",
            "--task-id",
            "STALE-PILOT",
            "--notes",
            "Exact successor maintenance task owns current work; no timing claim.",
        ]
    )

    assert session.cmd_usage(args) == 0
    entries = session._read_jsonl(usage_log)
    assert entries[-1]["checkpoint"] == "superseded"
    assert entries[-1]["elapsed_min"] is None
    assert "efficiency" not in entries[-1]
    assert session._active_usage_start(entries) is None


@pytest.mark.parametrize(
    ("extra_args", "error"),
    [
        ([], "requires an explicit --notes reason"),
        (["--task-id", "OTHER", "--notes", "wrong task"], "exact active task"),
        (
            ["--notes", "no timing", "--elapsed-min", "31"],
            "cannot claim elapsed time",
        ),
    ],
)
def test_superseded_usage_fails_closed_for_incomplete_or_mismatched_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    extra_args: list[str],
    error: str,
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log, task_id="STALE-PILOT")
    arguments = [
        "usage",
        "--checkpoint",
        "superseded",
        "--task-id",
        "STALE-PILOT",
        *extra_args,
    ]

    assert session.cmd_usage(session.build_parser().parse_args(arguments)) == 1
    assert error in capsys.readouterr().err
    assert session._active_usage_start(session._read_jsonl(usage_log)) is not None


def test_closeout_rejects_short_unresolved_candidate_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    arguments = _complete_efficiency_closeout_args()
    arguments[arguments.index("a" * 40)] = "deadbee"

    assert session.cmd_usage(session.build_parser().parse_args(arguments)) == 1
    assert "exact 40-character lowercase commit SHA" in capsys.readouterr().err


def test_usage_event_binds_to_latest_open_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    args = session.build_parser().parse_args(
        [
            "usage",
            "--event",
            "check quick",
            "--duration-sec",
            "12",
            "--result-code",
            "0",
        ]
    )

    assert session.cmd_usage(args) == 0
    event = json.loads(usage_log.read_text(encoding="utf-8").splitlines()[-1])
    assert event["task_id"] == "MAINT-0132"
    assert event["event"] == "check quick"
    assert event["duration_sec"] == 12


def test_active_usage_reports_derived_elapsed_and_recorded_steps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log, minutes_ago=20.25)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)
    with usage_log.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "schema_version": 2,
                    "timestamp": USAGE_NOW.isoformat(timespec="seconds"),
                    "checkpoint": "event",
                    "task_id": "MAINT-0132",
                    "event": "check quick",
                    "duration_sec": 12,
                    "result_code": 0,
                }
            )
            + "\n"
        )
    args = session.build_parser().parse_args(["usage", "--active", "--json"])

    assert session.cmd_usage(args) == 0
    active = session._active_usage_payload(session._read_jsonl(usage_log), USAGE_NOW)
    assert active is not None
    assert active["derived_elapsed_min"] == 20.25
    assert active["recorded_steps"][0]["event"] == "check quick"


def test_closeout_integration_projects_externally_closed_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    usage_log = tmp_path / "model_usage.jsonl"
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", usage_log)
    _write_usage_start(usage_log)
    monkeypatch.setattr(session, "_usage_now", lambda: USAGE_NOW)

    def resolve(value: str, *, label: str) -> tuple[str, str]:
        assert label in {"candidate head", "merge commit"}
        return value, "c" * 40

    monkeypatch.setattr(session, "_resolve_commit_tree", resolve)
    monkeypatch.setattr(
        session, "_commit_reachable_from_origin_main", lambda _commit: True
    )
    arguments = _complete_efficiency_closeout_args()
    arguments[arguments.index("0", arguments.index("--hosted-validation-runs"))] = "1"
    arguments.extend(["--pr-number", "845", "--merge-commit", "d" * 40])

    assert session.cmd_usage(session.build_parser().parse_args(arguments)) == 0
    entries = session._read_jsonl(usage_log)
    assert session._externally_closed_task_ids(entries) == {"MAINT-0132"}
    integration = entries[-1]["efficiency"]["integration"]
    assert integration["reviewed_tree_matches_merged_tree"] is True
    assert integration["pr_number"] == 845


def test_shared_usage_log_resolves_from_git_common_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        session.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["git", "rev-parse"], 0, ".git\n", ""
        ),
    )

    assert (
        session._resolve_shared_usage_log(tmp_path)
        == (tmp_path / ".git" / "codex-runtime" / "model_usage.jsonl").resolve()
    )


def test_session_entry_and_check_orchestrator_record_timed_events() -> None:
    run_sh = (REPO_ROOT / "run.sh").read_text(encoding="utf-8")
    check_all = (REPO_ROOT / "scripts/check_all.py").read_text(encoding="utf-8")
    brief = (REPO_ROOT / "scripts/agent_brief.sh").read_text(encoding="utf-8")

    assert "_cmd_session_begin" in run_sh
    assert 'usage --checkpoint start --task-id "$task_id"' in run_sh
    assert (
        '"$SCRIPTS/agent_start.sh" --quick --preflight-only --allow-clean-main-intake'
        in run_sh
    )
    assert '_run_with_usage_event "session end"' not in run_sh
    assert '"$VENV" "$SCRIPTS/session.py" end "$@"' in run_sh
    assert 'pytest_args+=("${value#Python/}")' in run_sh
    assert '"$VENV" -m pytest tests/ "$@"' not in run_sh
    assert "--preflight-only)" in (REPO_ROOT / "scripts/agent_start.sh").read_text(
        encoding="utf-8"
    )
    assert "_record_task_timing(" in check_all
    assert 'return "check quick"' in check_all
    assert "usage --closed-task-ids" in brief
    assert "!closed[id]" in brief


def test_tool_registry_discovers_all_copilot_skills():
    tool_registry = importlib.import_module("scripts.tool_registry")
    registry = tool_registry.load_registry()
    skill_names = {name for name in registry if name.startswith("skill:")}

    catalog = json.loads(
        (REPO_ROOT / ".github/skills/skill_tiers.json").read_text(encoding="utf-8")
    )
    expected = {
        f"skill:{entry['name']}"
        for tier in ("core", "specialist", "experimental")
        for entry in catalog[tier]
    }
    assert skill_names == expected
    assert "skill:quality-gate" in skill_names
    assert "skill:release-preflight" in skill_names
    assert "skill:user-acceptance-test" in skill_names
    assert "check streamlit code" not in registry


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
            {
                "local_state_receipt_hash": "sha256:test-hash",
                "receipt_status": "READY",
            },
            "docs/receipt.json",
            [],
        ),
    )

    ok, message = session._do_handoff(preserve_current_same_day=True)

    assert ok is True
    assert "Preserved" in message
    assert next_brief.read_text(encoding="utf-8") == expected


def test_handoff_parsers_preserve_wrapped_focus_and_completed_items():
    block = [
        "## 2026-09-04 — Session",
        "**Focus:** Reconstruct the delivery and distinguish necessary",
        "installed qualification from preventable rework.",
        "",
        "**Completed:**",
        "",
        "- Reconstructed the commit and hosted-check timeline, duration",
        "  limits, and repair classes.",
        "- Added the candidate-integrity command and explicit",
        "  closeout guidance.",
        "",
        "### Rework and recurrence",
        "",
        "- Normalize evidence before freezing",
        "  repository-facing hashes.",
        "",
        "### Issues encountered",
    ]

    assert session._parse_focus(block) == (
        "Reconstruct the delivery and distinguish necessary installed "
        "qualification from preventable rework."
    )
    assert session._parse_completed(block) == [
        "Reconstructed the commit and hosted-check timeline, duration limits, "
        "and repair classes.",
        "Added the candidate-integrity command and explicit closeout guidance.",
    ]
    assert session._parse_rework_and_recurrence(block) == [
        "Normalize evidence before freezing repository-facing hashes."
    ]


def _write_rework_index_fixture(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "patterns": [
                    {
                        "id": "RR-001",
                        "pattern": "Evidence bytes changed after freeze",
                        "occurrences": 2,
                        "short_solution": "Normalize evidence before freezing hashes.",
                        "observed_minutes": {
                            "minimum": 5,
                            "maximum": 8,
                            "basis": "Two timed repairs.",
                        },
                        "aggregate_parent": None,
                        "details": ["docs/postmortem.md#rr-001"],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_rework_index_drives_compact_handoff_and_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    index = tmp_path / "rework.json"
    _write_rework_index_fixture(index)
    monkeypatch.setattr(session, "REWORK_INDEX", index)
    block = [
        "### Rework and recurrence",
        "",
        "- `RR-001` occurrences=2; minutes=5-8; repeated normalization.",
    ]

    pattern_ids, errors = session._validate_rework_section(block)

    assert pattern_ids == ["RR-001"]
    assert errors == []
    assert session._rework_handoff_summary(block) == (
        "RR-001 x2 / 5-8m: Normalize evidence before freezing hashes."
    )
    args = SimpleNamespace(pattern_id=None, json_output=False)
    assert session.cmd_recurrence(args) == 0
    output = capsys.readouterr().out
    assert "RR-001 | 2x | 5-8m | Evidence bytes changed after freeze" in output
    assert "Control: Normalize evidence before freezing hashes." in output
    assert "Time basis: Two timed repairs." in output
    assert "docs/postmortem.md#rr-001" in output


def test_rework_section_rejects_stale_index_count_and_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    index = tmp_path / "rework.json"
    _write_rework_index_fixture(index)
    monkeypatch.setattr(session, "REWORK_INDEX", index)
    block = [
        "### Rework and recurrence",
        "- `RR-001` occurrences=1; minutes=unknown; stale projection.",
    ]

    _pattern_ids, errors = session._validate_rework_section(block)

    assert errors == [
        "SESSION_LOG: RR-001 occurrence count is stale",
        "SESSION_LOG: RR-001 observed minutes are stale",
    ]


def test_brief_receipt_identity_rejects_artifact_hash_substitution():
    receipt = {
        "local_state_receipt_hash": "sha256:" + "a" * 64,
        "receipt_status": "HOLD",
    }
    lines = [
        "- Git receipt: docs/verification/receipt.json | "
        + "sha256:"
        + "b" * 64
        + " | HOLD"
    ]

    errors = session._brief_receipt_identity_errors(
        lines, receipt, "docs/verification/receipt.json"
    )

    assert len(errors) == 1
    assert "local-state hash mismatch" in errors[0]


def test_session_receipt_path_accepts_wrapped_markdown_value():
    assert (
        session._parse_git_receipt_path(
            [
                "**Git handoff receipt:**",
                "`docs/verification/maint-011-git-handoff-receipt.json`",
            ]
        )
        == "docs/verification/maint-011-git-handoff-receipt.json"
    )


def test_historical_session_check_uses_hash_bound_receipt_observation_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    recorded_at = datetime.now(UTC) - timedelta(hours=1)
    state = _closeout_state(clean=True)
    state.observed_at_utc = recorded_at.isoformat()
    receipt = git_handoff_receipt.build_receipt(
        task_id="GIT-7E",
        integration_owner="Main Agent",
        local_state=state,
        evidence={
            "remote": {"status": "NOT_APPLICABLE", "reason_code": "LOCAL_ONLY"},
            "pull_request": {
                "status": "NOT_APPLICABLE",
                "reason_code": "LOCAL_ONLY",
            },
            "review": {"status": "NOT_APPLICABLE", "reason_code": "LOCAL_ONLY"},
            "integration": {
                "status": "NOT_APPLICABLE",
                "reason_code": "LOCAL_ONLY",
            },
            "retention": {
                "status": "OBSERVED",
                "query_status": "OK",
                "observed_at_utc": recorded_at.isoformat(),
                "owner": "Main Agent",
                "decision": "RETAIN_FEATURE_BRANCH_AND_WORKTREE",
                "holds": [],
            },
            "authorization": {
                "status": "UNKNOWN",
                "authorized_actions": [],
                "prohibited_actions": [],
                "next_action": "HOLD_FOR_EXACT_EVIDENCE",
            },
        },
        now=recorded_at,
    )
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    receipt_path = docs / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    monkeypatch.setattr(session, "REPO_ROOT", repo)
    block = ["**Git handoff receipt:**", "`docs/receipt.json`"]

    _, _, live_errors = session._resolve_git_receipt(block)
    _, _, historical_errors = session._resolve_git_receipt(
        block, validate_at_recorded_time=True
    )

    assert "HOLD_SET_MISMATCH" in live_errors
    assert historical_errors == []


def test_historical_session_check_rejects_unbound_receipt_observation_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    receipt = git_handoff_receipt.build_receipt(
        task_id="GIT-7E",
        integration_owner="Main Agent",
        local_state=_closeout_state(clean=True),
        evidence={},
        now=datetime.fromisoformat(_closeout_state(clean=True).observed_at_utc),
    )
    receipt["observed_at_utc"] = (
        datetime.fromisoformat(receipt["observed_at_utc"]) + timedelta(minutes=1)
    ).isoformat()
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    monkeypatch.setattr(session, "REPO_ROOT", repo)

    _, _, errors = session._resolve_git_receipt(
        ["**Git handoff receipt:** `docs/receipt.json`"],
        validate_at_recorded_time=True,
    )

    assert errors == [
        "Git handoff receipt observation time does not match local evidence"
    ]


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


def test_handoff_without_receipt_is_valid_for_same_checkout_delivery(
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

    assert ok is True, message
    handoff = next_brief.read_text(encoding="utf-8")
    assert "- Focus: missing receipt" in handoff
    assert "Git receipt:" not in handoff


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

### Rework and recurrence
- None encountered.
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(session, "SESSION_LOG", session_log)
    monkeypatch.setattr(session, "date", SessionDate)

    complete, issues = session.check_session_log_complete()

    assert complete is True
    assert issues == []


def test_session_log_completeness_rejects_missing_recurrence_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    class SessionDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2026, 8, 10)

    session_log = tmp_path / "SESSION_LOG.md"
    session_log.write_text(
        """# Log

## 2026-08-10 — Session
**Focus:** finish the bounded packet

**Completed:**
- Completed the owned packet.

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
    assert issues == ["SESSION_LOG: Missing or empty 'Rework and recurrence' section"]


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


def test_delivery_second_audit_rejection_requires_changed_acceptance_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    ledger = tmp_path / "usage.jsonl"
    contract = tmp_path / "acceptance.md"
    contract.write_text("first\n", encoding="utf-8")
    ledger.write_text(
        json.dumps(
            {
                "timestamp": "2026-09-04T10:00:00+00:00",
                "checkpoint": "start",
                "task_id": "DELIVERY-TEST",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    git = SimpleNamespace(
        branch="codex/test",
        default_base=SimpleNamespace(ref="origin/main"),
    )
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", ledger)
    monkeypatch.setattr(session, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(session, "collect_repository_state", lambda _root: git)
    monkeypatch.setattr(
        session, "_require_clean_candidate", lambda _head: ("a" * 40, "b" * 40)
    )
    monkeypatch.setattr(
        session, "_resolve_head_and_tree", lambda _head: ("a" * 40, "b" * 40)
    )

    def advance(*arguments: str) -> int:
        parsed = session.build_parser().parse_args(
            ["delivery", "--task-id", "DELIVERY-TEST", *arguments]
        )
        return session.cmd_delivery(parsed)

    acceptance = ["--acceptance-path", "acceptance.md"]
    assert advance("--to", "BOUNDED_UNITS", *acceptance) == 0
    assert advance("--to", "CONTENT_FROZEN") == 0
    with ledger.open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps(
                {
                    "timestamp": "9999-01-01T00:00:00+00:00",
                    "checkpoint": "event",
                    "task_id": "DELIVERY-TEST",
                    "event": "format changed",
                    "result_code": 0,
                }
            )
            + "\n"
        )
    assert advance("--to", "FORMATTED") == 0
    assert advance("--to", "FOCUSED_VERIFIED", "--evidence", "tests pass") == 0
    assert advance("--to", "PREPARED", "--evidence", "docs complete") == 0
    assert advance("--to", "CANDIDATE") == 0
    assert advance("--to", "AUDIT_REJECTED") == 0
    assert advance("--to", "CONTENT_FROZEN") == 0
    assert advance("--to", "FORMATTED") == 0
    assert advance("--to", "FOCUSED_VERIFIED", "--evidence", "tests pass") == 0
    assert advance("--to", "PREPARED", "--evidence", "repair ready") == 0
    assert advance("--to", "CANDIDATE") == 0
    assert advance("--to", "AUDIT_REJECTED") == 0
    assert (
        session._delivery_snapshot(session._read_jsonl(ledger), "DELIVERY-TEST")[
            "state"
        ]
        == "REPLAN"
    )
    assert advance("--to", "BOUNDED_UNITS", *acceptance) == 1
    contract.write_text("changed\n", encoding="utf-8")
    assert advance("--to", "BOUNDED_UNITS", *acceptance) == 0


def test_delivery_prepush_closeout_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    ledger = tmp_path / "usage.jsonl"
    snapshot = {
        "task_id": "DELIVERY-TEST",
        "state": "INTEGRITY_VERIFIED",
        "design_revision": 1,
        "acceptance_digest": "digest",
        "acceptance_paths": ["acceptance.md"],
        "candidate_heads": ["a" * 40],
        "candidate_trees": {"a" * 40: "b" * 40},
        "audit_rejections": 0,
        "design_candidate_count": 1,
        "design_audit_rejections": 0,
        "repair_batches": 0,
        "hosted_validation_runs": 0,
        "latest_candidate_head": "a" * 40,
        "latest_candidate_tree": "b" * 40,
    }
    entries = [
        {
            "timestamp": "2026-09-04T10:00:00+00:00",
            "checkpoint": "start",
            "task_id": "DELIVERY-TEST",
        },
        {
            "timestamp": "2026-09-04T10:01:00+00:00",
            "checkpoint": "delivery",
            "task_id": "DELIVERY-TEST",
            "delivery": snapshot,
        },
    ]
    ledger.write_text("\n".join(json.dumps(row) for row in entries) + "\n")
    calls: list[str] = []
    monkeypatch.setattr(session, "MODEL_USAGE_LOG", ledger)
    monkeypatch.setattr(
        session, "_resolve_head_and_tree", lambda _head: ("a" * 40, "b" * 40)
    )
    monkeypatch.setattr(
        session,
        "_run_final_closeout",
        lambda: calls.append("end") or 0,
    )
    args = session.build_parser().parse_args(
        ["delivery", "--task-id", "DELIVERY-TEST", "--guard-push"]
    )

    assert session.cmd_delivery(args) == 0
    assert session.cmd_delivery(args) == 0
    assert calls == ["end"]
