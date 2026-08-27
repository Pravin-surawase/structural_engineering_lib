"""Build fail-closed cleanup preservation and recovery evidence.

This helper is intentionally inspection-first. It records worktrees, refs,
large per-worktree caches, protected-source aggregates, and recovery proof. It
does not remove files, worktrees, refs, caches, or branches, and it never turns
an old cleanup decision into current authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

SCHEMA_VERSION = 1
TASK_ID = "MAINT-0136"
PRIMARY_REPO = Path("/Users/pravinsurawase/VS_code_project/structural_engineering_lib")
DIRTY_WORKTREE = Path(
    "/Users/pravinsurawase/.codex/worktrees/e54a/structural_engineering_lib"
)
DIRTY_BASE_SHA = "0fdb48edbb73114288feb8a246d6f30b80ac4d95"
CACHE_PATHS = (
    "react_app/node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "Python/.pytest_cache",
    "react_app/dist",
    "react_app/.vite",
)


class EvidenceError(RuntimeError):
    """Raised when required preservation evidence cannot be collected."""


def _environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        }
    )
    return env


def _run(
    args: Sequence[str],
    *,
    cwd: Path,
    timeout: float = 120.0,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        env=_environment(),
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise EvidenceError(f"{' '.join(args)} failed: {detail}")
    return result


def _json_command(args: Sequence[str], *, cwd: Path, timeout: float = 120.0) -> Any:
    result = _run(args, cwd=cwd, timeout=timeout)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"{' '.join(args)} returned invalid JSON: {exc}") from exc


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_size_bytes(path: Path) -> int:
    """Return the on-disk size measured by the platform du utility."""
    result = _run(["du", "-sk", "--", str(path)], cwd=path.parent)
    try:
        kib = int(result.stdout.split()[0])
    except (IndexError, ValueError) as exc:
        raise EvidenceError(f"could not parse du output for {path}") from exc
    return kib * 1024


def classify_worktree(
    item: dict[str, Any],
    *,
    current_path: Path,
    primary_path: Path,
    dirty_path: Path,
) -> tuple[str, list[str]]:
    """Return a preservation-only disposition for one live worktree."""
    path = Path(item["path"])
    if path == current_path:
        return "RETAIN_CURRENT_TASK", ["ACTIVE_PHASE_1_LANE"]
    if path == primary_path:
        return "RETAIN_INTEGRATION_ANCHOR", [
            "PRIMARY_CHECKOUT",
            "IGNORED_SOURCES_OWNER",
        ]
    if path == dirty_path or item.get("dirty_count", 0):
        return "RETAIN_DIRTY_UNIQUE", ["UNCOMMITTED_WORK", "PATCH_RECOVERY_REQUIRED"]
    return "HOLD_OWNER_RETENTION_EVIDENCE_REQUIRED", [
        "NO_CURRENT_OWNER_RETENTION_PROOF",
        "PHASE_2_NOT_AUTHORIZED",
    ]


def classify_cache(
    *,
    worktree_path: Path,
    current_path: Path,
    primary_path: Path,
    dirty: bool,
) -> tuple[str, list[str]]:
    """Return a non-destructive cache disposition."""
    if worktree_path == primary_path:
        return "RETAIN_PRIMARY_RUNTIME", ["PRIMARY_RUNTIME_DEPENDENCY"]
    if worktree_path == current_path:
        return "RETAIN_CURRENT_TASK_RUNTIME", ["ACTIVE_PHASE_1_LANE"]
    if dirty:
        return "RETAIN_DIRTY_LANE_RUNTIME", ["DIRTY_LANE_PRESERVATION"]
    return "CACHE_CANDIDATE_NOT_AUTHORIZED", [
        "CLEAN_INACTIVE_WORKTREE",
        "PHASE_2_NOT_AUTHORIZED",
    ]


def protected_source_inventory(private_root: Path) -> dict[str, Any]:
    """Digest protected sources without exposing filenames or content."""
    aggregate = hashlib.sha256()
    file_count = 0
    byte_count = 0
    excluded_roots = {"worktree_cleanup_archives", "__pycache__"}
    for path in sorted(private_root.rglob("*")):
        relative = path.relative_to(private_root)
        if any(part in excluded_roots for part in relative.parts) or not path.is_file():
            continue
        data_digest = sha256_file(path)
        size = path.stat().st_size
        aggregate.update(relative.as_posix().encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(str(size).encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(data_digest.encode("ascii"))
        aggregate.update(b"\n")
        file_count += 1
        byte_count += size
    return {
        "root": str(private_root),
        "file_count": file_count,
        "byte_count": byte_count,
        "aggregate_sha256": aggregate.hexdigest(),
        "filenames_recorded": False,
        "content_recorded": False,
        "excluded_from_digest": [
            "worktree_cleanup_archives/**",
            "**/__pycache__/**",
        ],
    }


def verify_private_library_snapshot(
    *, private_root: Path, runtime: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify an exact temporary copy without changing the canonical database."""
    before = protected_source_inventory(private_root)
    source_library = private_root / "is_code_library"
    with tempfile.TemporaryDirectory(
        prefix="maint-0136-private-verify-", dir=private_root
    ) as temp_root:
        snapshot = Path(temp_root)
        shutil.copytree(source_library, snapshot, dirs_exist_ok=True)
        verifier = _run(
            [
                str(runtime),
                str(source_library / "library.py"),
                "--library-root",
                str(snapshot),
                "verify",
            ],
            cwd=private_root.parent,
            timeout=180.0,
        )
        summary = verifier.stdout.strip().splitlines()[-1]
        summary = summary.rsplit(" database=", 1)[0]
    after = protected_source_inventory(private_root)
    if before != after:
        raise EvidenceError(
            "canonical protected-source aggregate changed during verification"
        )
    return after, {
        "status": "PASS",
        "target": "EXACT_TEMPORARY_SNAPSHOT",
        "summary": summary,
        "canonical_aggregate_unchanged": True,
        "temporary_snapshot_removed": True,
    }


