"""Prepare, but never execute, the MAINT-0136 Phase 2B cleanup decision.

The preparation is deliberately split into two surfaces.  It freezes the
remaining small regenerable-cache ceiling from Phase 1, and it inventories
worktrees only as retirement-review rows.  It has no deletion, worktree,
branch, ref, pull-request, prune, or archive mutation path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from scripts._lib import cleanup_preservation as preservation
from scripts._lib import phase2a_cache_cleanup as phase2a

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2B-PREPARATION"
PHASE1_BRANCH = "codex/maint-0136-cleanup-preservation"
PHASE2A_BRANCH = "codex/maint-0136-phase-2a-cache-cleanup"
PHASE2B_BRANCH = "codex/maint-0136-phase-2b-preparation"
SMALL_CACHE_PATHS = (
    ".pytest_cache",
    ".ruff_cache",
    "Python/.pytest_cache",
    "react_app/.vite",
    "react_app/dist",
)
PROTECTED_PATH_PARTS = {".git", ".venv", "private_sources"}


class PreparationError(RuntimeError):
    """Raised when Phase 2B preparation cannot be proven safe and current."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreparationError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PreparationError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _small_cache_identities(
    phase1_manifest: dict[str, Any],
) -> list[tuple[str, str]]:
    if phase1_manifest.get("task_id") != TASK_ID:
        raise PreparationError("Phase 1 manifest task identity does not match")
    identities = {
        (row["worktree_path"], row["relative_path"])
        for row in phase1_manifest.get("caches", [])
        if row.get("disposition") == "CACHE_CANDIDATE_NOT_AUTHORIZED"
        and row.get("relative_path") in SMALL_CACHE_PATHS
    }
    if not identities:
        raise PreparationError("Phase 1 manifest has no small-cache identities")
    return sorted(identities)


