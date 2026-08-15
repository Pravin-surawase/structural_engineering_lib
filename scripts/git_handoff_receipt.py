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
        section = _unknown()
        section["evidence_error"] = "MALFORMED"
        return section, [f"{name.upper()}_MALFORMED"]
    section = dict(raw)
    status, reason = _fresh_status(section, now, max_age=max_age)
    section["status"] = status
    if status != "OBSERVED":
        section["query_status"] = UNKNOWN
    if reason:
        section["evidence_error"] = reason
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


def _authorization_holds(
    authorization: object,
    *,
    task: object,
    local_state: object,
) -> list[str]:
    if not isinstance(authorization, Mapping):
        return ["AUTHORIZATION_MALFORMED"]
    holds: list[str] = []
    status = authorization.get("status")
    if status not in {"OBSERVED", UNKNOWN, NOT_CHECKED}:
        holds.append("AUTHORIZATION_STATUS_INVALID")
    elif status != "OBSERVED":
        holds.append("AUTHORIZATION_UNKNOWN")
    if (
        not isinstance(authorization.get("next_action"), str)
        or not authorization.get("next_action", "").strip()
    ):
        holds.append("NEXT_ACTION_UNKNOWN")
    for field in ("authorized_actions", "prohibited_actions"):
        actions = authorization.get(field)
        if not isinstance(actions, list) or any(
            not isinstance(action, str) or not action.strip() for action in actions
        ):
            holds.append("AUTHORIZATION_ACTIONS_MALFORMED")
            break
    authorized = authorization.get("authorized_actions", [])
    prohibited = authorization.get("prohibited_actions", [])
    if isinstance(authorized, list) and isinstance(prohibited, list):
        if set(authorized) & set(prohibited):
            holds.append("AUTHORIZATION_ACTION_CONTRADICTION")

    source = authorization.get("authority_source")
    if not isinstance(source, Mapping):
        holds.append("AUTHORIZATION_PROVENANCE_UNKNOWN")
    else:
        if source.get("kind") not in {
            "USER_DELEGATION",
            "ORCHESTRATOR_DELEGATION",
            "REPOSITORY_POLICY",
            "GITHUB_REVIEW",
        }:
            holds.append("AUTHORIZATION_SOURCE_KIND_INVALID")
        if (
            not isinstance(source.get("reference"), str)
            or not source.get("reference", "").strip()
        ):
            holds.append("AUTHORIZATION_SOURCE_REFERENCE_UNKNOWN")
        if _parse_time(source.get("observed_at_utc")) is None:
            holds.append("AUTHORIZATION_SOURCE_TIME_UNKNOWN")

    binding = authorization.get("target_binding")
    if not isinstance(binding, Mapping):
        holds.append("AUTHORIZATION_TARGET_BINDING_UNKNOWN")
    else:
        task_id = task.get("task_id") if isinstance(task, Mapping) else None
        branch = local_state.get("branch") if isinstance(local_state, Mapping) else None
        head_sha = (
            local_state.get("head_sha") if isinstance(local_state, Mapping) else None
        )
        if (
            binding.get("task_id") != task_id
            or binding.get("branch") != branch
            or binding.get("head_sha") != head_sha
        ):
            holds.append("AUTHORIZATION_TARGET_MISMATCH")
        bound_actions = binding.get("actions")
        if not isinstance(bound_actions, list) or bound_actions != authorized:
            holds.append("AUTHORIZATION_TARGET_ACTION_MISMATCH")
    return holds


def _stored_section_holds(
    receipt: Mapping[str, Any], name: str, now: datetime, *, max_age: int
) -> list[str]:
    section = receipt.get(name)
    prefix = name.upper()
    if not isinstance(section, Mapping):
        return [f"{prefix}_MALFORMED"]
    status, reason = _fresh_status(section, now, max_age=max_age)
    if reason:
        return [f"{prefix}_{reason}"]
    if status in {UNKNOWN, NOT_CHECKED}:
        evidence_error = section.get("evidence_error")
        if isinstance(evidence_error, str) and evidence_error:
            return [f"{prefix}_{evidence_error}"]
        return [f"{prefix}_{status}"]
    return []


