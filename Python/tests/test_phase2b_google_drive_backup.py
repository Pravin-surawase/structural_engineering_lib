"""Focused tests for the Phase 2B-R local backup package."""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest
from scripts._lib import phase2b_google_drive_backup as backup

pytestmark = pytest.mark.repo_only


def test_source_record_rejects_symlink(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.write_text("source", encoding="utf-8")
    link = tmp_path / "link"
    link.symlink_to(source)

    with pytest.raises(backup.BackupPackageError, match="not a regular file"):
        backup._source_record(link, "recovery/link", "TEST")


def test_verify_backup_archive_restores_exact_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "backup.tar.gz"
    payloads = {
        "recovery/git/all-refs.bundle": b"bundle",
        "recovery/worktrees/000/logs/session.json": b"session",
    }
    records = [
        {
            "archive_path": name,
            "category": "TEST",
            "size_bytes": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
            "mode": 0o600,
        }
        for name, value in payloads.items()
    ]
    manifest = {
        "schema_version": backup.SCHEMA_VERSION,
        "task_id": backup.TASK_ID,
        "packet_id": backup.PACKET_ID,
        "source_file_count": 2,
        "source_byte_count": 13,
        "records": records,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    with tarfile.open(archive_path, mode="w:gz") as archive:
        for name, value in payloads.items():
            archive.addfile(backup._tar_info(name, len(value)), io.BytesIO(value))
        archive.addfile(
            backup._tar_info(backup.PACKAGE_MANIFEST_PATH, len(manifest_bytes)),
            io.BytesIO(manifest_bytes),
        )

    result = backup.verify_backup_archive(archive_path)

    assert result == {
        "status": "PASS",
        "source_file_count": 2,
        "source_byte_count": 13,
        "package_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "temporary_restore_removed": True,
    }


def test_verify_backup_archive_rejects_tampered_record(tmp_path: Path) -> None:
    archive_path = tmp_path / "tampered.tar.gz"
    manifest = {
        "packet_id": backup.PACKET_ID,
        "source_file_count": 1,
        "source_byte_count": 4,
        "records": [
            {
                "archive_path": "recovery/source",
                "size_bytes": 4,
                "sha256": "0" * 64,
            }
        ],
    }
    manifest_bytes = json.dumps(manifest).encode()
    with tarfile.open(archive_path, mode="w:gz") as archive:
        archive.addfile(
            backup._tar_info("recovery/source", 4),
            io.BytesIO(b"data"),
        )
        archive.addfile(
            backup._tar_info(backup.PACKAGE_MANIFEST_PATH, len(manifest_bytes)),
            io.BytesIO(manifest_bytes),
        )

    with pytest.raises(backup.BackupPackageError, match="does not match"):
        backup.verify_backup_archive(archive_path)


def test_validate_live_sources_fails_on_head_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        backup.preservation,
        "_worktree_inventory",
        lambda _repo: {
            "current": {
                "branch": backup.BACKUP_BRANCH,
                "head_sha": "f" * 40,
                "operation": "none",
                "query_failures": [],
            }
        },
    )

    with pytest.raises(backup.BackupPackageError, match="frozen preparation"):
        backup._validate_live_sources(
            repo=tmp_path,
            primary_repo=tmp_path,
            preparation_manifest={
                "packet_id": backup.recovery.PACKET_ID,
                "status": "PHASE_2B_R_PREPARED_DESTINATION_HOLD",
            },
            recovery_evidence_path=tmp_path / "missing.json",
        )
