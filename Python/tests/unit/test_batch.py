# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Contract tests for strict project beam batch design."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from structural_lib.services import batch
from structural_lib.services.batch import (
    design_beams,
    design_beams_iter,
    design_project_beams_iter_v1,
    design_project_beams_v1,
)
from structural_lib.services.project_beam import (
    PROJECT_BEAM_SCHEMA_VERSION,
    ProjectBeamCalculationStatus,
    ProjectBeamEngineeringStatus,
    ProjectBeamIntakeStatus,
    ProjectBeamOverallStatus,
    validate_project_beam_design_input_v1,
)


def _canonical_beam(**overrides: Any) -> dict[str, Any]:
    beam: dict[str, Any] = {
        "schema_version": PROJECT_BEAM_SCHEMA_VERSION,
        "member_id": "B1",
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 452.0,
        "mu_knm": 100.0,
        "vu_kn": 50.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }
    beam.update(overrides)
    return beam


def _issue_codes(result: dict[str, Any]) -> set[str]:
    return {issue["code"] for issue in result["issues"]}


SERVICE_NEGATIVE_CASES: tuple[tuple[str, dict[str, Any], str, str], ...] = (
    (
        "unsupported schema version",
        {"schema_version": "project-beam-design/v2"},
        "PROJECT_BEAM_UNSUPPORTED_SCHEMA_VERSION",
        "schema_version",
    ),
    (
        "blank member identity",
        {"member_id": "   "},
        "PROJECT_BEAM_INVALID_MEMBER_ID",
        "member_id",
    ),
    (
        "unknown calculation-looking field",
        {"Mu (kN-m)": 100.0},
        "PROJECT_BEAM_UNKNOWN_FIELD",
        "Mu (kN-m)",
    ),
    (
        "missing required value",
        {"__remove__": "vu_kn"},
        "PROJECT_BEAM_REQUIRED_FIELD",
        "vu_kn",
    ),
    (
        "empty string",
        {"mu_knm": ""},
        "PROJECT_BEAM_INVALID_NUMBER",
        "mu_knm",
    ),
    (
        "whitespace",
        {"mu_knm": "   "},
        "PROJECT_BEAM_INVALID_NUMBER",
        "mu_knm",
    ),
    (
        "malformed numeric value",
        {"mu_knm": "one hundred"},
        "PROJECT_BEAM_INVALID_NUMBER",
        "mu_knm",
    ),
    (
        "NaN",
        {"mu_knm": float("nan")},
        "PROJECT_BEAM_NON_FINITE",
        "mu_knm",
    ),
    (
        "positive infinity",
        {"mu_knm": float("inf")},
        "PROJECT_BEAM_NON_FINITE",
        "mu_knm",
    ),
    (
        "negative infinity",
        {"mu_knm": float("-inf")},
        "PROJECT_BEAM_NON_FINITE",
        "mu_knm",
    ),
    (
        "explicit and derived depth conflict",
        {
            "effective_depth_basis": {
                "clear_cover_mm": 32.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 16.0,
            }
        },
        "PROJECT_BEAM_DEPTH_CONFLICT",
        "effective_depth_basis",
    ),
    (
        "non-positive section width",
        {"b_mm": 0.0},
        "PROJECT_BEAM_OUT_OF_RANGE",
        "b_mm",
    ),
    (
        "effective depth not below overall depth",
        {"d_mm": 500.0},
        "PROJECT_BEAM_DEPTH_OUT_OF_RANGE",
        "d_mm",
    ),
    (
        "invalid source metadata",
        {"source_metadata": "row 7"},
        "PROJECT_BEAM_INVALID_SOURCE_METADATA",
        "source_metadata",
    ),
)