def _derive_evidence_holds(
    receipt: Mapping[str, Any], now: datetime, *, max_age: int
) -> list[str]:
    """Derive authority holds from facts; never trust serialized hold claims."""
    holds: list[str] = []
    local = receipt.get("local")
    state = local.get("state") if isinstance(local, Mapping) else None
    if not isinstance(state, Mapping):
        holds.append("LOCAL_STATE_UNKNOWN")
        local_head = None
    else:
        local_head = state.get("head_sha")
        if (
            state.get("query_failures")
            or state.get("branch") == UNKNOWN
            or not _is_sha(local_head)
            or state.get("operation") == "unknown"
        ):
            holds.append("LOCAL_STATE_UNKNOWN")
        if (
            state.get("ready_local") is not True
            or state.get("derived_action") != "READY_LOCAL"
        ):
            derived_action = state.get("derived_action", UNKNOWN)
            holds.append(f"LOCAL_{derived_action}")

    for name in ("remote", "pull_request", "review", "integration", "retention"):
        holds.extend(_stored_section_holds(receipt, name, now, max_age=max_age))

    remote = receipt.get("remote")
    pr = receipt.get("pull_request")
    review = receipt.get("review")
    integration = receipt.get("integration")
    retention = receipt.get("retention")

    if isinstance(remote, Mapping) and remote.get("status") == "OBSERVED":
        remote_head = remote.get("head_sha")
        if not _is_sha(remote_head):
            holds.append("REMOTE_HEAD_UNKNOWN")
        if remote.get("branch_state") == "PRESENT" and remote_head != local_head:
            holds.append("REMOTE_HEAD_MISMATCH")

    pr_head = pr.get("head_sha") if isinstance(pr, Mapping) else None
    if isinstance(pr, Mapping) and pr.get("status") == "OBSERVED":
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
        if any(pr.get(field) in (None, "", UNKNOWN) for field in required_pr):
            holds.append("PULL_REQUEST_IDENTITY_UNKNOWN")
        if not _is_sha(pr.get("base_sha")) or not _is_sha(pr_head):
            holds.append("PULL_REQUEST_SHA_MALFORMED")
        if pr_head != local_head:
            holds.append("PULL_REQUEST_HEAD_MISMATCH")
        checks = pr.get("required_checks")
        if not isinstance(checks, list):
            holds.append("REQUIRED_CHECKS_MALFORMED")
        elif not checks:
            holds.append("REQUIRED_CHECKS_UNKNOWN")
        else:
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

    if isinstance(review, Mapping) and review.get("status") == "OBSERVED":
        if any(
            not _is_sha(review.get(field))
            for field in ("base_sha", "head_sha", "tree_sha")
        ):
            holds.append("REVIEW_IDENTITY_UNKNOWN")
        if review.get("head_sha") != pr_head:
            holds.append("REVIEWED_HEAD_MISMATCH")
        if not isinstance(pr, Mapping) or review.get("base_sha") != pr.get("base_sha"):
            holds.append("REVIEWED_BASE_MISMATCH")

    if isinstance(integration, Mapping) and integration.get("status") == "OBSERVED":
        if integration.get("method") == "squash" and (
            not _is_sha(integration.get("merge_sha"))
            or integration.get("reviewed_tree_sha")
            != integration.get("merged_tree_sha")
            or not _is_sha(integration.get("reviewed_tree_sha"))
        ):
            holds.append("SQUASH_TREE_EQUIVALENCE_UNKNOWN")

    if isinstance(retention, Mapping):
        retention_holds = retention.get("holds", [])
        if not isinstance(retention_holds, list) or any(
            not isinstance(item, str) or not item for item in retention_holds
        ):
            holds.append("RETENTION_HOLDS_MALFORMED")
        else:
            holds.extend(retention_holds)

    task_archive = receipt.get("task_archive")
    if (
        not isinstance(task_archive, Mapping)
        or task_archive.get("is_git_retention_evidence") is not False
    ):
        holds.append("TASK_ARCHIVE_RETENTION_CONTRADICTION")
    if receipt.get("receipt_grants_authority") is not False:
        holds.append("RECEIPT_AUTHORITY_BOUNDARY_MISSING")
    holds.extend(
        _authorization_holds(
            receipt.get("authorization"),
            task=receipt.get("task"),
            local_state=state,
        )
    )
    return sorted(set(holds))


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
    remote, _ = _normalise_section(supplied, "remote", observed_now, max_age=max_age)
    pull_request, _ = _normalise_section(
        supplied, "pull_request", observed_now, max_age=max_age
    )
    review, _ = _normalise_section(supplied, "review", observed_now, max_age=max_age)
    retention, _ = _normalise_section(
        supplied, "retention", observed_now, max_age=max_age
    )
    integration, _ = _normalise_section(
        supplied, "integration", observed_now, max_age=max_age
    )

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
    else:
        authorization = dict(authorization)
        if not authorization.get("next_action"):
            authorization["next_action"] = "HOLD_FOR_EXACT_EVIDENCE"

    local = _local_payload(local_state)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_kind": RECEIPT_KIND,
        "receipt_status": "HOLD",
        "receipt_grants_authority": False,
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
        "holds": [],
        "mutation_policy": "READ_ONLY_EVIDENCE_NO_GIT_OR_GITHUB_MUTATION",
    }
    derived_holds = _derive_evidence_holds(receipt, observed_now, max_age=max_age)
    receipt["holds"] = derived_holds
    receipt["receipt_status"] = "HOLD" if derived_holds else "READY"
    return receipt


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
    serialized_holds = receipt.get("holds")
    if not isinstance(serialized_holds, list) or any(
        not isinstance(hold, str) or not hold for hold in serialized_holds
    ):
        errors.append("HOLDS_MALFORMED")
        serialized_hold_set: set[str] = set()
    else:
        serialized_hold_set = set(serialized_holds)
        if len(serialized_hold_set) != len(serialized_holds):
            errors.append("HOLDS_DUPLICATE")

    receipt_status = receipt.get("receipt_status")
    if receipt_status not in {"READY", "HOLD"}:
        errors.append("RECEIPT_STATUS_INVALID")
    task_archive = receipt.get("task_archive")
    if (
        not isinstance(task_archive, Mapping)
        or task_archive.get("is_git_retention_evidence") is not False
    ):
        errors.append("TASK_ARCHIVE_RETENTION_CONTRADICTION")
    if receipt.get("receipt_grants_authority") is not False:
        errors.append("RECEIPT_AUTHORITY_BOUNDARY_MISSING")

    derived_holds = set(_derive_evidence_holds(receipt, observed_now, max_age=max_age))
    for hold in sorted(derived_holds - serialized_hold_set):
        errors.append(f"MISSING_REQUIRED_HOLD:{hold}")
    for hold in sorted(serialized_hold_set - derived_holds):
        errors.append(f"UNSUPPORTED_SERIALIZED_HOLD:{hold}")
    if serialized_hold_set != derived_holds:
        errors.append("HOLD_SET_MISMATCH")

    expected_status = "HOLD" if derived_holds else "READY"
    if receipt_status in {"READY", "HOLD"} and receipt_status != expected_status:
        errors.append("RECEIPT_STATUS_CONTRADICTION")
    if receipt_status == "READY" and (errors or derived_holds):
        errors.append("FALSE_READY_CLAIM")
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
