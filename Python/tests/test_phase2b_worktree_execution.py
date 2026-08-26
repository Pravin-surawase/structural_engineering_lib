"""Focused tests for exact Phase 2B-W worktree execution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts._lib import phase2b_worktree_execution as execution

pytestmark = pytest.mark.repo_only


def _target(path: Path, branch: str, head: str) -> dict[str, object]:
    ignored = {
        "file_count": 1,
        "byte_count": 4,
        "aggregate_sha256": f"ignored-{branch}",
        "category_summary": {},
        "filenames_recorded": False,
        "content_recorded": False,
    }
    return {
        "path": str(path),
        "branch": branch,
        "head_sha": head,
        "gross_size_bytes": 100,
        "ignored_state": ignored,
        "remote_exact_head": True,
        "integrated_into_live_origin_main": False,
        "git_operation_markers": [],
        "status": "REVALIDATED_READY",
    }


def _context(tmp_path: Path) -> dict[str, object]:
    repo = tmp_path / "repo"
    primary = tmp_path / "primary"
    first = tmp_path / "first"
    second = tmp_path / "second"
    archive = tmp_path / "archive.tar.gz"
    manifest_path = tmp_path / "manifest.json"
    for path in (repo, primary, first, second):
        path.mkdir()
    archive.write_bytes(b"backup")
    manifest_path.write_text("{}\n", encoding="utf-8")
    targets = [
        _target(first, "codex/first", "a" * 40),
        _target(second, "codex/second", "b" * 40),
    ]
    return {
        "repo": repo,
        "primary_repo": primary,
        "manifest_path": manifest_path,
        "manifest": {
            "binding": {"repo": str(repo)},
            "summary": {"target_gross_bytes": 200},
        },
        "targets": targets,
        "inventory": {"worktrees": [{"path": str(path)} for path in targets]},
        "open_pull_requests": [],
        "remote_heads": {
            "codex/first": "a" * 40,
            "codex/second": "b" * 40,
        },
        "live_origin_main": "c" * 40,
        "refs": {"count": 2, "sha256": "refs"},
        "protected_sources": {"file_count": 1, "aggregate_sha256": "protected"},
        "backup": {
            "archive_path": archive,
            "archive_size_bytes": archive.stat().st_size,
            "archive_sha256": execution.preservation.sha256_file(archive),
            "remote_status": "UPLOAD_AND_AUTHENTICATED_READBACK_PASS",
            "remote_restore_status": "PASS",
            "remote_shared": False,
        },
        "disk": {"available_bytes": 10},
    }


def _patch_execution(
    monkeypatch: pytest.MonkeyPatch,
    context: dict[str, object],
    removed: list[str],
) -> None:
    monkeypatch.setattr(execution, "_fresh_target_check", lambda **_kwargs: None)
    monkeypatch.setattr(execution, "_verify_branch_preserved", lambda *_args: None)
    monkeypatch.setattr(
        execution.preservation,
        "_worktree_inventory",
        lambda _repo: {"worktrees": []},
    )
    monkeypatch.setattr(
        execution.phase2a,
        "_refs_snapshot",
        lambda _repo: context["refs"],
    )
    monkeypatch.setattr(
        execution.preservation,
        "protected_source_inventory",
        lambda _root: context["protected_sources"],
    )
    monkeypatch.setattr(
        execution.preservation,
        "_disk_capacity",
        lambda _repo: {"available_bytes": 210},
    )

    def remove(_repo: Path, path: Path) -> None:
        removed.append(str(path))
        path.rmdir()

    context["remove"] = remove


def test_execute_removes_only_exact_targets_and_preserves_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _context(tmp_path)
    removed: list[str] = []
    _patch_execution(monkeypatch, context, removed)
    output = tmp_path / "execution.json"

    evidence = execution.execute(
        context=context,
        output_path=output,
        expected_digest="digest",
        expected_count=2,
        removal_authorized=True,
        remove=context["remove"],
    )

    assert evidence["status"] == "PASS"
    assert evidence["summary"]["removed_worktree_count"] == 2
    assert evidence["summary"]["gross_removed_path_bytes"] == 200
    assert removed == [row["path"] for row in context["targets"]]
    assert evidence["after"]["refs"] == context["refs"]
    assert evidence["authorization"]["target_binding"] == {
        "task_id": execution.PACKET_ID,
        "branch": execution.EXECUTION_BRANCH,
        "head_sha": execution.PREPARATION_COMMIT,
        "actions": [
            "REMOVE_ONLY_EXACT_FROZEN_WORKTREES",
            "COMMIT_EXECUTION_EVIDENCE",
        ],
    }
    assert output.is_file()


def test_execute_rejects_missing_exact_authorization_without_mutation(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path)
    output = tmp_path / "execution.json"

    with pytest.raises(execution.WorktreeExecutionError, match="not authorized"):
        execution.execute(
            context=context,
            output_path=output,
            expected_digest="digest",
            expected_count=2,
            removal_authorized=False,
        )

    assert not output.exists()
    assert all(Path(row["path"]).is_dir() for row in context["targets"])


def test_partial_failure_records_completed_removal_and_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _context(tmp_path)
    monkeypatch.setattr(execution, "_fresh_target_check", lambda **_kwargs: None)
    monkeypatch.setattr(execution, "_verify_branch_preserved", lambda *_args: None)
    output = tmp_path / "execution.json"
    calls = 0

    def remove(_repo: Path, path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise execution.WorktreeExecutionError("simulated failure")
        path.rmdir()

    with pytest.raises(execution.WorktreeExecutionError, match="simulated failure"):
        execution.execute(
            context=context,
            output_path=output,
            expected_digest="digest",
            expected_count=2,
            removal_authorized=True,
            remove=remove,
        )

    evidence = json.loads(output.read_text(encoding="utf-8"))
    assert evidence["status"] == "PARTIAL_EXECUTION_HOLD"
    assert evidence["failure"]["completed_worktree_removals"] == 1
    assert len(evidence["removals"]) == 1
    assert Path(context["targets"][1]["path"]).is_dir()


def test_manifest_digest_mismatch_rejects_before_execution() -> None:
    manifest = {
        "packet_id": execution.PREPARATION_PACKET_ID,
        "status": execution.PREPARATION_STATUS,
        "targets": [],
        "target_identity": [],
        "target_set_sha256": execution.preparation._canonical_sha256([]),
        "summary": {"target_count": 0, "target_gross_bytes": 0},
    }

    with pytest.raises(execution.WorktreeExecutionError, match="count or digest"):
        execution._validate_manifest(
            manifest,
            expected_digest="wrong",
            expected_count=0,
        )


def test_remove_command_never_uses_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def run(args: list[str], **_kwargs: object) -> object:
        calls.append(args)
        return object()

    monkeypatch.setattr(execution.preservation, "_run", run)
    execution._remove_worktree(tmp_path, tmp_path / "target")

    assert calls == [["git", "worktree", "remove", str(tmp_path / "target")]]
    assert "--force" not in calls[0]
