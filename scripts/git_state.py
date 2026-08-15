#!/usr/bin/env python3
"""Read-only, worktree-aware Git state authority.

When to use: task intake, session trust, local validation, and any repository
automation that needs Git facts without changing Git or contacting a remote.

The kernel deliberately returns hold states instead of recovery commands. Every
Git subprocess disables optional locks and terminal prompting. No command in
this module fetches, stages, commits, switches, synchronizes, or deletes.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 1
DEFAULT_COMMAND_TIMEOUT_SECONDS = 1.0
SIBLING_COMMAND_TIMEOUT_SECONDS = 0.5
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RELATION_STATUSES = frozenset(
    {"ahead", "behind", "diverged", "equal", "none", "unknown"}
)
OPERATION_STATUSES = frozenset(
    {"none", "merge", "cherry_pick", "revert", "bisect", "rebase"}
)
DERIVED_ACTIONS = frozenset(
    {
        "READY_LOCAL",
        "HOLD_UNKNOWN",
        "HOLD_OPERATION",
        "HOLD_LOCKED",
        "HOLD_DETACHED",
        "HOLD_MAIN",
        "HOLD_DIVERGED",
        "HOLD_BEHIND",
        "HOLD_DIRTY",
    }
)
REMOTE_FRESHNESS_STATUSES = frozenset({"NOT_CHECKED"})
# Local state is consumed immediately during session closeout. A small bounded
# skew admits ordinary clock precision while preventing old or future evidence
# from being upgraded to current authority.
MAX_EVIDENCE_AGE = timedelta(minutes=5)
MAX_FUTURE_SKEW = timedelta(seconds=5)


@dataclass
class QueryFailure:
    """One required Git query that did not produce trustworthy evidence."""

    command: str
    reason: str


@dataclass
class Relation:
    """Directional reachability from HEAD to one named ref."""

    ref: str
    sha: str | None
    ahead: int | None
    behind: int | None
    status: str


@dataclass
class TreeState:
    """Porcelain-v2 index and working-tree classification."""

    staged_paths: list[str] = field(default_factory=list)
    modified_paths: list[str] = field(default_factory=list)
    untracked_paths: list[str] = field(default_factory=list)
    conflicted_paths: list[str] = field(default_factory=list)
    clean: bool = False

    @property
    def dirty_count(self) -> int:
        return len(
            set(
                self.staged_paths
                + self.modified_paths
                + self.untracked_paths
                + self.conflicted_paths
            )
        )


@dataclass
class RepositoryState:
    """Complete local evidence and fail-closed derived action."""

    schema_version: int
    observed_at_utc: str
    repository_root: str
    worktree_root: str | None
    git_dir: str | None
    git_common_dir: str | None
    linked_worktree: bool | None
    branch: str
    head_sha: str | None
    default_base: Relation
    upstream: Relation
    tree: TreeState
    operation: str
    operation_markers: list[str]
    locks: list[str]
    remote_freshness: str
    derived_action: str
    hold_reasons: list[str]
    query_failures: list[QueryFailure]
    duration_ms: float

    @property
    def ready_local(self) -> bool:
        return self.derived_action == "READY_LOCAL"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["tree"]["dirty_count"] = self.tree.dirty_count
        payload["ready_local"] = self.ready_local
        return payload


class GitRunner:
    """Bounded read-only Git subprocess runner with explicit failure capture."""

    def __init__(
        self,
        repo: Path | str,
        *,
        timeout: float = DEFAULT_COMMAND_TIMEOUT_SECONDS,
    ) -> None:
        self.repo = Path(repo).resolve()
        self.timeout = timeout
        self.failures: list[QueryFailure] = []

    def _failure(self, args: Sequence[str], reason: str, *, required: bool) -> None:
        if required:
            self.failures.append(QueryFailure("git " + " ".join(args), reason))

    def run(
        self,
        args: Sequence[str],
        *,
        required: bool = True,
        timeout: float | None = None,
    ) -> str | None:
        env = os.environ.copy()
        env.update(
            {
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_TERMINAL_PROMPT": "0",
                "LC_ALL": "C",
            }
        )
        command = ["git", "-C", str(self.repo), *args]
        try:
            result = subprocess.run(
                command,
                cwd=self.repo,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout if timeout is None else timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            self._failure(args, "timed out", required=required)
            return None
        except OSError as exc:
            self._failure(args, f"could not execute: {exc}", required=required)
            return None
        if result.returncode != 0:
            detail = result.stderr.strip().splitlines()
            reason = detail[0] if detail else f"exit {result.returncode}"
            self._failure(args, reason, required=required)
            return None
        return result.stdout.rstrip("\n")


def _empty_relation(ref: str, status: str) -> Relation:
    return Relation(ref=ref, sha=None, ahead=None, behind=None, status=status)


def _status_path(line: str) -> str:
    """Return the display path from one porcelain-v2 record."""
    if line.startswith("? "):
        return line[2:]
    if line.startswith("! "):
        return line[2:]
    fields = line.split(" ")
    if line.startswith("1 ") and len(fields) >= 9:
        return " ".join(fields[8:])
    if line.startswith("2 ") and len(fields) >= 10:
        return " ".join(fields[9:]).split("\t", 1)[0]
    if line.startswith("u ") and len(fields) >= 11:
        return " ".join(fields[10:])
    return "<unknown-path>"


def _parse_status(raw: str | None) -> tuple[dict[str, str], TreeState]:
    headers: dict[str, str] = {}
    tree = TreeState()
    if raw is None:
        return headers, tree
    for line in raw.splitlines():
        if line.startswith("# "):
            key, _, value = line[2:].partition(" ")
            headers[key] = value
            continue
        if line.startswith("? "):
            tree.untracked_paths.append(_status_path(line))
            continue
        if line.startswith("u "):
            tree.conflicted_paths.append(_status_path(line))
            continue
        if line.startswith(("1 ", "2 ")):
            fields = line.split(" ")
            xy = fields[1] if len(fields) > 1 else ".."
            path = _status_path(line)
            if xy[0:1] not in {"", "."}:
                tree.staged_paths.append(path)
            if xy[1:2] not in {"", "."}:
                tree.modified_paths.append(path)
    tree.clean = tree.dirty_count == 0
    return headers, tree


def _absolute_path(raw: str | None, repo: Path) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    return path if path.is_absolute() else (repo / path).resolve()


def _git_path(runner: GitRunner, name: str) -> Path | None:
    return _absolute_path(
        runner.run(["rev-parse", "--path-format=absolute", "--git-path", name]),
        runner.repo,
    )


def _detect_operation(runner: GitRunner) -> tuple[str, list[str]]:
    marker_names = {
        "merge": ("MERGE_HEAD",),
        "cherry_pick": ("CHERRY_PICK_HEAD",),
        "revert": ("REVERT_HEAD",),
        "bisect": ("BISECT_START",),
        "rebase": ("rebase-merge", "rebase-apply"),
    }
    active: list[str] = []
    operation = "none"
    for candidate, names in marker_names.items():
        for name in names:
            path = _git_path(runner, name)
            if path is not None and path.exists():
                active.append(f"{name}:{path}")
                if operation == "none":
                    operation = candidate
    return operation, active


def _detect_locks(runner: GitRunner, common_dir: Path | None) -> list[str]:
    locks: list[str] = []
    for name in ("index.lock", "HEAD.lock"):
        path = _git_path(runner, name)
        if path is not None and path.exists():
            locks.append(f"{name}:{path}")
    if common_dir is not None:
        for name in ("packed-refs.lock", "config.lock", "shallow.lock"):
            path = common_dir / name
            if path.exists():
                locks.append(f"{name}:{path}")
        refs = common_dir / "refs"
        if refs.is_dir():
            for path in sorted(refs.glob("**/*.lock")):
                locks.append(f"shared-ref-lock:{path}")
    return locks


def _resolve_default_ref(runner: GitRunner, requested: str | None) -> str | None:
    if requested:
        verified = runner.run(
            ["rev-parse", "--verify", "--quiet", f"{requested}^{{commit}}"]
        )
        return requested if verified else None

    remote_head = runner.run(
        ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        required=False,
    )
    candidates = [remote_head] if remote_head else []
    candidates.extend(["origin/main", "main", "origin/master", "master"])
    for candidate in candidates:
        if not candidate:
            continue
        verified = runner.run(
            ["rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"],
            required=False,
        )
        if verified:
            return candidate
    runner.failures.append(
        QueryFailure("resolve default base", "no default base ref found")
    )
    return None


def _relation(runner: GitRunner, ref: str | None, *, none_status: str) -> Relation:
    if ref is None:
        return _empty_relation("NONE", none_status)
    sha = runner.run(["rev-parse", "--verify", f"{ref}^{{commit}}"])
    counts = runner.run(["rev-list", "--left-right", "--count", f"HEAD...{ref}"])
    if sha is None or counts is None:
        return _empty_relation(ref, "unknown")
    try:
        ahead_text, behind_text = counts.split()
        ahead, behind = int(ahead_text), int(behind_text)
    except (ValueError, TypeError):
        runner.failures.append(
            QueryFailure(
                f"git rev-list --left-right --count HEAD...{ref}",
                f"unexpected output: {counts!r}",
            )
        )
        return _empty_relation(ref, "unknown")
    if ahead and behind:
        status = "diverged"
    elif ahead:
        status = "ahead"
    elif behind:
        status = "behind"
    else:
        status = "equal"
    return Relation(ref=ref, sha=sha, ahead=ahead, behind=behind, status=status)


def _derive_action(
    *,
    branch: str,
    head_sha: str | None,
    tree: TreeState,
    operation: str,
    locks: list[str],
    default_base: Relation,
    upstream: Relation,
    failures: list[QueryFailure],
) -> tuple[str, list[str]]:
    reasons: list[tuple[str, str]] = []
    if failures or branch == "UNKNOWN" or head_sha is None:
        reasons.append(("HOLD_UNKNOWN", "required Git evidence is unknown"))
    if operation != "none":
        reasons.append(("HOLD_OPERATION", f"active Git operation: {operation}"))
    if locks:
        reasons.append(("HOLD_LOCKED", f"Git lock detected ({len(locks)})"))
    if branch == "DETACHED":
        reasons.append(("HOLD_DETACHED", "HEAD is detached"))
    elif branch in {"main", "master"}:
        reasons.append(("HOLD_MAIN", f"current branch is {branch}"))
    relations = (default_base, upstream)
    if any(relation.status == "diverged" for relation in relations):
        reasons.append(("HOLD_DIVERGED", "HEAD and a required ref have diverged"))
    elif any(relation.status == "behind" for relation in relations):
        reasons.append(("HOLD_BEHIND", "HEAD is behind a required ref"))
    if tree.conflicted_paths:
        reasons.append(
            ("HOLD_DIRTY", f"conflicted paths: {len(tree.conflicted_paths)}")
        )
    elif tree.dirty_count:
        reasons.append(("HOLD_DIRTY", f"changed paths: {tree.dirty_count}"))
    if not reasons:
        return "READY_LOCAL", []
    return reasons[0][0], [message for _action, message in reasons]


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_valid_git_refname(value: object, *, branch: bool = False) -> bool:
    """Apply Git's ref-format constraints without invoking Git."""
    if not isinstance(value, str) or not value or (not branch and value == "@"):
        return False
    if branch and (value.startswith("-") or value == "HEAD"):
        return False
    if (
        value.startswith("/")
        or value.endswith("/")
        or value.endswith(".")
        or "//" in value
        or ".." in value
        or "@{" in value
    ):
        return False
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    if any(char in " ~^:?*[\\" for char in value):
        return False
    components = value.split("/")
    return all(
        component and not component.startswith(".") and not component.endswith(".lock")
        for component in components
    )


