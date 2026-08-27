"""Prepare and execute the exact MAINT-0136 Phase 2C ref-cleanup packet.

Phase 2C is intentionally narrow.  It may remove only normal merged local
branches selected by the canonical branch-disposition classifier and exact
remote branches at the same integrated heads.  It never force-deletes a local
branch, prunes, garbage-collects, deletes tags or Codex-managed refs, removes a
worktree, closes a pull request, or deletes either recovery archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Sequence

from scripts import classify_branch_disposition as classifier
from scripts._lib import cleanup_preservation as preservation
from scripts._lib import phase2a_cache_cleanup as phase2a
from scripts._lib import phase2b_worktree_preparation as worktree_preparation

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2C"
EXECUTION_PACKET_ID = "MAINT-0136-PHASE-2C-EXECUTION"
PHASE2B_PACKET_ID = "MAINT-0136-PHASE-2B-W-EXECUTION"
PHASE2B_STATUS = "PASS"
MANIFEST_STATUS = "PHASE_2C_TARGETS_FROZEN_AWAITING_DIGEST_BOUND_AUTHORIZATION"
PREPARATION_BRANCH = "codex/maint-0136-phase-2c-preparation"
PREDECESSOR_COMMIT = "18ed2f1f65a24b54029875fd1cad640dc2f0fae0"
PREPARATION_COMMIT = "d207d58e21c59fe485c50f292de7d84f5c8b6e56"
OWNER_AUTHORITY_REFERENCE = (
    "active Codex task: please continue with 2c, you have full approval"
)
EXACT_EXECUTION_AUTHORITY_REFERENCE = (
    "active Codex task: I authorize Phase 2C execution for four local branches "
    "and two matching remote branches under target digest "
    "08a68419515cf9f469e8a7bb3d0a1f4e92218c7e086de5bb89c71368093b23c7"
)


class RefCleanupError(RuntimeError):
    """Raised when Phase 2C cannot preserve its exact cleanup boundary."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RefCleanupError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RefCleanupError(f"{path} must contain a JSON object")
    return value


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _local_heads(repo: Path) -> dict[str, str]:
    result = preservation._run(
        [
            "git",
            "for-each-ref",
            "--format=%(refname:strip=2)%09%(objectname)",
            "refs/heads",
        ],
        cwd=repo,
    )
    heads: dict[str, str] = {}
    for line in result.stdout.splitlines():
        branch, sha = line.split("\t", 1)
        heads[branch] = sha
    return heads


def _all_refs(repo: Path) -> dict[str, str]:
    result = preservation._run(
        ["git", "for-each-ref", "--format=%(refname)%09%(objectname)"], cwd=repo
    )
    refs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        ref, sha = line.split("\t", 1)
        refs[ref] = sha
    return refs


def _namespace_summary(refs: dict[str, str]) -> dict[str, int]:
    return {
        "local_heads": sum(ref.startswith("refs/heads/") for ref in refs),
        "remote_tracking": sum(ref.startswith("refs/remotes/") for ref in refs),
        "tags": sum(ref.startswith("refs/tags/") for ref in refs),
        "codex_managed": sum(ref.startswith("refs/codex/") for ref in refs),
        "other": sum(
            not ref.startswith(
                ("refs/heads/", "refs/remotes/", "refs/tags/", "refs/codex/")
            )
            for ref in refs
        ),
    }


def _worktree_identity(
    inventory: dict[str, Any], current_repo: Path
) -> list[dict[str, Any]]:
    current_repo = current_repo.resolve()
    return sorted(
        [
            {
                "path": row["path"],
                "branch": row.get("branch"),
                "head_sha": row.get("head_sha"),
                "dirty_count": (
                    "CURRENT_TASK_WRITES_IGNORED"
                    if Path(row["path"]).resolve() == current_repo
                    else row.get("dirty_count")
                ),
                "operation": row.get("operation"),
                "query_status": row.get("query_status"),
            }
            for row in inventory.get("worktrees", [])
        ],
        key=lambda row: row["path"],
    )


def _open_pull_requests(repo: Path) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "number": row["number"],
                "head_branch": row["headRefName"],
                "head_sha": row["headRefOid"],
                "url": row["url"],
            }
            for row in preservation._pull_requests(repo)
            if row.get("state") == "OPEN"
        ],
        key=lambda row: row["number"],
    )


