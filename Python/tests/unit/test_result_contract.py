"""Cross-element structural result status contract."""

from structural_lib.core.result_contract import adapt_legacy_result_status


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


def test_missing_axis_cannot_be_inferred_from_success_booleans() -> None:
    result = adapt_legacy_result_status(
        {"success": True, "is_safe": True, "engineering_status": "PASS"}
    )

    assert result.overall_status.value == "HOLD"
    assert result.engineering_status.value == "HOLD"