def _validate_relation(
    relation: object,
    *,
    name: str,
    allow_none: bool,
    query_failed: bool,
) -> list[str]:
    errors: list[str] = []
    required = ("ref", "sha", "ahead", "behind", "status")
    if not all(hasattr(relation, field) for field in required):
        return [f"{name} relation is malformed"]
    ref = relation.ref
    sha = relation.sha
    ahead = relation.ahead
    behind = relation.behind
    status = relation.status
    if (
        not isinstance(status, str)
        or status not in RELATION_STATUSES
        or (status == "none" and not allow_none)
    ):
        errors.append(f"{name} relation status is unsupported: {status!r}")
        return errors
    if status in {"ahead", "behind", "diverged", "equal"}:
        if ref == "NONE" or not _is_valid_git_refname(ref):
            errors.append(f"{name} relation ref is malformed")
        if not isinstance(sha, str) or SHA_RE.fullmatch(sha) is None:
            errors.append(f"{name} relation SHA is malformed")
        if not _is_nonnegative_int(ahead) or not _is_nonnegative_int(behind):
            errors.append(f"{name} relation counts are malformed")
        else:
            expected = (
                "diverged"
                if ahead and behind
                else "ahead" if ahead else "behind" if behind else "equal"
            )
            if status != expected:
                errors.append(f"{name} relation status contradicts counts")
    elif status == "none":
        if ref != "NONE" or any(value is not None for value in (sha, ahead, behind)):
            errors.append(f"{name} none relation is contradictory")
    elif status == "unknown":
        if ref != "NONE" and not _is_valid_git_refname(ref):
            errors.append(f"{name} relation ref is malformed")
        if any(value is not None for value in (sha, ahead, behind)):
            errors.append(f"{name} unknown relation is contradictory")
        if not query_failed:
            errors.append(f"{name} unknown relation lacks query failure evidence")
    return errors


