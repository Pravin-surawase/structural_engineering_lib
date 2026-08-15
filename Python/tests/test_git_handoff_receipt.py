"""Regressions for the durable, fail-closed task-to-Git handoff receipt."""

from __future__ import annotations

import importlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

git_state = importlib.import_module("scripts.git_state")
receipt_module = importlib.import_module("scripts.git_handoff_receipt")


NOW = datetime(2026, 8, 15, 9, 30, tzinfo=UTC)
HEAD = "a" * 40
BASE = "b" * 40
TREE = "c" * 40
MERGE = "d" * 40


def _state(*, failed: bool = False) -> git_state.RepositoryState:
    return git_state.RepositoryState(
        schema_version=1,
        observed_at_utc=NOW.isoformat(),
        repository_root="/tmp/repo",
        worktree_root="/tmp/repo",
        git_dir="/tmp/repo/.git",
        git_common_dir="/tmp/repo/.git",
        linked_worktree=False,
        branch="codex/git-7e",
        head_sha=HEAD,
        default_base=git_state.Relation("origin/main", BASE, 1, 0, "ahead"),
        upstream=git_state.Relation("origin/codex/git-7e", HEAD, 0, 0, "equal"),
        tree=git_state.TreeState(clean=True),
        operation="none",
        operation_markers=[],
        locks=[],
        remote_freshness="NOT_CHECKED",
        derived_action="HOLD_UNKNOWN" if failed else "READY_LOCAL",
        hold_reasons=["query failed"] if failed else [],
        query_failures=(
            [git_state.QueryFailure("git status", "failed")] if failed else []
        ),
        duration_ms=1.0,
    )


def _observed(**values):
    return {
        "status": "OBSERVED",
        "query_status": "OK",
        "observed_at_utc": NOW.isoformat(),
        **values,
    }


def _evidence() -> dict:
    return {
        "remote": _observed(
            branch_state="PRESENT",
            branch_ref="refs/heads/codex/git-7e",
            head_sha=HEAD,
            default_ref="refs/heads/main",
            default_sha=BASE,
        ),
        "pull_request": _observed(
            number=751,
            state="OPEN",
            base_ref="main",
            base_sha=BASE,
            head_ref="codex/git-7e",
            head_sha=HEAD,
            merge_state="CLEAN",
            required_checks=[
                {
                    "name": "PR Gate",
                    "head_sha": HEAD,
                    "status": "COMPLETED",
                    "conclusion": "SUCCESS",
                }
            ],
        ),
        "review": _observed(base_sha=BASE, head_sha=HEAD, tree_sha=TREE),
        "integration": {"status": "NOT_APPLICABLE", "reason_code": "PR_OPEN"},
        "retention": _observed(
            owner="Main Agent",
            decision="RETAIN_FEATURE_BRANCH_AND_WORKTREE",
            holds=[],
        ),
        "task_archive": {"status": "NOT_CHECKED"},
        "authorization": {
            "status": "OBSERVED",
            "authorized_actions": ["OPEN_DRAFT_PR"],
            "prohibited_actions": ["DELETE_BRANCH", "DELETE_WORKTREE"],
            "next_action": "WAIT_FOR_EXACT_HEAD_AUDIT",
        },
    }


def _receipt(evidence: dict | None = None, *, state=None) -> dict:
    return receipt_module.build_receipt(
        task_id="GIT-7E",
        integration_owner="Main Agent",
        local_state=state or _state(),
        evidence=_evidence() if evidence is None else evidence,
        owned_paths=["scripts/git_handoff_receipt.py"],
        shared_paths=["docs/SESSION_LOG.md"],
        forbidden_paths=["refs/**"],
        now=NOW,
    )


def test_valid_receipt_round_trips_with_exact_identity(tmp_path: Path):
    receipt = _receipt()
    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")

    loaded = receipt_module.load_receipt(path)

    assert receipt["receipt_status"] == "READY"
    assert receipt["holds"] == []
    assert loaded == receipt
    assert receipt_module.validate_receipt(loaded, now=NOW) == []
    assert loaded["local"]["state"]["head_sha"] == HEAD
    assert loaded["review"]["tree_sha"] == TREE
    assert loaded["task_archive"]["is_git_retention_evidence"] is False