def _archive_identity(
    path: Path, *, expected_size: int, expected_sha: str
) -> dict[str, Any]:
    path = path.resolve()
    if path.is_symlink() or not path.is_file():
        raise RefCleanupError(f"recovery archive is unavailable: {path}")
    size = path.stat().st_size
    digest = preservation.sha256_file(path)
    if size != expected_size or digest != expected_sha:
        raise RefCleanupError(f"recovery archive identity changed: {path}")
    return {
        "path": str(path),
        "size_bytes": size,
        "sha256": digest,
        "disposition": "RETAIN_RECOVERY_AUTHORITY",
    }


def _recovery_state(
    *,
    cleanup_recovery_path: Path,
    drive_backup_path: Path,
    local_package_path: Path,
    drive_observed_at_utc: str,
    drive_remote_size_bytes: int,
    drive_shared: bool,
    drive_downloadable: bool,
) -> dict[str, Any]:
    cleanup = _load_json(cleanup_recovery_path)
    drive = _load_json(drive_backup_path)
    local = _load_json(local_package_path)
    if (
        cleanup.get("status") != "LOCAL_RECOVERY_VERIFIED_OFF_DEVICE_HOLD"
        or drive.get("status") != worktree_preparation.BACKUP_STATUS
        or local.get("status") != worktree_preparation.LOCAL_PACKAGE_STATUS
    ):
        raise RefCleanupError("recovery evidence status changed")
    bundle = cleanup.get("git_bundle", {})
    local_archive = _archive_identity(
        Path(str(local.get("archive_path", ""))),
        expected_size=int(local.get("archive_size_bytes", -1)),
        expected_sha=str(local.get("archive_sha256", "")),
    )
    bundle_archive = _archive_identity(
        Path(str(bundle.get("path", ""))),
        expected_size=int(bundle.get("size_bytes", -1)),
        expected_sha=str(bundle.get("sha256", "")),
    )
    remote = drive.get("remote_archive", {})
    if (
        remote.get("status") != "UPLOAD_AND_AUTHENTICATED_READBACK_PASS"
        or drive.get("remote_restore", {}).get("status") != "PASS"
        or drive_remote_size_bytes != local_archive["size_bytes"]
        or drive_shared
        or not drive_downloadable
    ):
        raise RefCleanupError("live Google Drive recovery metadata is not safe")
    return {
        "local_archives": [bundle_archive, local_archive],
        "drive": {
            "status": "LIVE_METADATA_RECONFIRMED",
            "observed_at_utc": drive_observed_at_utc,
            "remote_size_bytes": drive_remote_size_bytes,
            "shared": drive_shared,
            "downloadable": drive_downloadable,
            "authenticated_readback_sha256": remote.get("downloaded_readback_sha256"),
            "authenticated_full_restore": "PASS",
            "file_id_recorded": False,
            "owner_identity_recorded": False,
        },
        "archive_deletion_targets": [],
        "archive_disposition": "RETAIN_BOTH_LOCAL_AND_OFF_DEVICE_RECOVERY",
    }


def _classifier_evidence(
    *,
    branches: list[dict[str, Any]],
    remote_heads: dict[str, str],
    open_prs: list[dict[str, Any]],
    live_origin_main: str,
    observed_at_utc: str,
) -> dict[str, Any]:
    open_by_branch: dict[str, list[dict[str, Any]]] = {}
    for row in open_prs:
        open_by_branch.setdefault(row["head_branch"], []).append(row)
    values: dict[str, Any] = {}
    for row in branches:
        branch = row["branch"]
        head = row["head_sha"]
        remote_head = remote_heads.get(branch)
        items = open_by_branch.get(branch, [])
        values[branch] = {
            "owner": PACKET_ID,
            "remote_ref": {
                "status": "PRESENT" if remote_head else "ABSENT",
                "ref": f"refs/heads/{branch}",
                "sha": remote_head,
            },
            "pull_requests": {
                "status": "OPEN" if items else "NONE_OPEN",
                "observed_at_utc": observed_at_utc,
                "head_sha": head,
                "items": items,
            },
            "retention": {
                "status": "NO_RETENTION",
                "observed_at_utc": observed_at_utc,
                "head_sha": head,
                "reason": None,
            },
        }
    return {
        "schema_version": classifier.SCHEMA_VERSION,
        "remote_freshness": {
            "status": "OBSERVED_AT",
            "observed_at_utc": observed_at_utc,
            "default_ref": "origin/main",
            "default_sha": live_origin_main,
        },
        "branches": values,
    }