def validate_repository_state_consistency(
    state: object, *, now_utc: datetime | None = None
) -> list[str]:
    """Validate the full canonical evidence contract without Git or network I/O."""
    required_fields = (
        "schema_version",
        "observed_at_utc",
        "repository_root",
        "worktree_root",
        "git_dir",
        "git_common_dir",
        "linked_worktree",
        "branch",
        "head_sha",
        "default_base",
        "upstream",
        "tree",
        "operation",
        "operation_markers",
        "locks",
        "remote_freshness",
        "derived_action",
        "hold_reasons",
        "query_failures",
        "duration_ms",
    )
    missing = [field for field in required_fields if not hasattr(state, field)]
    if missing:
        return [f"repository-state evidence is missing: {', '.join(missing)}"]

    errors: list[str] = []
    if state.schema_version != SCHEMA_VERSION or isinstance(state.schema_version, bool):
        errors.append(
            f"repository-state schema is unsupported: {state.schema_version!r}"
        )
    observed: datetime | None = None
    if not isinstance(state.observed_at_utc, str):
        errors.append("observed_at_utc is malformed")
    else:
        try:
            observed = datetime.fromisoformat(
                state.observed_at_utc.replace("Z", "+00:00")
            )
            if observed.tzinfo is None:
                errors.append("observed_at_utc lacks timezone")
                observed = None
        except ValueError:
            errors.append("observed_at_utc is malformed")
    current = now_utc or datetime.now(timezone.utc)
    if not isinstance(current, datetime) or current.tzinfo is None:
        errors.append("validation clock is malformed")
    elif observed is not None:
        current = current.astimezone(timezone.utc)
        observed = observed.astimezone(timezone.utc)
        if observed - current > MAX_FUTURE_SKEW:
            errors.append("observed_at_utc is in the future")
        elif current - observed > MAX_EVIDENCE_AGE:
            errors.append("observed_at_utc is stale")

    path_fields = ("repository_root", "worktree_root", "git_dir", "git_common_dir")
    for path_field in path_fields:
        value = getattr(state, path_field)
        if path_field == "repository_root" and (
            not isinstance(value, str) or not value or not Path(value).is_absolute()
        ):
            errors.append(f"{path_field} is malformed")
        elif value is not None and (
            not isinstance(value, str) or not value or not Path(value).is_absolute()
        ):
            errors.append(f"{path_field} is malformed")
    if isinstance(state.repository_root, str) and isinstance(state.worktree_root, str):
        if Path(state.repository_root) != Path(state.worktree_root):
            errors.append("repository_root contradicts worktree_root")
    if state.linked_worktree is not None and not isinstance(
        state.linked_worktree, bool
    ):
        errors.append("linked_worktree is malformed")
    if isinstance(state.git_dir, str) and isinstance(state.git_common_dir, str):
        expected_linked = state.git_dir != state.git_common_dir
        if state.linked_worktree is not expected_linked:
            errors.append("linked_worktree contradicts Git directory evidence")
        if state.linked_worktree is True and Path(state.git_dir).parent != (
            Path(state.git_common_dir) / "worktrees"
        ):
            errors.append("linked worktree Git directories are incoherent")
    elif state.linked_worktree is not None:
        errors.append("linked_worktree lacks complete Git directory evidence")

    if not isinstance(state.query_failures, list):
        errors.append("query_failures is malformed")
        query_failed = False
    else:
        query_failed = bool(state.query_failures)
        for failure in state.query_failures:
            if not all(
                hasattr(failure, field) for field in ("command", "reason")
            ) or not all(
                isinstance(getattr(failure, field, None), str)
                and bool(getattr(failure, field, None))
                for field in ("command", "reason")
            ):
                errors.append("query failure evidence is malformed")
                break
    if not query_failed and any(
        not isinstance(getattr(state, field), str)
        for field in ("worktree_root", "git_dir", "git_common_dir")
    ):
        errors.append("successful state lacks required Git path evidence")

    if not isinstance(state.branch, str) or not state.branch:
        errors.append("branch is malformed")
    if state.branch == "UNKNOWN":
        if state.head_sha is not None:
            errors.append("UNKNOWN branch contradicts HEAD SHA")
    elif state.branch != "DETACHED" and not _is_valid_git_refname(
        state.branch, branch=True
    ):
        errors.append("branch is malformed")
    if state.branch != "UNKNOWN" and (
        not isinstance(state.head_sha, str) or SHA_RE.fullmatch(state.head_sha) is None
    ):
        errors.append("head_sha is malformed")

    errors.extend(
        _validate_relation(
            state.default_base,
            name="default_base",
            allow_none=False,
            query_failed=query_failed,
        )
    )
    errors.extend(
        _validate_relation(
            state.upstream,
            name="upstream",
            allow_none=True,
            query_failed=query_failed,
        )
    )

    tree_fields = (
        "staged_paths",
        "modified_paths",
        "untracked_paths",
        "conflicted_paths",
        "clean",
        "dirty_count",
    )
    if not all(hasattr(state.tree, field) for field in tree_fields):
        errors.append("tree evidence is malformed")
    else:
        path_groups = [
            getattr(state.tree, field)
            for field in (
                "staged_paths",
                "modified_paths",
                "untracked_paths",
                "conflicted_paths",
            )
        ]
        if any(
            not isinstance(group, list)
            or any(not isinstance(path, str) or not path for path in group)
            or len(group) != len(set(group))
            for group in path_groups
        ):
            errors.append("tree path evidence is malformed")
        else:
            expected_count = len(set(path for group in path_groups for path in group))
            if state.tree.dirty_count != expected_count:
                errors.append("tree dirty_count contradicts paths")
            if not isinstance(state.tree.clean, bool):
                errors.append("tree clean flag is malformed")
            elif state.tree.clean and expected_count:
                errors.append("tree clean flag contradicts paths")
            elif not state.tree.clean and not expected_count and not query_failed:
                errors.append("tree dirty flag lacks paths or query failure")

    if (
        not isinstance(state.operation, str)
        or state.operation not in OPERATION_STATUSES
    ):
        errors.append(f"operation is unsupported: {state.operation!r}")
    if not isinstance(state.operation_markers, list) or any(
        not isinstance(marker, str) or not marker for marker in state.operation_markers
    ):
        errors.append("operation_markers is malformed")
    elif (state.operation == "none") != (not state.operation_markers):
        errors.append("operation contradicts operation markers")
    if not isinstance(state.locks, list) or any(
        not isinstance(lock, str) or not lock for lock in state.locks
    ):
        errors.append("locks are malformed")
    if (
        not isinstance(state.remote_freshness, str)
        or state.remote_freshness not in REMOTE_FRESHNESS_STATUSES
    ):
        errors.append(f"remote_freshness is unsupported: {state.remote_freshness!r}")
    if (
        not isinstance(state.derived_action, str)
        or state.derived_action not in DERIVED_ACTIONS
    ):
        errors.append(f"derived_action is unsupported: {state.derived_action!r}")
    if not isinstance(state.hold_reasons, list) or any(
        not isinstance(reason, str) or not reason for reason in state.hold_reasons
    ):
        errors.append("hold_reasons are malformed")
    if (
        not isinstance(state.duration_ms, (int, float))
        or isinstance(state.duration_ms, bool)
        or not math.isfinite(state.duration_ms)
        or state.duration_ms < 0
    ):
        errors.append("duration_ms is malformed")

    if errors:
        return errors
    expected_action, expected_reasons = _derive_action(
        branch=state.branch,
        head_sha=state.head_sha,
        tree=state.tree,
        operation=state.operation,
        locks=state.locks,
        default_base=state.default_base,
        upstream=state.upstream,
        failures=state.query_failures,
    )
    if state.derived_action != expected_action:
        errors.append(
            "derived_action contradicts canonical evidence: "
            f"expected {expected_action}, got {state.derived_action}"
        )
    if state.hold_reasons != expected_reasons:
        errors.append("hold_reasons contradict canonical evidence")
    return errors


