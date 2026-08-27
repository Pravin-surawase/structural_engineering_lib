"""Focused tests for MAINT-0136 Phase 2B-W target preparation."""

from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

import pytest
from scripts._lib import phase2b_worktree_preparation as preparation

pytestmark = pytest.mark.repo_only


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _inputs(tmp_path: Path) -> dict[str, Path]:
    repo = tmp_path / "repo"
    primary = tmp_path / "primary"
    remote = tmp_path / "remote"
    integrated = tmp_path / "integrated"
    dirty = tmp_path / "dirty"
    for path in (repo, primary, remote, integrated, dirty):
        path.mkdir()
    archive = tmp_path / "backup.tar.gz"
    ignored = {
        "file_count": 1,
        "byte_count": 4,
        "aggregate_sha256": "ignored-sha",
        "category_summary": {},
        "filenames_recorded": False,
        "content_recorded": False,
    }
    package = {
        "packet_id": preparation.backup.PACKET_ID,
        "source_file_count": 3,
        "source_byte_count": 12,
        "worktree_mapping": [
            {
                "label": "000",
                "worktree_path": str(remote),
                "branch": "codex/remote",
                "head_sha": "remote-head",
                "ignored_state": ignored,
            },
            {
                "label": "001",
                "worktree_path": str(integrated),
                "branch": "codex/integrated",
                "head_sha": "integrated-head",
                "ignored_state": ignored,
            },
            {
                "label": "002",
                "worktree_path": str(dirty),
                "branch": "codex/dirty",
                "head_sha": "dirty-head",
                "ignored_state": ignored,
            },
        ],
    }
    package_bytes = (json.dumps(package, indent=2, sort_keys=True) + "\n").encode()
    with tarfile.open(archive, mode="w:gz") as handle:
        info = tarfile.TarInfo(preparation.backup.PACKAGE_MANIFEST_PATH)
        info.size = len(package_bytes)
        handle.addfile(info, io.BytesIO(package_bytes))
    archive_sha = preparation.preservation.sha256_file(archive)
    package_sha = preparation.hashlib.sha256(package_bytes).hexdigest()
    local = tmp_path / "local.json"
    _write_json(
        local,
        {
            "packet_id": preparation.backup.PACKET_ID,
            "status": preparation.LOCAL_PACKAGE_STATUS,
            "archive_path": str(archive),
            "archive_size_bytes": archive.stat().st_size,
            "archive_sha256": archive_sha,
            "source_file_count": 3,
            "source_byte_count": 12,
            "package_manifest_sha256": package_sha,
        },
    )
    evidence = tmp_path / "evidence.json"
    _write_json(
        evidence,
        {
            "packet_id": preparation.backup.PACKET_ID,
            "status": preparation.BACKUP_STATUS,
            "local_package": {
                "archive_sha256": archive_sha,
                "package_manifest_sha256": package_sha,
            },
            "remote_archive": {
                "status": "UPLOAD_AND_AUTHENTICATED_READBACK_PASS",
                "local_and_downloaded_sha256_match": True,
                "downloaded_readback_sha256": archive_sha,
                "remote_size_bytes": archive.stat().st_size,
            },
            "remote_restore": {
                "status": "PASS",
                "package_manifest_sha256": package_sha,
            },
        },
    )
    return {
        "repo": repo,
        "primary": primary,
        "remote": remote,
        "integrated": integrated,
        "dirty": dirty,
        "local": local,
        "evidence": evidence,
    }


def _inventory(paths: dict[str, Path]) -> dict[str, object]:
    def row(path: Path, branch: str, head: str, dirty: int = 0) -> dict[str, object]:
        return {
            "path": str(path),
            "branch": branch,
            "head_sha": head,
            "dirty_count": dirty,
            "operation": "none",
            "query_status": "OK",
            "current": False,
        }

    return {
        "current": {
            "worktree_root": str(paths["repo"]),
            "branch": preparation.PREPARATION_BRANCH,
            "head_sha": preparation.BACKUP_COMMIT,
            "operation": "none",
            "query_failures": [],
        },
        "worktrees": [
            row(
                paths["repo"], preparation.PREPARATION_BRANCH, preparation.BACKUP_COMMIT
            ),
            row(paths["remote"], "codex/remote", "remote-head"),
            row(paths["integrated"], "codex/integrated", "integrated-head"),
            row(paths["dirty"], "codex/dirty", "dirty-head", 1),
        ],
    }


