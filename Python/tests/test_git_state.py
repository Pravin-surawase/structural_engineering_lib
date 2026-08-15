"""Outcome tests for the read-only, worktree-aware Git state authority."""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

git_state = importlib.import_module("scripts.git_state")


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _write(repo: Path, name: str, content: str) -> Path:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _commit(repo: Path, name: str, content: str, message: str) -> str:
    _write(repo, name, content)
    _git(repo, "add", name)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _repo(tmp_path: Path, name: str = "repo") -> Path:
    repo = tmp_path / name
    _git(tmp_path, "init", "-b", "main", str(repo))
    _git(repo, "config", "user.name", "GIT-7B Test")
    _git(repo, "config", "user.email", "git-7b@example.invalid")
    _commit(repo, "tracked.txt", "base\n", "initial")
    return repo


def _feature(repo: Path, name: str = "feature") -> None:
    _git(repo, "switch", "-c", name)


def _marker_path(repo: Path, marker: str) -> Path:
    raw = _git(
        repo, "rev-parse", "--path-format=absolute", "--git-path", marker
    ).stdout.strip()
    return Path(raw)


def _create_operation_marker(repo: Path, marker: str) -> Path:
    path = _marker_path(repo, marker)
    if marker.startswith("rebase-"):
        path.mkdir(parents=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_git(repo, "rev-parse", "HEAD").stdout, encoding="utf-8")
    return path


def test_clean_feature_main_and_detached_states_are_distinct(tmp_path: Path):
    repo = _repo(tmp_path)

    main = git_state.collect_repository_state(repo, default_ref="main")
    assert main.derived_action == "HOLD_MAIN"

    _feature(repo)
    feature = git_state.collect_repository_state(repo, default_ref="main")
    assert feature.derived_action == "READY_LOCAL"
    assert feature.upstream.status == "none"

    _git(repo, "switch", "--detach")
    detached = git_state.collect_repository_state(repo, default_ref="main")
    assert detached.branch == "DETACHED"
    assert detached.derived_action == "HOLD_DETACHED"


def test_porcelain_v2_classifies_each_dirty_surface(tmp_path: Path):
    repo = _repo(tmp_path)
    _feature(repo)
    _write(repo, "staged.txt", "staged\n")
    _git(repo, "add", "staged.txt")
    _write(repo, "tracked.txt", "modified\n")
    _write(repo, "untracked.txt", "untracked\n")

    state = git_state.collect_repository_state(repo, default_ref="main")

    assert state.derived_action == "HOLD_DIRTY"
    assert state.tree.staged_paths == ["staged.txt"]
    assert state.tree.modified_paths == ["tracked.txt"]
    assert state.tree.untracked_paths == ["untracked.txt"]
    assert state.tree.conflicted_paths == []


def test_state_consistency_recomputes_action_and_holds_without_git_io(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = _repo(tmp_path)
    _feature(repo)
    state = git_state.collect_repository_state(repo, default_ref="main")
    assert git_state.validate_repository_state_consistency(state) == []

    monkeypatch.setattr(
        git_state.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("consistency validation must not query Git")
        ),
    )
    state.operation = "merge"
    state.operation_markers = ["MERGE_HEAD:/tmp/repo/.git/MERGE_HEAD"]

    errors = git_state.validate_repository_state_consistency(state)

    assert any("derived_action contradicts" in error for error in errors)
    assert any("hold_reasons contradict" in error for error in errors)


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("head_sha", "head_sha is malformed"),
        ("empty_branch", "branch is malformed"),
        ("banana_relation", "relation status is unsupported"),
        ("uppercase_unknown_relation", "relation status is unsupported"),
        ("schema", "schema is unsupported"),
        ("remote_freshness", "remote_freshness is unsupported"),
        ("relation_counts", "relation status contradicts counts"),
        ("lowercase_unknown_without_failure", "lacks query failure evidence"),
        ("operation_enum", "operation is unsupported"),
        ("operation_markers", "operation contradicts operation markers"),
        ("linked_worktree", "linked_worktree contradicts"),
        ("query_failure", "query failure evidence is malformed"),
        ("tree_count", "tree dirty_count contradicts paths"),
    ],
)
def test_state_consistency_rejects_malformed_schema_and_enums_without_git_io(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
    expected: str,
):
    repo = _repo(tmp_path)
    _feature(repo)
    state = copy.deepcopy(git_state.collect_repository_state(repo, default_ref="main"))
    if case == "head_sha":
        state.head_sha = "not-a-sha"
    elif case == "empty_branch":
        state.branch = ""
    elif case == "banana_relation":
        state.default_base.status = "BANANA"
    elif case == "uppercase_unknown_relation":
        state.default_base.status = "UNKNOWN"
    elif case == "schema":
        state.schema_version = 999
    elif case == "remote_freshness":
        state.remote_freshness = "CURRENT"
    elif case == "relation_counts":
        state.default_base.behind = 1
    elif case == "lowercase_unknown_without_failure":
        state.default_base.status = "unknown"
        state.default_base.sha = None
        state.default_base.ahead = None
        state.default_base.behind = None
    elif case == "operation_enum":
        state.operation = "teleport"
    elif case == "operation_markers":
        state.operation_markers = ["MERGE_HEAD:/tmp/repo/.git/MERGE_HEAD"]
    elif case == "linked_worktree":
        state.linked_worktree = not state.linked_worktree
    elif case == "query_failure":
        state.query_failures = [SimpleNamespace(command="", reason="exit 128")]
    elif case == "tree_count":
        state.tree = SimpleNamespace(
            staged_paths=[],
            modified_paths=[],
            untracked_paths=[],
            conflicted_paths=[],
            clean=True,
            dirty_count=1,
        )

    monkeypatch.setattr(
        git_state.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("state validation must not query Git")
        ),
    )

    errors = git_state.validate_repository_state_consistency(state)

    assert any(expected in error for error in errors)