@pytest.mark.parametrize(
    ("case_name", "change", "expected_code", "expected_path"),
    SERVICE_NEGATIVE_CASES,
    ids=[case[0] for case in SERVICE_NEGATIVE_CASES],
)
def test_strict_service_negative_matrix_blocks_before_calculation(
    monkeypatch: pytest.MonkeyPatch,
    case_name: str,
    change: dict[str, Any],
    expected_code: str,
    expected_path: str,
) -> None:
    del case_name
    payload = _canonical_beam()
    if "__remove__" in change:
        payload.pop(change["__remove__"])
    else:
        payload.update(change)
    calculation_calls = 0

    def forbidden_calculation(**_: Any) -> None:
        nonlocal calculation_calls
        calculation_calls += 1
        raise AssertionError("blocked input reached the calculation core")

    monkeypatch.setattr(batch.api, "design_beam_is456", forbidden_calculation)

    result = design_project_beams_v1([payload]).to_dict()

    assert calculation_calls == 0
    assert result["summary"] == {
        "total": 1,
        "valid": 0,
        "blocked": 1,
        "evaluated": 0,
        "passed": 0,
        "failed": 0,
        "held": 0,
        "intake_status": "BLOCKED",
        "calculation_status": "NOT_EVALUATED",
        "engineering_status": "NOT_EVALUATED",
        "overall_status": "BLOCKED",
        "qualified_review_required": True,
        "result_envelope": {
            "schema_version": "structural-result-envelope/v2",
            "intake_status": "BLOCKED",
            "calculation_status": "NOT_EVALUATED",
            "engineering_status": "NOT_EVALUATED",
            "review_status": "QUALIFIED_REVIEW_REQUIRED",
            "qualified_review_required": True,
            "freshness_status": "CURRENT",
            "serviceability_escalation": None,
            "overall_status": "BLOCKED",
            "issues": [],
            "result_identity": None,
        },
    }
    member = result["members"][0]
    assert member["intake_status"] == "BLOCKED"
    assert member["calculation_status"] == "NOT_EVALUATED"
    assert member["engineering_status"] == "NOT_EVALUATED"
    assert member["overall_status"] == "BLOCKED"
    assert member["calculation"] is None
    assert expected_code in _issue_codes(member)
    assert expected_path in {
        issue["path"] for issue in member["issues"] if issue["code"] == expected_code
    }


@pytest.mark.parametrize(
    "field",
    [
        "schema_version",
        "member_id",
        "b_mm",
        "D_mm",
        "d_mm",
        "mu_knm",
        "vu_kn",
        "fck_nmm2",
        "fy_nmm2",
    ],
)
def test_every_canonical_calculation_field_is_required(field: str) -> None:
    payload = _canonical_beam()
    payload.pop(field)

    validation = validate_project_beam_design_input_v1(payload)

    assert validation.is_valid is False
    assert any(
        issue.code == "PROJECT_BEAM_REQUIRED_FIELD" and issue.path == field
        for issue in validation.issues
    )


def test_complete_effective_depth_basis_is_auditable_and_resolves_depth() -> None:
    payload = _canonical_beam()
    payload.pop("d_mm")
    payload["effective_depth_basis"] = {
        "clear_cover_mm": 32.0,
        "stirrup_diameter_mm": 8.0,
        "tension_bar_diameter_mm": 16.0,
    }

    validation = validate_project_beam_design_input_v1(payload)

    assert validation.is_valid is True
    assert validation.value is not None
    assert validation.value.resolved_d_mm == pytest.approx(452.0)
    assert validation.value.effective_depth_basis is not None
    assert (
        validation.value.to_dict()["effective_depth_basis"]
        == payload["effective_depth_basis"]
    )


def test_explicit_and_derived_effective_depth_produce_same_numeric_result() -> None:
    derived = _canonical_beam(member_id="B-DERIVED")
    derived.pop("d_mm")
    derived["effective_depth_basis"] = {
        "clear_cover_mm": 32.0,
        "stirrup_diameter_mm": 8.0,
        "tension_bar_diameter_mm": 16.0,
    }

    result = design_project_beams_v1(
        [_canonical_beam(member_id="B-EXPLICIT"), derived]
    ).to_dict()

    explicit_calculation = result["members"][0]["calculation"]
    derived_calculation = result["members"][1]["calculation"]
    for key in ("flexure", "shear", "utilization_ratio", "utilizations"):
        assert explicit_calculation[key] == derived_calculation[key]


