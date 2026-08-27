"""Freeze, but never execute, MAINT-0136 Phase 2B-W worktree retirement.

Only exact worktrees whose preserved ignored state is present in the verified
Phase 2B-R package may become targets.  Every lane must also be clean,
inactive, free of an open pull request, and either integrated into live
``origin/main`` or recoverable from an exact remote branch head.  This module
has no worktree-removal, branch/ref deletion, prune, reset, or cleanup path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import tarfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

from scripts._lib import cleanup_preservation as preservation
from scripts._lib import phase2b_google_drive_backup as backup
from scripts._lib import phase2b_recovery_preparation as recovery

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2B-W-PREPARATION"
PREPARATION_BRANCH = "codex/maint-0136-phase-2b-w-preparation"
BACKUP_COMMIT = "d44ec71df99baccd599cde50a6075a4a22d330c1"
BACKUP_STATUS = "OFF_DEVICE_BACKUP_VERIFIED_RESTORE_PASS_CLEANUP_HELD"
LOCAL_PACKAGE_STATUS = "LOCAL_PACKAGE_CREATED_AND_RESTORE_VERIFIED"


class WorktreePreparationError(RuntimeError):
    """Raised when an exact retirement target cannot be proven safely."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorktreePreparationError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorktreePreparationError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _package_manifest(archive_path: Path) -> tuple[dict[str, Any], str]:
    if archive_path.is_symlink() or not archive_path.is_file():
        raise WorktreePreparationError("verified local backup archive is unavailable")
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            member = archive.getmember(backup.PACKAGE_MANIFEST_PATH)
            if not member.isfile():
                raise WorktreePreparationError("backup package manifest is not regular")
            handle = archive.extractfile(member)
            if handle is None:
                raise WorktreePreparationError("backup package manifest cannot be read")
            with handle:
                manifest_bytes = handle.read()
    except (KeyError, OSError, tarfile.TarError) as exc:
        raise WorktreePreparationError(
            f"backup package manifest is unavailable: {exc}"
        ) from exc
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise WorktreePreparationError("backup package manifest is malformed") from exc
    if not isinstance(manifest, dict) or manifest.get("packet_id") != backup.PACKET_ID:
        raise WorktreePreparationError("backup package manifest identity changed")
    return manifest, hashlib.sha256(manifest_bytes).hexdigest()


