"""Focused tests for exact MAINT-0136 Phase 2C ref cleanup."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts._lib import phase2c_ref_cleanup as cleanup

from scripts import classify_branch_disposition as classifier

pytestmark = pytest.mark.repo_only


def _phase2b(branch: str, head: str, *, integrated: bool = True) -> dict[str, object]:
    return {
        "branch": branch,
        "head_sha": head,
        "recovery": {"integrated_into_live_origin_main": integrated},
    }


def _classified(branch: str, *, candidate: bool = True) -> dict[str, object]:
    return {
        "branch": branch,
        "disposition": (
            classifier.RETIREMENT_READY_PENDING_APPROVAL
            if candidate
            else classifier.HOLD_UNIQUE_OR_UNPUBLISHED_WORK
        ),
        "reason_codes": [] if candidate else ["LOCAL_REMOTE_HEAD_MISMATCH"],
    }


def test_selects_only_integrated_classifier_candidates() -> None:
    targets, holds = cleanup._select_targets(
        phase2b_targets=[
            _phase2b("codex/remote", "a" * 40),
            _phase2b("codex/absent", "b" * 40),
            _phase2b("codex/mismatch", "c" * 40),
            _phase2b("codex/not-integrated", "d" * 40, integrated=False),
        ],
        local_heads={
            "codex/remote": "a" * 40,
            "codex/absent": "b" * 40,
            "codex/mismatch": "c" * 40,
            "codex/not-integrated": "d" * 40,
        },
        remote_heads={"codex/remote": "a" * 40},
        open_prs=[],
        worktree_branches=set(),
        classifier_receipt={
            "targets": [
                _classified("codex/remote"),
                _classified("codex/absent"),
                _classified("codex/mismatch", candidate=False),
                _classified("codex/not-integrated"),
            ]
        },
    )

    assert [row["branch"] for row in targets] == [
        "codex/absent",
        "codex/remote",
    ]
    assert [row["delete_remote_branch"] for row in targets] == [False, True]
    assert {row["branch"] for row in holds} == {
        "codex/mismatch",
        "codex/not-integrated",
    }


def test_open_pr_and_attached_worktree_are_held() -> None:
    targets, holds = cleanup._select_targets(
        phase2b_targets=[
            _phase2b("codex/open", "a" * 40),
            _phase2b("codex/attached", "b" * 40),
        ],
        local_heads={"codex/open": "a" * 40, "codex/attached": "b" * 40},
        remote_heads={},
        open_prs=[{"head_branch": "codex/open"}],
        worktree_branches={"codex/attached"},
        classifier_receipt={
            "targets": [
                _classified("codex/open"),
                _classified("codex/attached"),
            ]
        },
    )

    assert targets == []
    reasons = {row["branch"]: row["reason_codes"] for row in holds}
    assert "OPEN_PULL_REQUEST" in reasons["codex/open"]
    assert "BRANCH_ATTACHED_TO_WORKTREE" in reasons["codex/attached"]


def _manifest(tmp_path: Path) -> dict[str, object]:
    branch = "codex/merged"
    head = "a" * 40
    target = {
        "branch": branch,
        "head_sha": head,
        "delete_local_branch": True,
        "delete_remote_branch": True,
        "remote_status": "EXACT_HEAD",
        "integrated_into_live_origin_main": True,
        "off_device_recovery_status": "AUTHENTICATED_READBACK_AND_RESTORE_PASS",
        "local_operation": "GIT_BRANCH_DELETE_NORMAL",
        "remote_operation": "GIT_PUSH_ORIGIN_DELETE_EXACT_BRANCH",
    }
    archive = tmp_path / "archive"
    archive.write_bytes(b"backup")
    archive_row = {
        "path": str(archive),
        "size_bytes": 6,
        "sha256": cleanup.preservation.sha256_file(archive),
        "disposition": "RETAIN_RECOVERY_AUTHORITY",
    }
    return {
        "packet_id": cleanup.PACKET_ID,
        "status": cleanup.MANIFEST_STATUS,
        "authorization": {},
        "binding": {},
        "target_set_sha256": cleanup._canonical_sha256(
            cleanup._target_identity([target])
        ),
        "targets": [target],
        "protected_sources": {"root": str(tmp_path / "private")},
        "recovery": {"local_archives": [archive_row]},
    }


def _patch_execution(
    monkeypatch: pytest.MonkeyPatch, manifest: dict[str, object]
) -> tuple[dict[str, str], dict[str, str]]:
    branch = manifest["targets"][0]["branch"]
    head = manifest["targets"][0]["head_sha"]
    local = {branch: head, "main": "m" * 40}
    remote = {branch: head, "main": "m" * 40}
    monkeypatch.setattr(cleanup, "_local_heads", lambda _repo: dict(local))
    monkeypatch.setattr(
        cleanup.preservation, "_remote_heads", lambda _repo: dict(remote)
    )
    monkeypatch.setattr(
        cleanup,
        "_all_refs",
        lambda _repo: {
            **{f"refs/heads/{key}": value for key, value in local.items()},
            **{f"refs/remotes/origin/{key}": value for key, value in remote.items()},
        },
    )
    monkeypatch.setattr(cleanup, "_open_pull_requests", lambda _repo: [])
    monkeypatch.setattr(
        cleanup.preservation,
        "_worktree_inventory",
        lambda _repo: {"worktrees": []},
    )
    monkeypatch.setattr(cleanup.preservation, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(
        cleanup.preservation,
        "protected_source_inventory",
        lambda _root: manifest["protected_sources"],
    )
    return local, remote


def test_execute_uses_remote_delete_then_normal_local_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest(tmp_path)
    (tmp_path / "private").mkdir()
    local, remote = _patch_execution(monkeypatch, manifest)
    calls: list[tuple[str, str]] = []

    def remove_remote(_repo: Path, branch: str) -> None:
        calls.append(("remote", branch))
        remote.pop(branch)

    def remove_local(_repo: Path, branch: str) -> None:
        calls.append(("local", branch))
        local.pop(branch)

    evidence = cleanup.execute(
        repo=tmp_path,
        manifest=manifest,
        output_path=tmp_path / "evidence.json",
        expected_digest=manifest["target_set_sha256"],
        expected_local_count=1,
        expected_remote_count=1,
        exact_authorization=True,
        remove_remote=remove_remote,
        remove_local=remove_local,
    )

    assert calls == [("remote", "codex/merged"), ("local", "codex/merged")]
    assert evidence["status"] == "PASS"
    assert evidence["mutations_performed"]["archive_deletions"] == 0


def test_execute_rejects_digest_drift_without_mutation(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    calls: list[str] = []

    with pytest.raises(cleanup.RefCleanupError, match="count or digest"):
        cleanup.execute(
            repo=tmp_path,
            manifest=manifest,
            output_path=tmp_path / "evidence.json",
            expected_digest="wrong",
            expected_local_count=1,
            expected_remote_count=1,
            exact_authorization=True,
            remove_remote=lambda *_args: calls.append("remote"),
            remove_local=lambda *_args: calls.append("local"),
        )

    assert calls == []
    assert not (tmp_path / "evidence.json").exists()


def test_default_delete_commands_never_force_or_prune(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def run(args: list[str], **_kwargs: object) -> object:
        calls.append(args)
        return object()

    monkeypatch.setattr(cleanup.preservation, "_run", run)
    cleanup._remove_remote(tmp_path, "codex/merged")
    cleanup._remove_local(tmp_path, "codex/merged")

    assert calls == [
        ["git", "push", "origin", "--delete", "codex/merged"],
        ["git", "branch", "-d", "codex/merged"],
    ]
    assert all("--force" not in call and "prune" not in call for call in calls)