def test_derived_depth_basis_reaches_the_canonical_calculation_unchanged() -> None:
    payload = _canonical_beam(
        member_id="etabs:P5-TRIAL-HALL:101",
        mu_knm=150.0,
        vu_kn=75.0,
        source_metadata={"snapshot_sha256": "a" * 64},
    )
    payload.pop("d_mm")
    payload["effective_depth_basis"] = {
        "clear_cover_mm": 40.0,
        "stirrup_diameter_mm": 8.0,
        "tension_bar_diameter_mm": 20.0,
    }

    validation = validate_project_beam_design_input_v1(payload)
    assert validation.value is not None
    member = design_project_beams_v1([payload]).to_dict()["members"][0]
    direct = batch.api.design_beam_is456(
        units="IS456",
        case_id=payload["member_id"],
        b_mm=payload["b_mm"],
        D_mm=payload["D_mm"],
        d_mm=None,
        mu_knm=payload["mu_knm"],
        vu_kn=payload["vu_kn"],
        fck_nmm2=payload["fck_nmm2"],
        fy_nmm2=payload["fy_nmm2"],
        effective_depth_basis=validation.value.effective_depth_basis,
    )

    assert direct.effective_depth_resolution == {
        "contract_version": "effective-depth-basis/v1",
        "source": "DERIVED",
        "D_mm": 500.0,
        "d_mm": 442.0,
        "effective_depth_basis": payload["effective_depth_basis"],
    }
    assert member["calculation"]["flexure"]["ast_required"] == pytest.approx(
        direct.flexure.Ast_required
    )
    assert (
        member["result_envelope"]["result_identity"]
        == direct.result_envelope["result_identity"]
    )


@pytest.mark.parametrize(
    ("basis", "expected_code", "expected_path"),
    [
        (
            {"clear_cover_mm": 32.0, "stirrup_diameter_mm": 8.0},
            "PROJECT_BEAM_REQUIRED_FIELD",
            "effective_depth_basis.tension_bar_diameter_mm",
        ),
        (
            {
                "clear_cover_mm": 32.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 16.0,
                "assumed_offset_mm": 8.0,
            },
            "PROJECT_BEAM_UNKNOWN_FIELD",
            "effective_depth_basis.assumed_offset_mm",
        ),
        (
            {
                "clear_cover_mm": 32.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": float("inf"),
            },
            "PROJECT_BEAM_NON_FINITE",
            "effective_depth_basis.tension_bar_diameter_mm",
        ),
    ],
)
def test_effective_depth_basis_rejects_incomplete_unknown_and_non_finite_values(
    basis: dict[str, Any], expected_code: str, expected_path: str
) -> None:
    payload = _canonical_beam()
    payload.pop("d_mm")
    payload["effective_depth_basis"] = basis

    validation = validate_project_beam_design_input_v1(payload)

    assert validation.is_valid is False
    assert any(
        issue.code == expected_code and issue.path == expected_path
        for issue in validation.issues
    )


def test_duplicate_member_id_blocks_every_duplicate_without_core_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calculation_calls = 0

    def forbidden_calculation(**_: Any) -> None:
        nonlocal calculation_calls
        calculation_calls += 1
        raise AssertionError("duplicate members reached the calculation core")

    monkeypatch.setattr(batch.api, "design_beam_is456", forbidden_calculation)

    result = design_project_beams_v1(
        [_canonical_beam(member_id="DUP"), _canonical_beam(member_id="DUP")]
    ).to_dict()

    assert calculation_calls == 0
    assert result["summary"]["blocked"] == 2
    assert result["summary"]["overall_status"] == "BLOCKED"
    assert all(
        "PROJECT_BEAM_DUPLICATE_MEMBER_ID" in _issue_codes(member)
        for member in result["members"]
    )


