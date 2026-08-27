"""Execute one exact MAINT-0136 Phase 2B-W worktree manifest.

The executor is fail closed.  It requires the owner-authorized target count and
SHA-256, revalidates every target against live Git/GitHub and the verified
backup, removes worktrees only through non-force ``git worktree remove``, and
writes an incremental recovery ledger.  It never deletes branches, refs, pull
requests, archives, protected sources, or the shared Python environment.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Sequence

from scripts._lib import cleanup_preservation as preservation
from scripts._lib import phase2a_cache_cleanup as phase2a
from scripts._lib import phase2b_recovery_preparation as recovery
from scripts._lib import phase2b_worktree_preparation as preparation

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2B-W-EXECUTION"
PREPARATION_PACKET_ID = "MAINT-0136-PHASE-2B-W-PREPARATION"
PREPARATION_STATUS = "PHASE_2B_W_TARGETS_FROZEN_AWAITING_DIGEST_BOUND_AUTHORIZATION"
EXECUTION_BRANCH = "codex/maint-0136-phase-2b-w-preparation"
PREPARATION_COMMIT = "e1f5ea184638133e7911e8ad0203194104c27276"


class WorktreeExecutionError(RuntimeError):
    """Raised when execution cannot preserve the exact authorized boundary."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorktreeExecutionError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorktreeExecutionError(f"{path} must contain a JSON object")
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


