"""Create and verify the MAINT-0136 Phase 2B-R backup package.

The package contains the frozen ignored state, protected sources, verified Git
bundle, and dirty-worktree patch. The CLI only creates or verifies a local
archive. Google Drive upload and metadata readback remain connector-owned.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import stat
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Sequence

from scripts._lib import cleanup_preservation as preservation
from scripts._lib import phase2b_recovery_preparation as recovery

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PACKET_ID = "MAINT-0136-PHASE-2B-R-GOOGLE-DRIVE-BACKUP"
BACKUP_BRANCH = "codex/maint-0136-phase-2b-r-google-drive-backup"
PREPARATION_COMMIT = "2e3558a7fda4f8ff778c6ecd5f0435d0415ca229"
PACKAGE_MANIFEST_PATH = "metadata/package-manifest.json"


class BackupPackageError(RuntimeError):
    """Raised when a source or archive cannot be proven exactly."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BackupPackageError(f"could not load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BackupPackageError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _hash_stream(handle: BinaryIO) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _safe_member_name(value: str) -> PurePosixPath:
    relative = PurePosixPath(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise BackupPackageError(f"unsafe archive member: {value}")
    return relative


def _source_record(source: Path, archive_path: str, category: str) -> dict[str, Any]:
    try:
        metadata = source.lstat()
    except FileNotFoundError as exc:
        raise BackupPackageError(f"backup source disappeared: {source}") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise BackupPackageError(f"backup source is not a regular file: {source}")
    _safe_member_name(archive_path)
    with source.open("rb") as handle:
        digest = _hash_stream(handle)
    return {
        "source": source,
        "archive_path": archive_path,
        "category": category,
        "size_bytes": metadata.st_size,
        "sha256": digest,
        "mode": stat.S_IMODE(metadata.st_mode),
    }


def _protected_records(private_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    excluded = {"worktree_cleanup_archives", "__pycache__"}
    for source in sorted(private_root.rglob("*")):
        relative = source.relative_to(private_root)
        if any(part in excluded for part in relative.parts) or not source.is_file():
            continue
        records.append(
            _source_record(
                source,
                f"recovery/protected_sources/{relative.as_posix()}",
                "PROTECTED_SOURCE",
            )
        )
    return records


def _worktree_records(
    source_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    mapping: list[dict[str, Any]] = []
    for index, row in enumerate(source_rows):
        worktree = Path(row["worktree_path"]).resolve()
        relative_paths = recovery._ignored_files(worktree)
        preserved = recovery._preserved_records(worktree, relative_paths)
        aggregate = recovery.ignored_state_inventory(worktree)
        if aggregate != row["ignored_state"]:
            raise BackupPackageError(f"ignored-state source drifted: {worktree}")
        label = f"{index:03d}"
        mapping.append(
            {
                "label": label,
                "worktree_path": str(worktree),
                "branch": row["branch"],
                "head_sha": row["head_sha"],
                "ignored_state": aggregate["preserve"],
            }
        )
        for preserved_record in preserved:
            relative = PurePosixPath(preserved_record["relative_path"])
            source = worktree.joinpath(*relative.parts)
            archive_path = (
                f"recovery/worktrees/{label}/{preserved_record['relative_path']}"
            )
            record = _source_record(source, archive_path, preserved_record["category"])
            if (
                record["size_bytes"] != preserved_record["size_bytes"]
                or record["sha256"] != preserved_record["sha256"]
            ):
                raise BackupPackageError(f"ignored-state content drifted: {worktree}")
            records.append(record)
    return records, mapping


def _validate_live_sources(
    *,
    repo: Path,
    primary_repo: Path,
    preparation_manifest: dict[str, Any],
    recovery_evidence_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inventory = preservation._worktree_inventory(repo)
    current = inventory.get("current", {})
    if current.get("branch") != BACKUP_BRANCH:
        raise BackupPackageError(f"backup must run on {BACKUP_BRANCH}")
    if current.get("head_sha") != PREPARATION_COMMIT:
        raise BackupPackageError("backup lane is not at the frozen preparation commit")
    if current.get("operation") != "none" or current.get("query_failures"):
        raise BackupPackageError("current Git state cannot be inspected safely")
    if (
        preparation_manifest.get("packet_id") != recovery.PACKET_ID
        or preparation_manifest.get("status") != "PHASE_2B_R_PREPARED_DESTINATION_HOLD"
    ):
        raise BackupPackageError("recovery preparation authority changed")

    pull_requests = preservation._pull_requests(repo)
    open_pr_branches = {
        row["headRefName"] for row in pull_requests if row.get("state") == "OPEN"
    }
    live_by_path = {
        str(Path(item["path"]).resolve()): item
        for item in inventory.get("worktrees", [])
    }
    source_rows = preparation_manifest["worktree_sources"]["rows"]
    for row in source_rows:
        worktree = Path(row["worktree_path"]).resolve()
        live = live_by_path.get(str(worktree))
        if live is None:
            raise BackupPackageError(f"backup source worktree disappeared: {worktree}")
        if (
            live.get("query_status") != "OK"
            or live.get("operation") != "none"
            or live.get("dirty_count") != 0
            or live.get("current")
            or live.get("branch") != row["branch"]
            or live.get("head_sha") != row["head_sha"]
            or live.get("branch") in open_pr_branches
        ):
            raise BackupPackageError(f"backup source identity drifted: {worktree}")

    prior_recovery = recovery._validate_existing_recovery(recovery_evidence_path, repo)
    bundle_path = Path(
        _load_json(recovery_evidence_path)["git_bundle"]["path"]
    ).resolve()
    patch_path = Path(
        _load_json(recovery_evidence_path)["dirty_worktree"]["patch_path"]
    ).resolve()
    records = [
        _source_record(
            bundle_path, "recovery/git/all-refs.bundle", "GIT_ALL_REFS_BUNDLE"
        ),
        _source_record(
            patch_path, "recovery/git/dirty-worktree.patch", "DIRTY_WORKTREE_PATCH"
        ),
    ]
    if records[0]["sha256"] != prior_recovery["bundle"]["sha256"]:
        raise BackupPackageError("Git bundle drifted after verification")
    if records[1]["sha256"] != prior_recovery["dirty_patch"]["sha256"]:
        raise BackupPackageError("dirty patch drifted after verification")

    private_root = primary_repo / "private_sources"
    protected = preservation.protected_source_inventory(private_root)
    if protected != preparation_manifest["protected_sources"]:
        raise BackupPackageError("protected-source aggregate drifted")
    protected_records = _protected_records(private_root)
    if (
        len(protected_records) != protected["file_count"]
        or sum(row["size_bytes"] for row in protected_records)
        != protected["byte_count"]
    ):
        raise BackupPackageError("protected-source record count drifted")
    records.extend(protected_records)

    worktree_records, mapping = _worktree_records(source_rows)
    records.extend(worktree_records)
    if (
        len(records)
        != 2
        + protected["file_count"]
        + preparation_manifest["worktree_sources"]["summary"]["preserve_file_count"]
    ):
        raise BackupPackageError("backup source record count changed")
    if (
        sum(row["size_bytes"] for row in records)
        != preparation_manifest["backup_requirement"]["source_byte_count"]
    ):
        raise BackupPackageError("backup source byte count changed")
    return sorted(records, key=lambda row: row["archive_path"]), mapping


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in ("archive_path", "category", "size_bytes", "sha256", "mode")
    }


def _tar_info(name: str, size: int, mode: int = 0o600) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name=name)
    info.size = size
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def create_backup_archive(
    *,
    repo: Path,
    primary_repo: Path,
    preparation_manifest_path: Path,
    recovery_evidence_path: Path,
    output: Path,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Create one deterministic-content backup archive after exact revalidation."""
    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise BackupPackageError(f"backup output already exists: {output}")
    preparation_manifest = _load_json(preparation_manifest_path)
    records, mapping = _validate_live_sources(
        repo=repo.resolve(),
        primary_repo=primary_repo.resolve(),
        preparation_manifest=preparation_manifest,
        recovery_evidence_path=recovery_evidence_path.resolve(),
    )
    package_manifest = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "observed_at_utc": observed_at_utc,
        "preparation_commit": PREPARATION_COMMIT,
        "preparation_manifest_sha256": preservation.sha256_file(
            preparation_manifest_path
        ),
        "source_file_count": len(records),
        "source_byte_count": sum(row["size_bytes"] for row in records),
        "records": [_public_record(row) for row in records],
        "worktree_mapping": mapping,
    }
    manifest_bytes = (
        json.dumps(package_manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(output, mode="w:gz", compresslevel=6) as archive:
            for record in records:
                info = _tar_info(
                    record["archive_path"], record["size_bytes"], record["mode"]
                )
                with record["source"].open("rb") as handle:
                    archive.addfile(info, handle)
            archive.addfile(
                _tar_info(PACKAGE_MANIFEST_PATH, len(manifest_bytes)),
                io.BytesIO(manifest_bytes),
            )
    except Exception:
        if output.is_file() and not output.is_symlink():
            output.unlink()
        raise
    verification = verify_backup_archive(output)
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "packet_id": PACKET_ID,
        "status": "LOCAL_PACKAGE_CREATED_AND_RESTORE_VERIFIED",
        "observed_at_utc": observed_at_utc,
        "archive_path": str(output),
        "archive_size_bytes": output.stat().st_size,
        "archive_sha256": preservation.sha256_file(output),
        "source_file_count": len(records),
        "source_byte_count": sum(row["size_bytes"] for row in records),
        "package_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "restore_verification": verification,
        "mutations_performed": {
            "source_deletions": 0,
            "worktree_removals": 0,
            "branch_deletions": 0,
            "ref_deletions": 0,
            "pull_request_closures": 0,
            "cache_deletions": 0,
        },
    }


def _manifest_from_archive(archive: tarfile.TarFile) -> dict[str, Any]:
    members = archive.getmembers()
    names = [member.name for member in members]
    if len(names) != len(set(names)):
        raise BackupPackageError("backup archive contains duplicate members")
    if any(not member.isfile() for member in members):
        raise BackupPackageError("backup archive contains non-regular members")
    for name in names:
        _safe_member_name(name)
    try:
        member = archive.getmember(PACKAGE_MANIFEST_PATH)
    except KeyError as exc:
        raise BackupPackageError("backup package manifest is missing") from exc
    handle = archive.extractfile(member)
    if handle is None:
        raise BackupPackageError("backup package manifest cannot be read")
    with handle:
        try:
            value = json.load(handle)
        except json.JSONDecodeError as exc:
            raise BackupPackageError("backup package manifest is malformed") from exc
    if not isinstance(value, dict) or value.get("packet_id") != PACKET_ID:
        raise BackupPackageError("backup package identity is invalid")
    return value


def _extract_archive(archive: tarfile.TarFile, restore_root: Path) -> None:
    root = restore_root.resolve()
    for member in archive.getmembers():
        relative = _safe_member_name(member.name)
        if not member.isfile():
            raise BackupPackageError("backup archive contains unsupported members")
        target = restore_root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.parent.resolve().is_relative_to(root):
            raise BackupPackageError("backup archive member escapes restore root")
        source = archive.extractfile(member)
        if source is None:
            raise BackupPackageError(f"archive member cannot be read: {member.name}")
        with source, target.open("wb") as handle:
            shutil.copyfileobj(source, handle)
        os.chmod(target, member.mode & 0o777)


def verify_backup_archive(archive_path: Path) -> dict[str, Any]:
    """Restore all package members into managed temporary storage and hash them."""
    archive_path = archive_path.resolve()
    if archive_path.is_symlink() or not archive_path.is_file():
        raise BackupPackageError(f"backup archive is unavailable: {archive_path}")
    with tempfile.TemporaryDirectory(prefix="maint-0136-restore-") as temp:
        restore_root = Path(temp) / "restored"
        restore_root.mkdir()
        with tarfile.open(archive_path, mode="r:gz") as archive:
            package_manifest = _manifest_from_archive(archive)
            _extract_archive(archive, restore_root)
        expected_records = package_manifest.get("records")
        if not isinstance(expected_records, list):
            raise BackupPackageError("backup record list is malformed")
        for record in expected_records:
            if not isinstance(record, dict):
                raise BackupPackageError("backup record is malformed")
            relative = _safe_member_name(str(record.get("archive_path", "")))
            restored = restore_root.joinpath(*relative.parts)
            if restored.is_symlink() or not restored.is_file():
                raise BackupPackageError("restored backup source is unavailable")
            if restored.stat().st_size != record.get(
                "size_bytes"
            ) or preservation.sha256_file(restored) != record.get("sha256"):
                raise BackupPackageError("restored backup content does not match")
        restored_sources = {
            path.relative_to(restore_root).as_posix()
            for path in restore_root.rglob("*")
            if path.is_file()
            and path.relative_to(restore_root).as_posix() != PACKAGE_MANIFEST_PATH
        }
        expected_paths = {str(row["archive_path"]) for row in expected_records}
        if restored_sources != expected_paths:
            raise BackupPackageError("restored backup file set does not match")
        result = {
            "status": "PASS",
            "source_file_count": package_manifest["source_file_count"],
            "source_byte_count": package_manifest["source_byte_count"],
            "package_manifest_sha256": preservation.sha256_file(
                restore_root / PACKAGE_MANIFEST_PATH
            ),
            "temporary_restore_removed": True,
        }
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--repo", type=Path, required=True)
    create.add_argument("--primary-repo", type=Path, required=True)
    create.add_argument("--preparation-manifest", type=Path, required=True)
    create.add_argument("--recovery-evidence", type=Path, required=True)
    create.add_argument("--archive-output", type=Path, required=True)
    create.add_argument("--evidence-output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--archive", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "create":
            result = create_backup_archive(
                repo=args.repo,
                primary_repo=args.primary_repo,
                preparation_manifest_path=args.preparation_manifest,
                recovery_evidence_path=args.recovery_evidence,
                output=args.archive_output,
                observed_at_utc=datetime.now(UTC).isoformat(),
            )
            _write_json(args.evidence_output, result)
        else:
            result = verify_backup_archive(args.archive)
    except (
        BackupPackageError,
        recovery.RecoveryPreparationError,
        preservation.EvidenceError,
        OSError,
        tarfile.TarError,
    ) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