def _validated_backup(
    *, backup_evidence_path: Path, local_package_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence = _load_json(backup_evidence_path)
    local = _load_json(local_package_path)
    if (
        evidence.get("packet_id") != backup.PACKET_ID
        or evidence.get("status") != BACKUP_STATUS
    ):
        raise WorktreePreparationError("off-device backup evidence is not verified")
    if (
        local.get("packet_id") != backup.PACKET_ID
        or local.get("status") != LOCAL_PACKAGE_STATUS
    ):
        raise WorktreePreparationError("local backup package evidence is not verified")
    remote = evidence.get("remote_archive", {})
    remote_restore = evidence.get("remote_restore", {})
    if (
        remote.get("status") != "UPLOAD_AND_AUTHENTICATED_READBACK_PASS"
        or not remote.get("local_and_downloaded_sha256_match")
        or remote_restore.get("status") != "PASS"
    ):
        raise WorktreePreparationError("remote backup readback or restore is not PASS")
    archive_path = Path(str(local.get("archive_path", ""))).resolve()
    expected_size = local.get("archive_size_bytes")
    expected_sha = local.get("archive_sha256")
    if (
        archive_path.stat().st_size != expected_size
        or preservation.sha256_file(archive_path) != expected_sha
        or remote.get("downloaded_readback_sha256") != expected_sha
        or remote.get("remote_size_bytes") != expected_size
    ):
        raise WorktreePreparationError("local and remote backup identities differ")
    package, package_sha = _package_manifest(archive_path)
    if package_sha != local.get("package_manifest_sha256") or package_sha != (
        remote_restore.get("package_manifest_sha256")
    ):
        raise WorktreePreparationError("backup package-manifest digest changed")
    if package.get("source_file_count") != local.get(
        "source_file_count"
    ) or package.get("source_byte_count") != local.get("source_byte_count"):
        raise WorktreePreparationError("backup package source totals changed")
    mapping = package.get("worktree_mapping")
    if not isinstance(mapping, list) or not mapping:
        raise WorktreePreparationError("backup worktree mapping is unavailable")
    paths = [row.get("worktree_path") for row in mapping if isinstance(row, dict)]
    if len(paths) != len(mapping) or len(paths) != len(set(paths)):
        raise WorktreePreparationError("backup worktree mapping is malformed")
    return evidence, package


def _safe_live_path(path: Path) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise WorktreePreparationError(f"worktree disappeared: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise WorktreePreparationError(f"worktree is not an exact directory: {path}")
    resolved = path.resolve(strict=True)
    if resolved != path:
        raise WorktreePreparationError(f"worktree path is not canonical: {path}")


def _live_origin_main(repo: Path, remote_heads: dict[str, str]) -> str:
    remote_main = remote_heads.get("main")
    if not remote_main:
        raise WorktreePreparationError("live origin/main head is unavailable")
    object_check = preservation._run(
        ["git", "cat-file", "-e", f"{remote_main}^{{commit}}"],
        cwd=repo,
        check=False,
    )
    if object_check.returncode != 0:
        raise WorktreePreparationError(
            "live origin/main object is not fetched into the repository"
        )
    return remote_main


def _candidate_row(
    *,
    backed: dict[str, Any],
    live: dict[str, Any] | None,
    repo: Path,
    primary_repo: Path,
    current_repo: Path,
    open_pr_branches: set[str],
    remote_heads: dict[str, str],
    live_origin_main: str,
) -> dict[str, Any]:
    raw_path = Path(str(backed["worktree_path"]))
    path = raw_path.resolve()
    branch = backed.get("branch")
    reasons: list[str] = []
    current_ignored: dict[str, Any] | None = None
    size_bytes: int | None = None
    remote_exact = False
    integrated = False

    if live is None:
        reasons.append("BACKED_WORKTREE_NO_LONGER_LIVE")
    else:
        if path in {primary_repo, current_repo}:
            reasons.append("PROTECTED_OR_CURRENT_WORKTREE")
        if live.get("query_status") != "OK":
            reasons.append("GIT_STATE_QUERY_NOT_OK")
        if live.get("operation") != "none":
            reasons.append("GIT_OPERATION_ACTIVE")
        if live.get("dirty_count") != 0:
            reasons.append("WORKTREE_DIRTY")
        if live.get("current"):
            reasons.append("WORKTREE_ACTIVE")
        if branch == "DETACHED" or live.get("branch") == "DETACHED":
            reasons.append("DETACHED_OR_UNKNOWN_OWNER")
        if live.get("branch") != branch or live.get("head_sha") != backed.get(
            "head_sha"
        ):
            reasons.append("BACKUP_IDENTITY_DRIFT")
        if branch in open_pr_branches:
            reasons.append("OPEN_PULL_REQUEST")

    if live is not None and not reasons:
        _safe_live_path(raw_path)
        current_ignored = recovery.ignored_state_inventory(path)["preserve"]
        if current_ignored != backed.get("ignored_state"):
            reasons.append("IGNORED_STATE_DRIFT_AFTER_BACKUP")
        remote_exact = remote_heads.get(str(branch)) == live.get("head_sha")
        integrated = preservation._is_ancestor(
            repo, str(live.get("head_sha")), live_origin_main
        )
        if not remote_exact and not integrated:
            reasons.append("NO_EXACT_REMOTE_OR_INTEGRATED_RECOVERY")
        size_bytes = preservation.path_size_bytes(path)

    if reasons:
        return {
            "path": str(path),
            "branch": branch,
            "head_sha": backed.get("head_sha"),
            "disposition": "HOLD",
            "reason_codes": sorted(set(reasons)),
        }
    return {
        "path": str(path),
        "branch": branch,
        "head_sha": live["head_sha"],
        "gross_size_bytes": size_bytes,
        "recovery": {
            "remote_exact_head": remote_exact,
            "integrated_into_live_origin_main": integrated,
            "backup_label": backed.get("label"),
            "ignored_state": current_ignored,
            "off_device_archive_status": "AUTHENTICATED_READBACK_AND_RESTORE_PASS",
        },
        "owner_retention_disposition": "RETIRE_WORKTREE_PRESERVE_BRANCH_AND_REF",
        "disposition": "FROZEN_TARGET_AWAITING_DIGEST_BOUND_AUTHORIZATION",
    }


def build_manifest(
    *,
    repo: Path,
    primary_repo: Path,
    backup_evidence_path: Path,
    local_package_path: Path,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Build an exact target manifest without removing any worktree."""
    repo = repo.resolve()
    primary_repo = primary_repo.resolve()
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if Path(str(current.get("worktree_root", ""))).resolve() != repo:
        raise WorktreePreparationError("Git-state current worktree does not match")
    if current.get("branch") != PREPARATION_BRANCH:
        raise WorktreePreparationError(
            f"worktree preparation must run on {PREPARATION_BRANCH}"
        )
    if current.get("head_sha") != BACKUP_COMMIT:
        raise WorktreePreparationError("preparation lane is not at the backup commit")
    if current.get("operation") != "none" or current.get("query_failures"):
        raise WorktreePreparationError("current Git state cannot be inspected safely")

    backup_evidence, package = _validated_backup(
        backup_evidence_path=backup_evidence_path.resolve(),
        local_package_path=local_package_path.resolve(),
    )
    pull_requests = preservation._pull_requests(repo)
    open_prs = sorted(
        [
            {
                "number": row["number"],
                "head_branch": row["headRefName"],
                "head_sha": row["headRefOid"],
                "url": row["url"],
            }
            for row in pull_requests
            if row.get("state") == "OPEN"
        ],
        key=lambda row: row["number"],
    )
    open_pr_branches = {row["head_branch"] for row in open_prs}
    remote_heads = preservation._remote_heads(repo)
    live_origin_main = _live_origin_main(repo, remote_heads)
    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    backed_rows = package["worktree_mapping"]

    def collect(backed: dict[str, Any]) -> dict[str, Any]:
        path = str(Path(str(backed["worktree_path"])).resolve())
        return _candidate_row(
            backed=backed,
            live=live_by_path.get(path),
            repo=repo,
            primary_repo=primary_repo,
            current_repo=repo,
            open_pr_branches=open_pr_branches,
            remote_heads=remote_heads,
            live_origin_main=live_origin_main,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        evaluated = list(executor.map(collect, backed_rows))
    targets = sorted(
        [row for row in evaluated if row["disposition"].startswith("FROZEN_")],
        key=lambda row: row["path"],
    )
    holds = sorted(
        [row for row in evaluated if row["disposition"] == "HOLD"],
        key=lambda row: row["path"],
    )
    backed_paths = {str(Path(row["worktree_path"]).resolve()) for row in backed_rows}
    unbacked_live = sorted(
        {
            path: {
                "path": path,
                "branch": item.get("branch"),
                "head_sha": item.get("head_sha"),
                "disposition": "RETAIN_NOT_IN_VERIFIED_BACKUP_MAPPING",
            }
            for path, item in live_by_path.items()
            if path not in backed_paths
        }.values(),
        key=lambda row: row["path"],
    )
    target_identity = [
        {
            "path": row["path"],
            "branch": row["branch"],
            "head_sha": row["head_sha"],
            "gross_size_bytes": row["gross_size_bytes"],
            "ignored_state_aggregate_sha256": row["recovery"]["ignored_state"][
                "aggregate_sha256"
            ],
        }
        for row in targets
    ]
    target_set_sha256 = _canonical_sha256(target_identity)
    target_bytes = sum(int(row["gross_size_bytes"]) for row in targets)
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": "PHASE_2B_W_TARGETS_FROZEN_AWAITING_DIGEST_BOUND_AUTHORIZATION",
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
                "reference": (
                    "active Codex task: approval for anything needed like "
                    "cleaning, delete and more"
                ),
            },
            "authorized_actions": [
                "INSPECT_LIVE_STATE",
                "FREEZE_EXACT_WORKTREE_TARGETS",
                "COMMIT_PREPARATION_EVIDENCE",
            ],
            "next_action": "WAIT_FOR_OWNER_DECISION",
            "target_binding": {
                "task_id": "MAINT-0136-PHASE-2B-W",
                "branch": current["branch"],
                "head_sha": current["head_sha"],
                "actions": [
                    "INSPECT_LIVE_STATE",
                    "FREEZE_EXACT_WORKTREE_TARGETS",
                    "COMMIT_PREPARATION_EVIDENCE",
                ],
            },
            "general_cleanup_authority_observed": True,
            "preparation_authorized": True,
            "worktree_removal_authorized": False,
            "reason": "The general approval preceded the immutable target digest.",
            "next_required_authority": {
                "action": "REMOVE_ONLY_EXACT_FROZEN_WORKTREES",
                "target_count": len(targets),
                "target_gross_bytes": target_bytes,
                "target_set_sha256": target_set_sha256,
            },
            "prohibited_actions": [
                "DELETE_BRANCH_OR_REF",
                "CLOSE_PULL_REQUEST",
                "DELETE_BACKUP_OR_ARCHIVE",
                "DELETE_PROTECTED_SOURCE",
                "DELETE_SHARED_VENV",
                "REMOVE_HELD_OR_UNBACKED_WORKTREE",
                "GIT_CLEAN",
                "PRUNE",
                "RESET",
                "FORCE_PUSH",
            ],
        },
        "binding": {
            "repo": str(repo),
            "branch": current["branch"],
            "head_sha_at_freeze": current["head_sha"],
            "live_origin_main_sha": live_origin_main,
            "topology_sha256": _canonical_sha256(inventory.get("worktrees", [])),
            "backup_evidence_sha256": preservation.sha256_file(
                backup_evidence_path.resolve()
            ),
            "local_package_evidence_sha256": preservation.sha256_file(
                local_package_path.resolve()
            ),
            "backup_archive_sha256": backup_evidence["local_package"]["archive_sha256"],
            "backup_package_manifest_sha256": backup_evidence["local_package"][
                "package_manifest_sha256"
            ],
            "backup_worktree_count": len(backed_rows),
        },
        "live_open_pull_requests": open_prs,
        "targets": targets,
        "target_identity": target_identity,
        "target_set_sha256": target_set_sha256,
        "holds": holds,
        "unbacked_live_worktrees": unbacked_live,
        "summary": {
            "live_worktree_count": len(live_by_path),
            "backed_worktree_count": len(backed_rows),
            "target_count": len(targets),
            "target_gross_bytes": target_bytes,
            "hold_count": len(holds),
            "unbacked_live_count": len(unbacked_live),
            "remote_exact_target_count": sum(
                bool(row["recovery"]["remote_exact_head"]) for row in targets
            ),
            "integrated_target_count": sum(
                bool(row["recovery"]["integrated_into_live_origin_main"])
                for row in targets
            ),
        },
        "execution_contract": {
            "allowed_operation": "GIT_WORKTREE_REMOVE_EXACT_PATH_WITHOUT_FORCE",
            "revalidate_before_each_removal": [
                "EXACT_PATH_BRANCH_AND_HEAD",
                "CLEAN_AND_INACTIVE",
                "NO_GIT_OPERATION_OR_CONFLICT",
                "NO_OPEN_PULL_REQUEST",
                "EXACT_REMOTE_OR_INTEGRATED_RECOVERY",
                "IGNORED_STATE_MATCHES_VERIFIED_BACKUP",
                "TARGET_SET_AND_TOPOLOGY_HAVE_NOT_DRIFTED",
            ],
            "stop_on_any_drift": True,
            "preserve_branches_refs_and_backups": True,
        },
        "mutations_performed": {
            "worktree_removals": 0,
            "branch_deletions": 0,
            "ref_deletions": 0,
            "cache_deletions": 0,
            "archive_deletions": 0,
            "protected_source_deletions": 0,
            "pull_request_closures": 0,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--primary-repo", type=Path, required=True)
    parser.add_argument("--backup-evidence", type=Path, required=True)
    parser.add_argument("--local-package-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        manifest = build_manifest(
            repo=args.repo,
            primary_repo=args.primary_repo,
            backup_evidence_path=args.backup_evidence,
            local_package_path=args.local_package_evidence,
            observed_at_utc=datetime.now(UTC).isoformat(),
        )
        _write_json(args.output, manifest)
    except (
        WorktreePreparationError,
        preservation.EvidenceError,
        recovery.RecoveryPreparationError,
        OSError,
    ) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "target_count": manifest["summary"]["target_count"],
                "target_gross_bytes": manifest["summary"]["target_gross_bytes"],
                "target_set_sha256": manifest["target_set_sha256"],
                "hold_count": manifest["summary"]["hold_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
