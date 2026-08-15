#!/usr/bin/env python3
"""Classify branch/worktree disposition from inspection-only evidence.

When to use: after the caller has refreshed remote and pull-request evidence.
This command performs bounded local Git reads only. It never contacts a remote,
changes refs or configuration, changes worktrees, or authorizes retirement.

The evidence file is JSON with this shape::

    {
      "schema_version": 1,
      "remote_freshness": {
        "status": "OBSERVED_AT",
        "observed_at_utc": "2026-08-15T05:00:00Z",
        "default_ref": "origin/main",
        "default_sha": "<sha>"
      },
      "branches": {
        "codex/example": {
          "owner": "TASK-123",
          "remote_ref": {
            "status": "PRESENT",
            "ref": "refs/heads/codex/example",
            "sha": "<sha>"
          },
          "pull_requests": {
            "status": "NONE_OPEN",
            "observed_at_utc": "2026-08-15T05:00:00Z",
            "head_sha": "<sha>",
            "items": []
          },
          "retention": {
            "status": "NO_RETENTION",
            "observed_at_utc": "2026-08-15T05:00:00Z",
            "head_sha": "<sha>",
            "reason": null
          }
        }
      }
    }

Use ``remote_ref.status = ABSENT`` only when the caller has just proved that
the remote branch is absent. ``NOT_CHECKED`` and every missing/failed query are
holds. The JSON receipt is evidence for a later, separately authorized action;
it is not an action request.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.git_state import collect_worktree_inventory  # noqa: E402

SCHEMA_VERSION = 1
DEFAULT_TIMEOUT_SECONDS = 2.0
MAX_EVIDENCE_AGE_SECONDS = 900.0

HOLD_ATTACHED_OR_DIRTY = "HOLD_ATTACHED_OR_DIRTY"
HOLD_UNKNOWN_OWNER = "HOLD_UNKNOWN_OWNER"
HOLD_OPEN_OR_DEPENDENT_PR = "HOLD_OPEN_OR_DEPENDENT_PR"
HOLD_UNIQUE_OR_UNPUBLISHED_WORK = "HOLD_UNIQUE_OR_UNPUBLISHED_WORK"
HOLD_EVIDENCE_RETENTION = "HOLD_EVIDENCE_RETENTION"
PATCH_EQUIVALENT_REVIEW_REQUIRED = "PATCH_EQUIVALENT_REVIEW_REQUIRED"
RETIREMENT_READY_PENDING_APPROVAL = "RETIREMENT_READY_PENDING_APPROVAL"


@dataclass(frozen=True)
class QueryFailure:
    """One required inspection that did not produce trustworthy evidence."""

    command: str
    reason: str


class GitRunner:
    """Run bounded, local-only Git queries and retain every failure."""

    def __init__(
        self,
        repo: Path | str,
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.repo = Path(repo).resolve()
        self.timeout = timeout
        self.failures: list[QueryFailure] = []

    def _record(self, args: Sequence[str], reason: str) -> None:
        self.failures.append(QueryFailure("git " + " ".join(args), reason))

    def run(
        self,
        args: Sequence[str],
        *,
        required: bool = True,
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
                timeout=self.timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            if required:
                self._record(args, "timed out")
            return None
        except OSError as exc:
            if required:
                self._record(args, f"could not execute: {exc}")
            return None
        if result.returncode != 0:
            if required:
                detail = result.stderr.strip().splitlines()
                self._record(
                    args,
                    detail[0] if detail else f"exit {result.returncode}",
                )
            return None
        return result.stdout.rstrip("\n")


def _ref_sha(runner: GitRunner, ref: str) -> str | None:
    """Resolve an exact ref without treating an absent optional ref as error."""
    output = runner.run(
        ["for-each-ref", "--format=%(objectname)", ref],
        required=False,
    )
    if output is None:
        runner.failures.append(QueryFailure(f"resolve {ref}", "query failed"))
        return None
    values = [line.strip() for line in output.splitlines() if line.strip()]
    if len(values) > 1:
        runner.failures.append(
            QueryFailure(f"resolve {ref}", "more than one exact ref matched")
        )
        return None
    return values[0] if values else None


def _required_ref_sha(runner: GitRunner, ref: str) -> str | None:
    sha = runner.run(["rev-parse", "--verify", f"{ref}^{{commit}}"])
    return sha.strip() if sha else None


def _parse_count(
    runner: GitRunner,
    command: Sequence[str],
    output: str | None,
) -> int | None:
    if output is None:
        return None
    try:
        return int(output.strip())
    except ValueError:
        runner.failures.append(
            QueryFailure(
                "git " + " ".join(command),
                f"unexpected integer output: {output!r}",
            )
        )
        return None


def _parse_cherry(
    runner: GitRunner,
    default_ref: str,
    target_ref: str,
) -> dict[str, Any]:
    command = ["cherry", default_ref, target_ref]
    output = runner.run(command)
    entries: list[dict[str, str]] = []
    if output is not None:
        for line in output.splitlines():
            marker, separator, sha = line.partition(" ")
            if marker not in {"+", "-"} or not separator or not sha.strip():
                runner.failures.append(
                    QueryFailure(
                        "git " + " ".join(command),
                        f"unexpected output line: {line!r}",
                    )
                )
                continue
            entries.append(
                {
                    "patch_status": ("UNIQUE" if marker == "+" else "EQUIVALENT"),
                    "sha": sha.strip(),
                }
            )
    return {
        "unique_patch_count": sum(item["patch_status"] == "UNIQUE" for item in entries),
        "equivalent_patch_count": sum(
            item["patch_status"] == "EQUIVALENT" for item in entries
        ),
        "entries": entries,
    }


def _branch_age_days(
    runner: GitRunner,
    target_ref: str,
    *,
    now: datetime,
) -> int | None:
    output = runner.run(["show", "-s", "--format=%ct", target_ref])
    if output is None:
        return None
    try:
        committed_at = datetime.fromtimestamp(int(output.strip()), tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        runner.failures.append(
            QueryFailure(
                f"git show -s --format=%ct {target_ref}",
                f"unexpected timestamp: {output!r}",
            )
        )
        return None
    return max(0, (now - committed_at).days)


def _worktree_matches(inventory: dict[str, Any], branch: str) -> list[dict[str, Any]]:
    return [
        item for item in inventory.get("worktrees", []) if item.get("branch") == branch
    ]


def _default_branch_name(default_ref: str, remote: str) -> str | None:
    """Return the branch portion of a configured local/remote default ref."""
    prefixes = ("refs/heads/", f"refs/remotes/{remote}/", f"{remote}/")
    for prefix in prefixes:
        if default_ref.startswith(prefix):
            name = default_ref.removeprefix(prefix)
            return name or None
    return default_ref if "/" not in default_ref else None


def _branch_evidence(evidence: dict[str, Any], branch: str) -> dict[str, Any]:
    branches = evidence.get("branches", {})
    if not isinstance(branches, dict):
        return {}
    value = branches.get(branch, {})
    return value if isinstance(value, dict) else {}


def _unknown(
    result: dict[str, Any],
    *reason_codes: str,
) -> dict[str, Any]:
    result["status"] = "UNKNOWN"
    result["disposition"] = HOLD_UNKNOWN_OWNER
    result["reason_codes"] = list(dict.fromkeys(reason_codes))
    result["next_action"] = (
        "Hold. Refresh or correct the named evidence and re-run inspection."
    )
    return result


def _observation_problem(value: Any, *, now: datetime) -> str | None:
    """Return why one required observation timestamp is not fresh enough."""
    if not isinstance(value, str) or not value.strip():
        return "MISSING"
    try:
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "INVALID"
    if observed.tzinfo is None:
        return "INVALID"
    age_seconds = (now - observed.astimezone(timezone.utc)).total_seconds()
    if age_seconds < -60:
        return "FUTURE"
    if age_seconds > MAX_EVIDENCE_AGE_SECONDS:
        return "STALE"
    return None


def _validate_supplied_evidence(
    *,
    evidence: dict[str, Any],
    branch_evidence: dict[str, Any],
    branch: str,
    default_ref: str,
    default_sha: str | None,
    local_sha: str | None,
    remote_tracking_sha: str | None,
    target_sha: str | None,
    now: datetime,
) -> list[str]:
    reasons: list[str] = []
    freshness = evidence.get("remote_freshness", {})
    if not isinstance(freshness, dict) or freshness.get("status") != "OBSERVED_AT":
        reasons.append("REMOTE_FRESHNESS_NOT_CHECKED")
    else:
        remote_time_problem = _observation_problem(
            freshness.get("observed_at_utc"), now=now
        )
        if remote_time_problem:
            reasons.append(f"REMOTE_OBSERVATION_{remote_time_problem}")
        if freshness.get("default_ref") != default_ref:
            reasons.append("REMOTE_DEFAULT_REF_MISMATCH")
        if not default_sha or freshness.get("default_sha") != default_sha:
            reasons.append("REMOTE_DEFAULT_SHA_MISMATCH")

    owner = branch_evidence.get("owner")
    if not isinstance(owner, str) or not owner.strip():
        reasons.append("OWNER_UNKNOWN")

    remote_ref_value = branch_evidence.get("remote_ref", {})
    if not isinstance(remote_ref_value, dict):
        reasons.append("REMOTE_REF_EVIDENCE_MISSING")
        remote_ref: dict[str, Any] = {}
    else:
        remote_ref = remote_ref_value
        expected_ref = f"refs/heads/{branch}"
        if remote_ref.get("ref") != expected_ref:
            reasons.append("REMOTE_BRANCH_REF_MISMATCH")
        remote_status = remote_ref.get("status")
        if remote_status == "PRESENT":
            supplied_sha = remote_ref.get("sha")
            if not supplied_sha:
                reasons.append("REMOTE_BRANCH_SHA_MISSING")
            if remote_tracking_sha and supplied_sha != remote_tracking_sha:
                reasons.append("REMOTE_TRACKING_SHA_MISMATCH")
        elif remote_status == "ABSENT":
            if remote_tracking_sha is not None:
                reasons.append("REMOTE_ABSENCE_CONTRADICTS_TRACKING_REF")
        else:
            reasons.append("REMOTE_REF_EVIDENCE_UNKNOWN")

    pull_requests = branch_evidence.get("pull_requests", {})
    if not isinstance(pull_requests, dict):
        reasons.append("PULL_REQUEST_EVIDENCE_MISSING")
    else:
        pr_status = pull_requests.get("status")
        if pr_status not in {"OPEN", "DEPENDENT", "NONE_OPEN"}:
            reasons.append("PULL_REQUEST_EVIDENCE_UNKNOWN")
        pr_time_problem = _observation_problem(
            pull_requests.get("observed_at_utc"), now=now
        )
        if pr_time_problem:
            reasons.append(f"PULL_REQUEST_OBSERVATION_{pr_time_problem}")
        if pr_status == "NONE_OPEN" and pull_requests.get("head_sha") != target_sha:
            reasons.append("PULL_REQUEST_HEAD_EVIDENCE_MISMATCH")

    retention = branch_evidence.get("retention", {})
    if not isinstance(retention, dict) or retention.get("status") not in {
        "RETAIN",
        "NO_RETENTION",
    }:
        reasons.append("RETENTION_EVIDENCE_UNKNOWN")
    else:
        retention_time_problem = _observation_problem(
            retention.get("observed_at_utc"), now=now
        )
        if retention_time_problem:
            reasons.append(f"RETENTION_OBSERVATION_{retention_time_problem}")
        if retention.get("head_sha") != target_sha:
            reasons.append("RETENTION_HEAD_EVIDENCE_MISMATCH")

    if local_sha and remote_ref.get("status") == "PRESENT":
        supplied_remote_sha = remote_ref.get("sha")
        if supplied_remote_sha and local_sha != supplied_remote_sha:
            # This is known unpublished/diverged work, not missing evidence.
            pass
    return reasons


def classify_branch(
    *,
    repo: Path,
    branch: str,
    default_ref: str,
    remote: str,
    evidence: dict[str, Any],
    inventory: dict[str, Any],
    now: datetime,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Classify one branch from local facts and caller-supplied remote facts."""
    started = time.perf_counter()
    runner = GitRunner(repo, timeout=timeout)
    local_ref = f"refs/heads/{branch}"
    remote_tracking_ref = f"refs/remotes/{remote}/{branch}"
    local_sha = _ref_sha(runner, local_ref)
    remote_tracking_sha = _ref_sha(runner, remote_tracking_ref)
    target_ref = local_ref if local_sha else remote_tracking_ref
    target_sha = local_sha or remote_tracking_sha
    default_sha = _required_ref_sha(runner, default_ref)
    branch_input = _branch_evidence(evidence, branch)
    worktrees = _worktree_matches(inventory, branch)

    result: dict[str, Any] = {
        "branch": branch,
        "status": "HOLD",
        "disposition": HOLD_UNKNOWN_OWNER,
        "reason_codes": [],
        "identity": {
            "local_ref": local_ref,
            "local_sha": local_sha,
            "remote_tracking_ref": remote_tracking_ref,
            "remote_tracking_sha": remote_tracking_sha,
            "inspected_ref": target_ref if target_sha else None,
            "head_sha": target_sha,
            "is_default_branch": branch == _default_branch_name(default_ref, remote),
        },
        "owner": branch_input.get("owner"),
        "worktrees": worktrees,
        "pull_requests": branch_input.get("pull_requests", {}),
        "retention": branch_input.get("retention", {}),
        "remote_ref_evidence": branch_input.get("remote_ref", {}),
        "facts": {
            "age_days": None,
            "age_is_authority": False,
            "ahead_commit_count": None,
            "behind_commit_count": None,
            "reachable_from_default": None,
            "cherry": {
                "unique_patch_count": None,
                "equivalent_patch_count": None,
                "entries": [],
            },
            "tree": {
                "branch_tree_sha": None,
                "default_tree_sha": None,
                "equal": None,
            },
        },
        "query_failures": [],
        "next_action": "Hold pending complete evidence.",
        "duration_ms": None,
    }

    if target_sha is None:
        runner.failures.append(
            QueryFailure(
                f"resolve {local_ref} or {remote_tracking_ref}",
                "target branch is absent from local refs",
            )
        )
    if target_sha is not None and default_sha is not None:
        ahead_command = ["rev-list", "--count", f"{default_ref}..{target_ref}"]
        behind_command = ["rev-list", "--count", f"{target_ref}..{default_ref}"]
        ahead = _parse_count(runner, ahead_command, runner.run(ahead_command))
        behind = _parse_count(runner, behind_command, runner.run(behind_command))
        cherry = _parse_cherry(runner, default_ref, target_ref)
        branch_tree_sha = runner.run(
            ["rev-parse", "--verify", f"{target_ref}^{{tree}}"]
        )
        default_tree_sha = runner.run(
            ["rev-parse", "--verify", f"{default_ref}^{{tree}}"]
        )
        result["facts"].update(
            {
                "age_days": _branch_age_days(runner, target_ref, now=now),
                "ahead_commit_count": ahead,
                "behind_commit_count": behind,
                "reachable_from_default": ahead == 0 if ahead is not None else None,
                "cherry": cherry,
                "tree": {
                    "branch_tree_sha": branch_tree_sha,
                    "default_tree_sha": default_tree_sha,
                    "equal": (
                        branch_tree_sha == default_tree_sha
                        if branch_tree_sha and default_tree_sha
                        else None
                    ),
                },
            }
        )

    unknown_reasons = _validate_supplied_evidence(
        evidence=evidence,
        branch_evidence=branch_input,
        branch=branch,
        default_ref=default_ref,
        default_sha=default_sha,
        local_sha=local_sha,
        remote_tracking_sha=remote_tracking_sha,
        target_sha=target_sha,
        now=now,
    )
    inventory_failures = inventory.get("query_failures", [])
    if inventory_failures:
        unknown_reasons.append("WORKTREE_INVENTORY_QUERY_FAILED")
    if any(item.get("query_status") == "UNKNOWN" for item in worktrees):
        unknown_reasons.append("ATTACHED_WORKTREE_QUERY_FAILED")
    if runner.failures:
        unknown_reasons.append("GIT_QUERY_FAILED")

    result["query_failures"] = [asdict(item) for item in runner.failures]
    result["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
    if unknown_reasons:
        return _unknown(result, *unknown_reasons)

    if result["identity"]["is_default_branch"]:
        result.update(
            {
                "status": "HOLD",
                "disposition": HOLD_EVIDENCE_RETENTION,
                "reason_codes": ["DEFAULT_BRANCH_INTEGRATION_ANCHOR"],
                "next_action": "Hold. The configured default branch is never a retirement candidate.",
            }
        )
        return result

    dirty_worktrees = [item for item in worktrees if item.get("dirty_count", 0)]
    active_worktrees = [
        item for item in worktrees if item.get("operation") not in {None, "none"}
    ]
    if worktrees:
        reasons = []
        if dirty_worktrees:
            reasons.append("DIRTY_WORKTREE")
        if active_worktrees:
            reasons.append("WORKTREE_OPERATION_ACTIVE")
        if not reasons:
            reasons.append("ATTACHED_WORKTREE")
        result.update(
            {
                "status": "HOLD",
                "disposition": HOLD_ATTACHED_OR_DIRTY,
                "reason_codes": reasons,
                "next_action": (
                    "Hold. Attachment and dirty/operation state require separate "
                    "ownership resolution; no retirement action is authorized."
                ),
            }
        )
        return result

    pull_requests = branch_input["pull_requests"]
    if pull_requests["status"] in {"OPEN", "DEPENDENT"}:
        result.update(
            {
                "status": "HOLD",
                "disposition": HOLD_OPEN_OR_DEPENDENT_PR,
                "reason_codes": [f"{pull_requests['status']}_PULL_REQUEST"],
                "next_action": "Hold while the open or dependent PR exists.",
            }
        )
        return result

    retention = branch_input["retention"]
    if retention["status"] == "RETAIN":
        result.update(
            {
                "status": "HOLD",
                "disposition": HOLD_EVIDENCE_RETENTION,
                "reason_codes": ["EXPLICIT_RETENTION"],
                "next_action": "Hold as explicitly retained evidence.",
            }
        )
        return result

    remote_ref = branch_input["remote_ref"]
    local_remote_mismatch = (
        local_sha is not None
        and remote_ref["status"] == "PRESENT"
        and remote_ref.get("sha") != local_sha
    )
    ahead = result["facts"]["ahead_commit_count"]
    cherry = result["facts"]["cherry"]
    tree_equal = result["facts"]["tree"]["equal"]
    patch_equivalent = (
        ahead is not None
        and ahead > 0
        and cherry["unique_patch_count"] == 0
        and cherry["equivalent_patch_count"] > 0
    )
    if local_remote_mismatch:
        result.update(
            {
                "status": "HOLD",
                "disposition": HOLD_UNIQUE_OR_UNPUBLISHED_WORK,
                "reason_codes": ["LOCAL_REMOTE_HEAD_MISMATCH"],
                "next_action": "Hold. Local and observed remote heads differ.",
            }
        )
        return result
    if ahead and (patch_equivalent or tree_equal is True):
        reason = "PATCH_EQUIVALENT" if patch_equivalent else "TREE_EQUIVALENT"
        result.update(
            {
                "status": "REVIEW_REQUIRED",
                "disposition": PATCH_EQUIVALENT_REVIEW_REQUIRED,
                "reason_codes": [reason],
                "next_action": (
                    "Review the exact patch/tree and integration receipt; "
                    "equivalence alone is not retirement authority."
                ),
            }
        )
        return result
    if ahead:
        result.update(
            {
                "status": "HOLD",
                "disposition": HOLD_UNIQUE_OR_UNPUBLISHED_WORK,
                "reason_codes": ["UNIQUE_COMMITS_OR_PATCHES"],
                "next_action": "Hold and preserve the unique work before any topology change.",
            }
        )
        return result

    result.update(
        {
            "status": "CANDIDATE",
            "disposition": RETIREMENT_READY_PENDING_APPROVAL,
            "reason_codes": ["FULL_EVIDENCE_REVIEW_COMPLETE"],
            "next_action": (
                "Obtain separate exact-target authorization, then re-inspect "
                "before any local, remote, or worktree action."
            ),
        }
    )
    return result


def classify_repository(
    *,
    repo: Path | str,
    branches: Sequence[str],
    evidence: dict[str, Any] | None = None,
    default_ref: str = "origin/main",
    remote: str = "origin",
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a machine-readable, inspection-only disposition receipt."""
    started = time.perf_counter()
    root = Path(repo).resolve()
    supplied = evidence or {}
    observed_now = now or datetime.now(timezone.utc)
    input_reasons: list[str] = []
    if evidence is not None and supplied.get("schema_version") != SCHEMA_VERSION:
        input_reasons.append("EVIDENCE_SCHEMA_UNKNOWN")
    if not isinstance(supplied.get("branches", {}), dict):
        input_reasons.append("BRANCH_EVIDENCE_INVALID")
    remote_freshness = supplied.get("remote_freshness", {})
    if not isinstance(remote_freshness, dict):
        input_reasons.append("REMOTE_FRESHNESS_EVIDENCE_INVALID")
        remote_freshness = {"status": "UNKNOWN"}
    inventory = collect_worktree_inventory(
        root,
        default_ref=default_ref,
        timeout=min(timeout, 0.5),
    )
    targets = [
        classify_branch(
            repo=root,
            branch=branch,
            default_ref=default_ref,
            remote=remote,
            evidence=supplied,
            inventory=inventory,
            now=observed_now,
            timeout=timeout,
        )
        for branch in dict.fromkeys(branches)
    ]
    if input_reasons:
        for target in targets:
            _unknown(target, *target["reason_codes"], *input_reasons)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "observed_at_utc": observed_now.isoformat(),
        "repository_root": str(root),
        "default_ref": default_ref,
        "remote": remote,
        "remote_freshness": remote_freshness or {"status": "NOT_CHECKED"},
        "mutation_policy": "INSPECTION_ONLY",
        "authorization": "SEPARATE_EXACT_TARGET_APPROVAL_REQUIRED",
        "targets": targets,
        "query_failures": inventory.get("query_failures", []),
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
    }
    receipt["status"] = (
        "UNKNOWN"
        if receipt["query_failures"]
        or any(target["status"] == "UNKNOWN" for target in targets)
        else "INSPECTED"
    )
    return receipt


def _local_branches(repo: Path, timeout: float) -> tuple[list[str], list[QueryFailure]]:
    runner = GitRunner(repo, timeout=timeout)
    output = runner.run(["for-each-ref", "--format=%(refname:strip=2)", "refs/heads"])
    branches = (
        []
        if output is None
        else sorted(
            branch
            for branch in output.splitlines()
            if branch and branch not in {"main", "master"}
        )
    )
    return branches, runner.failures


def _load_evidence(path: Path | None) -> tuple[dict[str, Any], str | None]:
    if path is None:
        return {}, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"could not read evidence: {exc}"
    if not isinstance(payload, dict):
        return {}, "evidence root must be a JSON object"
    if payload.get("schema_version") != SCHEMA_VERSION:
        return {}, f"evidence schema_version must be {SCHEMA_VERSION}"
    return payload, None


def _format_human(receipt: dict[str, Any]) -> str:
    lines = [
        "Branch disposition: INSPECTION_ONLY",
        f"  remote freshness: {receipt['remote_freshness'].get('status', 'NOT_CHECKED')}",
    ]
    for target in receipt["targets"]:
        age = target["facts"]["age_days"]
        age_text = "unknown" if age is None else f"{age}d metadata-only"
        lines.append(
            f"  {target['branch']}: {target['disposition']} "
            f"[{', '.join(target['reason_codes'])}] age={age_text}"
        )
    lines.append(
        "No branch, ref, worktree, configuration, or GitHub state was changed."
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument(
        "--branch",
        action="append",
        dest="branches",
        help="Exact branch name; repeat for multiple targets",
    )
    targets.add_argument(
        "--all-local",
        action="store_true",
        help="Inspect every local branch except main/master",
    )
    parser.add_argument("--default-ref", default="origin/main")
    parser.add_argument("--remote", default="origin")
    parser.add_argument(
        "--evidence",
        type=Path,
        help="Caller-supplied refreshed remote/PR/retention JSON",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    evidence, evidence_error = _load_evidence(args.evidence)
    branches = args.branches or []
    branch_query_failures: list[QueryFailure] = []
    if args.all_local:
        branches, branch_query_failures = _local_branches(args.repo, args.timeout)
    if not branches and not branch_query_failures:
        print("No non-default branch targets were found.", file=sys.stderr)
        return 2
    receipt = classify_repository(
        repo=args.repo,
        branches=branches,
        evidence=evidence if args.evidence is not None else None,
        default_ref=args.default_ref,
        remote=args.remote,
        timeout=args.timeout,
    )
    if evidence_error or branch_query_failures:
        reason = evidence_error or "; ".join(
            f"{item.command}: {item.reason}" for item in branch_query_failures
        )
        receipt["query_failures"].append(
            {"command": "load classifier inputs", "reason": reason}
        )
        receipt["status"] = "UNKNOWN"
        for target in receipt["targets"]:
            _unknown(target, "CLASSIFIER_INPUT_QUERY_FAILED")
    output = (
        json.dumps(receipt, indent=2, sort_keys=True)
        if args.as_json
        else _format_human(receipt)
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