def _select_targets(
    *,
    phase2b_targets: list[dict[str, Any]],
    local_heads: dict[str, str],
    remote_heads: dict[str, str],
    open_prs: list[dict[str, Any]],
    worktree_branches: set[str],
    classifier_receipt: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    classified = {row["branch"]: row for row in classifier_receipt["targets"]}
    open_branches = {row["head_branch"] for row in open_prs}
    targets: list[dict[str, Any]] = []
    holds: list[dict[str, Any]] = []
    for row in sorted(phase2b_targets, key=lambda item: item["branch"]):
        branch = row["branch"]
        head = row["head_sha"]
        reasons: list[str] = []
        if local_heads.get(branch) != head:
            reasons.append("LOCAL_BRANCH_IDENTITY_CHANGED")
        if branch in worktree_branches:
            reasons.append("BRANCH_ATTACHED_TO_WORKTREE")
        if branch in open_branches:
            reasons.append("OPEN_PULL_REQUEST")
        result = classified.get(branch)
        if result is None:
            reasons.append("CANONICAL_CLASSIFIER_NOT_RUN")
        elif result.get("disposition") != classifier.RETIREMENT_READY_PENDING_APPROVAL:
            reasons.extend(result.get("reason_codes", ["CLASSIFIER_HOLD"]))
        if not row.get("recovery", {}).get("integrated_into_live_origin_main"):
            reasons.append("HEAD_NOT_INTEGRATED_INTO_LIVE_ORIGIN_MAIN")
        if reasons:
            holds.append(
                {
                    "branch": branch,
                    "head_sha": head,
                    "disposition": "RETAIN",
                    "reason_codes": sorted(set(reasons)),
                }
            )
            continue
        remote_head = remote_heads.get(branch)
        targets.append(
            {
                "branch": branch,
                "head_sha": head,
                "delete_local_branch": True,
                "delete_remote_branch": remote_head == head,
                "remote_status": ("EXACT_HEAD" if remote_head == head else "ABSENT"),
                "integrated_into_live_origin_main": True,
                "off_device_recovery_status": "AUTHENTICATED_READBACK_AND_RESTORE_PASS",
                "local_operation": "GIT_BRANCH_DELETE_NORMAL",
                "remote_operation": (
                    "GIT_PUSH_ORIGIN_DELETE_EXACT_BRANCH"
                    if remote_head == head
                    else "NONE_REMOTE_ALREADY_ABSENT"
                ),
            }
        )
    return targets, holds


def _target_identity(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "branch": row["branch"],
            "head_sha": row["head_sha"],
            "delete_local_branch": row["delete_local_branch"],
            "delete_remote_branch": row["delete_remote_branch"],
            "local_operation": row["local_operation"],
            "remote_operation": row["remote_operation"],
        }
        for row in targets
    ]