def restore_sample(
    *,
    bundle: Path,
    patch: Path,
    source_log: Path,
    base_sha: str,
) -> dict[str, Any]:
    """Prove that the recovery bundle and dirty patch reproduce the source."""
    with tempfile.TemporaryDirectory(prefix="maint-0136-restore-") as temp_root:
        restored = Path(temp_root) / "restored"
        _run(["git", "clone", "--quiet", str(bundle), str(restored)], cwd=bundle.parent)
        _run(["git", "checkout", "--quiet", base_sha], cwd=restored)
        _run(["git", "apply", "--check", str(patch)], cwd=restored)
        _run(["git", "apply", str(patch)], cwd=restored)
        _run(["git", "fsck", "--full", "--no-dangling"], cwd=restored)
        restored_log = restored / "docs" / "SESSION_LOG.md"
        source_sha = sha256_file(source_log)
        restored_sha = sha256_file(restored_log)
        if source_sha != restored_sha:
            raise EvidenceError("restored dirty session log does not match source")
        checked_out_base = _run(
            ["git", "rev-parse", "HEAD"], cwd=restored
        ).stdout.strip()
    return {
        "checked_out_base": checked_out_base,
        "patch_apply_check": "PASS",
        "patch_apply": "PASS",
        "source_session_log_sha256": source_sha,
        "restored_session_log_sha256": restored_sha,
        "content_match": True,
        "git_fsck": "PASS",
        "temporary_restore_removed": True,
    }


def _worktree_inventory(repo: Path) -> dict[str, Any]:
    return _json_command(
        [sys.executable, str(repo / "scripts/git_state.py"), "--json", "--worktrees"],
        cwd=repo,
        timeout=180.0,
    )


def _remote_heads(repo: Path) -> dict[str, str]:
    result = _run(["git", "ls-remote", "--heads", "origin"], cwd=repo)
    heads: dict[str, str] = {}
    for line in result.stdout.splitlines():
        sha, ref = line.split("\t", 1)
        heads[ref.removeprefix("refs/heads/")] = sha
    return heads


def _pull_requests(repo: Path) -> list[dict[str, Any]]:
    fields = (
        "number,state,isDraft,headRefName,baseRefName,headRefOid,mergeCommit,"
        "mergedAt,closedAt,title,url,author"
    )
    payload = _json_command(
        ["gh", "pr", "list", "--state", "all", "--limit", "1000", "--json", fields],
        cwd=repo,
        timeout=180.0,
    )
    if not isinstance(payload, list):
        raise EvidenceError("gh pr list did not return an array")
    return payload


def _local_branches(repo: Path) -> dict[str, dict[str, Any]]:
    template = "%(refname:strip=2)%09%(objectname)%09%(upstream:short)"
    result = _run(
        ["git", "for-each-ref", f"--format={template}", "refs/heads"], cwd=repo
    )
    branches: dict[str, dict[str, Any]] = {}
    for line in result.stdout.splitlines():
        name, sha, upstream = (line.split("\t") + [""])[:3]
        branches[name] = {"sha": sha, "upstream": upstream or None}
    return branches