@pytest.mark.parametrize(
    ("evidence", "reason"),
    [
        ({}, "REMOTE_NOT_CHECKED"),
        (
            {**_evidence(), "remote": {"status": "NOT_CHECKED"}},
            "REMOTE_NOT_CHECKED",
        ),
        (
            {
                **_evidence(),
                "remote": _observed(
                    branch_state="PRESENT",
                    head_sha=HEAD,
                    observed_at_utc=(NOW - timedelta(hours=1)).isoformat(),
                ),
            },
            "REMOTE_STALE_EVIDENCE",
        ),
        (
            {
                **_evidence(),
                "remote": {
                    **_observed(branch_state="PRESENT", head_sha=HEAD),
                    "query_status": "FAILED",
                },
            },
            "REMOTE_QUERY_FAILED",
        ),
    ],
)
def test_missing_not_checked_stale_and_query_failed_evidence_hold(evidence, reason):
    receipt = _receipt(evidence)

    assert receipt["receipt_status"] == "HOLD"
    assert reason in receipt["holds"]


def test_failed_git_state_is_unknown_even_when_hosted_evidence_is_green():
    receipt = _receipt(state=_state(failed=True))

    assert receipt["receipt_status"] == "HOLD"
    assert "LOCAL_STATE_UNKNOWN" in receipt["holds"]


def test_dirty_or_interrupted_local_state_holds_even_when_queries_succeed():
    state = _state()
    state.tree = git_state.TreeState(clean=False, modified_paths=["owned.py"])
    state.derived_action = "HOLD_DIRTY"

    receipt = _receipt(state=state)

    assert receipt["receipt_status"] == "HOLD"
    assert "LOCAL_HOLD_DIRTY" in receipt["holds"]


def test_not_applicable_requires_a_reason_and_never_replaces_unknown():
    evidence = _evidence()
    evidence["review"] = {"status": "NOT_APPLICABLE"}

    receipt = _receipt(evidence)

    assert receipt["review"]["status"] == "UNKNOWN"
    assert "REVIEW_NOT_APPLICABLE_WITHOUT_REASON" in receipt["holds"]


def test_exact_head_and_check_contradictions_fail_closed():
    evidence = _evidence()
    evidence["pull_request"] = {
        **evidence["pull_request"],
        "head_sha": "e" * 40,
    }

    receipt = _receipt(evidence)

    assert receipt["receipt_status"] == "HOLD"
    assert "PULL_REQUEST_HEAD_MISMATCH" in receipt["holds"]
    assert "REVIEWED_HEAD_MISMATCH" in receipt["holds"]
    assert "REQUIRED_CHECK_HEAD_MISMATCH" in receipt["holds"]


def test_squash_merge_needs_tree_equivalence_and_does_not_grant_retirement():
    evidence = _evidence()
    evidence["integration"] = _observed(
        method="squash",
        merge_sha=MERGE,
        reviewed_tree_sha=TREE,
        merged_tree_sha="e" * 40,
    )
    evidence["retention"] = {"status": "NOT_CHECKED"}

    receipt = _receipt(evidence)

    assert "SQUASH_TREE_EQUIVALENCE_UNKNOWN" in receipt["holds"]
    assert "RETENTION_NOT_CHECKED" in receipt["holds"]
    assert receipt["receipt_status"] == "HOLD"


def test_stored_hash_or_identity_tampering_is_rejected():
    receipt = _receipt()
    receipt["local"]["state"]["head_sha"] = "f" * 40

    errors = receipt_module.validate_receipt(receipt, now=NOW)

    assert "LOCAL_STATE_HASH_MISMATCH" in errors
    assert "REMOTE_HEAD_MISMATCH" in errors


def test_stored_observed_evidence_expires_instead_of_remaining_authority():
    receipt = _receipt()

    errors = receipt_module.validate_receipt(receipt, now=NOW + timedelta(hours=1))

    assert "REMOTE_STALE_EVIDENCE" in errors
    assert "PULL_REQUEST_STALE_EVIDENCE" in errors


def test_receipt_module_has_no_independent_git_or_network_reader():
    source = Path(receipt_module.__file__).read_text(encoding="utf-8")

    assert "subprocess" not in source
    assert "urlopen" not in source
    assert "requests." not in source
    assert "collect_repository_state" in source