def test_state_consistency_accepts_canonical_unknown_only_with_query_failure(
    tmp_path: Path,
):
    state = git_state.collect_repository_state(tmp_path / "missing")

    assert state.default_base.status == "unknown"
    assert state.query_failures
    assert git_state.validate_repository_state_consistency(state) == []


def test_conflicted_paths_never_return_ready(tmp_path: Path):
    repo = _repo(tmp_path)
    _feature(repo, "left")
    _commit(repo, "tracked.txt", "left\n", "left")
    _git(repo, "switch", "main")
    _commit(repo, "tracked.txt", "right\n", "right")
    merge = _git(repo, "merge", "left", check=False)
    assert merge.returncode != 0

    state = git_state.collect_repository_state(repo, default_ref="main")

    assert state.tree.conflicted_paths == ["tracked.txt"]
    assert state.operation == "merge"
    assert state.derived_action != "READY_LOCAL"
    assert not git_state._guard_allows(state, "validation", allow_completion=False)


@pytest.mark.parametrize(
    ("marker", "operation"),
    [
        ("MERGE_HEAD", "merge"),
        ("CHERRY_PICK_HEAD", "cherry_pick"),
        ("REVERT_HEAD", "revert"),
        ("BISECT_START", "bisect"),
        ("rebase-merge", "rebase"),
    ],
)
def test_operation_markers_fail_closed_in_normal_checkout(
    tmp_path: Path, marker: str, operation: str
):
    repo = _repo(tmp_path)
    _feature(repo)
    _create_operation_marker(repo, marker)

    state = git_state.collect_repository_state(repo, default_ref="main")

    assert state.operation == operation
    assert state.derived_action != "READY_LOCAL"
    assert not git_state._guard_allows(state, "operation", allow_completion=False)


@pytest.mark.parametrize(
    ("marker", "operation"),
    [
        ("MERGE_HEAD", "merge"),
        ("CHERRY_PICK_HEAD", "cherry_pick"),
        ("REVERT_HEAD", "revert"),
        ("BISECT_START", "bisect"),
        ("rebase-apply", "rebase"),
    ],
)
def test_operation_markers_use_linked_worktree_git_path(
    tmp_path: Path, marker: str, operation: str
):
    repo = _repo(tmp_path)
    linked = tmp_path / "linked"
    _git(repo, "worktree", "add", "-b", "linked", str(linked))
    marker_path = _create_operation_marker(linked, marker)

    state = git_state.collect_repository_state(linked, default_ref="main")

    assert state.linked_worktree is True
    assert marker_path.exists()
    assert not (linked / ".git" / marker).exists()
    assert state.operation == operation
    assert state.derived_action != "READY_LOCAL"


