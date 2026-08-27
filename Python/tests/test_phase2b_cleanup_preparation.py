"""Focused tests for read-only MAINT-0136 Phase 2B preparation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts._lib import phase2b_cleanup_preparation as preparation

pytestmark = pytest.mark.repo_only


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _inputs(tmp_path: Path) -> dict[str, Path]:
    paths = {
        name: tmp_path / name
        for name in ("repo", "primary", "phase1", "phase2a", "dirty", "old")
    }
    for path in paths.values():
        path.mkdir()
    (paths["old"] / ".ruff_cache").mkdir()
    (paths["old"] / ".ruff_cache" / "cache.bin").write_bytes(b"cache")
    phase1_manifest = tmp_path / "phase1.json"
    _write_json(
        phase1_manifest,
        {
            "task_id": preparation.TASK_ID,
            "caches": [
                {
                    "worktree_path": str(paths["old"]),
                    "relative_path": ".ruff_cache",
                    "disposition": "CACHE_CANDIDATE_NOT_AUTHORIZED",
                },
                {
                    "worktree_path": str(paths["old"]),
                    "relative_path": ".mypy_cache",
                    "disposition": "CACHE_CANDIDATE_NOT_AUTHORIZED",
                },
            ],
        },
    )
    phase2a_targets = tmp_path / "phase2a-targets.json"
    _write_json(
        phase2a_targets,
        {
            "packet_id": preparation.phase2a.PACKET_ID,
            "status": "PHASE_2A_TARGETS_FROZEN",
            "target_set_sha256": "target-set",
            "summary": {"target_count": 1, "target_bytes": 10},
            "targets": [
                {
                    "worktree_path": str(paths["old"]),
                    "relative_path": ".mypy_cache",
                }
            ],
        },
    )
    phase2a_evidence = tmp_path / "phase2a-evidence.json"
    phase2a_targets_sha256 = preparation.preservation.sha256_file(phase2a_targets)
    _write_json(
        phase2a_evidence,
        {
            "packet_id": preparation.phase2a.PACKET_ID,
            "status": "PASS",
            "target_manifest": {
                "sha256": phase2a_targets_sha256,
                "target_set_sha256": "target-set",
            },
            "execution": {
                "failure": None,
                "removed_target_count": 1,
                "removed_bytes": 10,
            },
        },
    )
    recovery = tmp_path / "recovery.json"
    _write_json(recovery, {"status": "LOCAL_RECOVERY_VERIFIED_OFF_DEVICE_HOLD"})
    paths.update(
        {
            "phase1_manifest": phase1_manifest,
            "phase2a_targets": phase2a_targets,
            "phase2a_evidence": phase2a_evidence,
            "recovery": recovery,
        }
    )
    return paths


def _inventory(paths: dict[str, Path]) -> dict[str, object]:
    return {
        "current": {
            "worktree_root": str(paths["repo"]),
            "branch": preparation.PHASE2B_BRANCH,
            "head_sha": "phase2a-head",
            "operation": "none",
            "query_failures": [],
        },
        "worktrees": [
            {
                "path": str(paths["repo"]),
                "branch": preparation.PHASE2B_BRANCH,
                "head_sha": "phase2a-head",
                "dirty_count": 1,
                "operation": "none",
                "query_status": "OK",
                "current": True,
            },
            {
                "path": str(paths["phase2a"]),
                "branch": preparation.PHASE2A_BRANCH,
                "head_sha": "phase2a-head",
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "current": False,
            },
            {
                "path": str(paths["old"]),
                "branch": "codex/old-task",
                "head_sha": "old-head",
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "current": False,
            },
        ],
    }


def _patch_live_collectors(
    monkeypatch: pytest.MonkeyPatch,
    paths: dict[str, Path],
    *,
    pull_requests: list[dict[str, object]] | None = None,
) -> None:
    monkeypatch.setattr(
        preparation.preservation,
        "_worktree_inventory",
        lambda _repo: _inventory(paths),
    )
    monkeypatch.setattr(
        preparation.preservation,
        "_pull_requests",
        lambda _repo: pull_requests or [],
    )
    monkeypatch.setattr(
        preparation.preservation,
        "_remote_heads",
        lambda _repo: {"codex/old-task": "old-head"},
    )
    monkeypatch.setattr(
        preparation,
        "_worktree_review_rows",
        lambda **_kwargs: [
            {
                "path": str(paths["old"]),
                "branch": "codex/old-task",
                "head_sha": "old-head",
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "size_bytes": 100,
                "remote_exact_head": True,
                "reachable_from_observed_origin_main": False,
                "open_pull_request": False,
                "ignored_local_state": {
                    "entry_count": 1,
                    "path_set_sha256": "ignored",
                    "paths_recorded": False,
                    "session_state_present": True,
                    "pipeline_state_present": False,
                    "protected_source_indicator_present": False,
                },
                "disposition": "RETIREMENT_REVIEW_ONLY",
                "reason_codes": ["PHASE_2B_EXECUTION_NOT_AUTHORIZED"],
            }
        ],
    )
    monkeypatch.setattr(
        preparation.preservation,
        "_destination_status",
        lambda: {"status": "HOLD_DESTINATION_UNAVAILABLE"},
    )
    monkeypatch.setattr(
        preparation,
        "_external_volume_status",
        lambda: {
            "candidate_count": 0,
            "names_recorded": False,
            "usable_destination_proven": False,
            "status": "HOLD_NO_EXTERNAL_VOLUME_MOUNTED",
        },
    )
    monkeypatch.setattr(
        preparation.preservation,
        "protected_source_inventory",
        lambda _path: {"file_count": 2, "byte_count": 20},
    )
    monkeypatch.setattr(
        preparation.preservation,
        "_disk_capacity",
        lambda _repo: {
            "total_bytes": 1000,
            "used_bytes": 830,
            "available_bytes": 170,
            "capacity_percent": 83,
        },
    )
    monkeypatch.setattr(preparation.preservation, "path_size_bytes", lambda _path: 5)
    monkeypatch.setattr(
        preparation.phase2a,
        "_refs_snapshot",
        lambda _repo: {"count": 3, "sha256": "refs"},
    )


def _build(paths: dict[str, Path]) -> dict[str, object]:
    return preparation.build_preparation_manifest(
        repo=paths["repo"],
        primary_repo=paths["primary"],
        phase1_worktree=paths["phase1"],
        phase2a_worktree=paths["phase2a"],
        dirty_worktree=paths["dirty"],
        phase1_manifest_path=paths["phase1_manifest"],
        phase2a_targets_path=paths["phase2a_targets"],
        phase2a_evidence_path=paths["phase2a_evidence"],
        recovery_evidence_path=paths["recovery"],
        observed_at_utc="2026-08-26T00:00:00+00:00",
    )


def test_preparation_proposes_only_small_phase1_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live_collectors(monkeypatch, paths)

    manifest = _build(paths)

    packet = manifest["small_cache_packet"]
    assert manifest["status"] == "PHASE_2B_PREPARED_NOT_AUTHORIZED"
    assert packet["summary"]["target_count"] == 1
    assert packet["targets"][0]["relative_path"] == ".ruff_cache"
    assert manifest["authorization"]["phase_2b_execution_authorized"] is False
    assert manifest["recommendation"]["decision"] == "DO_NOT_EXECUTE_PHASE_2B_YET"
    assert (paths["old"] / ".ruff_cache").is_dir()


def test_open_pr_cache_is_held_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live_collectors(
        monkeypatch,
        paths,
        pull_requests=[
            {
                "number": 99,
                "state": "OPEN",
                "headRefName": "codex/old-task",
                "headRefOid": "old-head",
                "url": "https://example.invalid/pr/99",
            }
        ],
    )

    manifest = _build(paths)

    packet = manifest["small_cache_packet"]
    assert packet["summary"]["target_count"] == 0
    assert packet["held_candidates"][0]["reason"] == "OPEN_PULL_REQUEST"
    assert (paths["old"] / ".ruff_cache").is_dir()


def test_preparation_rejects_reappeared_phase2a_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _inputs(tmp_path)
    _patch_live_collectors(monkeypatch, paths)
    (paths["old"] / ".mypy_cache").mkdir()

    with pytest.raises(preparation.PreparationError, match="reappeared"):
        _build(paths)

    assert (paths["old"] / ".ruff_cache").is_dir()
    assert (paths["old"] / ".mypy_cache").is_dir()


def test_cache_contract_rejects_symlink(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    outside = tmp_path / "outside"
    worktree.mkdir()
    outside.mkdir()
    (worktree / ".ruff_cache").symlink_to(outside, target_is_directory=True)

    with pytest.raises(preparation.PreparationError, match="symlink"):
        preparation._validate_cache_path(worktree, ".ruff_cache")