def _validate_cache_path(worktree: Path, relative_path: str) -> Path:
    if relative_path not in SMALL_CACHE_PATHS:
        raise PreparationError(f"unauthorized cache relative path: {relative_path}")
    relative = PurePosixPath(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise PreparationError(f"unsafe cache relative path: {relative_path}")
    if PROTECTED_PATH_PARTS.intersection(relative.parts):
        raise PreparationError(f"protected path part in target: {relative_path}")
    try:
        worktree_root = worktree.resolve(strict=True)
    except OSError as exc:
        raise PreparationError(f"worktree is unavailable: {worktree}") from exc
    target = worktree.joinpath(*relative.parts)
    if target.is_symlink():
        raise PreparationError(f"cache target is a symlink: {target}")
    if not target.is_dir():
        raise PreparationError(f"cache target is not a directory: {target}")
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        raise PreparationError(f"cache target is unavailable: {target}") from exc
    expected = worktree_root.joinpath(*relative.parts)
    if resolved != expected or not resolved.is_relative_to(worktree_root):
        raise PreparationError(f"cache target escapes its worktree: {target}")
    return target


def _recreation_basis(
    *, worktree: Path, relative_path: str, head_sha: str
) -> dict[str, Any]:
    if relative_path in {".pytest_cache", "Python/.pytest_cache"}:
        return {
            "kind": "TOOL_GENERATED_PYTEST_CACHE",
            "command_basis": "repository pytest invocation",
            "head_sha": head_sha,
        }
    if relative_path == ".ruff_cache":
        return {
            "kind": "TOOL_GENERATED_RUFF_CACHE",
            "command_basis": "repository Ruff invocation",
            "head_sha": head_sha,
        }

    lock_relative = "react_app/package-lock.json"
    lockfile = worktree / lock_relative
    if lockfile.is_symlink() or not lockfile.is_file():
        raise PreparationError(f"npm lockfile is unavailable in {worktree}")
    result = preservation._run(
        ["git", "cat-file", "-e", f"{head_sha}:{lock_relative}"],
        cwd=worktree,
        check=False,
    )
    if result.returncode != 0:
        raise PreparationError(
            f"npm lockfile is not present at {head_sha} in {worktree}"
        )
    return {
        "kind": (
            "REACT_BUILD_OUTPUT" if relative_path == "react_app/dist" else "VITE_CACHE"
        ),
        "path": lock_relative,
        "sha256": preservation.sha256_file(lockfile),
        "head_sha": head_sha,
        "recreate_command": (
            "./run.sh frontend build"
            if relative_path == "react_app/dist"
            else "./run.sh dev"
        ),
    }


def _validate_phase2a_completion(
    *,
    phase2a_worktree: Path,
    phase2a_item: dict[str, Any],
    targets_path: Path,
    evidence_path: Path,
) -> dict[str, Any]:
    targets = _load_json(targets_path)
    evidence = _load_json(evidence_path)
    if targets.get("packet_id") != phase2a.PACKET_ID:
        raise PreparationError("Phase 2A target packet identity does not match")
    if targets.get("status") != "PHASE_2A_TARGETS_FROZEN":
        raise PreparationError("Phase 2A targets are not frozen")
    if (
        evidence.get("packet_id") != phase2a.PACKET_ID
        or evidence.get("status") != "PASS"
    ):
        raise PreparationError("Phase 2A execution evidence is not PASS")
    if evidence.get("target_manifest", {}).get("target_set_sha256") != targets.get(
        "target_set_sha256"
    ):
        raise PreparationError("Phase 2A target-set evidence does not match")
    if evidence.get("target_manifest", {}).get("sha256") != preservation.sha256_file(
        targets_path
    ):
        raise PreparationError("Phase 2A target-manifest digest does not match")
    execution = evidence.get("execution", {})
    if execution.get("failure") is not None:
        raise PreparationError("Phase 2A execution records a failure")
    if execution.get("removed_target_count") != targets.get("summary", {}).get(
        "target_count"
    ):
        raise PreparationError("Phase 2A removed-target count does not match")
    if execution.get("removed_bytes") != targets.get("summary", {}).get("target_bytes"):
        raise PreparationError("Phase 2A removed-byte count does not match")
    if phase2a_item.get("branch") != PHASE2A_BRANCH:
        raise PreparationError("Phase 2A live branch identity changed")
    if (
        phase2a_item.get("query_status") != "OK"
        or phase2a_item.get("operation") != "none"
    ):
        raise PreparationError("Phase 2A worktree state is not safely inspectable")
    if phase2a_item.get("dirty_count") != 0:
        raise PreparationError("Phase 2A worktree is no longer clean")

    surviving: list[str] = []
    for row in targets.get("targets", []):
        target = Path(row["worktree_path"]) / row["relative_path"]
        if os.path.lexists(target):
            surviving.append(str(target))
    if surviving:
        raise PreparationError(
            f"{len(surviving)} Phase 2A cache targets have reappeared"
        )
    return {
        "worktree_path": str(phase2a_worktree),
        "branch": phase2a_item["branch"],
        "head_sha": phase2a_item["head_sha"],
        "target_manifest_sha256": preservation.sha256_file(targets_path),
        "execution_evidence_sha256": preservation.sha256_file(evidence_path),
        "target_set_sha256": targets["target_set_sha256"],
        "removed_target_count": execution["removed_target_count"],
        "removed_bytes": execution["removed_bytes"],
        "all_targets_still_absent": True,
    }


def _ignored_state(worktree: Path) -> dict[str, Any]:
    result = preservation._run(
        [
            "git",
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "--directory",
            "-z",
        ],
        cwd=worktree,
    )
    entries = sorted(entry for entry in result.stdout.split("\0") if entry)
    return {
        "entry_count": len(entries),
        "path_set_sha256": _canonical_sha256(entries),
        "paths_recorded": False,
        "session_state_present": any(
            entry == "logs/sessions/" or entry.startswith("logs/sessions/")
            for entry in entries
        ),
        "pipeline_state_present": any(
            entry == "logs/pipelines/" or entry.startswith("logs/pipelines/")
            for entry in entries
        ),
        "protected_source_indicator_present": any(
            entry == "private_sources/" or entry.startswith("private_sources/")
            for entry in entries
        ),
    }


def _external_volume_status(volume_root: Path = Path("/Volumes")) -> dict[str, Any]:
    if not volume_root.is_dir():
        return {
            "candidate_count": 0,
            "names_recorded": False,
            "usable_destination_proven": False,
            "status": "HOLD_VOLUME_ROOT_UNAVAILABLE",
        }
    candidates = [
        path
        for path in volume_root.iterdir()
        if path.name != "Macintosh HD" and not path.is_symlink()
    ]
    return {
        "candidate_count": len(candidates),
        "names_recorded": False,
        "usable_destination_proven": False,
        "status": (
            "REVIEW_CANDIDATE_VOLUME"
            if candidates
            else "HOLD_NO_EXTERNAL_VOLUME_MOUNTED"
        ),
    }


def _worktree_review_row(
    *,
    item: dict[str, Any],
    repo: Path,
    primary_repo: Path,
    phase1_worktree: Path,
    phase2a_worktree: Path,
    dirty_worktree: Path,
    open_pr_branches: set[str],
    remote_heads: dict[str, str],
) -> dict[str, Any]:
    path = Path(item["path"]).resolve()
    branch = item.get("branch")
    ignored = _ignored_state(path)
    reason_codes = ["PHASE_2B_EXECUTION_NOT_AUTHORIZED"]
    if path == primary_repo:
        disposition = "RETAIN_PRIMARY_CHECKOUT"
        reason_codes += ["INTEGRATION_ANCHOR", "PROTECTED_SOURCES_OWNER"]
    elif path == repo:
        disposition = "RETAIN_CURRENT_PREPARATION_LANE"
        reason_codes += ["ACTIVE_TASK"]
    elif path == phase1_worktree:
        disposition = "RETAIN_PHASE_1_PREDECESSOR"
        reason_codes += ["OPEN_PULL_REQUEST", "PUBLICATION_PREDECESSOR"]
    elif path == phase2a_worktree:
        disposition = "RETAIN_PHASE_2A_PREDECESSOR"
        reason_codes += ["IMMUTABLE_LOCAL_CANDIDATE"]
    elif path == dirty_worktree or item.get("dirty_count"):
        disposition = "RETAIN_DIRTY_OR_UNIQUE_LANE"
        reason_codes += ["UNCOMMITTED_WORK"]
    elif branch == "DETACHED":
        disposition = "HOLD_DETACHED_OWNER_REVIEW"
        reason_codes += ["DETACHED_HEAD", "OWNER_RETENTION_NOT_CONFIRMED"]
    elif branch in open_pr_branches:
        disposition = "RETAIN_OPEN_PULL_REQUEST_LANE"
        reason_codes += ["OPEN_PULL_REQUEST"]
    else:
        disposition = "RETIREMENT_REVIEW_ONLY"
        reason_codes += [
            "OWNER_RETENTION_NOT_CONFIRMED",
            "OFF_DEVICE_RECOVERY_UNAVAILABLE",
        ]
        if ignored["entry_count"]:
            reason_codes.append("IGNORED_LOCAL_STATE_PRESENT")
    remote_sha = remote_heads.get(branch) if branch and branch != "DETACHED" else None
    reachable = None
    if item.get("head_sha"):
        reachable = preservation._is_ancestor(repo, item["head_sha"], "origin/main")
    return {
        "path": str(path),
        "branch": branch,
        "head_sha": item.get("head_sha"),
        "dirty_count": item.get("dirty_count"),
        "operation": item.get("operation"),
        "query_status": item.get("query_status"),
        "size_bytes": preservation.path_size_bytes(path),
        "remote_exact_head": (
            remote_sha == item.get("head_sha") if remote_sha else False
        ),
        "reachable_from_observed_origin_main": reachable,
        "open_pull_request": branch in open_pr_branches,
        "ignored_local_state": ignored,
        "disposition": disposition,
        "reason_codes": reason_codes,
    }


def _worktree_review_rows(
    *,
    inventory: dict[str, Any],
    repo: Path,
    primary_repo: Path,
    phase1_worktree: Path,
    phase2a_worktree: Path,
    dirty_worktree: Path,
    open_pr_branches: set[str],
    remote_heads: dict[str, str],
) -> list[dict[str, Any]]:
    def collect(item: dict[str, Any]) -> dict[str, Any]:
        return _worktree_review_row(
            item=item,
            repo=repo,
            primary_repo=primary_repo,
            phase1_worktree=phase1_worktree,
            phase2a_worktree=phase2a_worktree,
            dirty_worktree=dirty_worktree,
            open_pr_branches=open_pr_branches,
            remote_heads=remote_heads,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        rows = list(executor.map(collect, inventory.get("worktrees", [])))
    return sorted(rows, key=lambda row: row["path"])


def build_preparation_manifest(
    *,
    repo: Path,
    primary_repo: Path,
    phase1_worktree: Path,
    phase2a_worktree: Path,
    dirty_worktree: Path,
    phase1_manifest_path: Path,
    phase2a_targets_path: Path,
    phase2a_evidence_path: Path,
    recovery_evidence_path: Path,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Return the live Phase 2B decision packet without mutating cleanup targets."""
    repo = repo.resolve()
    primary_repo = primary_repo.resolve()
    phase1_worktree = phase1_worktree.resolve()
    phase2a_worktree = phase2a_worktree.resolve()
    dirty_worktree = dirty_worktree.resolve()
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if Path(current.get("worktree_root", "")).resolve() != repo:
        raise PreparationError("Git-state current worktree does not match --repo")
    if current.get("branch") != PHASE2B_BRANCH:
        raise PreparationError(
            f"Phase 2B preparation must run on {PHASE2B_BRANCH}, found {current.get('branch')}"
        )
    if current.get("operation") != "none" or current.get("query_failures"):
        raise PreparationError("current Git state is not safe for preparation")

    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    phase2a_item = live_by_path.get(str(phase2a_worktree))
    if phase2a_item is None:
        raise PreparationError("Phase 2A predecessor worktree is not live")
    phase2a_completion = _validate_phase2a_completion(
        phase2a_worktree=phase2a_worktree,
        phase2a_item=phase2a_item,
        targets_path=phase2a_targets_path.resolve(),
        evidence_path=phase2a_evidence_path.resolve(),
    )
    if current.get("head_sha") != phase2a_completion["head_sha"]:
        raise PreparationError(
            "preparation lane is not based on exact Phase 2A candidate"
        )

    phase1_manifest = _load_json(phase1_manifest_path.resolve())
    identities = _small_cache_identities(phase1_manifest)
    pull_requests = preservation._pull_requests(repo)
    open_prs = sorted(
        (
            {
                "number": row["number"],
                "head_branch": row["headRefName"],
                "head_sha": row["headRefOid"],
                "url": row["url"],
            }
            for row in pull_requests
            if row.get("state") == "OPEN"
        ),
        key=lambda row: row["number"],
    )
    open_pr_branches = {row["head_branch"] for row in open_prs}
    excluded = {
        str(primary_repo): "PRIMARY_CHECKOUT",
        str(repo): "CURRENT_PHASE_2B_PREPARATION",
        str(phase1_worktree): "PHASE_1_PREDECESSOR",
        str(phase2a_worktree): "PHASE_2A_PREDECESSOR",
        str(dirty_worktree): "DIRTY_UNIQUE_LANE",
    }
    targets: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []
    for worktree_text, relative_path in identities:
        worktree = Path(worktree_text).resolve()
        item = live_by_path.get(str(worktree))
        reason = excluded.get(str(worktree))
        if item is None:
            reason = reason or "WORKTREE_NO_LONGER_LIVE"
        elif item.get("query_status") != "OK":
            reason = reason or "GIT_STATE_QUERY_NOT_OK"
        elif item.get("operation") != "none":
            reason = reason or "GIT_OPERATION_ACTIVE"
        elif item.get("dirty_count") != 0:
            reason = reason or "WORKTREE_DIRTY"
        elif item.get("current"):
            reason = reason or "CURRENT_WORKTREE"
        elif item.get("branch") in open_pr_branches:
            reason = reason or "OPEN_PULL_REQUEST"
        target_path = worktree / relative_path
        if reason is None and not os.path.lexists(target_path):
            reason = "CACHE_ALREADY_ABSENT"
        if reason is not None:
            held.append(
                {
                    "worktree_path": str(worktree),
                    "relative_path": relative_path,
                    "reason": reason,
                }
            )
            continue
        target = _validate_cache_path(worktree, relative_path)
        targets.append(
            {
                "worktree_path": str(worktree),
                "relative_path": relative_path,
                "absolute_path": str(target),
                "branch": item.get("branch"),
                "head_sha": item["head_sha"],
                "size_bytes": preservation.path_size_bytes(target),
                "recreation_basis": _recreation_basis(
                    worktree=worktree,
                    relative_path=relative_path,
                    head_sha=item["head_sha"],
                ),
                "disposition": "PROPOSED_PENDING_EXACT_OWNER_AUTHORIZATION",
            }
        )
    targets.sort(key=lambda row: (row["worktree_path"], row["relative_path"]))
    held.sort(key=lambda row: (row["worktree_path"], row["relative_path"]))

    remote_heads = preservation._remote_heads(repo)
    worktree_rows = _worktree_review_rows(
        inventory=inventory,
        repo=repo,
        primary_repo=primary_repo,
        phase1_worktree=phase1_worktree,
        phase2a_worktree=phase2a_worktree,
        dirty_worktree=dirty_worktree,
        open_pr_branches=open_pr_branches,
        remote_heads=remote_heads,
    )
    review_rows = [
        row for row in worktree_rows if row["disposition"] == "RETIREMENT_REVIEW_ONLY"
    ]
    recovery = _load_json(recovery_evidence_path.resolve())
    if recovery.get("status") != "LOCAL_RECOVERY_VERIFIED_OFF_DEVICE_HOLD":
        raise PreparationError("recovery evidence status changed unexpectedly")
    live_destination = preservation._destination_status()
    external_volumes = _external_volume_status()
    protected_sources = preservation.protected_source_inventory(
        primary_repo / "private_sources"
    )
    disk = preservation._disk_capacity(repo)
    target_bytes = sum(row["size_bytes"] for row in targets)
    worktree_total_bytes = sum(row["size_bytes"] for row in worktree_rows)
    review_bytes = sum(row["size_bytes"] for row in review_rows)
    target_fraction = (
        target_bytes / worktree_total_bytes if worktree_total_bytes else 0.0
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": "PHASE_2B_PREPARED_NOT_AUTHORIZED",
        "observed_at_utc": observed_at_utc,
        "authorization": {
            "status": "OBSERVED",
            "query_status": "OK",
            "observed_at_utc": observed_at_utc,
            "authority_source": {
                "kind": "USER_DELEGATION",
                "status": "OBSERVED",
                "query_status": "OK",
                "observed_at_utc": observed_at_utc,
                "reference": "active Codex task: so lets prepare for 2b",
            },
            "authorized_actions": [
                "INSPECT_LIVE_STATE",
                "PREPARE_EXACT_DECISION_PACKET",
                "COMMIT_PREPARATION_EVIDENCE",
            ],
            "next_action": "COMMIT_PREPARATION_EVIDENCE",
            "phase_2b_execution_authorized": False,
            "prohibited_actions": [
                "DELETE_CACHE",
                "REMOVE_WORKTREE",
                "DELETE_BRANCH_OR_REF",
                "CLOSE_PULL_REQUEST",
                "DELETE_ARCHIVE",
                "DELETE_PROTECTED_SOURCE",
                "DELETE_SHARED_VENV",
                "GIT_CLEAN",
                "PRUNE",
                "RESET",
                "FORCE_PUSH",
            ],
            "target_binding": {
                "task_id": TASK_ID,
                "branch": current["branch"],
                "head_sha": current["head_sha"],
                "actions": [
                    "INSPECT_LIVE_STATE",
                    "PREPARE_EXACT_DECISION_PACKET",
                    "COMMIT_PREPARATION_EVIDENCE",
                ],
            },
        },
        "binding": {
            "repo": str(repo),
            "branch": current["branch"],
            "head_sha_at_freeze": current["head_sha"],
            "phase1_manifest_sha256": preservation.sha256_file(
                phase1_manifest_path.resolve()
            ),
            "phase2a_completion": phase2a_completion,
            "topology_sha256": _canonical_sha256(
                phase2a._topology_rows(inventory, current_repo=repo)
            ),
            "refs": phase2a._refs_snapshot(repo),
        },
        "recovery": {
            "prior_evidence_sha256": preservation.sha256_file(
                recovery_evidence_path.resolve()
            ),
            "same_disk_status": recovery["status"],
            "live_off_device_destination": live_destination,
            "live_external_volumes": external_volumes,
            "worktree_retirement_recovery_gate": "HOLD",
        },
        "disk": disk,
        "protected_sources": protected_sources,
        "open_pull_requests": open_prs,
        "small_cache_packet": {
            "status": "PROPOSED_NOT_AUTHORIZED",
            "phase1_identity_count": len(identities),
            "targets": targets,
            "held_candidates": held,
            "target_set_sha256": _canonical_sha256(targets),
            "summary": {
                "target_count": len(targets),
                "target_bytes": target_bytes,
                "held_candidate_count": len(held),
                "worktree_total_fraction": target_fraction,
                "by_relative_path": {
                    relative: {
                        "count": sum(
                            row["relative_path"] == relative for row in targets
                        ),
                        "bytes": sum(
                            row["size_bytes"]
                            for row in targets
                            if row["relative_path"] == relative
                        ),
                    }
                    for relative in SMALL_CACHE_PATHS
                },
            },
        },
        "worktree_retirement": {
            "status": "REVIEW_ONLY_NOT_AUTHORIZED",
            "rows": worktree_rows,
            "summary": {
                "worktree_count": len(worktree_rows),
                "worktree_total_bytes": worktree_total_bytes,
                "review_only_count": len(review_rows),
                "review_only_gross_bytes": review_bytes,
                "ignored_entry_count": sum(
                    row["ignored_local_state"]["entry_count"] for row in worktree_rows
                ),
                "ignored_session_state_worktree_count": sum(
                    row["ignored_local_state"]["session_state_present"]
                    for row in worktree_rows
                ),
                "ignored_pipeline_state_worktree_count": sum(
                    row["ignored_local_state"]["pipeline_state_present"]
                    for row in worktree_rows
                ),
            },
        },
        "branch_ref_archive_cleanup": {
            "status": "HELD_NOT_PROPOSED",
            "reason_codes": [
                "NO_MEANINGFUL_IMMEDIATE_DISK_RELIEF",
                "OWNER_RETENTION_NOT_CONFIRMED",
                "OFF_DEVICE_RECOVERY_UNAVAILABLE",
                "PREDECESSOR_PUBLICATION_ORDER_UNRESOLVED",
            ],
        },
        "recommendation": {
            "decision": "DO_NOT_EXECUTE_PHASE_2B_YET",
            "small_cache_packet": "SKIP_AS_LOW_VALUE_UNLESS_OWNER_EXPLICITLY_REQUESTS",
            "worktree_retirement": "PREPARE_RECOVERY_AND_OWNER_RETENTION_NEXT",
            "branch_ref_archive_cleanup": "DEFER",
            "reason": (
                "The remaining exact cache ceiling is small relative to the live "
                "worktree surface, while worktree retirement would touch ignored local "
                "session and pipeline state without off-device recovery."
            ),
        },
        "mutations_performed": {
            "file_deletions": 0,
            "cache_deletions": 0,
            "worktree_removals": 0,
            "branch_deletions": 0,
            "ref_deletions": 0,
            "archive_deletions": 0,
            "pr_closures": 0,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--primary-repo", type=Path, required=True)
    parser.add_argument("--phase1-worktree", type=Path, required=True)
    parser.add_argument("--phase2a-worktree", type=Path, required=True)
    parser.add_argument("--dirty-worktree", type=Path, required=True)
    parser.add_argument("--phase1-manifest", type=Path, required=True)
    parser.add_argument("--phase2a-targets", type=Path, required=True)
    parser.add_argument("--phase2a-evidence", type=Path, required=True)
    parser.add_argument("--recovery-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_preparation_manifest(
            repo=args.repo,
            primary_repo=args.primary_repo,
            phase1_worktree=args.phase1_worktree,
            phase2a_worktree=args.phase2a_worktree,
            dirty_worktree=args.dirty_worktree,
            phase1_manifest_path=args.phase1_manifest,
            phase2a_targets_path=args.phase2a_targets,
            phase2a_evidence_path=args.phase2a_evidence,
            recovery_evidence_path=args.recovery_evidence,
            observed_at_utc=datetime.now(UTC).isoformat(),
        )
        _write_json(args.output, result)
    except (PreparationError, preservation.EvidenceError) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": result["status"],
                "recommendation": result["recommendation"]["decision"],
                "small_cache_targets": result["small_cache_packet"]["summary"][
                    "target_count"
                ],
                "small_cache_bytes": result["small_cache_packet"]["summary"][
                    "target_bytes"
                ],
                "retirement_review_count": result["worktree_retirement"]["summary"][
                    "review_only_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