def test_duplicate_identity_blocks_valid_twin_of_an_already_invalid_member(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calculation_calls = 0

    def forbidden_calculation(**_: Any) -> None:
        nonlocal calculation_calls
        calculation_calls += 1
        raise AssertionError("valid duplicate twin reached the calculation core")

    monkeypatch.setattr(batch.api, "design_beam_is456", forbidden_calculation)
    invalid_twin = _canonical_beam(member_id="DUP")
    invalid_twin.pop("vu_kn")

    result = design_project_beams_v1(
        [_canonical_beam(member_id="DUP"), invalid_twin]
    ).to_dict()

    assert calculation_calls == 0
    assert result["summary"]["blocked"] == 2
    assert all(
        "PROJECT_BEAM_DUPLICATE_MEMBER_ID" in _issue_codes(member)
        for member in result["members"]
    )


def test_mixed_batch_accounts_for_valid_and_blocked_members_without_pass() -> None:
    blocked = _canonical_beam(member_id="B-BLOCKED")
    blocked.pop("vu_kn")

    result = design_project_beams_v1(
        [_canonical_beam(member_id="B-VALID"), blocked]
    ).to_dict()

    assert len(result["members"]) == 2
    assert result["summary"] == {
        "total": 2,
        "valid": 1,
        "blocked": 1,
        "evaluated": 1,
        "passed": 1,
        "failed": 0,
        "held": 0,
        "intake_status": "BLOCKED",
        "calculation_status": "COMPLETED",
        "engineering_status": "PASS",
        "overall_status": "BLOCKED",
        "qualified_review_required": True,
        "result_envelope": {
            "schema_version": "structural-result-envelope/v2",
            "intake_status": "BLOCKED",
            "calculation_status": "COMPLETED",
            "engineering_status": "PASS",
            "review_status": "QUALIFIED_REVIEW_REQUIRED",
            "qualified_review_required": True,
            "freshness_status": "CURRENT",
            "serviceability_escalation": None,
            "overall_status": "BLOCKED",
            "issues": [],
            "result_identity": None,
        },
    }


def test_strict_iterator_validates_batch_but_calculates_members_lazily(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    real_design = batch.api.design_beam_is456

    def recording_design(**kwargs: Any) -> Any:
        calls.append(kwargs["case_id"])
        return real_design(**kwargs)

    monkeypatch.setattr(batch.api, "design_beam_is456", recording_design)

    results = iter(
        design_project_beams_iter_v1(
            [_canonical_beam(member_id="B1"), _canonical_beam(member_id="B2")]
        )
    )

    assert calls == []
    assert next(results).member_id == "B1"
    assert calls == ["B1"]


def test_legacy_iterator_does_not_precalculate_entire_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    real_design = batch.api.design_beam_is456

    def recording_design(**kwargs: Any) -> Any:
        calls.append(kwargs["case_id"])
        return real_design(**kwargs)

    monkeypatch.setattr(batch.api, "design_beam_is456", recording_design)
    beams = [
        {
            "id": member_id,
            "width": 300,
            "depth": 500,
            "d_mm": 452,
            "moment": 100,
            "shear": 50,
            "fck": 25,
            "fy": 500,
        }
        for member_id in ("B1", "B2")
    ]

    results = iter(design_beams_iter(beams))

    assert calls == []
    assert next(results)["data"]["beam_id"] == "B1"
    assert calls == ["B1"]


def test_empty_batch_is_blocked_and_never_passes() -> None:
    result = design_project_beams_v1([]).to_dict()

    assert result["members"] == []
    assert result["summary"]["total"] == 0
    assert result["summary"]["intake_status"] == "BLOCKED"
    assert result["summary"]["calculation_status"] == "NOT_EVALUATED"
    assert result["summary"]["engineering_status"] == "NOT_EVALUATED"
    assert result["summary"]["overall_status"] == "BLOCKED"
    assert result["summary"]["passed"] == 0


def test_explicit_zero_actions_are_valid_service_inputs() -> None:
    validation = validate_project_beam_design_input_v1(
        _canonical_beam(mu_knm=0.0, vu_kn=0.0)
    )

    assert validation.is_valid is True
    assert validation.value is not None
    assert validation.value.mu_knm == 0.0
    assert validation.value.vu_kn == 0.0


def test_accepted_pilot_beam_preserves_numerical_outcome() -> None:
    result = design_project_beams_v1([_canonical_beam(member_id="PILOT-B1")]).to_dict()

    assert result["summary"]["overall_status"] == "PASS"
    member = result["members"][0]
    assert member["intake_status"] == "VALID"
    assert member["calculation_status"] == "COMPLETED"
    assert member["engineering_status"] == "PASS"
    assert member["review_status"] == "QUALIFIED_REVIEW_REQUIRED"
    assert member["calculation"]["flexure"] == pytest.approx(
        {
            "ast_required": 554.6500059968348,
            "asc_required": 0.0,
            "mu_lim": 204.7219242624,
            "xu": 89.3602787439345,
            "is_safe": True,
        }
    )
    assert member["calculation"]["shear"]["is_safe"] is True
    assert member["calculation"]["utilization_ratio"] == pytest.approx(
        0.4884674680559672
    )


def test_source_metadata_cannot_change_calculation_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[dict[str, Any]] = []
    real_design = batch.api.design_beam_is456

    def recording_design(**kwargs: Any) -> Any:
        captured.append(deepcopy(kwargs))
        return real_design(**kwargs)

    monkeypatch.setattr(batch.api, "design_beam_is456", recording_design)
    first = _canonical_beam(source_metadata={"import": {"row": 7}})
    second = _canonical_beam(
        member_id="B2", source_metadata={"manual": {"note": "changed"}}
    )

    result = design_project_beams_v1([first, second]).to_dict()

    assert len(captured) == 2
    assert {key: value for key, value in captured[0].items() if key != "case_id"} == {
        key: value for key, value in captured[1].items() if key != "case_id"
    }
    assert (
        result["members"][0]["input"]["source_metadata"]
        != result["members"][1]["input"]["source_metadata"]
    )


def test_unsupported_units_block_before_calculation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calculation_calls = 0

    def forbidden_calculation(**_: Any) -> None:
        nonlocal calculation_calls
        calculation_calls += 1
        raise AssertionError("unsupported units reached the calculation core")

    monkeypatch.setattr(batch.api, "design_beam_is456", forbidden_calculation)

    result = design_project_beams_v1([_canonical_beam()], units="SI").to_dict()

    assert calculation_calls == 0
    assert result["summary"]["overall_status"] == "BLOCKED"
    assert "PROJECT_BEAM_UNSUPPORTED_UNITS" in _issue_codes(result["members"][0])


def test_calculation_error_is_a_stable_hold_without_raw_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing_calculation(**_: Any) -> None:
        raise RuntimeError("secret unstable core detail")

    monkeypatch.setattr(batch.api, "design_beam_is456", failing_calculation)

    result = design_project_beams_v1([_canonical_beam()]).to_dict()

    member = result["members"][0]
    assert member["intake_status"] == "VALID"
    assert member["calculation_status"] == "ERROR"
    assert member["engineering_status"] == "HOLD"
    assert member["overall_status"] == "ERROR"
    assert member["issues"] == [
        {
            "code": "PROJECT_BEAM_CALCULATION_ERROR",
            "path": "$",
            "message": "Calculation could not be completed for the validated member.",
        }
    ]
    assert "secret unstable core detail" not in str(result)


def test_legacy_alias_surface_delegates_without_structural_defaults() -> None:
    outcome = next(
        iter(
            design_beams_iter(
                [
                    {
                        "id": "B-LEGACY",
                        "width": 300,
                        "depth": 500,
                        "d_mm": 452,
                        "moment": 100,
                        "shear": 50,
                        "fck": 25,
                        "fy": 500,
                    }
                ]
            )
        )
    )

    assert outcome["success"] is True
    assert outcome["data"]["beam_id"] == "B-LEGACY"
    assert outcome["data"]["intake_status"] == "VALID"
    assert outcome["data"]["calculation_status"] == "COMPLETED"
    assert outcome["data"]["status"] == "PASS"


def test_legacy_missing_material_and_depth_values_block() -> None:
    result = design_beams(
        [{"id": "B-INCOMPLETE", "width": 300, "depth": 500, "moment": 100}]
    )

    assert result["results"] == []
    assert len(result["errors"]) == 1
    assert result["summary"]["blocked"] == 1
    assert result["summary"]["status"] == "BLOCKED"
    assert result["summary"]["is_safe"] is False
    assert {
        "d_mm",
        "vu_kn",
        "fck_nmm2",
        "fy_nmm2",
    }.issubset({issue["path"] for issue in result["errors"][0]["issues"]})


def test_legacy_conflicting_aliases_block_instead_of_using_first_value() -> None:
    result = design_beams(
        [
            {
                "id": "B-CONFLICT",
                "width": 300,
                "b_mm": 350,
                "depth": 500,
                "d_mm": 452,
                "moment": 100,
                "shear": 50,
                "fck": 25,
                "fy": 500,
            }
        ]
    )

    assert result["results"] == []
    assert "PROJECT_BEAM_ALIAS_CONFLICT" in {
        issue["code"] for issue in result["errors"][0]["issues"]
    }


def test_unsafe_shear_remains_a_completed_engineering_failure() -> None:
    result = design_project_beams_v1(
        [_canonical_beam(member_id="B-UNSAFE-SHEAR", vu_kn=600.0)]
    ).to_dict()

    member = result["members"][0]
    assert member["intake_status"] == ProjectBeamIntakeStatus.VALID
    assert member["calculation_status"] == ProjectBeamCalculationStatus.COMPLETED
    assert member["engineering_status"] == ProjectBeamEngineeringStatus.FAIL
    assert member["overall_status"] == ProjectBeamOverallStatus.FAIL
    assert member["calculation"]["flexure"]["is_safe"] is True
    assert member["calculation"]["shear"]["is_safe"] is False
    assert result["summary"]["failed"] == 1
    assert result["summary"]["overall_status"] == "FAIL"
