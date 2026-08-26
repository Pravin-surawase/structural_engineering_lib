"""Focused tests for MAINT-0136 Phase 2B-R recovery preparation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath

import pytest
from scripts._lib import phase2b_recovery_preparation as recovery

pytestmark = pytest.mark.repo_only


def _git_ignored_worktree(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    (path / ".gitignore").write_text(
        "logs/\n.ruff_cache/\n.hypothesis/\nsite/\nPython/dist/\n",
        encoding="utf-8",
    )
    (path / "logs").mkdir()
    (path / "logs" / "sessions.json").write_text("session", encoding="utf-8")
    (path / ".ruff_cache").mkdir()
    (path / ".ruff_cache" / "cache.bin").write_bytes(b"cache")
    (path / ".hypothesis").mkdir()
    (path / ".hypothesis" / "example").write_bytes(b"hypothesis")
    (path / "site").mkdir()
    (path / "site" / "index.html").write_text("generated", encoding="utf-8")
    (path / "Python" / "dist").mkdir(parents=True)
    (path / "Python" / "dist" / "package.whl").write_bytes(b"wheel")


def test_ignored_inventory_separates_preserved_state(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    _git_ignored_worktree(worktree)

    inventory = recovery.ignored_state_inventory(worktree)

    assert inventory["preserve"]["file_count"] == 3
    assert inventory["preserve"]["byte_count"] == len(b"sessionhypothesiswheel")
    assert inventory["regenerable_excluded"]["file_count"] == 2
    assert inventory["preserve"]["filenames_recorded"] is False
    assert inventory["preserve"]["content_recorded"] is False


def test_regenerable_classification_is_narrow() -> None:
    assert recovery._is_regenerable(PurePosixPath("site/index.html"))
    assert recovery._is_regenerable(PurePosixPath("Python/pkg/__pycache__/a.pyc"))
    assert recovery._is_regenerable(PurePosixPath("react_app/dist/app.js"))
    assert not recovery._is_regenerable(PurePosixPath("logs/sessions/a.json"))
    assert not recovery._is_regenerable(PurePosixPath("Python/dist/package.whl"))
    assert not recovery._is_regenerable(
        PurePosixPath("tmp/deleted_backups/receipt.json")
    )


def test_archive_restore_round_trip_matches_source(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    _git_ignored_worktree(worktree)
    archive = tmp_path / "preserved.tar.gz"
    restored = tmp_path / "restored"

    evidence = recovery.create_preserved_state_archive(worktree, archive)
    result = recovery.restore_preserved_state_archive(archive, restored, evidence)

    assert result["status"] == "PASS"
    assert result["file_count"] == 3
    assert (restored / "logs" / "sessions.json").read_text(encoding="utf-8") == (
        "session"
    )
    assert not (restored / ".ruff_cache").exists()
    assert not (restored / "site").exists()


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_manifest_freezes_sources_and_holds_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = {name: tmp_path / name for name in ("repo", "primary", "phase2b", "old")}
    for name in ("repo", "primary", "phase2b"):
        paths[name].mkdir()
    _git_ignored_worktree(paths["old"])
    phase2b_manifest_path = tmp_path / "phase2b.json"
    _write_json(
        phase2b_manifest_path,
        {
            "packet_id": recovery.phase2b.PACKET_ID,
            "status": "PHASE_2B_PREPARED_NOT_AUTHORIZED",
            "worktree_retirement": {
                "summary": {"review_only_count": 1},
                "rows": [
                    {
                        "path": str(paths["old"]),
                        "branch": "codex/old",
                        "head_sha": "old-head",
                        "disposition": "RETIREMENT_REVIEW_ONLY",
                    }
                ],
            },
        },
    )
    recovery_evidence = tmp_path / "recovery.json"
    _write_json(recovery_evidence, {"status": "unused by monkeypatch"})
    inventory = {
        "current": {
            "worktree_root": str(paths["repo"]),
            "branch": recovery.PHASE2B_R_BRANCH,
            "head_sha": "phase2b-head",
            "operation": "none",
            "query_failures": [],
        },
        "worktrees": [
            {
                "path": str(paths["repo"]),
                "branch": recovery.PHASE2B_R_BRANCH,
                "head_sha": "phase2b-head",
                "dirty_count": 1,
                "operation": "none",
                "query_status": "OK",
                "current": True,
            },
            {
                "path": str(paths["phase2b"]),
                "branch": recovery.PHASE2B_PREP_BRANCH,
                "head_sha": "phase2b-head",
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "current": False,
            },
            {
                "path": str(paths["old"]),
                "branch": "codex/old",
                "head_sha": "old-head",
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "current": False,
            },
        ],
    }
    monkeypatch.setattr(
        recovery.preservation, "_worktree_inventory", lambda _repo: inventory
    )
    monkeypatch.setattr(recovery.preservation, "_pull_requests", lambda _repo: [])
    monkeypatch.setattr(
        recovery,
        "_validate_existing_recovery",
        lambda _path, _repo: {
            "evidence_sha256": "recovery",
            "bundle": {"size_bytes": 10, "sha256": "bundle"},
            "dirty_patch": {"size_bytes": 2, "sha256": "patch"},
            "prior_protected_sources": {
                "file_count": 2,
                "byte_count": 20,
                "aggregate_sha256": "protected",
            },
        },
    )
    monkeypatch.setattr(
        recovery.preservation,
        "protected_source_inventory",
        lambda _path: {
            "file_count": 2,
            "byte_count": 20,
            "aggregate_sha256": "protected",
        },
    )
    monkeypatch.setattr(
        recovery.preservation,
        "_destination_status",
        lambda: {"status": "HOLD_DESTINATION_UNAVAILABLE"},
    )
    monkeypatch.setattr(
        recovery.phase2b,
        "_external_volume_status",
        lambda: {"candidate_count": 0, "status": "HOLD_NO_EXTERNAL_VOLUME_MOUNTED"},
    )
    monkeypatch.setattr(
        recovery.phase2a,
        "_refs_snapshot",
        lambda _repo: {"count": 2, "sha256": "refs"},
    )

    manifest = recovery.build_recovery_manifest(
        repo=paths["repo"],
        primary_repo=paths["primary"],
        phase2b_worktree=paths["phase2b"],
        phase2b_manifest_path=phase2b_manifest_path,
        recovery_evidence_path=recovery_evidence,
        observed_at_utc="2026-08-26T00:00:00+00:00",
    )

    assert manifest["status"] == "PHASE_2B_R_PREPARED_DESTINATION_HOLD"
    assert manifest["worktree_sources"]["summary"]["worktree_count"] == 1
    assert manifest["worktree_sources"]["summary"]["preserve_file_count"] == 3
    assert manifest["authorization"]["backup_execution_authorized"] is False
    assert manifest["authorization"]["cleanup_execution_authorized"] is False
    assert all(value == 0 for value in manifest["mutations_performed"].values())