def collect_repository_state(
    repo: Path | str = REPO_ROOT,
    *,
    default_ref: str | None = None,
    timeout: float = DEFAULT_COMMAND_TIMEOUT_SECONDS,
    runner: GitRunner | None = None,
) -> RepositoryState:
    """Collect one local repository/worktree state without mutation or network."""
    started = time.perf_counter()
    active_runner = runner or GitRunner(repo, timeout=timeout)
    requested_root = active_runner.repo
    status_raw = active_runner.run(
        ["status", "--porcelain=v2", "--branch", "--untracked-files=all"]
    )
    headers, tree = _parse_status(status_raw)

    worktree_root = _absolute_path(
        active_runner.run(["rev-parse", "--path-format=absolute", "--show-toplevel"]),
        requested_root,
    )
    git_dir = _absolute_path(
        active_runner.run(["rev-parse", "--path-format=absolute", "--git-dir"]),
        requested_root,
    )
    common_dir = _absolute_path(
        active_runner.run(["rev-parse", "--path-format=absolute", "--git-common-dir"]),
        requested_root,
    )

    branch_header = headers.get("branch.head")
    if status_raw is None:
        branch = "UNKNOWN"
    elif branch_header == "(detached)":
        branch = "DETACHED"
    elif not branch_header or branch_header == "(unknown)":
        branch = "UNKNOWN"
    else:
        branch = branch_header
    oid = headers.get("branch.oid")
    head_sha = None if not oid or oid == "(initial)" else oid

    resolved_default = _resolve_default_ref(active_runner, default_ref)
    default_base = _relation(active_runner, resolved_default, none_status="unknown")
    upstream_ref = headers.get("branch.upstream")
    upstream = _relation(active_runner, upstream_ref, none_status="none")
    operation, operation_markers = _detect_operation(active_runner)
    locks = _detect_locks(active_runner, common_dir)
    linked = (
        git_dir != common_dir
        if git_dir is not None and common_dir is not None
        else None
    )
    action, hold_reasons = _derive_action(
        branch=branch,
        head_sha=head_sha,
        tree=tree,
        operation=operation,
        locks=locks,
        default_base=default_base,
        upstream=upstream,
        failures=active_runner.failures,
    )
    return RepositoryState(
        schema_version=SCHEMA_VERSION,
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        repository_root=str(requested_root),
        worktree_root=str(worktree_root) if worktree_root else None,
        git_dir=str(git_dir) if git_dir else None,
        git_common_dir=str(common_dir) if common_dir else None,
        linked_worktree=linked,
        branch=branch,
        head_sha=head_sha,
        default_base=default_base,
        upstream=upstream,
        tree=tree,
        operation=operation,
        operation_markers=operation_markers,
        locks=locks,
        remote_freshness="NOT_CHECKED",
        derived_action=action,
        hold_reasons=hold_reasons,
        query_failures=list(active_runner.failures),
        duration_ms=round((time.perf_counter() - started) * 1000, 3),
    )


