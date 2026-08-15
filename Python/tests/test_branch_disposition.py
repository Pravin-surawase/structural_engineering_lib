"""Outcome tests for the inspection-only branch disposition classifier."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

classifier = importlib.import_module("scripts.classify_branch_disposition")


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    command_env = os.environ.copy()
    command_env.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    if env:
        command_env.update(env)
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
        env=command_env,
    )


def _write(repo: Path, name: str, content: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _commit(
    repo: Path,
    name: str,
    content: str,
    message: str,
    *,
    committed_at: str | None = None,
) -> str:
    _write(repo, name, content)
    _git(repo, "add", name)
    env = None
    if committed_at:
        env = {
            "GIT_AUTHOR_DATE": committed_at,
            "GIT_COMMITTER_DATE": committed_at,
        }
    _git(repo, "commit", "-m", message, env=env)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _repo(tmp_path: Path, *, old: bool = False) -> Path:
    repo = tmp_path / "repo"
    _git(tmp_path, "init", "-b", "main", str(repo))
    _git(repo, "config", "user.name", "GIT-7D2 Test")
    _git(repo, "config", "user.email", "git-7d2@example.invalid")
    _commit(
        repo,
        "tracked.txt",
        "base\n",
        "initial",
        committed_at="2000-01-01T00:00:00+0000" if old else None,
    )
    return repo


def _sha(repo: Path, ref: str) -> str:
    return _git(repo, "rev-parse", f"{ref}^{{commit}}").stdout.strip()


def _evidence(
    repo: Path,
    branch: str,
    *,
    pr_status: str = "NONE_OPEN",
    retention_status: str = "NO_RETENTION",
    remote_status: str = "ABSENT",
    remote_sha: str | None = None,
    default_ref: str = "main",
) -> dict:
    head_sha = _sha(repo, branch)
    remote_ref = {
        "status": remote_status,
        "ref": f"refs/heads/{branch}",
        "sha": remote_sha or head_sha,
    }
    if remote_status == "ABSENT":
        remote_ref = {"status": "ABSENT", "ref": f"refs/heads/{branch}"}
    observed = "2026-08-15T00:00:00Z"
    return {
        "schema_version": 1,
        "remote_freshness": {
            "status": "OBSERVED_AT",
            "observed_at_utc": observed,
            "default_ref": default_ref,
            "default_sha": _sha(repo, default_ref),
        },
        "branches": {
            branch: {
                "owner": "GIT-7D2-test",
                "remote_ref": remote_ref,
                "pull_requests": {
                    "status": pr_status,
                    "observed_at_utc": observed,
                    "head_sha": head_sha,
                    "items": ([{"number": 1}] if pr_status != "NONE_OPEN" else []),
                },
                "retention": {
                    "status": retention_status,
                    "observed_at_utc": observed,
                    "head_sha": head_sha,
                    "reason": (
                        "forensic evidence" if retention_status == "RETAIN" else None
                    ),
                },
            }
        },
    }


def _classify(
    repo: Path,
    branch: str,
    evidence: dict | None = None,
    *,
    default_ref: str = "main",
) -> dict:
    receipt = classifier.classify_repository(
        repo=repo,
        branches=[branch],
        evidence=evidence,
        default_ref=default_ref,
        now=datetime(2026, 8, 15, tzinfo=UTC),
    )
    return receipt["targets"][0]


def test_attached_and_dirty_worktrees_have_distinct_reasoned_holds(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "switch", "-c", "attached")
    evidence = _evidence(repo, "attached")

    attached = _classify(repo, "attached", evidence)
    _write(repo, "dirty.txt", "owned but not clean\n")
    dirty = _classify(repo, "attached", evidence)

    assert attached["disposition"] == classifier.HOLD_ATTACHED_OR_DIRTY
    assert attached["reason_codes"] == ["ATTACHED_WORKTREE"]
    assert dirty["disposition"] == classifier.HOLD_ATTACHED_OR_DIRTY
    assert dirty["reason_codes"] == ["DIRTY_WORKTREE"]


def test_open_pr_unique_work_retention_and_ready_candidate_are_distinct(
    tmp_path: Path,
):
    repo = _repo(tmp_path)
    for branch in ("open-pr", "retained", "ready"):
        _git(repo, "branch", branch)

    _git(repo, "switch", "-c", "unique")
    _commit(repo, "unique.txt", "unique\n", "unique work")
    _git(repo, "switch", "main")

    open_pr = _classify(repo, "open-pr", _evidence(repo, "open-pr", pr_status="OPEN"))
    unique = _classify(repo, "unique", _evidence(repo, "unique"))
    retained = _classify(
        repo,
        "retained",
        _evidence(repo, "retained", retention_status="RETAIN"),
    )
    ready = _classify(repo, "ready", _evidence(repo, "ready"))

    assert open_pr["disposition"] == classifier.HOLD_OPEN_OR_DEPENDENT_PR
    assert unique["disposition"] == classifier.HOLD_UNIQUE_OR_UNPUBLISHED_WORK
    assert retained["disposition"] == classifier.HOLD_EVIDENCE_RETENTION
    assert ready["disposition"] == classifier.RETIREMENT_READY_PENDING_APPROVAL
    assert ready["status"] == "CANDIDATE"
    assert "separate exact-target authorization" in ready["next_action"]


def test_squash_patch_equivalence_requires_review(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "switch", "-c", "squash-source")
    _commit(repo, "tracked.txt", "integrated\n", "feature patch")
    _git(repo, "switch", "main")
    _commit(repo, "tracked.txt", "integrated\n", "squashed integration")

    result = _classify(repo, "squash-source", _evidence(repo, "squash-source"))

    assert result["facts"]["ahead_commit_count"] == 1
    assert result["facts"]["cherry"]["unique_patch_count"] == 0
    assert result["facts"]["cherry"]["equivalent_patch_count"] == 1
    assert result["disposition"] == classifier.PATCH_EQUIVALENT_REVIEW_REQUIRED
    assert result["status"] == "REVIEW_REQUIRED"


def test_git_query_failure_is_unknown_not_integrated_or_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")
    evidence = _evidence(repo, "candidate")
    real_run = classifier.GitRunner.run

    def fail_rev_list(self, args, **kwargs):
        if args and args[0] == "rev-list":
            self.failures.append(
                classifier.QueryFailure("git " + " ".join(args), "simulated failure")
            )
            return None
        return real_run(self, args, **kwargs)

    monkeypatch.setattr(classifier.GitRunner, "run", fail_rev_list)
    result = _classify(repo, "candidate", evidence)

    assert result["status"] == "UNKNOWN"
    assert result["disposition"] == classifier.HOLD_UNKNOWN_OWNER
    assert "GIT_QUERY_FAILED" in result["reason_codes"]
    assert result["facts"]["reachable_from_default"] is None


def test_age_is_metadata_and_never_sufficient_authority(tmp_path: Path):
    repo = _repo(tmp_path, old=True)
    _git(repo, "branch", "very-old")

    result = _classify(repo, "very-old")

    assert result["facts"]["age_days"] > 9_000
    assert result["facts"]["age_is_authority"] is False
    assert result["status"] == "UNKNOWN"
    assert result["disposition"] != classifier.RETIREMENT_READY_PENDING_APPROVAL
    assert "OWNER_UNKNOWN" in result["reason_codes"]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _filesystem_snapshot(repo: Path) -> dict[str, tuple[int, str]]:
    snapshot: dict[str, tuple[int, str]] = {}
    for path in sorted(repo.rglob("*")):
        if path.is_file():
            snapshot[str(path.relative_to(repo))] = (
                path.stat().st_mtime_ns,
                _digest(path),
            )
    return snapshot


def test_classifier_does_not_mutate_files_refs_index_or_config(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")
    evidence = _evidence(repo, "candidate")
    refs_before = _git(repo, "for-each-ref", "--format=%(refname) %(objectname)").stdout
    config_before = (repo / ".git" / "config").read_bytes()
    index = repo / ".git" / "index"
    index_before = (index.stat().st_mtime_ns, index.read_bytes())
    files_before = _filesystem_snapshot(repo)

    result = _classify(repo, "candidate", evidence)

    refs_after = _git(repo, "for-each-ref", "--format=%(refname) %(objectname)").stdout
    assert result["disposition"] == classifier.RETIREMENT_READY_PENDING_APPROVAL
    assert refs_after == refs_before
    assert (repo / ".git" / "config").read_bytes() == config_before
    assert (index.stat().st_mtime_ns, index.read_bytes()) == index_before
    assert _filesystem_snapshot(repo) == files_before


def test_not_checked_remote_freshness_is_explicit_unknown(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")

    receipt = classifier.classify_repository(
        repo=repo,
        branches=["candidate"],
        default_ref="main",
    )
    encoded = json.dumps(receipt)

    assert receipt["remote_freshness"] == {"status": "NOT_CHECKED"}
    assert receipt["targets"][0]["status"] == "UNKNOWN"
    assert "OBSERVED_AT" not in encoded
    assert classifier.RETIREMENT_READY_PENDING_APPROVAL not in encoded


def test_stale_caller_evidence_is_unknown(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")
    evidence = _evidence(repo, "candidate")
    evidence["remote_freshness"]["observed_at_utc"] = "2026-08-14T00:00:00Z"

    result = _classify(repo, "candidate", evidence)

    assert result["status"] == "UNKNOWN"
    assert "REMOTE_OBSERVATION_STALE" in result["reason_codes"]
    assert result["disposition"] != classifier.RETIREMENT_READY_PENDING_APPROVAL


def test_remote_absence_and_retention_evidence_are_exact_and_fresh(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")
    wrong_remote = _evidence(repo, "candidate")
    wrong_remote["branches"]["candidate"]["remote_ref"]["ref"] = "refs/heads/different"
    stale_retention = _evidence(repo, "candidate")
    stale_retention["branches"]["candidate"]["retention"][
        "observed_at_utc"
    ] = "2026-08-14T00:00:00Z"

    wrong_remote_result = _classify(repo, "candidate", wrong_remote)
    stale_retention_result = _classify(repo, "candidate", stale_retention)

    assert wrong_remote_result["status"] == "UNKNOWN"
    assert "REMOTE_BRANCH_REF_MISMATCH" in wrong_remote_result["reason_codes"]
    assert stale_retention_result["status"] == "UNKNOWN"
    assert "RETENTION_OBSERVATION_STALE" in stale_retention_result["reason_codes"]


def test_default_branch_is_never_a_retirement_candidate(tmp_path: Path):
    repo = _repo(tmp_path)
    main_result = _classify(repo, "main", _evidence(repo, "main"))
    _git(repo, "branch", "develop")
    develop_result = _classify(
        repo,
        "develop",
        _evidence(repo, "develop", default_ref="develop"),
        default_ref="develop",
    )

    for result in (main_result, develop_result):
        assert result["disposition"] == classifier.HOLD_EVIDENCE_RETENTION
        assert result["reason_codes"] == ["DEFAULT_BRANCH_INTEGRATION_ANCHOR"]
        assert result["identity"]["is_default_branch"] is True


def test_git_commands_are_local_read_only_and_cli_has_no_action_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")
    evidence = _evidence(repo, "candidate")
    real_run = subprocess.run
    commands: list[list[str]] = []

    def observe(*args, **kwargs):
        command = args[0] if args else kwargs.get("args")
        if isinstance(command, list):
            commands.append(command)
        return real_run(*args, **kwargs)

    monkeypatch.setattr(classifier.subprocess, "run", observe)
    monkeypatch.setattr(
        importlib.import_module("scripts.git_state").subprocess, "run", observe
    )
    result = _classify(repo, "candidate", evidence)

    forbidden = {
        "fetch",
        "prune",
        "push",
        "update-ref",
        "checkout",
        "switch",
        "reset",
        "stash",
        "rebase",
        "clean",
        "config",
    }
    assert result["disposition"] == classifier.RETIREMENT_READY_PENDING_APPROVAL
    assert commands
    assert all(command[0] == "git" for command in commands)
    assert not any(forbidden.intersection(command[3:]) for command in commands)
    worktree_commands = [command for command in commands if "worktree" in command]
    assert all(command[3:5] == ["worktree", "list"] for command in worktree_commands)

    help_result = real_run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "classify_branch_disposition.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--delete" not in help_result.stdout
    assert "--execute" not in help_result.stdout
    assert "--apply" not in help_result.stdout


def test_cli_emits_machine_readable_receipt(tmp_path: Path):
    repo = _repo(tmp_path)
    _git(repo, "branch", "candidate")
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "classify_branch_disposition.py"),
        "--repo",
        str(repo),
        "--default-ref",
        "main",
        "--branch",
        "candidate",
        "--json",
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    assert payload["schema_version"] == 1
    assert payload["mutation_policy"] == "INSPECTION_ONLY"
    assert payload["authorization"] == "SEPARATE_EXACT_TARGET_APPROVAL_REQUIRED"
    assert payload["targets"][0]["status"] == "UNKNOWN"
