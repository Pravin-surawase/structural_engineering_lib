"""Freeze and execute the exact MAINT-0136 Phase 2A cache packet.

The packet is intentionally narrow: only ``react_app/node_modules`` and
``.mypy_cache`` identities already present in the frozen Phase 1 manifest may
be selected.  Primary, current, predecessor, dirty, missing, or changed lanes
fail closed.  No Git worktree, branch, ref, protected source, or shared Python
runtime operation is implemented here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from scripts._lib import cleanup_preservation as preservation

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2A-CACHE"
AUTHORIZED_RELATIVE_PATHS = (".mypy_cache", "react_app/node_modules")
PROTECTED_PATH_PARTS = {".git", ".venv", "private_sources"}
PHASE1_BRANCH = "codex/maint-0136-cleanup-preservation"
PHASE2A_BRANCH = "codex/maint-0136-phase-2a-cache-cleanup"


class CacheCleanupError(RuntimeError):
    """Raised when the exact cache packet cannot be proven safe."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CacheCleanupError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CacheCleanupError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _phase1_candidate_identities(
    phase1_manifest: dict[str, Any],
) -> list[tuple[str, str]]:
    if phase1_manifest.get("task_id") != TASK_ID:
        raise CacheCleanupError("Phase 1 manifest task identity does not match")
    identities = {
        (row["worktree_path"], row["relative_path"])
        for row in phase1_manifest.get("caches", [])
        if row.get("disposition") == "CACHE_CANDIDATE_NOT_AUTHORIZED"
        and row.get("relative_path") in AUTHORIZED_RELATIVE_PATHS
    }
    if not identities:
        raise CacheCleanupError("Phase 1 manifest has no authorized cache identities")
    return sorted(identities)