def _patch_live(monkeypatch: pytest.MonkeyPatch, paths: dict[str, Path]) -> None:
    monkeypatch.setattr(
        preparation.preservation,
        "_worktree_inventory",
        lambda _repo: _inventory(paths),
    )
    monkeypatch.setattr(preparation.preservation, "_pull_requests", lambda _repo: [])
    monkeypatch.setattr(
        preparation.preservation,
        "_remote_heads",
        lambda _repo: {"main": "main-head", "codex/remote": "remote-head"},
    )
    monkeypatch.setattr(
        preparation,
        "_live_origin_main",
        lambda _repo, _heads: "main-head",
    )
    monkeypatch.setattr(
        preparation.preservation,
        "_is_ancestor",
        lambda _repo, sha, _main: sha == "integrated-head",
    )
    monkeypatch.setattr(preparation.preservation, "path_size_bytes", lambda _path: 100)
    monkeypatch.setattr(
        preparation.recovery,
        "ignored_state_inventory",
        lambda _path: {
            "preserve": {
                "file_count": 1,
                "byte_count": 4,
                "aggregate_sha256": "ignored-sha",
                "category_summary": {},
                "filenames_recorded": False,
                "content_recorded": False,
            }
        },
    )


def _build(paths: dict[str, Path]) -> dict[str, object]:
    return preparation.build_manifest(
        repo=paths["repo"],
        primary_repo=paths["primary"],
        backup_evidence_path=paths["evidence"],
        local_package_path=paths["local"],
        observed_at_utc="2026-08-27T00:00:00+00:00",
    )


def test_freezes_only_remote_or_integrated_backed_worktrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live(monkeypatch, paths)

    manifest = _build(paths)

    assert manifest["summary"]["target_count"] == 2
    assert manifest["summary"]["target_gross_bytes"] == 200
    assert {row["branch"] for row in manifest["targets"]} == {
        "codex/remote",
        "codex/integrated",
    }
    assert manifest["summary"]["remote_exact_target_count"] == 1
    assert manifest["summary"]["integrated_target_count"] == 1
    assert manifest["authorization"]["worktree_removal_authorized"] is False
    assert paths["remote"].is_dir()
    assert paths["integrated"].is_dir()


def test_dirty_backed_worktree_is_held_without_inspecting_ignored_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live(monkeypatch, paths)

    manifest = _build(paths)

    dirty = next(row for row in manifest["holds"] if row["branch"] == "codex/dirty")
    assert dirty["reason_codes"] == ["WORKTREE_DIRTY"]
    assert paths["dirty"].is_dir()


def test_open_pull_request_lane_is_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live(monkeypatch, paths)
    monkeypatch.setattr(
        preparation.preservation,
        "_pull_requests",
        lambda _repo: [
            {
                "number": 99,
                "state": "OPEN",
                "headRefName": "codex/remote",
                "headRefOid": "remote-head",
                "url": "https://example.invalid/99",
            }
        ],
    )

    manifest = _build(paths)

    held = next(row for row in manifest["holds"] if row["branch"] == "codex/remote")
    assert held["reason_codes"] == ["OPEN_PULL_REQUEST"]
    assert paths["remote"].is_dir()


def test_local_only_unintegrated_lane_is_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live(monkeypatch, paths)
    monkeypatch.setattr(
        preparation.preservation,
        "_remote_heads",
        lambda _repo: {"main": "main-head"},
    )
    monkeypatch.setattr(
        preparation.preservation,
        "_is_ancestor",
        lambda _repo, _sha, _main: False,
    )

    manifest = _build(paths)

    held = next(row for row in manifest["holds"] if row["branch"] == "codex/remote")
    assert held["reason_codes"] == ["NO_EXACT_REMOTE_OR_INTEGRATED_RECOVERY"]
    assert paths["remote"].is_dir()


def test_ignored_state_drift_holds_exact_lane(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live(monkeypatch, paths)
    original = preparation.recovery.ignored_state_inventory
    monkeypatch.setattr(
        preparation.recovery,
        "ignored_state_inventory",
        lambda path: (
            {"preserve": {"aggregate_sha256": "drift"}}
            if path == paths["remote"]
            else original(path)
        ),
    )

    manifest = _build(paths)

    held = next(row for row in manifest["holds"] if row["branch"] == "codex/remote")
    assert "IGNORED_STATE_DRIFT_AFTER_BACKUP" in held["reason_codes"]
    assert paths["remote"].is_dir()


def test_rejects_remote_archive_identity_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live(monkeypatch, paths)
    evidence = json.loads(paths["evidence"].read_text(encoding="utf-8"))
    evidence["remote_archive"]["remote_size_bytes"] += 1
    _write_json(paths["evidence"], evidence)

    with pytest.raises(
        preparation.WorktreePreparationError,
        match="local and remote backup identities differ",
    ):
        _build(paths)

    assert paths["remote"].is_dir()