def test_index_lock_is_reported_without_deleting_or_retrying(tmp_path: Path):
    repo = _repo(tmp_path)
    _feature(repo)
    lock = _marker_path(repo, "index.lock")
    lock.write_text("owned elsewhere\n", encoding="utf-8")

    state = git_state.collect_repository_state(repo, default_ref="main")

    assert state.derived_action == "HOLD_LOCKED"
    assert any(item.startswith("index.lock:") for item in state.locks)
    assert lock.read_text(encoding="utf-8") == "owned elsewhere\n"


def test_compatibility_guards_delegate_without_blocking_operation_completion(
    tmp_path: Path,
):
    repo = _repo(tmp_path)
    linked = tmp_path / "linked"
    _git(repo, "worktree", "add", "-b", "linked", str(linked))
    _create_operation_marker(linked, "MERGE_HEAD")
    merge_guard = REPO_ROOT / "scripts" / "check_unfinished_merge.sh"
    branch_guard = REPO_ROOT / "scripts" / "check_not_main.sh"

    standalone = subprocess.run(
        [
            str(merge_guard),
            "--repo",
            str(linked),
            "--default-ref",
            "main",
        ],
        capture_output=True,
        text=True,
    )
    completion = subprocess.run(
        [
            str(merge_guard),
            "--allow-operation-completion",
            "--repo",
            str(linked),
            "--default-ref",
            "main",
        ],
        capture_output=True,
        text=True,
    )
    main_guard = subprocess.run(
        [str(branch_guard), "--repo", str(repo), "--default-ref", "main"],
        capture_output=True,
        text=True,
    )

    assert standalone.returncode == 1
    assert "HOLD_OPERATION" in standalone.stdout
    assert completion.returncode == 0
    assert "HOLD_OPERATION" in completion.stdout
    assert main_guard.returncode == 1
    assert "HOLD_MAIN" in main_guard.stdout


def test_query_error_and_timeout_are_unknown_not_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = _repo(tmp_path)
    _feature(repo)
    runner = git_state.GitRunner(repo)
    real_run = runner.run

    def timed_out(args, **kwargs):
        if args and args[0] == "status":
            runner.failures.append(git_state.QueryFailure("git status", "timed out"))
            return None
        return real_run(args, **kwargs)

    monkeypatch.setattr(runner, "run", timed_out)
    timed_out_state = git_state.collect_repository_state(repo, runner=runner)
    missing_state = git_state.collect_repository_state(tmp_path / "missing")

    assert timed_out_state.derived_action == "HOLD_UNKNOWN"
    assert timed_out_state.tree.clean is False
    assert missing_state.derived_action == "HOLD_UNKNOWN"
    assert missing_state.query_failures


def test_upstream_ahead_behind_and_diverged_directions(tmp_path: Path):
    ahead_repo = _repo(tmp_path, "ahead")
    _feature(ahead_repo)
    _git(ahead_repo, "branch", "--set-upstream-to=main")
    _commit(ahead_repo, "ahead.txt", "ahead\n", "ahead")
    ahead = git_state.collect_repository_state(ahead_repo, default_ref="main")
    assert (ahead.upstream.ahead, ahead.upstream.behind, ahead.upstream.status) == (
        1,
        0,
        "ahead",
    )

    behind_repo = _repo(tmp_path, "behind")
    _feature(behind_repo)
    _git(behind_repo, "branch", "--set-upstream-to=main")
    _git(behind_repo, "switch", "main")
    _commit(behind_repo, "behind.txt", "behind\n", "advance main")
    _git(behind_repo, "switch", "feature")
    behind = git_state.collect_repository_state(behind_repo, default_ref="main")
    assert (behind.upstream.ahead, behind.upstream.behind, behind.upstream.status) == (
        0,
        1,
        "behind",
    )
    assert behind.derived_action == "HOLD_BEHIND"

    diverged_repo = _repo(tmp_path, "diverged")
    _feature(diverged_repo)
    _git(diverged_repo, "branch", "--set-upstream-to=main")
    _commit(diverged_repo, "feature.txt", "feature\n", "feature")
    _git(diverged_repo, "switch", "main")
    _commit(diverged_repo, "main.txt", "main\n", "main")
    _git(diverged_repo, "switch", "feature")
    diverged = git_state.collect_repository_state(diverged_repo, default_ref="main")
    assert (
        diverged.upstream.ahead,
        diverged.upstream.behind,
        diverged.upstream.status,
    ) == (1, 1, "diverged")
    assert diverged.derived_action == "HOLD_DIVERGED"