def build_manifest(
    *,
    repo: Path,
    primary_repo: Path,
    phase2b_manifest_path: Path,
    phase2b_execution_path: Path,
    cleanup_recovery_path: Path,
    drive_backup_path: Path,
    local_package_path: Path,
    observed_at_utc: str,
    drive_observed_at_utc: str,
    drive_remote_size_bytes: int,
    drive_shared: bool,
    drive_downloadable: bool,
) -> dict[str, Any]:
    """Build one exact Phase 2C manifest without deleting a ref or archive."""
    repo = repo.resolve()
    primary_repo = primary_repo.resolve()
    phase2b_manifest = _load_json(phase2b_manifest_path.resolve())
    phase2b_execution = _load_json(phase2b_execution_path.resolve())
    if (
        phase2b_execution.get("packet_id") != PHASE2B_PACKET_ID
        or phase2b_execution.get("status") != PHASE2B_STATUS
        or phase2b_execution.get("summary", {}).get("removed_worktree_count") != 63
        or phase2b_execution.get("summary", {}).get("target_set_sha256")
        != phase2b_manifest.get("target_set_sha256")
    ):
        raise RefCleanupError("Phase 2B-W execution identity is not complete")
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if (
        Path(str(current.get("worktree_root", ""))).resolve() != repo
        or current.get("branch") != PREPARATION_BRANCH
        or current.get("head_sha") != PREDECESSOR_COMMIT
        or current.get("operation") != "none"
        or current.get("query_failures")
    ):
        raise RefCleanupError("Phase 2C execution lane identity changed")
    if any(
        row.get("query_status") != "OK" or row.get("operation") != "none"
        for row in inventory.get("worktrees", [])
    ):
        raise RefCleanupError("a live worktree query or Git operation is unsafe")
    remote_heads = preservation._remote_heads(repo)
    live_origin_main = worktree_preparation._live_origin_main(repo, remote_heads)
    local_heads = _local_heads(repo)
    open_prs = _open_pull_requests(repo)
    worktree_branches = {
        row["branch"]
        for row in inventory.get("worktrees", [])
        if row.get("branch") != "DETACHED"
    }
    integrated_rows = [
        row
        for row in phase2b_manifest.get("targets", [])
        if row.get("recovery", {}).get("integrated_into_live_origin_main")
        and preservation._is_ancestor(repo, row["head_sha"], live_origin_main)
    ]
    evidence = _classifier_evidence(
        branches=integrated_rows,
        remote_heads=remote_heads,
        open_prs=open_prs,
        live_origin_main=live_origin_main,
        observed_at_utc=observed_at_utc,
    )
    observed = datetime.fromisoformat(observed_at_utc.replace("Z", "+00:00"))
    classified = classifier.classify_repository(
        repo=repo,
        branches=[row["branch"] for row in integrated_rows],
        evidence=evidence,
        default_ref="origin/main",
        remote="origin",
        now=observed,
    )
    if classified.get("status") != "INSPECTED" or classified.get("query_failures"):
        raise RefCleanupError("canonical branch classifier did not pass")
    targets, phase2b_holds = _select_targets(
        phase2b_targets=phase2b_manifest.get("targets", []),
        local_heads=local_heads,
        remote_heads=remote_heads,
        open_prs=open_prs,
        worktree_branches=worktree_branches,
        classifier_receipt=classified,
    )
    non_phase2b_holds = [
        {
            "branch": branch,
            "head_sha": sha,
            "disposition": "RETAIN",
            "reason_codes": [
                (
                    "DEFAULT_BRANCH"
                    if branch == "main"
                    else "ATTACHED_OR_OUTSIDE_PHASE_2B_BACKED_TARGET_SET"
                )
            ],
        }
        for branch, sha in sorted(local_heads.items())
        if branch not in {row["branch"] for row in phase2b_manifest.get("targets", [])}
    ]
    target_identity = _target_identity(targets)
    refs = _all_refs(repo)
    recovery = _recovery_state(
        cleanup_recovery_path=cleanup_recovery_path.resolve(),
        drive_backup_path=drive_backup_path.resolve(),
        local_package_path=local_package_path.resolve(),
        drive_observed_at_utc=drive_observed_at_utc,
        drive_remote_size_bytes=drive_remote_size_bytes,
        drive_shared=drive_shared,
        drive_downloadable=drive_downloadable,
    )
    protected = preservation.protected_source_inventory(
        primary_repo / "private_sources"
    )
    remote_delete_count = sum(row["delete_remote_branch"] for row in targets)
    target_digest = _canonical_sha256(target_identity)
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": MANIFEST_STATUS,
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
                "reference": OWNER_AUTHORITY_REFERENCE,
            },
            "authorized_actions": [
                "INSPECT_LIVE_STATE",
                "FREEZE_EXACT_PHASE_2C_TARGETS",
                "COMMIT_PREPARATION_EVIDENCE",
            ],
            "next_action": "WAIT_FOR_OWNER_DECISION",
            "target_binding": {
                "task_id": PACKET_ID,
                "branch": PREPARATION_BRANCH,
                "head_sha": PREDECESSOR_COMMIT,
                "actions": [
                    "INSPECT_LIVE_STATE",
                    "FREEZE_EXACT_PHASE_2C_TARGETS",
                    "COMMIT_PREPARATION_EVIDENCE",
                ],
            },
            "phase_scope": "PHASE_2C_BRANCH_REF_ARCHIVE_CLEANUP_FULL_APPROVAL",
            "phase_preparation_authorized": True,
            "exact_target_execution_authorized": False,
            "reason": (
                "The full Phase 2C approval preceded the immutable exact target "
                "digest required by the canonical branch classifier."
            ),
            "next_required_authority": {
                "action": "DELETE_ONLY_EXACT_FROZEN_PHASE_2C_TARGETS",
                "local_branch_target_count": len(targets),
                "remote_branch_target_count": remote_delete_count,
                "total_ref_deletion_count": len(targets) + remote_delete_count,
                "target_set_sha256": target_digest,
            },
            "prohibited_actions": [
                "FORCE_DELETE_LOCAL_BRANCH",
                "DELETE_NONINTEGRATED_BRANCH",
                "DELETE_BRANCH_WITH_WORKTREE_OR_OPEN_PR",
                "DELETE_TAG",
                "DELETE_CODEX_MANAGED_REF",
                "DELETE_RECOVERY_ARCHIVE",
                "DELETE_PROTECTED_SOURCE",
                "REMOVE_WORKTREE",
                "PRUNE",
                "GARBAGE_COLLECT",
                "FORCE_PUSH",
                "CLOSE_PULL_REQUEST",
            ],
        },
        "binding": {
            "predecessor_commit": PREDECESSOR_COMMIT,
            "phase2b_target_set_sha256": phase2b_manifest.get("target_set_sha256"),
            "live_origin_main_sha": live_origin_main,
        },
        "target_identity": target_identity,
        "target_set_sha256": target_digest,
        "targets": targets,
        "holds": sorted(
            phase2b_holds + non_phase2b_holds, key=lambda row: row["branch"]
        ),
        "canonical_classifier_input": evidence,
        "canonical_classifier": classified,
        "recovery": recovery,
        "protected_sources": protected,
        "before": {
            "worktrees": _worktree_identity(inventory, repo),
            "open_pull_requests": open_prs,
            "local_heads": local_heads,
            "live_remote_heads": remote_heads,
            "refs": refs,
            "refs_snapshot": phase2a._refs_snapshot(repo),
            "ref_namespaces": _namespace_summary(refs),
        },
        "summary": {
            "local_branch_target_count": len(targets),
            "remote_branch_target_count": remote_delete_count,
            "total_ref_deletion_count": len(targets) + remote_delete_count,
            "held_local_branch_count": len(local_heads) - len(targets),
            "archive_target_count": 0,
            "worktree_target_count": 0,
            "tag_target_count": 0,
            "codex_managed_ref_target_count": 0,
            "expected_local_head_count_after": len(local_heads) - len(targets),
            "expected_live_remote_head_count_after": len(remote_heads)
            - remote_delete_count,
            "expected_local_ref_count_after": len(refs)
            - len(targets)
            - remote_delete_count,
        },
        "mutation_policy": "EXACT_TARGETS_ONLY_NO_FORCE_NO_PRUNE_ARCHIVES_RETAINED",
    }


