"""Focused tests for the exact MAINT-0136 Phase 2A cache packet."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts._lib import phase2a_cache_cleanup as cleanup

pytestmark = pytest.mark.repo_only


def _inventory(
    repo: Path, target: Path, *, target_head: str = "target-head"
) -> dict[str, object]:
    return {
        "current": {
            "worktree_root": str(repo),
            "branch": cleanup.PHASE2A_BRANCH,
            "head_sha": "phase2-head",
        },
        "worktrees": [
            {
                "path": str(repo),
                "branch": cleanup.PHASE2A_BRANCH,
                "head_sha": "phase2-head",
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "current": True,
            },
            {
                "path": str(target),
                "branch": "codex/old-task",
                "head_sha": target_head,
                "dirty_count": 0,
                "operation": "none",
                "query_status": "OK",
                "current": False,
            },
        ],
    }


def _phase1_manifest(path: Path, target: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "task_id": cleanup.TASK_ID,
                "caches": [
                    {
                        "worktree_path": str(target),
                        "relative_path": ".mypy_cache",
                        "disposition": "CACHE_CANDIDATE_NOT_AUTHORIZED",
                    },
                    {
                        "worktree_path": str(target),
                        "relative_path": ".ruff_cache",
                        "disposition": "CACHE_CANDIDATE_NOT_AUTHORIZED",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def test_freeze_is_bounded_by_phase1_identities(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "phase2"
    target = tmp_path / "old"
    primary = tmp_path / "primary"
    predecessor = tmp_path / "phase1"
    dirty = tmp_path / "dirty"
    for path in (repo, target, primary, predecessor, dirty):
        path.mkdir()
    (target / ".mypy_cache").mkdir()
    (target / ".mypy_cache" / "cache.json").write_text("{}", encoding="utf-8")
    (target / ".ruff_cache").mkdir()
    phase1 = tmp_path / "phase1.json"
    _phase1_manifest(phase1, target)
    monkeypatch.setattr(
        cleanup.preservation,
        "_worktree_inventory",
        lambda _repo: _inventory(repo, target),
    )
    monkeypatch.setattr(cleanup.preservation, "path_size_bytes", lambda _path: 2)

    manifest = cleanup.build_target_manifest(
        repo=repo,
        primary_repo=primary,
        phase1_worktree=predecessor,
        dirty_worktree=dirty,
        phase1_manifest_path=phase1,
        observed_at_utc="2026-08-26T00:00:00+00:00",
    )

    assert manifest["summary"]["target_count"] == 1
    assert manifest["targets"][0]["relative_path"] == ".mypy_cache"
    assert manifest["target_set_sha256"] == cleanup._target_set_sha256(
        manifest["targets"]
    )
    assert (target / ".mypy_cache").is_dir()
    assert (target / ".ruff_cache").is_dir()


def test_target_contract_rejects_symlink(tmp_path: Path, symlink_factory) -> None:
    worktree = tmp_path / "worktree"
    outside = tmp_path / "outside"
    worktree.mkdir()
    outside.mkdir()
    symlink_factory(worktree / ".mypy_cache", outside, target_is_directory=True)

    with pytest.raises(cleanup.CacheCleanupError, match="symlink"):
        cleanup._validate_target_path(worktree, ".mypy_cache")


def test_execution_refuses_topology_drift_without_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "phase2"
    target = tmp_path / "old"
    repo.mkdir()
    target.mkdir()
    cache = target / ".mypy_cache"
    cache.mkdir()
    inventory = _inventory(repo, target)
    topology = cleanup._topology_rows(inventory, current_repo=repo)
    targets = [
        {
            "worktree_path": str(target),
            "relative_path": ".mypy_cache",
            "absolute_path": str(cache),
            "branch": "codex/old-task",
            "head_sha": "target-head",
            "size_bytes": 0,
            "recreation_basis": {
                "kind": "TOOL_GENERATED_MYPY_CACHE",
                "command_basis": "repository mypy invocation",
                "head_sha": "target-head",
            },
        }
    ]
    phase1_manifest = tmp_path / "phase1.json"
    phase1_manifest.write_text("{}", encoding="utf-8")
    manifest = {
        "packet_id": cleanup.PACKET_ID,
        "status": "PHASE_2A_TARGETS_FROZEN",
        "binding": {
            "repo": str(repo),
            "head_sha": "phase2-head",
            "phase1_manifest_path": str(phase1_manifest),
            "phase1_manifest_sha256": cleanup.preservation.sha256_file(phase1_manifest),
            "topology_sha256": cleanup._canonical_sha256(topology),
        },
        "targets": targets,
        "target_set_sha256": cleanup._target_set_sha256(targets),
    }
    manifest_path = tmp_path / "targets.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    drifted = _inventory(repo, target, target_head="changed-head")
    monkeypatch.setattr(
        cleanup.preservation, "_worktree_inventory", lambda _repo: drifted
    )

    with pytest.raises(cleanup.CacheCleanupError, match="topology changed"):
        cleanup.execute_manifest(repo=repo, manifest_path=manifest_path)

    assert cache.is_dir()


def test_execution_removes_only_the_exact_frozen_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "phase2"
    target = tmp_path / "old"
    primary = tmp_path / "primary"
    for path in (repo, target, primary):
        path.mkdir()
    cache = target / ".mypy_cache"
    cache.mkdir()
    (cache / "cache.json").write_text("{}", encoding="utf-8")
    sentinel = target / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    private_root = primary / "private_sources"
    private_root.mkdir()
    (private_root / "protected.bin").write_bytes(b"protected")

    inventory = _inventory(repo, target)
    topology = cleanup._topology_rows(inventory, current_repo=repo)
    recreation_basis = {
        "kind": "TOOL_GENERATED_MYPY_CACHE",
        "command_basis": "repository mypy invocation",
        "head_sha": "target-head",
    }
    targets = [
        {
            "worktree_path": str(target),
            "relative_path": ".mypy_cache",
            "absolute_path": str(cache),
            "branch": "codex/old-task",
            "head_sha": "target-head",
            "size_bytes": 7,
            "recreation_basis": recreation_basis,
        }
    ]
    phase1_manifest = tmp_path / "phase1.json"
    phase1_manifest.write_text("{}", encoding="utf-8")
    manifest = {
        "packet_id": cleanup.PACKET_ID,
        "status": "PHASE_2A_TARGETS_FROZEN",
        "binding": {
            "repo": str(repo),
            "head_sha": "phase2-head",
            "phase1_manifest_path": str(phase1_manifest),
            "phase1_manifest_sha256": cleanup.preservation.sha256_file(phase1_manifest),
            "topology_sha256": cleanup._canonical_sha256(topology),
        },
        "targets": targets,
        "target_set_sha256": cleanup._target_set_sha256(targets),
    }
    manifest_path = tmp_path / "targets.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        cleanup.preservation, "_worktree_inventory", lambda _repo: inventory
    )
    monkeypatch.setattr(cleanup.preservation, "path_size_bytes", lambda _path: 7)
    monkeypatch.setattr(cleanup.preservation, "PRIMARY_REPO", primary)
    monkeypatch.setattr(
        cleanup,
        "_refs_snapshot",
        lambda _repo: {"count": 2, "sha256": "refs-digest"},
    )
    monkeypatch.setattr(
        cleanup.preservation,
        "_disk_capacity",
        lambda _repo: {
            "total_bytes": 100,
            "used_bytes": 50,
            "available_bytes": 50,
            "capacity_percent": 50,
        },
    )

    evidence = cleanup.execute_manifest(repo=repo, manifest_path=manifest_path)

    assert evidence["status"] == "PASS"
    assert evidence["execution"]["removed_target_count"] == 1
    assert not cache.exists()
    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert (private_root / "protected.bin").read_bytes() == b"protected"