def _is_ancestor(repo: Path, sha: str, default_ref: str) -> bool:
    result = _run(
        ["git", "merge-base", "--is-ancestor", sha, default_ref],
        cwd=repo,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise EvidenceError(f"could not compare {sha} with {default_ref}")
    return result.returncode == 0


def _branch_inventory(
    *,
    repo: Path,
    worktrees: list[dict[str, Any]],
    remote_heads: dict[str, str],
    pull_requests: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    local = _local_branches(repo)
    worktrees_by_branch: dict[str, list[dict[str, Any]]] = {}
    for item in worktrees:
        branch = item.get("branch")
        if branch and branch != "DETACHED":
            worktrees_by_branch.setdefault(branch, []).append(
                {
                    "path": item["path"],
                    "head_sha": item.get("head_sha"),
                    "dirty_count": item.get("dirty_count"),
                    "derived_action": item.get("derived_action"),
                }
            )
    prs_by_branch: dict[str, list[dict[str, Any]]] = {}
    for item in pull_requests:
        prs_by_branch.setdefault(item["headRefName"], []).append(item)
    rows: list[dict[str, Any]] = []
    for name in sorted(set(local) | set(remote_heads)):
        local_item = local.get(name)
        remote_sha = remote_heads.get(name)
        attached = worktrees_by_branch.get(name, [])
        if name == "main":
            disposition = "RETAIN_DEFAULT_BRANCH"
            reasons = ["DEFAULT_BRANCH"]
        elif name == "codex/maint-0136-cleanup-preservation":
            disposition = "RETAIN_CURRENT_TASK"
            reasons = ["ACTIVE_PHASE_1_LANE"]
        else:
            disposition = "HOLD_OWNER_RETENTION_EVIDENCE_REQUIRED"
            reasons = ["NO_CURRENT_OWNER_RETENTION_PROOF", "PHASE_2_NOT_AUTHORIZED"]
            if attached:
                reasons.append("ATTACHED_WORKTREE")
            if any(pr["state"] == "OPEN" for pr in prs_by_branch.get(name, [])):
                reasons.append("OPEN_PULL_REQUEST")
        sha = local_item["sha"] if local_item else remote_sha
        rows.append(
            {
                "name": name,
                "local": local_item,
                "remote": (
                    {"status": "PRESENT", "sha": remote_sha}
                    if remote_sha
                    else {"status": "ABSENT", "sha": None}
                ),
                "attached_worktrees": attached,
                "pull_requests": sorted(
                    prs_by_branch.get(name, []), key=lambda item: item["number"]
                ),
                "reachable_from_observed_origin_main": (
                    _is_ancestor(repo, sha, "origin/main") if sha else None
                ),
                "disposition": disposition,
                "reason_codes": reasons,
            }
        )
    return rows


def _destination_status() -> dict[str, Any]:
    result = subprocess.run(
        ["tmutil", "destinationinfo"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30.0,
    )
    available = result.returncode == 0 and "No destinations configured" not in (
        result.stdout + result.stderr
    )
    return {
        "status": "AVAILABLE" if available else "HOLD_DESTINATION_UNAVAILABLE",
        "tmutil_exit_code": result.returncode,
        "same_disk_artifacts_are_disaster_recovery": False,
    }


def _disk_capacity(repo: Path) -> dict[str, int]:
    result = _run(["df", "-k", str(repo)], cwd=repo)
    fields = result.stdout.splitlines()[-1].split()
    return {
        "total_bytes": int(fields[1]) * 1024,
        "used_bytes": int(fields[2]) * 1024,
        "available_bytes": int(fields[3]) * 1024,
        "capacity_percent": int(fields[4].removesuffix("%")),
    }


def build_evidence(
    *,
    repo: Path,
    primary_repo: Path,
    dirty_worktree: Path,
    recovery_dir: Path,
    observed_at_utc: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Collect and return the manifest and recovery evidence payloads."""
    inventory = _worktree_inventory(repo)
    worktrees = inventory["worktrees"]
    current_path = repo.resolve()
    worktree_rows: list[dict[str, Any]] = []
    cache_rows: list[dict[str, Any]] = []
    for item in worktrees:
        path = Path(item["path"])
        disposition, reasons = classify_worktree(
            item,
            current_path=current_path,
            primary_path=primary_repo,
            dirty_path=dirty_worktree,
        )
        row = dict(item)
        row.update(
            {
                "size_bytes": path_size_bytes(path),
                "disposition": disposition,
                "reason_codes": reasons,
            }
        )
        worktree_rows.append(row)
        for relative in CACHE_PATHS:
            cache_path = path / relative
            if not cache_path.exists():
                continue
            cache_disposition, cache_reasons = classify_cache(
                worktree_path=path,
                current_path=current_path,
                primary_path=primary_repo,
                dirty=bool(item.get("dirty_count")),
            )
            cache_rows.append(
                {
                    "worktree_path": str(path),
                    "relative_path": relative,
                    "size_bytes": path_size_bytes(cache_path),
                    "disposition": cache_disposition,
                    "reason_codes": cache_reasons,
                }
            )

    bundle = recovery_dir / "structural-engineering-lib-all-refs.bundle"
    patch = recovery_dir / "e54a-session-log.patch"
    source_log = dirty_worktree / "docs" / "SESSION_LOG.md"
    bundle_verify = _run(["git", "bundle", "verify", str(bundle)], cwd=repo)
    bundle_heads = _run(["git", "bundle", "list-heads", str(bundle)], cwd=repo)
    restore = restore_sample(
        bundle=bundle,
        patch=patch,
        source_log=source_log,
        base_sha=DIRTY_BASE_SHA,
    )
    private_root = primary_repo / "private_sources"
    private_inventory, private_verifier = verify_private_library_snapshot(
        private_root=private_root,
        runtime=Path(sys.executable),
    )
    tracked_private = _run(
        ["git", "ls-files", "--", "private_sources"], cwd=primary_repo
    ).stdout.splitlines()
    ignored = _run(
        ["git", "check-ignore", "private_sources"], cwd=primary_repo
    ).stdout.strip()
    destination = _destination_status()
    recovery = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "observed_at_utc": observed_at_utc,
        "status": "LOCAL_RECOVERY_VERIFIED_OFF_DEVICE_HOLD",
        "recovery_tier": "SAME_DISK_ONLY",
        "archive_directory": str(recovery_dir),
        "git_bundle": {
            "path": str(bundle),
            "size_bytes": bundle.stat().st_size,
            "sha256": sha256_file(bundle),
            "verification": "PASS" if bundle_verify.returncode == 0 else "FAIL",
            "ref_count": len(bundle_heads.stdout.splitlines()),
            "contains_complete_history": "complete history"
            in (bundle_verify.stdout + bundle_verify.stderr),
        },
        "dirty_worktree": {
            "path": str(dirty_worktree),
            "base_sha": DIRTY_BASE_SHA,
            "patch_path": str(patch),
            "patch_size_bytes": patch.stat().st_size,
            "patch_sha256": sha256_file(patch),
            "restore_sample": restore,
        },
        "protected_sources": {
            **private_inventory,
            "git_tracked_path_count": len(tracked_private),
            "git_ignore_check": "PASS" if ignored == "private_sources" else "FAIL",
            "library_verifier": private_verifier,
        },
        "off_device_recovery": destination,
        "decision": (
            "The same-disk bundle and patch are verified recovery aids. They do not "
            "qualify as external disaster recovery, so Phase 2 remains held."
        ),
        "mutations_performed": {
            "file_deletions": 0,
            "cache_deletions": 0,
            "worktree_removals": 0,
            "branch_deletions": 0,
            "ref_deletions": 0,
            "pr_closures": 0,
        },
    }

    remote_heads = _remote_heads(repo)
    pull_requests = _pull_requests(repo)
    live_main = _json_command(
        ["gh", "api", "repos/{owner}/{repo}/commits/main"], cwd=repo
    )
    branches = _branch_inventory(
        repo=repo,
        worktrees=worktrees,
        remote_heads=remote_heads,
        pull_requests=pull_requests,
    )
    candidate_cache_rows = [
        row
        for row in cache_rows
        if row["disposition"] == "CACHE_CANDIDATE_NOT_AUTHORIZED"
    ]
    authorized_actions = [
        "INSPECT_LIVE_GIT_AND_DISK_STATE",
        "CREATE_ISOLATED_PHASE_1_WORKTREE",
        "CREATE_AND_VERIFY_RECOVERY_ARTIFACTS",
        "FREEZE_PRESERVATION_MANIFEST",
        "COMMIT_INTENDED_PATHS",
        "PUSH_FEATURE_BRANCH",
        "CREATE_OR_UPDATE_PR",
        "MERGE_UNCHANGED_GREEN_PR",
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "observed_at_utc": observed_at_utc,
        "status": "PHASE_1_LOCAL_PRESERVATION_COMPLETE_OFF_DEVICE_HOLD",
        "authorization": {
            "status": "OBSERVED",
            "query_status": "OK",
            "observed_at_utc": observed_at_utc,
            "authority_source": {
                "kind": "USER_DELEGATION",
                "status": "OBSERVED",
                "query_status": "OK",
                "observed_at_utc": observed_at_utc,
                "reference": (
                    "active Codex task: okay I authorize Phase 0 and Phase 1"
                ),
            },
            "authorized_phases": [0, 1],
            "authorized_actions": authorized_actions,
            "next_action": "COMMIT_INTENDED_PATHS",
            "target_binding": {
                "task_id": TASK_ID,
                "branch": inventory["current"]["branch"],
                "head_sha": inventory["current"]["head_sha"],
                "actions": authorized_actions,
            },
            "prohibited_actions": [
                "DELETE_FILE",
                "DELETE_CACHE",
                "REMOVE_WORKTREE",
                "DELETE_LOCAL_BRANCH",
                "DELETE_REMOTE_BRANCH",
                "DELETE_REF",
                "PRUNE",
                "GIT_CLEAN",
                "PUBLISH_RELEASE",
            ],
        },
        "baseline": {
            "origin_main_sha": inventory["current"]["default_base"]["sha"],
            "hosted_main_sha": live_main["sha"],
            "main_identity_match": inventory["current"]["default_base"]["sha"]
            == live_main["sha"],
            "current_branch": inventory["current"]["branch"],
            "current_head_sha": inventory["current"]["head_sha"],
            "git_state_query_status": (
                "OK" if not inventory.get("query_failures") else "FAILED"
            ),
            "remote_heads_query_status": "OK",
            "pull_requests_query_status": "OK",
            "historical_cleanup_evidence": {
                "path": "docs/verification/post-india2-cleanup-disposition-evidence.json",
                "status": "HISTORICAL_NOT_CURRENT_AUTHORITY",
            },
        },
        "summary": {
            "worktree_count": len(worktree_rows),
            "preexisting_worktree_count": len(worktree_rows) - 1,
            "detached_worktree_count": sum(
                row["branch"] == "DETACHED" for row in worktree_rows
            ),
            "dirty_worktree_count": sum(
                row["dirty_count"] > 0 for row in worktree_rows
            ),
            "preexisting_dirty_worktree_count": sum(
                row["dirty_count"] > 0 and not row["current"] for row in worktree_rows
            ),
            "worktree_total_bytes": sum(row["size_bytes"] for row in worktree_rows),
            "branch_or_pr_head_count": len(branches),
            "remote_branch_count": len(remote_heads),
            "cache_path_count": len(cache_rows),
            "cache_total_bytes": sum(row["size_bytes"] for row in cache_rows),
            "phase_2_cache_candidate_count": len(candidate_cache_rows),
            "phase_2_cache_candidate_bytes": sum(
                row["size_bytes"] for row in candidate_cache_rows
            ),
            "phase_2_authorized": False,
        },
        "disk_capacity": _disk_capacity(repo),
        "worktrees": worktree_rows,
        "branches": branches,
        "caches": cache_rows,
        "recovery_evidence": {
            "path": "docs/verification/maint-0136-cleanup-recovery-evidence.json",
            "status": recovery["status"],
            "git_bundle_sha256": recovery["git_bundle"]["sha256"],
            "dirty_patch_sha256": recovery["dirty_worktree"]["patch_sha256"],
            "off_device_recovery_status": destination["status"],
        },
        "decision": (
            "Freeze and preserve the observed topology. No file, cache, worktree, "
            "branch, remote ref, or pull request is authorized for cleanup."
        ),
    }
    return manifest, recovery


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--primary-repo", type=Path, default=PRIMARY_REPO)
    parser.add_argument("--dirty-worktree", type=Path, default=DIRTY_WORKTREE)
    parser.add_argument("--recovery-dir", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    parser.add_argument("--recovery-output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    observed_at_utc = datetime.now(UTC).isoformat()
    manifest, recovery = build_evidence(
        repo=args.repo.resolve(),
        primary_repo=args.primary_repo.resolve(),
        dirty_worktree=args.dirty_worktree.resolve(),
        recovery_dir=args.recovery_dir.resolve(),
        observed_at_utc=observed_at_utc,
    )
    args.manifest_output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.recovery_output.write_text(
        json.dumps(recovery, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "worktree_count": manifest["summary"]["worktree_count"],
                "branch_or_pr_head_count": manifest["summary"][
                    "branch_or_pr_head_count"
                ],
                "phase_2_cache_candidate_bytes": manifest["summary"][
                    "phase_2_cache_candidate_bytes"
                ],
                "off_device_recovery_status": recovery["off_device_recovery"]["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