def _remove_remote(repo: Path, branch: str) -> None:
    preservation._run(["git", "push", "origin", "--delete", branch], cwd=repo)


def _remove_local(repo: Path, branch: str) -> None:
    preservation._run(["git", "branch", "-d", branch], cwd=repo)


def _assert_fresh_target(
    *, repo: Path, target: dict[str, Any], open_prs: list[dict[str, Any]]
) -> None:
    branch = target["branch"]
    head = target["head_sha"]
    local = _local_heads(repo)
    remote = preservation._remote_heads(repo)
    inventory = preservation._worktree_inventory(repo)
    if local.get(branch) != head:
        raise RefCleanupError(f"local target identity changed: {branch}")
    if any(row.get("branch") == branch for row in inventory.get("worktrees", [])):
        raise RefCleanupError(f"target branch gained a worktree: {branch}")
    if any(row["head_branch"] == branch for row in open_prs):
        raise RefCleanupError(f"target branch gained an open PR: {branch}")
    if not preservation._is_ancestor(repo, head, "origin/main"):
        raise RefCleanupError(f"target is no longer integrated: {branch}")
    expected_remote = head if target["delete_remote_branch"] else None
    if remote.get(branch) != expected_remote:
        raise RefCleanupError(f"remote target identity changed: {branch}")


