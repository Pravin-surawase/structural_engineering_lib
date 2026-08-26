"""Focused tests for fail-closed cleanup preservation evidence."""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

cleanup = importlib.import_module("scripts._lib.cleanup_preservation")


def _worktree(path: Path, *, dirty_count: int = 0) -> dict[str, object]:
    return {"path": str(path), "dirty_count": dirty_count}


def test_worktree_dispositions_fail_closed(tmp_path: Path):
    current = tmp_path / "current"
    primary = tmp_path / "primary"
    dirty = tmp_path / "dirty"
    other = tmp_path / "other"

    assert (
        cleanup.classify_worktree(
            _worktree(current),
            current_path=current,
            primary_path=primary,
            dirty_path=dirty,
        )[0]
        == "RETAIN_CURRENT_TASK"
    )
    assert (
        cleanup.classify_worktree(
            _worktree(primary),
            current_path=current,
            primary_path=primary,
            dirty_path=dirty,
        )[0]
        == "RETAIN_INTEGRATION_ANCHOR"
    )
    assert (
        cleanup.classify_worktree(
            _worktree(dirty, dirty_count=1),
            current_path=current,
            primary_path=primary,
            dirty_path=dirty,
        )[0]
        == "RETAIN_DIRTY_UNIQUE"
    )
    assert (
        cleanup.classify_worktree(
            _worktree(other),
            current_path=current,
            primary_path=primary,
            dirty_path=dirty,
        )[0]
        == "HOLD_OWNER_RETENTION_EVIDENCE_REQUIRED"
    )


def test_cache_candidates_exclude_primary_current_and_dirty(tmp_path: Path):
    current = tmp_path / "current"
    primary = tmp_path / "primary"
    other = tmp_path / "other"

    assert (
        cleanup.classify_cache(
            worktree_path=primary,
            current_path=current,
            primary_path=primary,
            dirty=False,
        )[0]
        == "RETAIN_PRIMARY_RUNTIME"
    )
    assert (
        cleanup.classify_cache(
            worktree_path=current,
            current_path=current,
            primary_path=primary,
            dirty=False,
        )[0]
        == "RETAIN_CURRENT_TASK_RUNTIME"
    )
    assert (
        cleanup.classify_cache(
            worktree_path=other,
            current_path=current,
            primary_path=primary,
            dirty=True,
        )[0]
        == "RETAIN_DIRTY_LANE_RUNTIME"
    )
    assert (
        cleanup.classify_cache(
            worktree_path=other,
            current_path=current,
            primary_path=primary,
            dirty=False,
        )[0]
        == "CACHE_CANDIDATE_NOT_AUTHORIZED"
    )


def test_protected_source_digest_is_deterministic_and_excludes_archives(
    tmp_path: Path,
):
    private_root = tmp_path / "private_sources"
    (private_root / "library").mkdir(parents=True)
    (private_root / "library" / "one.bin").write_bytes(b"one")
    (private_root / "library" / "two.bin").write_bytes(b"two")
    archive = private_root / "worktree_cleanup_archives" / "packet"
    archive.mkdir(parents=True)
    (archive / "ignored.bundle").write_bytes(b"first")
    pycache = private_root / "library" / "__pycache__"
    pycache.mkdir()
    (pycache / "ignored.pyc").write_bytes(b"compiled")

    first = cleanup.protected_source_inventory(private_root)
    (archive / "ignored.bundle").write_bytes(b"second")
    second = cleanup.protected_source_inventory(private_root)

    assert first == second
    assert first["file_count"] == 2
    assert first["byte_count"] == 6
    assert first["aggregate_sha256"] != hashlib.sha256(b"").hexdigest()
    assert first["filenames_recorded"] is False
    assert first["content_recorded"] is False
