"""Cross-element structural result status, issue, and identity contract."""

import pytest

from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    FreshnessStatus,
    IntakeStatus,
    ResultIdentityV1,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
    adapt_legacy_result_status,
)


def test_complete_explicit_axes_can_report_pass() -> None:
    result = adapt_legacy_result_status(
        {
            "intake_status": "VALID",
            "calculation_status": "COMPLETED",
            "engineering_status": "PASS",
        }
    )

    assert result.overall_status.value == "PASS"
    assert result.to_dict()["qualified_review_required"] is True
    assert result.to_dict()["freshness_status"] == "CURRENT"


def test_missing_axis_cannot_be_inferred_from_success_booleans() -> None:
    result = adapt_legacy_result_status(
        {"success": True, "is_safe": True, "engineering_status": "PASS"}
    )

    assert result.overall_status.value == "HOLD"
    assert result.engineering_status.value == "HOLD"
    assert result.to_dict()["issues"][0]["code"] == "CANONICAL_STATUS_INCOMPLETE"


@pytest.mark.parametrize(
    ("intake", "calculation", "engineering", "freshness", "expected"),
    [
        ("VALID", "COMPLETED", "PASS", "CURRENT", "PASS"),
        ("VALID", "COMPLETED", "FAIL", "CURRENT", "FAIL"),
        ("BLOCKED", "NOT_EVALUATED", "NOT_EVALUATED", "CURRENT", "BLOCKED"),
        ("VALID", "ERROR", "HOLD", "CURRENT", "ERROR"),
        ("VALID", "NOT_EVALUATED", "NOT_EVALUATED", "CURRENT", "NOT_EVALUATED"),
        ("VALID", "COMPLETED", "PASS", "STALE", "STALE"),
        ("PARTIAL", "COMPLETED", "PASS", "CURRENT", "HOLD"),
    ],
)
def test_fail_closed_aggregate_preserves_each_outcome(
    intake: str,
    calculation: str,
    engineering: str,
    freshness: str,
    expected: str,
) -> None:
    envelope = StructuralResultEnvelopeV2(
        intake_status=IntakeStatus(intake),
        calculation_status=CalculationStatus(calculation),
        engineering_status=EngineeringStatus(engineering),
        freshness_status=FreshnessStatus(freshness),
    )

    assert envelope.overall_status.value == expected


def test_issue_and_replay_identity_are_canonical_transport_fields() -> None:
    envelope = StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.VALID,
        calculation_status=CalculationStatus.COMPLETED,
        engineering_status=EngineeringStatus.FAIL,
        issues=(
            StructuralIssueV1(
                code="BEAM_DESIGN_CHECK_FAILED",
                path="$.calculation",
                message="One or more evaluated checks failed.",
            ),
        ),
        result_identity=ResultIdentityV1(
            contract_version="canonical-beam-result/v1",
            library_version="0.23.1a2",
            input_hash="a" * 64,
            calculation_identity="b" * 64,
        ),
    ).to_dict()

    assert envelope["schema_version"] == "structural-result-envelope/v2"
    assert envelope["issues"][0]["path"] == "$.calculation"
    assert envelope["result_identity"]["input_hash"] == "a" * 64