def test_default_base_and_upstream_are_independent_relations(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "switch", "-c", "tracking")
    _commit(repo, "tracking.txt", "tracking\n", "tracking")
    _git(repo, "switch", "main")
    _feature(repo)
    _commit(repo, "feature.txt", "feature\n", "feature")
    _git(repo, "branch", "--set-upstream-to=tracking")

    state = git_state.collect_repository_state(repo, default_ref="main")

    assert state.default_base.ref == "main"
    assert state.default_base.status == "ahead"
    assert state.upstream.ref == "tracking"
    assert state.upstream.status == "diverged"


def test_sibling_inventory_is_optional_lock_safe_and_unknown_on_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = _repo(tmp_path)
    linked_paths: list[Path] = []
    for index in range(1, 6):
        linked = tmp_path / f"linked-{index}"
        _git(repo, "worktree", "add", "-b", f"lane-{index}", str(linked))
        linked_paths.append(linked)
    _write(linked_paths[0], "dirty.txt", "dirty\n")

    real_run = git_state.subprocess.run
    observed_envs: list[dict[str, str]] = []

    def observe(*args, **kwargs):
        observed_envs.append(kwargs.get("env", {}))
        return real_run(*args, **kwargs)

    monkeypatch.setattr(git_state.subprocess, "run", observe)
    inventory = git_state.collect_worktree_inventory(repo, default_ref="main")

    assert len(inventory["worktrees"]) == 6
    assert any(item["dirty_count"] == 1 for item in inventory["worktrees"])
    assert observed_envs
    assert all(env.get("GIT_OPTIONAL_LOCKS") == "0" for env in observed_envs)
    assert all(env.get("GIT_TERMINAL_PROMPT") == "0" for env in observed_envs)

    real_collector = git_state.collect_repository_state

    def one_unknown(path, **kwargs):
        state = real_collector(path, **kwargs)
        if Path(path).name == "linked-5":
            state.query_failures.append(
                git_state.QueryFailure("git status", "timed out")
            )
            state.derived_action = "HOLD_UNKNOWN"
        return state

    unknown_inventory = git_state.collect_worktree_inventory(
        repo, default_ref="main", collector=one_unknown
    )
    assert any(
        item["query_status"] == "UNKNOWN" for item in unknown_inventory["worktrees"]
    )


def test_collection_is_non_mutating_and_meets_local_performance_budget(tmp_path: Path):
    repo = _repo(tmp_path)
    _feature(repo)
    refs_before = _git(repo, "for-each-ref", "--format=%(refname) %(objectname)").stdout
    status_before = _git(repo, "status", "--porcelain=v2", "--branch").stdout
    index = _marker_path(repo, "index")
    index_mtime_before = index.stat().st_mtime_ns

    durations = [
        git_state.collect_repository_state(repo, default_ref="main").duration_ms
        for _ in range(20)
    ]

    refs_after = _git(repo, "for-each-ref", "--format=%(refname) %(objectname)").stdout
    assert refs_after == refs_before
    assert index.stat().st_mtime_ns == index_mtime_before
    status_after = _git(repo, "status", "--porcelain=v2", "--branch").stdout
    assert status_after == status_before
    assert all(duration <= 500 for duration in durations)


def test_six_worktree_inventory_meets_budget(tmp_path: Path):
    repo = _repo(tmp_path)
    for index in range(1, 6):
        _git(
            repo,
            "worktree",
            "add",
            "-b",
            f"lane-{index}",
            str(tmp_path / f"lane-{index}"),
        )

    inventory = git_state.collect_worktree_inventory(repo, default_ref="main")

    assert len(inventory["worktrees"]) == 6
    assert inventory["duration_ms"] <= 2000


def test_cli_emits_typed_json_and_fail_closed_branch_guard(tmp_path: Path):
    repo = _repo(tmp_path)
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "git_state.py"),
        "--repo",
        str(repo),
        "--default-ref",
        "main",
        "--json",
    ]
    report = subprocess.run(command, capture_output=True, text=True, check=True)
    payload = json.loads(report.stdout)

    assert payload["schema_version"] == 1
    assert payload["derived_action"] == "HOLD_MAIN"
    branch_guard = subprocess.run(
        [*command[:-1], "--guard", "branch"], capture_output=True, text=True
    )
    assert branch_guard.returncode == 1
