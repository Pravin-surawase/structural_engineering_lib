"""Lossless offline inspection of native readiness evidence; no engineering resolution."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from structural_lib.beam.semantics import FreshnessState
from structural_lib.core.analysis_snapshot import AnalysisSnapshotV1
from structural_lib.core.beam_readiness import BeamReadinessDocumentV1
from structural_lib.services.analysis_snapshot import (
    canonical_snapshot_json_bytes,
    validate_analysis_snapshot,
)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate readiness JSON field: {key}")
        value[key] = item
    return value


def _identity(kind: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_snapshot_json_bytes(value)).hexdigest()
    return f"{kind}:pf4-canonical-json-v1:{digest}"


def canonical_beam_readiness_json(document: BeamReadinessDocumentV1) -> str:
    """Return the native interchange JSON without recalculating or changing its claims."""
    return canonical_snapshot_json_bytes(document).decode("utf-8")


def parse_beam_readiness_json(payload: str | bytes) -> BeamReadinessDocumentV1:
    """Validate a native readiness document, its exact request and source evidence.

    This does not invoke .NET, ETABS or Excel, resolve edits, or establish that the
    recorded native engine ran. Request edits require native ``Assess`` again.
    Use ``beam_readiness_freshness`` with current bindings before displaying a
    recorded result as current. Integrity hashes are not signatures or approval.
    """
    raw = json.loads(payload, object_pairs_hook=_unique_object)
    document = BeamReadinessDocumentV1.model_validate_json(payload)
    if canonical_snapshot_json_bytes(raw) != canonical_snapshot_json_bytes(document):
        raise ValueError("Readiness projection would lose or alter evidence")
    basis = {**raw, "document_id": ""}
    if document.document_id != _identity("beam_readiness_document", basis):
        raise ValueError("Readiness document identity mismatch")
    request_basis = {
        "request": raw["request"],
        "policy_revision": document.policy_revision,
        "engine_identity": document.engine_identity,
    }
    if document.request_id != _identity("beam_readiness_request", request_basis):
        raise ValueError("Readiness request identity mismatch")
    ids = document.request.member_ids
    if (
        not document.request.cohort_id.strip()
        or not ids
        or any(not x.strip() for x in ids)
        or len(set(ids)) != len(ids)
    ):
        raise ValueError("Named cohort requires distinct requested member identities")
    if tuple(x.member_id for x in document.members) != ids:
        raise ValueError("Every requested member must have exactly one ordered outcome")
    snapshot = document.request.snapshot
    valid_source = (
        snapshot is not None
        and validate_analysis_snapshot(snapshot).snapshot is not None
    )
    if (
        snapshot is not None
        and not valid_source
        and any(x.state != "failed" for x in document.members)
    ):
        raise ValueError("Invalid source evidence cannot establish readiness")
    ledger = document.ledger
    if ledger is not None:
        if (
            snapshot is None
            or ledger.snapshot_sha256 != snapshot.snapshot_sha256
            or ledger.member_ids != ids
            or ledger.preset_revision != document.request.preset.revision
        ):
            raise ValueError("Ledger does not bind the exact cohort, source and preset")
        if len({(x.subject_id, x.key) for x in ledger.fields}) != len(ledger.fields):
            raise ValueError("Ledger repeats an effective field")
    for member in document.members:
        if member.ready_for_selected_profile != (member.state == "complete"):
            raise ValueError("Ready flag disagrees with the recorded native run state")
        if member.ready_for_selected_profile:
            acceptance = document.request.acceptance
            if (
                not valid_source
                or ledger is None
                or acceptance is None
                or not acceptance.inputs.project.values_accepted
                or acceptance.ledger_revision != ledger.revision
                or not member.effective_input_id
            ):
                raise ValueError(
                    "Ready result lacks revision-bound accepted input evidence"
                )
    return document


def beam_readiness_freshness(
    document: BeamReadinessDocumentV1,
    *,
    current_snapshot: AnalysisSnapshotV1,
    current_ledger_revision: str,
    current_request_id: str,
    current_engine_identity: str,
) -> FreshnessState:
    """Compare explicit current native bindings; never trust stored currentness.

    The caller obtains ``current_request_id`` and ``current_engine_identity``
    from the native owner. Python cannot resolve edited project inputs itself.
    """
    checked = parse_beam_readiness_json(canonical_beam_readiness_json(document))
    if validate_analysis_snapshot(current_snapshot).snapshot is None:
        return FreshnessState.STALE
    return (
        FreshnessState.CURRENT
        if checked.request.snapshot is not None
        and checked.ledger is not None
        and checked.request.snapshot.snapshot_sha256 == current_snapshot.snapshot_sha256
        and checked.ledger.revision == current_ledger_revision
        and checked.request_id == current_request_id
        and checked.engine_identity == current_engine_identity
        else FreshnessState.STALE
    )


__all__ = [
    "parse_beam_readiness_json",
    "canonical_beam_readiness_json",
    "beam_readiness_freshness",
]