def _manifest_identity(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    targets = manifest.get("targets")
    identity = manifest.get("target_identity")
    if not isinstance(targets, list) or not isinstance(identity, list):
        raise WorktreeExecutionError("target manifest rows are malformed")
    expected = [
        {
            "path": row.get("path"),
            "branch": row.get("branch"),
            "head_sha": row.get("head_sha"),
            "gross_size_bytes": row.get("gross_size_bytes"),
            "ignored_state_aggregate_sha256": row.get("recovery", {})
            .get("ignored_state", {})
            .get("aggregate_sha256"),
        }
        for row in targets
    ]
    if identity != expected:
        raise WorktreeExecutionError("target identity rows do not match targets")
    return identity


def _validate_manifest(
    manifest: dict[str, Any], *, expected_digest: str, expected_count: int
) -> list[dict[str, Any]]:
    if (
        manifest.get("packet_id") != PREPARATION_PACKET_ID
        or manifest.get("status") != PREPARATION_STATUS
    ):
        raise WorktreeExecutionError("Phase 2B-W preparation identity changed")
    identity = _manifest_identity(manifest)
    digest = preparation._canonical_sha256(identity)
    if (
        digest != manifest.get("target_set_sha256")
        or digest != expected_digest
        or len(identity) != expected_count
        or manifest.get("summary", {}).get("target_count") != expected_count
    ):
        raise WorktreeExecutionError("authorized target count or digest does not match")
    if sum(int(row["gross_size_bytes"]) for row in identity) != manifest.get(
        "summary", {}
    ).get("target_gross_bytes"):
        raise WorktreeExecutionError("authorized target byte total does not match")
    return manifest["targets"]


def _operation_markers(worktree: Path) -> list[str]:
    git_dir_text = preservation._run(
        ["git", "rev-parse", "--absolute-git-dir"], cwd=worktree
    ).stdout.strip()
    git_dir = Path(git_dir_text)
    markers = [
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "REBASE_HEAD",
        "BISECT_START",
        "rebase-apply",
        "rebase-merge",
    ]
    return sorted(marker for marker in markers if (git_dir / marker).exists())


def _target_live_row(
    *,
    target: dict[str, Any],
    live: dict[str, Any] | None,
    repo: Path,
    open_pr_branches: set[str],
    remote_heads: dict[str, str],
    live_origin_main: str,
) -> dict[str, Any]:
    path = Path(str(target["path"]))
    if live is None:
        raise WorktreeExecutionError(f"authorized worktree is no longer live: {path}")
    preparation._safe_live_path(path)
    if (
        live.get("query_status") != "OK"
        or live.get("operation") != "none"
        or live.get("dirty_count") != 0
        or live.get("current")
    ):
        raise WorktreeExecutionError(f"authorized worktree is active or dirty: {path}")
    if live.get("branch") != target.get("branch") or live.get("head_sha") != target.get(
        "head_sha"
    ):
        raise WorktreeExecutionError(f"authorized worktree identity drifted: {path}")
    if target.get("branch") == "DETACHED":
        raise WorktreeExecutionError(f"detached worktree cannot execute: {path}")
    if target.get("branch") in open_pr_branches:
        raise WorktreeExecutionError(f"authorized worktree now has an open PR: {path}")
    markers = _operation_markers(path)
    if markers:
        raise WorktreeExecutionError(f"authorized worktree has Git operation: {path}")
    ignored = recovery.ignored_state_inventory(path)["preserve"]
    if ignored != target.get("recovery", {}).get("ignored_state"):
        raise WorktreeExecutionError(
            f"authorized ignored state drifted after backup: {path}"
        )
    size_bytes = preservation.path_size_bytes(path)
    if size_bytes != target.get("gross_size_bytes"):
        raise WorktreeExecutionError(f"authorized worktree size drifted: {path}")
    remote_exact = remote_heads.get(str(target["branch"])) == target["head_sha"]
    integrated = preservation._is_ancestor(repo, target["head_sha"], live_origin_main)
    if not remote_exact and not integrated:
        raise WorktreeExecutionError(
            f"authorized worktree lost remote/integrated recovery: {path}"
        )
    return {
        "path": str(path.resolve()),
        "branch": target["branch"],
        "head_sha": target["head_sha"],
        "gross_size_bytes": size_bytes,
        "ignored_state": ignored,
        "remote_exact_head": remote_exact,
        "integrated_into_live_origin_main": integrated,
        "git_operation_markers": markers,
        "status": "REVALIDATED_READY",
    }


def revalidate_all(
    *,
    repo: Path,
    primary_repo: Path,
    manifest_path: Path,
    backup_evidence_path: Path,
    local_package_path: Path,
    expected_digest: str,
    expected_count: int,
    active_target_overlap_count: int,
) -> dict[str, Any]:
    """Revalidate the full target set without performing any removal."""
    repo = repo.resolve()
    primary_repo = primary_repo.resolve()
    if active_target_overlap_count != 0:
        raise WorktreeExecutionError("an authorized target is active in Codex")
    manifest = _load_json(manifest_path.resolve())
    targets = _validate_manifest(
        manifest,
        expected_digest=expected_digest,
        expected_count=expected_count,
    )
    backup_evidence, package = preparation._validated_backup(
        backup_evidence_path=backup_evidence_path.resolve(),
        local_package_path=local_package_path.resolve(),
    )
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if Path(str(current.get("worktree_root", ""))).resolve() != repo:
        raise WorktreeExecutionError("current Git worktree does not match executor")
    if (
        current.get("branch") != EXECUTION_BRANCH
        or current.get("head_sha") != PREPARATION_COMMIT
        or current.get("operation") != "none"
        or current.get("query_failures")
    ):
        raise WorktreeExecutionError("execution lane identity is not frozen")
    if len(inventory.get("worktrees", [])) != manifest.get("summary", {}).get(
        "live_worktree_count"
    ):
        raise WorktreeExecutionError("live worktree topology count drifted")
    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    if str(primary_repo) not in live_by_path or str(repo) not in live_by_path:
        raise WorktreeExecutionError("protected primary or executor lane is missing")
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
    live_origin_main = preparation._live_origin_main(repo, remote_heads)
    rows = [
        _target_live_row(
            target=target,
            live=live_by_path.get(str(Path(target["path"]).resolve())),
            repo=repo,
            open_pr_branches=open_pr_branches,
            remote_heads=remote_heads,
            live_origin_main=live_origin_main,
        )
        for target in targets
    ]
    package_paths = {
        str(Path(row["worktree_path"]).resolve()) for row in package["worktree_mapping"]
    }
    if any(row["path"] not in package_paths for row in rows):
        raise WorktreeExecutionError("authorized target is absent from backup mapping")
    refs = phase2a._refs_snapshot(repo)
    protected = preservation.protected_source_inventory(
        primary_repo / "private_sources"
    )
    archive_path = Path(
        _load_json(local_package_path.resolve())["archive_path"]
    ).resolve()
    return {
        "repo": repo,
        "primary_repo": primary_repo,
        "manifest_path": manifest_path.resolve(),
        "manifest": manifest,
        "targets": rows,
        "inventory": inventory,
        "open_pull_requests": open_prs,
        "remote_heads": remote_heads,
        "live_origin_main": live_origin_main,
        "refs": refs,
        "protected_sources": protected,
        "backup": {
            "archive_path": archive_path,
            "archive_size_bytes": archive_path.stat().st_size,
            "archive_sha256": preservation.sha256_file(archive_path),
            "remote_status": backup_evidence["remote_archive"]["status"],
            "remote_restore_status": backup_evidence["remote_restore"]["status"],
            "remote_shared": backup_evidence["remote_archive"]["shared"],
        },
        "disk": preservation._disk_capacity(repo),
    }


def _remove_worktree(repo: Path, path: Path) -> None:
    preservation._run(["git", "worktree", "remove", str(path)], cwd=repo)


def _verify_branch_preserved(repo: Path, branch: str, head_sha: str) -> None:
    result = preservation._run(
        ["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd=repo
    )
    actual = result.stdout.split()[0] if result.stdout.split() else ""
    if actual != head_sha:
        raise WorktreeExecutionError(f"branch was not preserved exactly: {branch}")


def _fresh_target_check(
    *,
    target: dict[str, Any],
    repo: Path,
    live_origin_main: str,
    remote_heads: dict[str, str],
) -> None:
    path = Path(target["path"])
    preparation._safe_live_path(path)
    status = preservation._run(
        ["git", "status", "--porcelain=v1", "-z"], cwd=path
    ).stdout
    if status:
        raise WorktreeExecutionError(f"target became dirty before removal: {path}")
    branch = preservation._run(
        ["git", "branch", "--show-current"], cwd=path
    ).stdout.strip()
    head_sha = preservation._run(["git", "rev-parse", "HEAD"], cwd=path).stdout.strip()
    if branch != target["branch"] or head_sha != target["head_sha"]:
        raise WorktreeExecutionError(f"target identity changed before removal: {path}")
    if _operation_markers(path):
        raise WorktreeExecutionError(
            f"target operation appeared before removal: {path}"
        )
    ignored = recovery.ignored_state_inventory(path)["preserve"]
    if ignored != target["ignored_state"]:
        raise WorktreeExecutionError(f"target ignored state changed: {path}")
    if preservation.path_size_bytes(path) != target["gross_size_bytes"]:
        raise WorktreeExecutionError(f"target size changed before removal: {path}")
    remote_exact = remote_heads.get(target["branch"]) == target["head_sha"]
    integrated = preservation._is_ancestor(repo, target["head_sha"], live_origin_main)
    if not remote_exact and not integrated:
        raise WorktreeExecutionError(f"target recovery changed before removal: {path}")


def _execution_evidence(
    *, context: dict[str, Any], expected_digest: str, expected_count: int
) -> dict[str, Any]:
    observed = datetime.now(UTC).isoformat()
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": "EXECUTION_STARTED",
        "observed_at_utc": observed,
        "authorization": {
            "status": "OBSERVED",
            "query_status": "OK",
            "observed_at_utc": observed,
            "authority_source": {
                "kind": "USER_DELEGATION",
                "status": "OBSERVED",
                "query_status": "OK",
                "observed_at_utc": observed,
                "reference": (
                    "active Codex task: I authorize Phase 2B-W execution for "
                    "the exact 63-worktree manifest and target digest"
                ),
            },
            "authorized_action": "REMOVE_ONLY_EXACT_FROZEN_WORKTREES",
            "authorized_actions": [
                "REMOVE_ONLY_EXACT_FROZEN_WORKTREES",
                "COMMIT_EXECUTION_EVIDENCE",
            ],
            "next_action": "COMMIT_EXECUTION_EVIDENCE",
            "target_binding": {
                "task_id": PACKET_ID,
                "branch": EXECUTION_BRANCH,
                "head_sha": PREPARATION_COMMIT,
                "actions": [
                    "REMOVE_ONLY_EXACT_FROZEN_WORKTREES",
                    "COMMIT_EXECUTION_EVIDENCE",
                ],
            },
            "target_count": expected_count,
            "target_set_sha256": expected_digest,
            "non_force_only": True,
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
            "preparation_commit": PREPARATION_COMMIT,
            "preparation_manifest_sha256": preservation.sha256_file(
                context["manifest_path"]
            ),
            "target_count": expected_count,
            "target_gross_bytes": context["manifest"]["summary"]["target_gross_bytes"],
            "target_set_sha256": expected_digest,
            "live_origin_main_sha": context["live_origin_main"],
            "active_target_overlap_count": 0,
        },
        "before": {
            "live_worktree_count": len(context["inventory"]["worktrees"]),
            "refs": context["refs"],
            "protected_sources": context["protected_sources"],
            "backup": {
                key: value
                for key, value in context["backup"].items()
                if key != "archive_path"
            },
            "disk": context["disk"],
            "open_pull_request_count": len(context["open_pull_requests"]),
        },
        "targets": context["targets"],
        "removals": [],
        "failure": None,
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


def execute(
    *,
    context: dict[str, Any],
    output_path: Path,
    expected_digest: str,
    expected_count: int,
    removal_authorized: bool,
    remove: Callable[[Path, Path], None] = _remove_worktree,
) -> dict[str, Any]:
    """Remove all exact targets and retain an incremental execution ledger."""
    if not removal_authorized:
        raise WorktreeExecutionError("exact worktree removal is not authorized")
    output_path = output_path.resolve()
    if output_path.exists() or output_path.is_symlink():
        raise WorktreeExecutionError(
            f"execution evidence already exists: {output_path}"
        )
    evidence = _execution_evidence(
        context=context,
        expected_digest=expected_digest,
        expected_count=expected_count,
    )
    _write_json_atomic(output_path, evidence)
    repo = context["repo"]
    try:
        for index, target in enumerate(context["targets"], start=1):
            _fresh_target_check(
                target=target,
                repo=repo,
                live_origin_main=context["live_origin_main"],
                remote_heads=context["remote_heads"],
            )
            path = Path(target["path"])
            remove(repo, path)
            if path.exists() or path.is_symlink():
                raise WorktreeExecutionError(
                    f"removed worktree path still exists: {path}"
                )
            _verify_branch_preserved(repo, target["branch"], target["head_sha"])
            evidence["removals"].append(
                {
                    "index": index,
                    "path": target["path"],
                    "branch": target["branch"],
                    "head_sha": target["head_sha"],
                    "gross_size_bytes": target["gross_size_bytes"],
                    "operation": "GIT_WORKTREE_REMOVE_WITHOUT_FORCE",
                    "path_absent": True,
                    "branch_preserved": True,
                    "status": "PASS",
                }
            )
            evidence["mutations_performed"]["worktree_removals"] = len(
                evidence["removals"]
            )
            _write_json_atomic(output_path, evidence)
    except Exception as exc:
        evidence["status"] = "PARTIAL_EXECUTION_HOLD"
        evidence["failure"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "completed_worktree_removals": len(evidence["removals"]),
        }
        _write_json_atomic(output_path, evidence)
        raise

    try:
        after_inventory = preservation._worktree_inventory(repo)
        expected_after = len(context["inventory"]["worktrees"]) - expected_count
        live_after = {
            str(Path(row["path"]).resolve()) for row in after_inventory["worktrees"]
        }
        if len(after_inventory["worktrees"]) != expected_after or any(
            row["path"] in live_after for row in context["targets"]
        ):
            raise WorktreeExecutionError("post-removal topology does not match")
        refs_after = phase2a._refs_snapshot(repo)
        if refs_after != context["refs"]:
            raise WorktreeExecutionError(
                "branch or ref set changed during worktree removal"
            )
        protected_after = preservation.protected_source_inventory(
            context["primary_repo"] / "private_sources"
        )
        if protected_after != context["protected_sources"]:
            raise WorktreeExecutionError("protected-source aggregate changed")
        archive_path = context["backup"]["archive_path"]
        archive_after = {
            "archive_size_bytes": archive_path.stat().st_size,
            "archive_sha256": preservation.sha256_file(archive_path),
        }
        if archive_after != {
            "archive_size_bytes": context["backup"]["archive_size_bytes"],
            "archive_sha256": context["backup"]["archive_sha256"],
        }:
            raise WorktreeExecutionError("verified backup archive changed")
    except Exception as exc:
        evidence["status"] = "POST_EXECUTION_HOLD"
        evidence["failure"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "completed_worktree_removals": len(evidence["removals"]),
        }
        _write_json_atomic(output_path, evidence)
        raise
    evidence["status"] = "PASS"
    evidence["completed_at_utc"] = datetime.now(UTC).isoformat()
    evidence["after"] = {
        "live_worktree_count": len(after_inventory["worktrees"]),
        "refs": refs_after,
        "protected_sources": protected_after,
        "backup": archive_after,
        "disk": preservation._disk_capacity(repo),
        "all_target_paths_absent": True,
        "all_target_branches_preserved": True,
    }
    evidence["summary"] = {
        "authorized_target_count": expected_count,
        "removed_worktree_count": len(evidence["removals"]),
        "gross_removed_path_bytes": sum(
            row["gross_size_bytes"] for row in evidence["removals"]
        ),
        "target_set_sha256": expected_digest,
        "remaining_live_worktree_count": len(after_inventory["worktrees"]),
    }
    _write_json_atomic(output_path, evidence)
    return evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preview", "execute"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--repo", type=Path, required=True)
        subparser.add_argument("--primary-repo", type=Path, required=True)
        subparser.add_argument("--manifest", type=Path, required=True)
        subparser.add_argument("--backup-evidence", type=Path, required=True)
        subparser.add_argument("--local-package-evidence", type=Path, required=True)
        subparser.add_argument("--expected-target-set-sha256", required=True)
        subparser.add_argument("--expected-target-count", type=int, required=True)
        subparser.add_argument("--active-target-overlap-count", type=int, required=True)
    execute_parser = subparsers.choices["execute"]
    execute_parser.add_argument("--output", type=Path, required=True)
    execute_parser.add_argument(
        "--confirm-exact-authorization",
        action="store_true",
        help="Required only after the owner confirms the exact count and digest.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        context = revalidate_all(
            repo=args.repo,
            primary_repo=args.primary_repo,
            manifest_path=args.manifest,
            backup_evidence_path=args.backup_evidence,
            local_package_path=args.local_package_evidence,
            expected_digest=args.expected_target_set_sha256,
            expected_count=args.expected_target_count,
            active_target_overlap_count=args.active_target_overlap_count,
        )
        if args.command == "preview":
            result = {
                "status": "PREVIEW_PASS_NO_MUTATION",
                "target_count": len(context["targets"]),
                "target_gross_bytes": sum(
                    row["gross_size_bytes"] for row in context["targets"]
                ),
                "target_set_sha256": args.expected_target_set_sha256,
                "live_worktree_count": len(context["inventory"]["worktrees"]),
            }
        else:
            result = execute(
                context=context,
                output_path=args.output,
                expected_digest=args.expected_target_set_sha256,
                expected_count=args.expected_target_count,
                removal_authorized=args.confirm_exact_authorization,
            )
    except (
        WorktreeExecutionError,
        preparation.WorktreePreparationError,
        preservation.EvidenceError,
        recovery.RecoveryPreparationError,
        OSError,
    ) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    if args.command == "execute":
        result = {
            "status": result["status"],
            **result["summary"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
