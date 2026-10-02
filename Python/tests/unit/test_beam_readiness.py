"""Native/Python readiness interchange and current-basis evidence."""

import copy
import gzip
import json
from pathlib import Path

import pytest

from structural_lib.beam.semantics import FreshnessState
from structural_lib.beam_readiness import (
    BeamReadinessDocumentV1,
    beam_readiness_freshness,
    canonical_beam_readiness_json,
    parse_beam_readiness_json,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "contracts/structural-engineering/conformance/beam-readiness-v1.gz"


def fixture_json() -> str:
    return gzip.decompress(FIXTURE.read_bytes()).decode("utf-8")


def test_native_cohort_round_trips_without_changing_source_or_claims() -> None:
    payload = fixture_json()
    document = parse_beam_readiness_json(payload)
    assert canonical_beam_readiness_json(document) + "\n" == payload
    assert document.request.cohort_id == "lnv01-wp11-owned-rectangular-v1"
    assert document.request.member_ids == (
        "member:PF9_B0001",
        "member:PF9_B0002",
        "member:PF9_B0003",
    )
    assert all(x.ready_for_selected_profile for x in document.members)
    assert document.engineering == "not_evaluated"
    assert document.approval == "unreviewed"
    assert "HOLD" in document.source_qualification
    source = document.request.snapshot
    assert source is not None
    assert (
        source.snapshot_sha256
        == "9ced40204f6db621b4b22c7a8a755d1a77ec77c69aaf9a4d76dc12316a72bf84"
    )
    assert (
        json.loads(payload)["request"]["snapshot"]
        == json.loads(canonical_beam_readiness_json(document))["request"]["snapshot"]
    )
    roles = document.request.acceptance.inputs.selection_roles
    assert {x.role for x in roles} == {"uls", "sls_total", "sls_sustained"}
    assert {x.selection_id for x in roles} == {
        x.selection_id for x in source.result_selections
    }
    assert all(x.action_basis.value == "static_concurrent" for x in source.action_rows)
    assert document.ledger is not None
    zero = next(x for x in document.ledger.fields if x.key == "member.left_centre")
    assert (zero.state, zero.entered_state, zero.source_state) == (
        "zero",
        "zero",
        "absent",
    )
    assert any(x.origin == "source" for x in document.ledger.fields)
    assert any(x.origin == "derived" for x in document.ledger.fields)
    assert any(x.state == "defaulted" for x in document.ledger.fields)


def test_currentness_requires_full_explicit_native_bindings() -> None:
    document = parse_beam_readiness_json(fixture_json())
    bindings = {
        "current_snapshot": document.request.snapshot,
        "current_ledger_revision": document.ledger.revision,
        "current_request_id": document.request_id,
        "current_engine_identity": document.engine_identity,
    }
    assert beam_readiness_freshness(document, **bindings) is FreshnessState.CURRENT
    for key in (
        "current_ledger_revision",
        "current_request_id",
        "current_engine_identity",
    ):
        assert (
            beam_readiness_freshness(document, **{**bindings, key: "changed"})
            is FreshnessState.STALE
        )
    source = document.request.snapshot
    epoch = source.model_copy(
        update={
            "source_identity": source.source_identity.model_copy(
                update={"result_epoch_id": "changed"}
            )
        }
    )
    assert (
        beam_readiness_freshness(document, **{**bindings, "current_snapshot": epoch})
        is FreshnessState.STALE
    )


@pytest.mark.parametrize(
    "change", ["role", "intent", "state", "accounting", "unknown", "approval"]
)
def test_altered_native_evidence_is_rejected(change: str) -> None:
    raw = copy.deepcopy(json.loads(fixture_json()))
    if change == "role":
        raw["request"]["acceptance"]["inputs"]["selection_roles"][0][
            "role"
        ] = "sls_total"
    elif change == "intent":
        next(x for x in raw["ledger"]["fields"] if x["key"] == "member.intent")[
            "value"
        ] = "Other"
    elif change == "state":
        raw["ledger"]["fields"][0]["state"] = "supplied"
    elif change == "accounting":
        raw["members"].pop()
    elif change == "unknown":
        raw["request"]["acceptance"]["inputs"]["project"]["inferred_acceptance"] = True
    else:
        raw["approval"] = "approved"
    with pytest.raises(ValueError):
        parse_beam_readiness_json(json.dumps(raw))


def test_duplicate_keys_and_schema_drift_are_rejected() -> None:
    payload = fixture_json()
    with pytest.raises(ValueError, match="Duplicate readiness JSON"):
        parse_beam_readiness_json(
            payload.replace(
                '"schema_version":"beam-readiness/v1"',
                '"schema_version":"beam-readiness/v1","schema_version":"beam-readiness/v1"',
                1,
            )
        )
    schema = (
        ROOT / "contracts/structural-engineering/schemas/beam-readiness.schema.json"
    )
    assert (
        json.loads(schema.read_text(encoding="utf-8"))
        == BeamReadinessDocumentV1.model_json_schema()
    )


def test_native_non_ready_documents_preserve_all_requested_outcomes() -> None:
    base = json.loads(fixture_json())
    cases_path = FIXTURE.with_name("beam-readiness-cases-v1.json")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    assert {x["name"] for x in cases} == {
        "provisional",
        "missing",
        "unsupported",
        "failed",
    }
    for case in cases:
        raw = copy.deepcopy(base)
        for change in case["changes"]:
            parent = raw
            for part in change["path"][:-1]:
                parent = parent[int(part)] if isinstance(parent, list) else parent[part]
            key = change["path"][-1]
            parent[int(key) if isinstance(parent, list) else key] = change["value"]
        document = parse_beam_readiness_json(json.dumps(raw))
        assert [x.state for x in document.members] == case["expected_states"]
        assert len(document.members) == len(document.request.member_ids) == 3
        assert not any(x.ready_for_selected_profile for x in document.members)