def _parse_worktrees(raw: str | None) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in [*(raw or "").splitlines(), ""]:
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return records


def collect_worktree_inventory(
    repo: Path | str = REPO_ROOT,
    *,
    default_ref: str | None = None,
    timeout: float = SIBLING_COMMAND_TIMEOUT_SECONDS,
    collector: Callable[..., RepositoryState] = collect_repository_state,
) -> dict[str, Any]:
    """Collect bounded per-worktree summaries; a failed sibling stays unknown."""
    started = time.perf_counter()
    root = Path(repo).resolve()
    current = collector(root, default_ref=default_ref, timeout=timeout)
    runner = GitRunner(root, timeout=timeout)
    raw = runner.run(["worktree", "list", "--porcelain"])
    worktrees: list[dict[str, Any]] = []
    current_root = (
        Path(current.worktree_root).resolve() if current.worktree_root else root
    )
    for record in _parse_worktrees(raw):
        path = Path(record.get("worktree", ""))
        try:
            is_current = path.resolve() == current_root
        except OSError:
            is_current = False
        state = (
            current
            if is_current
            else collector(path, default_ref=default_ref, timeout=timeout)
        )
        worktrees.append(
            {
                "path": str(path),
                "current": is_current,
                "branch": state.branch,
                "head_sha": state.head_sha,
                "dirty_count": state.tree.dirty_count,
                "operation": state.operation,
                "derived_action": state.derived_action,
                "query_status": "UNKNOWN" if state.query_failures else "OK",
            }
        )
    failures = [asdict(item) for item in runner.failures]
    if raw is None and not worktrees:
        worktrees.append(
            {
                "path": str(root),
                "current": True,
                "branch": current.branch,
                "head_sha": current.head_sha,
                "dirty_count": current.tree.dirty_count,
                "operation": current.operation,
                "derived_action": "HOLD_UNKNOWN",
                "query_status": "UNKNOWN",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "current": current.to_dict(),
        "worktrees": worktrees,
        "query_failures": failures,
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def _relation_text(relation: Relation) -> str:
    if relation.status in {"none", "unknown"}:
        return f"{relation.ref} ({relation.status})"
    short = relation.sha[:8] if relation.sha else "unknown"
    return f"{relation.ref}@{short} (+{relation.ahead}/-{relation.behind})"


def format_human(state: RepositoryState) -> str:
    """Concise stable output for humans and check orchestration."""
    head = state.head_sha[:8] if state.head_sha else "unknown"
    tree = state.tree
    lines = [
        f"Git state: {state.derived_action}",
        f"  lane: {state.branch} @ {head}",
        f"  tree: staged={len(tree.staged_paths)} modified={len(tree.modified_paths)} "
        f"untracked={len(tree.untracked_paths)} conflicted={len(tree.conflicted_paths)}",
        f"  default: {_relation_text(state.default_base)}",
        f"  upstream: {_relation_text(state.upstream)}",
        f"  operation: {state.operation} | locks={len(state.locks)} | "
        f"remote={state.remote_freshness}",
        f"  observed: {state.duration_ms:.1f} ms",
    ]
    for reason in state.hold_reasons:
        lines.append(f"  hold: {reason}")
    for failure in state.query_failures:
        lines.append(f"  unknown: {failure.command}: {failure.reason}")
    return "\n".join(lines)


def _guard_allows(
    state: RepositoryState, guard: str, *, allow_completion: bool
) -> bool:
    if guard == "branch":
        return (
            state.branch not in {"main", "master", "DETACHED", "UNKNOWN"}
            and not state.query_failures
        )
    if guard == "operation":
        if state.query_failures or state.locks or state.tree.conflicted_paths:
            return False
        return allow_completion or state.operation == "none"
    if guard == "validation":
        if (
            state.query_failures
            or state.operation != "none"
            or state.locks
            or state.branch in {"DETACHED", "UNKNOWN"}
            or state.tree.conflicted_paths
            or state.default_base.status in {"behind", "diverged", "unknown"}
            or state.upstream.status in {"behind", "diverged", "unknown"}
        ):
            return False
        return True
    raise ValueError(f"unknown guard: {guard}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--default-ref")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--worktrees", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--guard", choices=("branch", "operation", "validation"))
    parser.add_argument(
        "--allow-operation-completion",
        action="store_true",
        help="For the pre-commit compatibility entrypoint only.",
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_COMMAND_TIMEOUT_SECONDS
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.allow_operation_completion and args.guard != "operation":
        print(
            "ERROR: --allow-operation-completion requires --guard operation",
            file=sys.stderr,
        )
        return 2
    if args.worktrees:
        inventory = collect_worktree_inventory(
            args.repo, default_ref=args.default_ref, timeout=args.timeout
        )
        if args.as_json:
            print(json.dumps(inventory, indent=2, sort_keys=True))
        else:
            print(
                format_human(
                    collect_repository_state(args.repo, default_ref=args.default_ref)
                )
            )
            print(
                f"Worktrees: {len(inventory['worktrees'])} ({inventory['duration_ms']:.1f} ms)"
            )
            for item in inventory["worktrees"]:
                marker = "*" if item["current"] else " "
                print(
                    f" {marker} {item['branch']} | dirty={item['dirty_count']} | "
                    f"{item['query_status']} | {item['path']}"
                )
        unknown = bool(inventory["query_failures"]) or any(
            item["query_status"] == "UNKNOWN" for item in inventory["worktrees"]
        )
        return 1 if args.strict and unknown else 0

    state = collect_repository_state(
        args.repo, default_ref=args.default_ref, timeout=args.timeout
    )
    print(
        json.dumps(state.to_dict(), indent=2, sort_keys=True)
        if args.as_json
        else format_human(state)
    )
    if args.guard:
        return (
            0
            if _guard_allows(
                state,
                args.guard,
                allow_completion=args.allow_operation_completion,
            )
            else 1
        )
    if args.strict:
        return 0 if state.ready_local else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
