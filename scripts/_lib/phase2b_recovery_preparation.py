"""Prepare exact off-device recovery inputs for MAINT-0136 Phase 2B-R.

This module inventories ignored worktree state, existing Git recovery artifacts,
and protected-source aggregates without recording ignored or protected filenames.
It can exercise the byte-for-byte archive/restore primitive in managed test
directories, but its CLI only writes a preparation manifest. It never deletes,
removes, archives, copies to a destination, or changes Git/GitHub state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tarfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterable, Sequence

from scripts._lib import cleanup_preservation as preservation
from scripts._lib import phase2a_cache_cleanup as phase2a
from scripts._lib import phase2b_cleanup_preparation as phase2b

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2B-R-PREPARATION"
PHASE2B_PREP_BRANCH = "codex/maint-0136-phase-2b-preparation"
PHASE2B_R_BRANCH = "codex/maint-0136-phase-2b-r-recovery-preparation"
REGENERABLE_PARTS = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
REGENERABLE_PREFIXES = (
    "Python/build/",
    "react_app/.vite/",
    "react_app/dist/",
    "react_app/dist-ssr/",
    "site/",
)
RESTORE_RESERVE_BYTES = 64 * 1024 * 1024


class RecoveryPreparationError(RuntimeError):
    """Raised when recovery preparation cannot prove its source boundary."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecoveryPreparationError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RecoveryPreparationError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _safe_relative_path(value: str) -> PurePosixPath:
    relative = PurePosixPath(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise RecoveryPreparationError(f"unsafe ignored path: {value}")
    return relative


def _is_regenerable(relative: PurePosixPath) -> bool:
    value = relative.as_posix()
    return (
        bool(REGENERABLE_PARTS.intersection(relative.parts))
        or value.startswith(REGENERABLE_PREFIXES)
        or any(part.endswith(".egg-info") for part in relative.parts)
        or value.endswith((".pyc", ".pyo"))
        or relative.name == ".DS_Store"
    )


def _preservation_category(relative: PurePosixPath) -> str:
    value = relative.as_posix()
    if relative.parts[0] == "logs":
        return "SESSION_PIPELINE_AND_TRUST_STATE"
    if ".hypothesis" in relative.parts:
        return "HYPOTHESIS_REPRODUCTION_STATE"
    if value.startswith("Python/dist/"):
        return "BUILT_RELEASE_ARTIFACT"
    if value.startswith("tmp/deleted_backups/"):
        return "SAFE_DELETE_RECOVERY_ARTIFACT"
    if relative.parts[0] == ".benchmarks":
        return "BENCHMARK_STATE"
    return "UNKNOWN_IGNORED_STATE_PRESERVE"


def _ignored_files(worktree: Path) -> list[PurePosixPath]:
    result = preservation._run(
        [
            "git",
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "-z",
        ],
        cwd=worktree,
    )
    return sorted(
        (_safe_relative_path(value) for value in result.stdout.split("\0") if value),
        key=PurePosixPath.as_posix,
    )


def _hash_stream(handle: BinaryIO) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _aggregate_records(records: Iterable[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record["relative_path"].encode("utf-8", "surrogateescape"))
        digest.update(b"\0")
        digest.update(str(record["size_bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _preserved_records(
    worktree: Path, relative_paths: Iterable[PurePosixPath]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative in relative_paths:
        if _is_regenerable(relative):
            continue
        target = worktree.joinpath(*relative.parts)
        try:
            metadata = target.lstat()
        except FileNotFoundError as exc:
            raise RecoveryPreparationError(
                f"ignored source disappeared during inventory: {worktree}"
            ) from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise RecoveryPreparationError(
                f"ignored symlink requires explicit review in {worktree}"
            )
        if not stat.S_ISREG(metadata.st_mode):
            raise RecoveryPreparationError(
                f"ignored non-regular source requires explicit review in {worktree}"
            )
        with target.open("rb") as handle:
            sha256 = _hash_stream(handle)
        records.append(
            {
                "relative_path": relative.as_posix(),
                "size_bytes": metadata.st_size,
                "sha256": sha256,
                "category": _preservation_category(relative),
            }
        )
    return sorted(records, key=lambda row: row["relative_path"])


def ignored_state_inventory(worktree: Path) -> dict[str, Any]:
    """Return aggregate ignored-state evidence without exposing filenames."""
    relative_paths = _ignored_files(worktree)
    preserve_records = _preserved_records(worktree, relative_paths)
    preserve_set = {row["relative_path"] for row in preserve_records}
    category_summary: dict[str, dict[str, int]] = {}
    for record in preserve_records:
        summary = category_summary.setdefault(
            record["category"], {"file_count": 0, "byte_count": 0}
        )
        summary["file_count"] += 1
        summary["byte_count"] += record["size_bytes"]
    regenerable_count = 0
    regenerable_bytes = 0
    for relative in relative_paths:
        if relative.as_posix() in preserve_set:
            continue
        target = worktree.joinpath(*relative.parts)
        try:
            metadata = target.lstat()
        except FileNotFoundError as exc:
            raise RecoveryPreparationError(
                f"ignored source disappeared during inventory: {worktree}"
            ) from exc
        if not stat.S_ISREG(metadata.st_mode):
            raise RecoveryPreparationError(
                f"regenerable ignored source is not a regular file in {worktree}"
            )
        regenerable_count += 1
        regenerable_bytes += metadata.st_size
    return {
        "preserve": {
            "file_count": len(preserve_records),
            "byte_count": sum(row["size_bytes"] for row in preserve_records),
            "aggregate_sha256": _aggregate_records(preserve_records),
            "category_summary": dict(sorted(category_summary.items())),
            "filenames_recorded": False,
            "content_recorded": False,
        },
        "regenerable_excluded": {
            "file_count": regenerable_count,
            "byte_count": regenerable_bytes,
            "classification": "PROVEN_BUILD_TEST_TOOL_OUTPUT",
        },
        "total_ignored_file_count": len(relative_paths),
    }


def _explicit_tree_aggregate(root: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for target in sorted(path for path in root.rglob("*") if path.is_file()):
        relative = target.relative_to(root).as_posix()
        with target.open("rb") as handle:
            sha256 = _hash_stream(handle)
        records.append(
            {
                "relative_path": relative,
                "size_bytes": target.stat().st_size,
                "sha256": sha256,
            }
        )
    return {
        "file_count": len(records),
        "byte_count": sum(row["size_bytes"] for row in records),
        "aggregate_sha256": _aggregate_records(records),
    }


def create_preserved_state_archive(
    worktree: Path, archive_path: Path
) -> dict[str, Any]:
    """Create one archive primitive for managed tests or a later approved caller."""
    if archive_path.exists() or archive_path.is_symlink():
        raise RecoveryPreparationError(f"archive target already exists: {archive_path}")
    relative_paths = _ignored_files(worktree)
    records = _preserved_records(worktree, relative_paths)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, mode="w:gz") as archive:
        for record in records:
            source = worktree.joinpath(*PurePosixPath(record["relative_path"]).parts)
            archive.add(source, arcname=record["relative_path"], recursive=False)
    return {
        "archive_path": str(archive_path),
        "archive_sha256": preservation.sha256_file(archive_path),
        "source_file_count": len(records),
        "source_byte_count": sum(row["size_bytes"] for row in records),
        "source_aggregate_sha256": _aggregate_records(records),
    }


def restore_preserved_state_archive(
    archive_path: Path, restore_root: Path, expected: dict[str, Any]
) -> dict[str, Any]:
    """Extract regular members safely and verify restored content aggregate."""
    if restore_root.exists() or restore_root.is_symlink():
        raise RecoveryPreparationError(f"restore target already exists: {restore_root}")
    restore_root.mkdir(parents=True)
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive.getmembers():
            relative = _safe_relative_path(member.name)
            if not member.isfile():
                raise RecoveryPreparationError(
                    f"archive contains unsupported member type: {member.name}"
                )
            target = restore_root.joinpath(*relative.parts)
            resolved_parent = target.parent.resolve()
            if not resolved_parent.is_relative_to(restore_root.resolve()):
                raise RecoveryPreparationError("archive member escapes restore root")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise RecoveryPreparationError(
                    f"archive member cannot be read: {member.name}"
                )
            with source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)
            os.chmod(target, member.mode & 0o777)
    restored = _explicit_tree_aggregate(restore_root)
    expected_summary = {
        "file_count": expected["source_file_count"],
        "byte_count": expected["source_byte_count"],
        "aggregate_sha256": expected["source_aggregate_sha256"],
    }
    if restored != expected_summary:
        raise RecoveryPreparationError("restored archive content does not match source")
    return {**restored, "status": "PASS"}


def _validate_existing_recovery(
    recovery_evidence_path: Path, repo: Path
) -> dict[str, Any]:
    evidence = _load_json(recovery_evidence_path)
    if evidence.get("status") != "LOCAL_RECOVERY_VERIFIED_OFF_DEVICE_HOLD":
        raise RecoveryPreparationError("Phase 1 recovery evidence status changed")
    bundle = Path(evidence.get("git_bundle", {}).get("path", ""))
    patch = Path(evidence.get("dirty_worktree", {}).get("patch_path", ""))
    for label, target in (("bundle", bundle), ("patch", patch)):
        if target.is_symlink() or not target.is_file():
            raise RecoveryPreparationError(f"Phase 1 {label} is unavailable")
    bundle_evidence = evidence["git_bundle"]
    patch_evidence = evidence["dirty_worktree"]
    if (
        bundle.stat().st_size != bundle_evidence["size_bytes"]
        or preservation.sha256_file(bundle) != bundle_evidence["sha256"]
    ):
        raise RecoveryPreparationError("Phase 1 Git bundle identity changed")
    if (
        patch.stat().st_size != patch_evidence["patch_size_bytes"]
        or preservation.sha256_file(patch) != patch_evidence["patch_sha256"]
    ):
        raise RecoveryPreparationError("Phase 1 dirty patch identity changed")
    verification = preservation._run(["git", "bundle", "verify", str(bundle)], cwd=repo)
    if verification.returncode != 0:
        raise RecoveryPreparationError("Phase 1 Git bundle no longer verifies")
    return {
        "evidence_sha256": preservation.sha256_file(recovery_evidence_path),
        "bundle": {
            "size_bytes": bundle_evidence["size_bytes"],
            "sha256": bundle_evidence["sha256"],
            "verification": "PASS",
        },
        "dirty_patch": {
            "size_bytes": patch_evidence["patch_size_bytes"],
            "sha256": patch_evidence["patch_sha256"],
            "restore_sample_status": "PASS",
        },
        "prior_protected_sources": {
            "file_count": evidence["protected_sources"]["file_count"],
            "byte_count": evidence["protected_sources"]["byte_count"],
            "aggregate_sha256": evidence["protected_sources"]["aggregate_sha256"],
        },
    }


def _source_row(
    row: dict[str, Any], live_item: dict[str, Any], open_pr_branches: set[str]
) -> dict[str, Any]:
    worktree = Path(row["path"]).resolve()
    if live_item.get("query_status") != "OK" or live_item.get("operation") != "none":
        raise RecoveryPreparationError(f"worktree state cannot be proven: {worktree}")
    if live_item.get("dirty_count") != 0 or live_item.get("current"):
        raise RecoveryPreparationError(f"worktree is active or dirty: {worktree}")
    if live_item.get("branch") in open_pr_branches:
        raise RecoveryPreparationError(f"worktree branch has an open PR: {worktree}")
    if live_item.get("branch") != row.get("branch") or live_item.get(
        "head_sha"
    ) != row.get("head_sha"):
        raise RecoveryPreparationError(f"worktree identity changed: {worktree}")
    return {
        "worktree_path": str(worktree),
        "branch": live_item["branch"],
        "head_sha": live_item["head_sha"],
        "ignored_state": ignored_state_inventory(worktree),
        "disposition": "BACKUP_SOURCE_FROZEN_DESTINATION_HOLD",
    }


def _source_rows(
    rows: list[dict[str, Any]],
    live_by_path: dict[str, dict[str, Any]],
    open_pr_branches: set[str],
) -> list[dict[str, Any]]:
    def collect(row: dict[str, Any]) -> dict[str, Any]:
        worktree = Path(row["path"]).resolve()
        live_item = live_by_path.get(str(worktree))
        if live_item is None:
            raise RecoveryPreparationError(f"worktree is no longer live: {worktree}")
        return _source_row(row, live_item, open_pr_branches)

    with ThreadPoolExecutor(max_workers=8) as executor:
        result = list(executor.map(collect, rows))
    return sorted(result, key=lambda row: row["worktree_path"])


def build_recovery_manifest(
    *,
    repo: Path,
    primary_repo: Path,
    phase2b_worktree: Path,
    phase2b_manifest_path: Path,
    recovery_evidence_path: Path,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Build an exact recovery source packet without copying any source data."""
    repo = repo.resolve()
    primary_repo = primary_repo.resolve()
    phase2b_worktree = phase2b_worktree.resolve()
    phase2b_manifest_path = phase2b_manifest_path.resolve()
    recovery_evidence_path = recovery_evidence_path.resolve()
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if Path(current.get("worktree_root", "")).resolve() != repo:
        raise RecoveryPreparationError("Git-state current worktree does not match")
    if current.get("branch") != PHASE2B_R_BRANCH:
        raise RecoveryPreparationError(
            f"recovery preparation must run on {PHASE2B_R_BRANCH}"
        )
    if current.get("operation") != "none" or current.get("query_failures"):
        raise RecoveryPreparationError("current Git state is not safely inspectable")

    phase2b_manifest = _load_json(phase2b_manifest_path)
    if (
        phase2b_manifest.get("packet_id") != phase2b.PACKET_ID
        or phase2b_manifest.get("status") != "PHASE_2B_PREPARED_NOT_AUTHORIZED"
    ):
        raise RecoveryPreparationError("Phase 2B preparation authority changed")
    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    phase2b_item = live_by_path.get(str(phase2b_worktree))
    if phase2b_item is None:
        raise RecoveryPreparationError("Phase 2B predecessor is not live")
    if (
        phase2b_item.get("branch") != PHASE2B_PREP_BRANCH
        or phase2b_item.get("dirty_count") != 0
        or phase2b_item.get("operation") != "none"
        or phase2b_item.get("query_status") != "OK"
    ):
        raise RecoveryPreparationError("Phase 2B predecessor is not immutable")
    if current.get("head_sha") != phase2b_item.get("head_sha"):
        raise RecoveryPreparationError("recovery lane is not based on Phase 2B head")

    pull_requests = preservation._pull_requests(repo)
    open_pr_branches = {
        row["headRefName"] for row in pull_requests if row.get("state") == "OPEN"
    }
    review_rows = [
        row
        for row in phase2b_manifest.get("worktree_retirement", {}).get("rows", [])
        if row.get("disposition") == "RETIREMENT_REVIEW_ONLY"
    ]
    if len(review_rows) != phase2b_manifest["worktree_retirement"]["summary"].get(
        "review_only_count"
    ):
        raise RecoveryPreparationError("Phase 2B review-row count changed")
    source_rows = _source_rows(review_rows, live_by_path, open_pr_branches)

    recovery = _validate_existing_recovery(recovery_evidence_path, repo)
    protected_sources = preservation.protected_source_inventory(
        primary_repo / "private_sources"
    )
    if (
        protected_sources["aggregate_sha256"]
        != recovery["prior_protected_sources"]["aggregate_sha256"]
    ):
        raise RecoveryPreparationError("protected-source aggregate changed")
    if (
        protected_sources["file_count"]
        != recovery["prior_protected_sources"]["file_count"]
        or protected_sources["byte_count"]
        != recovery["prior_protected_sources"]["byte_count"]
    ):
        raise RecoveryPreparationError("protected-source inventory changed")

    preserve_files = sum(
        row["ignored_state"]["preserve"]["file_count"] for row in source_rows
    )
    preserve_bytes = sum(
        row["ignored_state"]["preserve"]["byte_count"] for row in source_rows
    )
    regenerable_files = sum(
        row["ignored_state"]["regenerable_excluded"]["file_count"]
        for row in source_rows
    )
    regenerable_bytes = sum(
        row["ignored_state"]["regenerable_excluded"]["byte_count"]
        for row in source_rows
    )
    component_bytes = {
        "worktree_preserved_ignored_state": preserve_bytes,
        "git_bundle": recovery["bundle"]["size_bytes"],
        "dirty_patch": recovery["dirty_patch"]["size_bytes"],
        "protected_sources": protected_sources["byte_count"],
    }
    source_bytes = sum(component_bytes.values())
    required_free_bytes = source_bytes * 2 + RESTORE_RESERVE_BYTES
    time_machine = preservation._destination_status()
    external_volumes = phase2b._external_volume_status()
    destination_available = (
        time_machine["status"] == "AVAILABLE" or external_volumes["candidate_count"] > 0
    )
    status = (
        "PHASE_2B_R_PREPARED_DESTINATION_REVIEW"
        if destination_available
        else "PHASE_2B_R_PREPARED_DESTINATION_HOLD"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": status,
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
                "reference": "active Codex task: okay let continue",
            },
            "authorized_actions": [
                "INSPECT_RECOVERY_INPUTS",
                "FREEZE_RECOVERY_SOURCE_MANIFEST",
                "COMMIT_PREPARATION_EVIDENCE",
            ],
            "next_action": "COMMIT_PREPARATION_EVIDENCE",
            "backup_execution_authorized": False,
            "cleanup_execution_authorized": False,
            "prohibited_actions": [
                "COPY_TO_UNVERIFIED_DESTINATION",
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
                    "INSPECT_RECOVERY_INPUTS",
                    "FREEZE_RECOVERY_SOURCE_MANIFEST",
                    "COMMIT_PREPARATION_EVIDENCE",
                ],
            },
        },
        "binding": {
            "repo": str(repo),
            "branch": current["branch"],
            "head_sha_at_freeze": current["head_sha"],
            "phase2b_worktree": str(phase2b_worktree),
            "phase2b_head_sha": phase2b_item["head_sha"],
            "phase2b_manifest_sha256": preservation.sha256_file(phase2b_manifest_path),
            "topology_sha256": _canonical_sha256(
                phase2a._topology_rows(inventory, current_repo=repo)
            ),
            "refs": phase2a._refs_snapshot(repo),
        },
        "existing_recovery": recovery,
        "protected_sources": protected_sources,
        "worktree_sources": {
            "rows": source_rows,
            "summary": {
                "worktree_count": len(source_rows),
                "preserve_file_count": preserve_files,
                "preserve_byte_count": preserve_bytes,
                "regenerable_excluded_file_count": regenerable_files,
                "regenerable_excluded_byte_count": regenerable_bytes,
                "filenames_recorded": False,
                "content_recorded": False,
            },
        },
        "backup_requirement": {
            "component_bytes": component_bytes,
            "source_byte_count": source_bytes,
            "required_destination_free_bytes": required_free_bytes,
            "free_space_formula": "2 * source bytes + 64 MiB restore reserve",
            "destination_contract": [
                "SEPARATE_PHYSICAL_OR_OFF_DEVICE_FAILURE_DOMAIN",
                "ENCRYPTION_PROVEN",
                "WRITABLE_EXACT_DESTINATION",
                "SUFFICIENT_FREE_SPACE",
                "SOURCE_DIGEST_RECHECK_BEFORE_COPY",
                "MANAGED_RESTORE_AGGREGATE_MATCH",
                "NO_SOURCE_OR_WORKTREE_REMOVAL",
            ],
        },
        "destination_readiness": {
            "time_machine": time_machine,
            "external_volumes": external_volumes,
            "usable_encrypted_destination_proven": False,
            "status": "HOLD_DESTINATION_UNAVAILABLE_OR_UNVERIFIED",
        },
        "next_gate": {
            "decision": "MOUNT_OR_SELECT_ENCRYPTED_OFF_DEVICE_DESTINATION",
            "required_user_authorization": (
                "Authorize backup to one exact verified destination only; cleanup "
                "remains separately held."
            ),
            "worktree_retirement_authorized": False,
        },
        "mutations_performed": {
            "backup_copies": 0,
            "archive_creations": 0,
            "restore_directories": 0,
            "file_deletions": 0,
            "cache_deletions": 0,
            "worktree_removals": 0,
            "branch_deletions": 0,
            "ref_deletions": 0,
            "pr_closures": 0,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--primary-repo", type=Path, required=True)
    parser.add_argument("--phase2b-worktree", type=Path, required=True)
    parser.add_argument("--phase2b-manifest", type=Path, required=True)
    parser.add_argument("--recovery-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_recovery_manifest(
            repo=args.repo,
            primary_repo=args.primary_repo,
            phase2b_worktree=args.phase2b_worktree,
            phase2b_manifest_path=args.phase2b_manifest,
            recovery_evidence_path=args.recovery_evidence,
            observed_at_utc=datetime.now(UTC).isoformat(),
        )
        _write_json(args.output, result)
    except (RecoveryPreparationError, preservation.EvidenceError) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    summary = result["worktree_sources"]["summary"]
    print(
        json.dumps(
            {
                "status": result["status"],
                "worktree_count": summary["worktree_count"],
                "preserve_file_count": summary["preserve_file_count"],
                "preserve_byte_count": summary["preserve_byte_count"],
                "regenerable_excluded_file_count": summary[
                    "regenerable_excluded_file_count"
                ],
                "regenerable_excluded_byte_count": summary[
                    "regenerable_excluded_byte_count"
                ],
                "required_destination_free_bytes": result["backup_requirement"][
                    "required_destination_free_bytes"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--primary-repo", type=Path, required=True)
    parser.add_argument("--phase2b-worktree", type=Path, required=True)
    parser.add_argument("--phase2b-manifest", type=Path, required=True)
    parser.add_argument("--recovery-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_recovery_manifest(
            repo=args.repo,
            primary_repo=args.primary_repo,
            phase2b_worktree=args.phase2b_worktree,
            phase2b_manifest_path=args.phase2b_manifest,
            recovery_evidence_path=args.recovery_evidence,
            observed_at_utc=datetime.now(UTC).isoformat(),
        )
        _write_json(args.output, result)
    except (RecoveryPreparationError, preservation.EvidenceError) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": result["status"],
                "worktree_count": result["worktree_sources"]["summary"][
                    "worktree_count"
                ],
                "preserve_bytes": result["worktree_sources"]["summary"][
                    "preserve_byte_count"
                ],
                "regenerable_excluded_bytes": result["worktree_sources"]["summary"][
                    "regenerable_excluded_byte_count"
                ],
                "required_destination_free_bytes": result["backup_requirement"][
                    "required_destination_free_bytes"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