def _execution_authorization(
    *,
    observed_at_utc: str,
    target_set_sha256: str,
    local_branch_target_count: int,
    remote_branch_target_count: int,
) -> dict[str, Any]:
    actions = [
        "DELETE_EXACT_INTEGRATED_LOCAL_BRANCHES_NORMAL",
        "DELETE_EXACT_MATCHING_REMOTE_BRANCHES",
        "COMMIT_PHASE_2C_EXECUTION_EVIDENCE",
    ]
    return {
        "status": "OBSERVED",
        "query_status": "OK",
        "observed_at_utc": observed_at_utc,
        "authority_source": {
            "kind": "USER_DELEGATION",
            "scope": "DIGEST_BOUND_EXACT_TARGET_SET",
            "status": "OBSERVED",
            "query_status": "OK",
            "observed_at_utc": observed_at_utc,
            "reference": EXACT_EXECUTION_AUTHORITY_REFERENCE,
        },
        "authorized_actions": actions,
        "next_action": "COMMIT_PHASE_2C_EXECUTION_EVIDENCE",
        "target_binding": {
            "task_id": EXECUTION_PACKET_ID,
            "branch": PREPARATION_BRANCH,
            "head_sha": PREPARATION_COMMIT,
            "actions": actions,
            "target_set_sha256": target_set_sha256,
            "local_branch_target_count": local_branch_target_count,
            "remote_branch_target_count": remote_branch_target_count,
            "total_ref_deletion_count": (
                local_branch_target_count + remote_branch_target_count
            ),
        },
        "phase_scope": "EXACT_FROZEN_PHASE_2C_BRANCH_REF_TARGETS",
        "phase_preparation_authorized": True,
        "exact_target_execution_authorized": True,
        "reason": "The owner explicitly authorized the frozen target counts and digest.",
        "prohibited_actions": [
            "FORCE_DELETE_LOCAL_BRANCH",
            "DELETE_NONINTEGRATED_BRANCH",
            "DELETE_BRANCH_WITH_WORKTREE_OR_OPEN_PR",
            "DELETE_TAG",
            "DELETE_CODEX_MANAGED_REF",
            "DELETE_RECOVERY_ARCHIVE",
            "DELETE_PROTECTED_SOURCE",
            "REMOVE_WORKTREE",
            "PRUNE",
            "GARBAGE_COLLECT",
            "FORCE_PUSH",
            "CLOSE_PULL_REQUEST",
        ],
    }


