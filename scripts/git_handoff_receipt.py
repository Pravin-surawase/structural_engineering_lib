#!/usr/bin/env python3
"""Build and validate fail-closed task-to-Git handoff receipts.

Local facts come only from :mod:`scripts.git_state`. Remote, pull-request,
review, check, and retention facts are caller-supplied evidence; this module
does not contact a remote or mutate Git/GitHub state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT
from git_state import RepositoryState, collect_repository_state

SCHEMA_VERSION = 1
RECEIPT_KIND = "task_to_git_handoff"
UNKNOWN = "UNKNOWN"
NOT_CHECKED = "NOT_CHECKED"
MAX_EVIDENCE_AGE_SECONDS = 900
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _unknown(status: str = UNKNOWN) -> dict[str, Any]:
    return {"status": status, "query_status": UNKNOWN}


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _fresh_status(
    section: Mapping[str, Any], now: datetime, *, max_age: int
) -> tuple[str, str | None]:
    status = section.get("status", UNKNOWN)
    if status in {UNKNOWN, NOT_CHECKED}:
        return str(status), None
    if status == "NOT_APPLICABLE":
        if not section.get("reason_code"):
            return UNKNOWN, "NOT_APPLICABLE_WITHOUT_REASON"
        return "NOT_APPLICABLE", None
    if status != "OBSERVED":
        return UNKNOWN, "MALFORMED_STATUS"
    if section.get("query_status") != "OK":
        return UNKNOWN, "QUERY_FAILED"
    observed = _parse_time(section.get("observed_at_utc"))
    if observed is None:
        return UNKNOWN, "MALFORMED_OBSERVATION_TIME"
    age = (now - observed).total_seconds()
    if age < -5:
        return UNKNOWN, "FUTURE_EVIDENCE"
    if age > max_age:
        return UNKNOWN, "STALE_EVIDENCE"
    return "OBSERVED", None


def _normalise_section(
    evidence: Mapping[str, Any], name: str, now: datetime, *, max_age: int
) -> tuple[dict[str, Any], list[str]]:
    raw = evidence.get(name)
    if raw is None:
        return _unknown(NOT_CHECKED), [f"{name.upper()}_NOT_CHECKED"]
    if not isinstance(raw, Mapping):
        return _unknown(), [f"{name.upper()}_MALFORMED"]
    section = dict(raw)
    status, reason = _fresh_status(section, now, max_age=max_age)
    section["status"] = status
    if status != "OBSERVED":
        section["query_status"] = UNKNOWN
    if reason:
        return section, [f"{name.upper()}_{reason}"]
    if status in {UNKNOWN, NOT_CHECKED}:
        return section, [f"{name.upper()}_{status}"]
    return section, []


def _local_payload(state: RepositoryState) -> dict[str, Any]:
    state_payload = state.to_dict()
    return {
        "authority": "scripts/git_state.py",
        "receipt_sha256": _sha256(state_payload),
        "state": state_payload,
    }


def build_receipt(
    *,
    task_id: str,
    integration_owner: str,
    local_state: RepositoryState,
    evidence: Mapping[str, Any] | None = None,
    owned_paths: Sequence[str] = (),
    shared_paths: Sequence[str] = (),
    forbidden_paths: Sequence[str] = (),
    now: datetime | None = None,
    max_age: int = MAX_EVIDENCE_AGE_SECONDS,
) -> dict[str, Any]:
    """Create one receipt. Missing or inconsistent facts become explicit holds."""
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    supplied = evidence or {}
    holds: list[str] = []

    if (
        local_state.query_failures
        or local_state.branch == UNKNOWN
        or not _is_sha(local_state.head_sha)
        or local_state.operation == "unknown"
    ):
        holds.append("LOCAL_STATE_UNKNOWN")
    if not local_state.ready_local:
        holds.append(f"LOCAL_{local_state.derived_action}")

    remote, remote_holds = _normalise_section(
        supplied, "remote", observed_now, max_age=max_age
    )
    pull_request, pr_holds = _normalise_section(
        supplied, "pull_request", observed_now, max_age=max_age
    )
    review, review_holds = _normalise_section(
        supplied, "review", observed_now, max_age=max_age
    )
    retention, retention_holds = _normalise_section(
        supplied, "retention", observed_now, max_age=max_age
    )
    integration, integration_holds = _normalise_section(
        supplied, "integration", observed_now, max_age=max_age
    )
    holds.extend(
        remote_holds + pr_holds + review_holds + retention_holds + integration_holds
    )

    local_head = local_state.head_sha
    remote_head = remote.get("head_sha")
    pr_head = pull_request.get("head_sha")
    reviewed_head = review.get("head_sha")
    if remote.get("status") == "OBSERVED" and not _is_sha(remote_head):
        holds.append("REMOTE_HEAD_UNKNOWN")
    if pull_request.get("status") == "OBSERVED":
        required_pr = (
            "number",
            "state",
            "base_ref",
            "base_sha",
            "head_ref",
            "head_sha",
            "merge_state",
            "required_checks",
        )
        if any(pull_request.get(field) in (None, "", UNKNOWN) for field in required_pr):
            holds.append("PULL_REQUEST_IDENTITY_UNKNOWN")
        if not _is_sha(pull_request.get("base_sha")) or not _is_sha(pr_head):
            holds.append("PULL_REQUEST_SHA_MALFORMED")
    if review.get("status") == "OBSERVED":
        for field in ("base_sha", "head_sha", "tree_sha"):
            if not _is_sha(review.get(field)):
                holds.append("REVIEW_IDENTITY_UNKNOWN")
                break

    published_claim = (
        remote.get("status") == "OBSERVED" and remote.get("branch_state") == "PRESENT"
    )
    if published_claim and local_head != remote_head:
        holds.append("REMOTE_HEAD_MISMATCH")
    if pull_request.get("status") == "OBSERVED" and pr_head != local_head:
        holds.append("PULL_REQUEST_HEAD_MISMATCH")
    if review.get("status") == "OBSERVED" and reviewed_head != pr_head:
        holds.append("REVIEWED_HEAD_MISMATCH")
    if (
        review.get("status") == "OBSERVED"
        and pull_request.get("status") == "OBSERVED"
        and review.get("base_sha") != pull_request.get("base_sha")
    ):
        holds.append("REVIEWED_BASE_MISMATCH")

    checks = pull_request.get("required_checks", [])
    if checks not in (None, UNKNOWN) and not isinstance(checks, list):
        holds.append("REQUIRED_CHECKS_MALFORMED")
    if isinstance(checks, list):
        if pull_request.get("status") == "OBSERVED" and not checks:
            holds.append("REQUIRED_CHECKS_UNKNOWN")
        for check in checks:
            if not isinstance(check, Mapping):
                holds.append("REQUIRED_CHECK_MALFORMED")
                continue
            if check.get("head_sha") != pr_head:
                holds.append("REQUIRED_CHECK_HEAD_MISMATCH")
            if (
                check.get("status") != "COMPLETED"
                or check.get("conclusion") != "SUCCESS"
            ):
                holds.append("REQUIRED_CHECK_NOT_SUCCESSFUL")

    if integration.get("status") == "OBSERVED":
        # Squash integration is content evidence, never ancestry/retention authority.
        if integration.get("method") == "squash" and (
            not _is_sha(integration.get("merge_sha"))
            or integration.get("reviewed_tree_sha")
            != integration.get("merged_tree_sha")
            or not _is_sha(integration.get("reviewed_tree_sha"))
        ):
            holds.append("SQUASH_TREE_EQUIVALENCE_UNKNOWN")

    task_archive = supplied.get("task_archive", {"status": NOT_CHECKED})
    if not isinstance(task_archive, Mapping):
        task_archive = {"status": UNKNOWN}
    task_archive = dict(task_archive)
    task_archive["is_git_retention_evidence"] = False

    authorization = supplied.get("authorization")
    if not isinstance(authorization, Mapping):
        authorization = {
            "status": UNKNOWN,
            "authorized_actions": [],
            "prohibited_actions": [],
            "next_action": "HOLD_FOR_EXACT_EVIDENCE",
        }
        holds.append("AUTHORIZATION_UNKNOWN")
    else:
        authorization = dict(authorization)
        if not authorization.get("next_action"):
            authorization["next_action"] = "HOLD_FOR_EXACT_EVIDENCE"
            holds.append("NEXT_ACTION_UNKNOWN")

    holds.extend(str(item) for item in retention.get("holds", []) if item)
    holds = sorted(set(holds))
    local = _local_payload(local_state)
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_kind": RECEIPT_KIND,
        "receipt_status": "HOLD" if holds else "READY",
        "observed_at_utc": observed_now.isoformat(),
        "task": {
            "task_id": task_id,
            "integration_owner": integration_owner,
            "owned_paths": list(owned_paths),
            "shared_paths": list(shared_paths),
            "forbidden_paths": list(forbidden_paths),
        },
        "local_state_receipt_hash": f"sha256:{local['receipt_sha256']}",
        "local": local,
        "remote": remote,
        "pull_request": pull_request,
        "review": review,
        "integration": integration,
        "retention": retention,
        "task_archive": task_archive,
        "authorization": authorization,
        "holds": holds,
        "mutation_policy": "READ_ONLY_EVIDENCE_NO_GIT_OR_GITHUB_MUTATION",
    }


def validate_receipt(
    receipt: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age: int = MAX_EVIDENCE_AGE_SECONDS,
) -> list[str]:
    """Validate a stored receipt without upgrading unknown evidence to success."""
    errors: list[str] = []
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if receipt.get("schema_version") != SCHEMA_VERSION:
        errors.append("SCHEMA_VERSION_UNKNOWN")
    if receipt.get("receipt_kind") != RECEIPT_KIND:
        errors.append("RECEIPT_KIND_UNKNOWN")
    task = receipt.get("task")
    if not isinstance(task, Mapping) or not task.get("task_id"):
        errors.append("TASK_ID_UNKNOWN")
    local = receipt.get("local")
    if (
        not isinstance(local, Mapping)
        or local.get("authority") != "scripts/git_state.py"
    ):
        errors.append("LOCAL_AUTHORITY_UNKNOWN")
    else:
        state = local.get("state")
        if not isinstance(state, Mapping):
            errors.append("LOCAL_STATE_UNKNOWN")
        elif local.get("receipt_sha256") != _sha256(state):
            errors.append("LOCAL_STATE_HASH_MISMATCH")
        expected_hash = f"sha256:{local.get('receipt_sha256', '')}"
        if receipt.get("local_state_receipt_hash") != expected_hash:
            errors.append("LOCAL_STATE_RECEIPT_HASH_MISMATCH")
    holds = receipt.get("holds")
    if not isinstance(holds, list):
        errors.append("HOLDS_MALFORMED")
    if receipt.get("receipt_status") == "READY" and (errors or holds):
        errors.append("FALSE_READY_CLAIM")
    task_archive = receipt.get("task_archive")
    if (
        not isinstance(task_archive, Mapping)
        or task_archive.get("is_git_retention_evidence") is not False
    ):
        errors.append("TASK_ARCHIVE_RETENTION_CONTRADICTION")
    for name in ("remote", "pull_request", "review", "integration", "retention"):
        section = receipt.get(name)
        if not isinstance(section, Mapping):
            errors.append(f"{name.upper()}_MALFORMED")
            continue
        _status, reason = _fresh_status(section, observed_now, max_age=max_age)
        if reason:
            errors.append(f"{name.upper()}_{reason}")
    if isinstance(local, Mapping) and isinstance(local.get("state"), Mapping):
        local_state = local["state"]
        local_head = local_state.get("head_sha")
        remote = receipt.get("remote", {})
        pr = receipt.get("pull_request", {})
        review = receipt.get("review", {})
        if isinstance(remote, Mapping) and remote.get("status") == "OBSERVED":
            if (
                remote.get("branch_state") == "PRESENT"
                and remote.get("head_sha") != local_head
            ):
                errors.append("REMOTE_HEAD_MISMATCH")
        if isinstance(pr, Mapping) and pr.get("status") == "OBSERVED":
            if pr.get("head_sha") != local_head:
                errors.append("PULL_REQUEST_HEAD_MISMATCH")
            checks = pr.get("required_checks")
            if not isinstance(checks, list):
                errors.append("REQUIRED_CHECKS_MALFORMED")
            else:
                for check in checks:
                    if not isinstance(check, Mapping):
                        errors.append("REQUIRED_CHECK_MALFORMED")
                    elif check.get("head_sha") != pr.get("head_sha"):
                        errors.append("REQUIRED_CHECK_HEAD_MISMATCH")
                    elif (
                        check.get("status") != "COMPLETED"
                        or check.get("conclusion") != "SUCCESS"
                    ):
                        errors.append("REQUIRED_CHECK_NOT_SUCCESSFUL")
        if isinstance(review, Mapping) and review.get("status") == "OBSERVED":
            if not isinstance(pr, Mapping) or review.get("head_sha") != pr.get(
                "head_sha"
            ):
                errors.append("REVIEWED_HEAD_MISMATCH")
            if not isinstance(pr, Mapping) or review.get("base_sha") != pr.get(
                "base_sha"
            ):
                errors.append("REVIEWED_BASE_MISMATCH")
    integration = receipt.get("integration")
    if isinstance(integration, Mapping) and integration.get("status") == "OBSERVED":
        if integration.get("method") == "squash" and (
            integration.get("reviewed_tree_sha") != integration.get("merged_tree_sha")
            or not _is_sha(integration.get("reviewed_tree_sha"))
        ):
            errors.append("SQUASH_TREE_EQUIVALENCE_UNKNOWN")
    return sorted(set(errors))


def load_receipt(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("receipt root must be an object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser(
        "create", help="Build a receipt from local state and supplied evidence"
    )
    create.add_argument("--task-id", required=True)
    create.add_argument("--integration-owner", required=True)
    create.add_argument("--repo", type=Path, default=REPO_ROOT)
    create.add_argument("--evidence", type=Path)
    create.add_argument("--owned-path", action="append", default=[])
    create.add_argument("--shared-path", action="append", default=[])
    create.add_argument("--forbidden-path", action="append", default=[])
    create.add_argument("--output", type=Path)
    validate = sub.add_parser("validate", help="Validate one stored receipt")
    validate.add_argument("receipt", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate":
        try:
            receipt = load_receipt(args.receipt)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Task-to-Git handoff receipt invalid: {exc}")
            return 1
        errors = validate_receipt(receipt)
        if errors:
            print("Task-to-Git handoff receipt invalid:")
            for error in errors:
                print(f"  - {error}")
            return 1
        print(
            "Task-to-Git handoff receipt valid: "
            f"{receipt['task']['task_id']} | {receipt['receipt_status']}"
        )
        return 0

    evidence: dict[str, Any] = {}
    if args.evidence:
        try:
            value = json.loads(args.evidence.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Evidence query failed or malformed: {exc}", file=sys.stderr)
            value = {}
        if isinstance(value, dict):
            evidence = value
    receipt = build_receipt(
        task_id=args.task_id,
        integration_owner=args.integration_owner,
        local_state=collect_repository_state(args.repo),
        evidence=evidence,
        owned_paths=args.owned_path,
        shared_paths=args.shared_path,
        forbidden_paths=args.forbidden_path,
    )
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