def _topology_rows(
    inventory: dict[str, Any], *, current_repo: Path
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_repo = current_repo.resolve()
    for item in inventory.get("worktrees", []):
        path = Path(item["path"]).resolve()
        rows.append(
            {
                "path": str(path),
                "branch": item.get("branch"),
                "head_sha": item.get("head_sha"),
                "dirty_count": (
                    "CURRENT_TASK_WRITES_IGNORED"
                    if path == current_repo
                    else item.get("dirty_count")
                ),
                "operation": item.get("operation"),
                "query_status": item.get("query_status"),
            }
        )
    return sorted(rows, key=lambda row: row["path"])


def _validate_target_path(worktree: Path, relative_path: str) -> Path:
    if relative_path not in AUTHORIZED_RELATIVE_PATHS:
        raise CacheCleanupError(f"unauthorized cache relative path: {relative_path}")
    relative = PurePosixPath(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise CacheCleanupError(f"unsafe cache relative path: {relative_path}")
    if PROTECTED_PATH_PARTS.intersection(relative.parts):
        raise CacheCleanupError(f"protected path part in target: {relative_path}")

    try:
        worktree_root = worktree.resolve(strict=True)
    except OSError as exc:
        raise CacheCleanupError(f"worktree is unavailable: {worktree}") from exc
    target = worktree.joinpath(*relative.parts)
    if target.is_symlink():
        raise CacheCleanupError(f"cache target is a symlink: {target}")
    if not target.is_dir():
        raise CacheCleanupError(f"cache target is not a directory: {target}")
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        raise CacheCleanupError(f"cache target is unavailable: {target}") from exc
    expected = worktree_root.joinpath(*relative.parts)
    if resolved != expected or not resolved.is_relative_to(worktree_root):
        raise CacheCleanupError(f"cache target escapes its worktree: {target}")
    return target


def _recreation_basis(
    *, worktree: Path, relative_path: str, head_sha: str
) -> dict[str, Any]:
    if relative_path == ".mypy_cache":
        return {
            "kind": "TOOL_GENERATED_MYPY_CACHE",
            "command_basis": "repository mypy invocation",
            "head_sha": head_sha,
        }

    lock_relative = "react_app/package-lock.json"
    lockfile = worktree / lock_relative
    if lockfile.is_symlink() or not lockfile.is_file():
        raise CacheCleanupError(f"npm lockfile is unavailable in {worktree}")
    result = preservation._run(
        ["git", "cat-file", "-e", f"{head_sha}:{lock_relative}"],
        cwd=worktree,
        check=False,
    )
    if result.returncode != 0:
        raise CacheCleanupError(
            f"npm lockfile is not present at {head_sha} in {worktree}"
        )
    return {
        "kind": "NPM_LOCKFILE",
        "path": lock_relative,
        "sha256": preservation.sha256_file(lockfile),
        "head_sha": head_sha,
        "recreate_command": "npm ci",
    }


def _target_set_sha256(targets: list[dict[str, Any]]) -> str:
    return _canonical_sha256(targets)


def _refs_snapshot(repo: Path) -> dict[str, Any]:
    result = preservation._run(
        ["git", "for-each-ref", "--format=%(refname)%09%(objectname)"], cwd=repo
    )
    lines = sorted(line for line in result.stdout.splitlines() if line)
    return {"count": len(lines), "sha256": _canonical_sha256(lines)}


def build_target_manifest(
    *,
    repo: Path,
    primary_repo: Path,
    phase1_worktree: Path,
    dirty_worktree: Path,
    phase1_manifest_path: Path,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Return the exact Phase 2A target manifest without mutating caches."""
    repo = repo.resolve()
    primary_repo = primary_repo.resolve()
    phase1_worktree = phase1_worktree.resolve()
    dirty_worktree = dirty_worktree.resolve()
    phase1_manifest_path = phase1_manifest_path.resolve()
    phase1_manifest = _load_json(phase1_manifest_path)
    candidate_identities = _phase1_candidate_identities(phase1_manifest)
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if Path(current.get("worktree_root", "")).resolve() != repo:
        raise CacheCleanupError("Git-state current worktree does not match --repo")
    if current.get("branch") != PHASE2A_BRANCH:
        raise CacheCleanupError(
            f"Phase 2A must run on {PHASE2A_BRANCH}, found {current.get('branch')}"
        )

    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    excluded = {
        str(primary_repo): "PRIMARY_CHECKOUT",
        str(repo): "CURRENT_PHASE_2A_TASK",
        str(phase1_worktree): "FROZEN_PHASE_1_PREDECESSOR",
        str(dirty_worktree): "DIRTY_UNIQUE_LANE",
    }
    targets: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []
    for worktree_text, relative_path in candidate_identities:
        worktree = Path(worktree_text).resolve()
        identity = {
            "worktree_path": str(worktree),
            "relative_path": relative_path,
        }
        item = live_by_path.get(str(worktree))
        reason: str | None = excluded.get(str(worktree))
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
        target_path = worktree / relative_path
        if reason is None and not os.path.lexists(target_path):
            reason = "CACHE_ALREADY_ABSENT"
        if reason is not None:
            held.append({**identity, "reason": reason})
            continue

        target = _validate_target_path(worktree, relative_path)
        head_sha = str(item["head_sha"])
        targets.append(
            {
                **identity,
                "absolute_path": str(target),
                "branch": item.get("branch"),
                "head_sha": head_sha,
                "size_bytes": preservation.path_size_bytes(target),
                "recreation_basis": _recreation_basis(
                    worktree=worktree,
                    relative_path=relative_path,
                    head_sha=head_sha,
                ),
            }
        )

    targets.sort(key=lambda row: (row["worktree_path"], row["relative_path"]))
    held.sort(key=lambda row: (row["worktree_path"], row["relative_path"]))
    topology = _topology_rows(inventory, current_repo=repo)
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": "PHASE_2A_TARGETS_FROZEN",
        "observed_at_utc": observed_at_utc,
        "authorization": {
            "source": "active Codex task: okay start phase 2A",
            "recovery_tier": "REGENERABLE_CACHE_SAME_DISK_ACCEPTED",
            "authorized_relative_paths": list(AUTHORIZED_RELATIVE_PATHS),
            "prohibited_operations": [
                "DELETE_FILE_OUTSIDE_EXACT_CACHE_TARGETS",
                "REMOVE_WORKTREE",
                "DELETE_BRANCH_OR_REF",
                "CLOSE_PULL_REQUEST",
                "GIT_CLEAN",
                "PRUNE",
                "DELETE_PROTECTED_SOURCE",
                "DELETE_SHARED_VENV",
            ],
        },
        "binding": {
            "repo": str(repo),
            "branch": current["branch"],
            "head_sha": current["head_sha"],
            "phase1_branch": PHASE1_BRANCH,
            "phase1_manifest_path": str(phase1_manifest_path),
            "phase1_manifest_sha256": preservation.sha256_file(phase1_manifest_path),
            "phase1_candidate_identity_count": len(candidate_identities),
            "topology_sha256": _canonical_sha256(topology),
        },
        "excluded_worktrees": [
            {"path": path, "reason": reason}
            for path, reason in sorted(excluded.items())
        ],
        "targets": targets,
        "held_candidates": held,
        "summary": {
            "target_count": len(targets),
            "target_bytes": sum(row["size_bytes"] for row in targets),
            "node_modules_count": sum(
                row["relative_path"] == "react_app/node_modules" for row in targets
            ),
            "mypy_cache_count": sum(
                row["relative_path"] == ".mypy_cache" for row in targets
            ),
            "held_candidate_count": len(held),
        },
        "target_set_sha256": _target_set_sha256(targets),
    }


def _validate_execution_preconditions(
    *, repo: Path, manifest: dict[str, Any]
) -> tuple[dict[str, Any], list[Path]]:
    if manifest.get("packet_id") != PACKET_ID:
        raise CacheCleanupError("target manifest packet identity does not match")
    if manifest.get("status") != "PHASE_2A_TARGETS_FROZEN":
        raise CacheCleanupError("target manifest is not frozen")
    binding = manifest.get("binding", {})
    if Path(binding.get("repo", "")).resolve() != repo:
        raise CacheCleanupError("target manifest is bound to a different repository")
    phase1_manifest_path = Path(binding.get("phase1_manifest_path", "")).resolve()
    if not phase1_manifest_path.is_file() or preservation.sha256_file(
        phase1_manifest_path
    ) != binding.get("phase1_manifest_sha256"):
        raise CacheCleanupError("frozen Phase 1 manifest changed after target freeze")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        raise CacheCleanupError("target manifest has no executable targets")
    if _target_set_sha256(targets) != manifest.get("target_set_sha256"):
        raise CacheCleanupError("target-set digest does not match the manifest")

    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if current.get("branch") != PHASE2A_BRANCH:
        raise CacheCleanupError("execution is not on the Phase 2A branch")
    if current.get("head_sha") != binding.get("head_sha"):
        raise CacheCleanupError("Phase 2A HEAD changed after target freeze")
    topology = _topology_rows(inventory, current_repo=repo)
    if _canonical_sha256(topology) != binding.get("topology_sha256"):
        raise CacheCleanupError("worktree topology changed after target freeze")

    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    validated: list[Path] = []
    for row in targets:
        worktree = Path(row["worktree_path"]).resolve()
        relative_path = row["relative_path"]
        if row.get("absolute_path") != str(worktree / relative_path):
            raise CacheCleanupError("absolute target path does not match its identity")
        item = live_by_path.get(str(worktree))
        if item is None:
            raise CacheCleanupError(f"target worktree is no longer live: {worktree}")
        if (
            item.get("query_status") != "OK"
            or item.get("operation") != "none"
            or item.get("dirty_count") != 0
            or item.get("current")
            or item.get("head_sha") != row.get("head_sha")
            or item.get("branch") != row.get("branch")
        ):
            raise CacheCleanupError(f"target worktree state changed: {worktree}")
        target = _validate_target_path(worktree, relative_path)
        current_size = preservation.path_size_bytes(target)
        if current_size != row.get("size_bytes"):
            raise CacheCleanupError(f"cache size changed after freeze: {target}")
        basis = _recreation_basis(
            worktree=worktree,
            relative_path=relative_path,
            head_sha=str(row["head_sha"]),
        )
        if basis != row.get("recreation_basis"):
            raise CacheCleanupError(f"recreation basis changed after freeze: {target}")
        validated.append(target)
    return inventory, validated


def execute_manifest(*, repo: Path, manifest_path: Path) -> dict[str, Any]:
    """Delete only the frozen exact targets and return before/after evidence."""
    repo = repo.resolve()
    manifest_path = manifest_path.resolve()
    manifest = _load_json(manifest_path)
    inventory_before, targets = _validate_execution_preconditions(
        repo=repo, manifest=manifest
    )
    primary_repo = preservation.PRIMARY_REPO.resolve()
    private_root = primary_repo / "private_sources"
    protected_before = preservation.protected_source_inventory(private_root)
    refs_before = _refs_snapshot(repo)
    disk_before = preservation._disk_capacity(repo)

    removed: list[dict[str, Any]] = []
    failure: str | None = None
    for row, target in zip(manifest["targets"], targets, strict=True):
        try:
            target = _validate_target_path(
                Path(row["worktree_path"]).resolve(), row["relative_path"]
            )
            shutil.rmtree(target)
            if os.path.lexists(target):
                raise OSError("target still exists after removal")
        except OSError as exc:
            failure = f"{target}: {exc}"
            break
        removed.append(
            {
                "absolute_path": str(target),
                "worktree_path": row["worktree_path"],
                "relative_path": row["relative_path"],
                "size_bytes": row["size_bytes"],
                "status": "REMOVED",
            }
        )

    inventory_after = preservation._worktree_inventory(repo)
    protected_after = preservation.protected_source_inventory(private_root)
    refs_after = _refs_snapshot(repo)
    disk_after = preservation._disk_capacity(repo)
    topology_before = _canonical_sha256(
        _topology_rows(inventory_before, current_repo=repo)
    )
    topology_after = _canonical_sha256(
        _topology_rows(inventory_after, current_repo=repo)
    )
    protected_unchanged = protected_before == protected_after
    refs_unchanged = refs_before == refs_after
    topology_unchanged = topology_before == topology_after
    all_removed = len(removed) == len(targets)
    status = (
        "PASS"
        if failure is None
        and all_removed
        and protected_unchanged
        and refs_unchanged
        and topology_unchanged
        else "PARTIAL_FAILURE"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": status,
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "target_manifest": {
            "path": str(manifest_path),
            "sha256": preservation.sha256_file(manifest_path),
            "target_set_sha256": manifest["target_set_sha256"],
        },
        "execution": {
            "requested_target_count": len(targets),
            "removed_target_count": len(removed),
            "removed_bytes": sum(row["size_bytes"] for row in removed),
            "failure": failure,
            "removed": removed,
        },
        "preservation": {
            "topology_unchanged": topology_unchanged,
            "topology_sha256_before": topology_before,
            "topology_sha256_after": topology_after,
            "refs_unchanged": refs_unchanged,
            "refs_before": refs_before,
            "refs_after": refs_after,
            "protected_sources_unchanged": protected_unchanged,
            "protected_sources_before": protected_before,
            "protected_sources_after": protected_after,
            "worktree_removals": 0,
            "branch_or_ref_deletions": 0,
            "pull_request_closures": 0,
        },
        "disk": {
            "before": disk_before,
            "after": disk_after,
            "available_bytes_delta": (
                disk_after["available_bytes"] - disk_before["available_bytes"]
            ),
            "filesystem_accounting_may_be_deferred": True,
        },
        "recovery": {
            "tier": "REGENERABLE_CACHE_SAME_DISK_ACCEPTED",
            "node_modules_basis": "frozen per-HEAD package-lock.json plus npm ci",
            "mypy_basis": "tool-generated cache",
            "cache_bytes_are_not_independently_backed_up": True,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--repo", type=Path, required=True)
    freeze.add_argument("--primary-repo", type=Path, required=True)
    freeze.add_argument("--phase1-worktree", type=Path, required=True)
    freeze.add_argument("--dirty-worktree", type=Path, required=True)
    freeze.add_argument("--phase1-manifest", type=Path, required=True)
    freeze.add_argument("--manifest-output", type=Path, required=True)

    execute = subparsers.add_parser("execute")
    execute.add_argument("--repo", type=Path, required=True)
    execute.add_argument("--manifest", type=Path, required=True)
    execute.add_argument("--evidence-output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "freeze":
            result = build_target_manifest(
                repo=args.repo,
                primary_repo=args.primary_repo,
                phase1_worktree=args.phase1_worktree,
                dirty_worktree=args.dirty_worktree,
                phase1_manifest_path=args.phase1_manifest,
                observed_at_utc=datetime.now(UTC).isoformat(),
            )
            _write_json(args.manifest_output, result)
            summary = {"status": result["status"], **result["summary"]}
        else:
            result = execute_manifest(repo=args.repo, manifest_path=args.manifest)
            _write_json(args.evidence_output, result)
            summary = {"status": result["status"], **result["execution"]}
    except (CacheCleanupError, preservation.EvidenceError) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if result["status"] in {"PHASE_2A_TARGETS_FROZEN", "PASS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