def execute(
    *,
    repo: Path,
    manifest: dict[str, Any],
    output_path: Path,
    expected_digest: str,
    expected_local_count: int,
    expected_remote_count: int,
    exact_authorization: bool,
    remove_remote: Callable[[Path, str], None] = _remove_remote,
    remove_local: Callable[[Path, str], None] = _remove_local,
) -> dict[str, Any]:
    """Execute only one frozen Phase 2C target identity."""
    repo = repo.resolve()
    output_path = output_path.resolve()
    identity = _target_identity(manifest.get("targets", []))
    digest = _canonical_sha256(identity)
    if not exact_authorization:
        raise RefCleanupError("Phase 2C exact execution is not authorized")
    if (
        manifest.get("packet_id") != PACKET_ID
        or manifest.get("status") != MANIFEST_STATUS
        or digest != manifest.get("target_set_sha256")
        or digest != expected_digest
        or len(identity) != expected_local_count
        or sum(row["delete_remote_branch"] for row in manifest["targets"])
        != expected_remote_count
    ):
        raise RefCleanupError("Phase 2C target count or digest changed")
    if output_path.exists() or output_path.is_symlink():
        raise RefCleanupError(f"execution evidence already exists: {output_path}")
    before_refs = _all_refs(repo)
    before_local = _local_heads(repo)
    before_remote = preservation._remote_heads(repo)
    before_inventory = preservation._worktree_inventory(repo)
    before_protected = manifest["protected_sources"]
    archive_before = manifest["recovery"]["local_archives"]
    open_prs = _open_pull_requests(repo)
    observed_at_utc = datetime.now(UTC).isoformat()
    evidence: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": EXECUTION_PACKET_ID,
        "status": "EXECUTION_STARTED",
        "observed_at_utc": observed_at_utc,
        "authorization": _execution_authorization(
            observed_at_utc=observed_at_utc,
            target_set_sha256=expected_digest,
            local_branch_target_count=expected_local_count,
            remote_branch_target_count=expected_remote_count,
        ),
        "binding": {
            **manifest["binding"],
            "preparation_commit": PREPARATION_COMMIT,
            "target_set_sha256": expected_digest,
            "local_branch_target_count": expected_local_count,
            "remote_branch_target_count": expected_remote_count,
        },
        "targets": manifest["targets"],
        "removals": [],
        "failure": None,
        "mutations_performed": {
            "local_branch_deletions": 0,
            "remote_branch_deletions": 0,
            "tag_deletions": 0,
            "codex_managed_ref_deletions": 0,
            "archive_deletions": 0,
            "worktree_removals": 0,
            "pull_request_closures": 0,
        },
        "before": {
            "refs": before_refs,
            "ref_namespaces": _namespace_summary(before_refs),
            "local_heads": before_local,
            "live_remote_heads": before_remote,
            "worktrees": _worktree_identity(before_inventory, repo),
            "protected_sources": before_protected,
            "local_archives": archive_before,
        },
    }
    _write_json_atomic(output_path, evidence)
    try:
        for target in manifest["targets"]:
            _assert_fresh_target(repo=repo, target=target, open_prs=open_prs)
            row = {
                "branch": target["branch"],
                "head_sha": target["head_sha"],
                "remote_operation": "NOT_REQUIRED",
                "local_operation": "PENDING",
                "status": "STARTED",
            }
            if target["delete_remote_branch"]:
                remove_remote(repo, target["branch"])
                if target["branch"] in preservation._remote_heads(repo):
                    raise RefCleanupError(
                        f"remote branch survived deletion: {target['branch']}"
                    )
                row["remote_operation"] = "GIT_PUSH_ORIGIN_DELETE_EXACT_BRANCH"
                evidence["mutations_performed"]["remote_branch_deletions"] += 1
                evidence["removals"].append(row)
                _write_json_atomic(output_path, evidence)
            remove_local(repo, target["branch"])
            if target["branch"] in _local_heads(repo):
                raise RefCleanupError(
                    f"local branch survived deletion: {target['branch']}"
                )
            row["local_operation"] = "GIT_BRANCH_DELETE_NORMAL"
            row["status"] = "PASS"
            evidence["mutations_performed"]["local_branch_deletions"] += 1
            if row not in evidence["removals"]:
                evidence["removals"].append(row)
            _write_json_atomic(output_path, evidence)
    except Exception as exc:
        evidence["status"] = "PARTIAL_EXECUTION_HOLD"
        evidence["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        _write_json_atomic(output_path, evidence)
        raise
    after_refs = _all_refs(repo)
    after_local = _local_heads(repo)
    after_remote = preservation._remote_heads(repo)
    after_inventory = preservation._worktree_inventory(repo)
    removed_refs = sorted(set(before_refs) - set(after_refs))
    expected_removed_refs = sorted(
        [f"refs/heads/{row['branch']}" for row in manifest["targets"]]
        + [
            f"refs/remotes/origin/{row['branch']}"
            for row in manifest["targets"]
            if row["delete_remote_branch"]
        ]
    )
    archive_after = [
        _archive_identity(
            Path(row["path"]),
            expected_size=row["size_bytes"],
            expected_sha=row["sha256"],
        )
        for row in archive_before
    ]
    protected_after = preservation.protected_source_inventory(
        Path(before_protected["root"])
    )
    if (
        removed_refs != expected_removed_refs
        or set(after_refs) - set(before_refs)
        or len(after_local) != len(before_local) - expected_local_count
        or len(after_remote) != len(before_remote) - expected_remote_count
        or _worktree_identity(after_inventory, repo)
        != _worktree_identity(before_inventory, repo)
        or protected_after != before_protected
        or archive_after != archive_before
    ):
        evidence["status"] = "POST_EXECUTION_HOLD"
        evidence["failure"] = {
            "type": "RefCleanupError",
            "message": "post-execution preservation identity changed",
        }
        _write_json_atomic(output_path, evidence)
        raise RefCleanupError("post-execution preservation identity changed")
    evidence["status"] = "PASS"
    evidence["completed_at_utc"] = datetime.now(UTC).isoformat()
    evidence["after"] = {
        "refs": after_refs,
        "ref_namespaces": _namespace_summary(after_refs),
        "local_heads": after_local,
        "live_remote_heads": after_remote,
        "worktrees": _worktree_identity(after_inventory, repo),
        "protected_sources": protected_after,
        "local_archives": archive_after,
        "removed_refs": removed_refs,
        "only_exact_target_refs_removed": True,
    }
    evidence["summary"] = {
        "local_branch_deletion_count": expected_local_count,
        "remote_branch_deletion_count": expected_remote_count,
        "total_local_ref_deletion_count": len(expected_removed_refs),
        "target_set_sha256": expected_digest,
        "remaining_local_branch_count": len(after_local),
        "remaining_live_remote_branch_count": len(after_remote),
        "remaining_local_ref_count": len(after_refs),
    }
    _write_json_atomic(output_path, evidence)
    return evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--repo", type=Path, required=True)
    prepare.add_argument("--primary-repo", type=Path, required=True)
    prepare.add_argument("--phase2b-manifest", type=Path, required=True)
    prepare.add_argument("--phase2b-execution", type=Path, required=True)
    prepare.add_argument("--cleanup-recovery", type=Path, required=True)
    prepare.add_argument("--drive-backup", type=Path, required=True)
    prepare.add_argument("--local-package", type=Path, required=True)
    prepare.add_argument("--drive-observed-at-utc", required=True)
    prepare.add_argument("--drive-remote-size-bytes", type=int, required=True)
    prepare.add_argument("--drive-shared", choices=("true", "false"), required=True)
    prepare.add_argument("--drive-downloadable", action="store_true")
    prepare.add_argument("--output", type=Path, required=True)
    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("--repo", type=Path, required=True)
    execute_parser.add_argument("--manifest", type=Path, required=True)
    execute_parser.add_argument("--expected-target-set-sha256", required=True)
    execute_parser.add_argument("--expected-local-count", type=int, required=True)
    execute_parser.add_argument("--expected-remote-count", type=int, required=True)
    execute_parser.add_argument(
        "--confirm-full-phase-2c-authorization", action="store_true"
    )
    execute_parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "prepare":
            observed = datetime.now(UTC).isoformat()
            result = build_manifest(
                repo=args.repo,
                primary_repo=args.primary_repo,
                phase2b_manifest_path=args.phase2b_manifest,
                phase2b_execution_path=args.phase2b_execution,
                cleanup_recovery_path=args.cleanup_recovery,
                drive_backup_path=args.drive_backup,
                local_package_path=args.local_package,
                observed_at_utc=observed,
                drive_observed_at_utc=args.drive_observed_at_utc,
                drive_remote_size_bytes=args.drive_remote_size_bytes,
                drive_shared=args.drive_shared == "true",
                drive_downloadable=args.drive_downloadable,
            )
            _write_json_atomic(args.output.resolve(), result)
        else:
            manifest = _load_json(args.manifest.resolve())
            result = execute(
                repo=args.repo,
                manifest=manifest,
                output_path=args.output,
                expected_digest=args.expected_target_set_sha256,
                expected_local_count=args.expected_local_count,
                expected_remote_count=args.expected_remote_count,
                exact_authorization=args.confirm_full_phase_2c_authorization,
            )
    except (
        RefCleanupError,
        preservation.EvidenceError,
        worktree_preparation.WorktreePreparationError,
        OSError,
    ) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    summary = result.get("summary", {})
    print(
        json.dumps(
            {
                "status": result["status"],
                "target_set_sha256": result.get("target_set_sha256")
                or summary.get("target_set_sha256"),
                "local_branch_count": summary.get("local_branch_target_count")
                or summary.get("local_branch_deletion_count"),
                "remote_branch_count": summary.get("remote_branch_target_count")
                or summary.get("remote_branch_deletion_count"),
                "remaining_local_branch_count": summary.get(
                    "remaining_local_branch_count"
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
