# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""G0-bounded IS 13920 rectangular-column confinement contract tests."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.traceability import get_clause_refs
from structural_lib.codes.is13920.column import (
    DuctileColumnResult,
    calculate_ash_required,
    calculate_confining_length,
    calculate_special_confining_spacing,
    check_column_ductility,
    check_column_geometry,
    get_max_longitudinal_steel,
    get_min_longitudinal_steel,
)


def _benchmark_kwargs() -> dict[str, object]:
    return {
        "b_mm": 400.0,
        "D_mm": 500.0,
        "clear_height_mm": 3000.0,
        "bar_dia_mm": 20.0,
        "fck": 25.0,
        "fy": 415.0,
        "Ag_mm2": 200000.0,
        "Ak_mm2": 134400.0,
        "h_mm": 420.0,
        "provided_confining_spacing_mm": 100.0,
        "provided_confining_length_mm": 500.0,
        "provided_ash_mm2": 223.0,
        "is_is13920_applicable": True,
        "applicability_basis": "Project seismic design basis",
        "is_rectangular_section": True,
    }


def test_geometry_accepts_exact_dimension_and_ratio_boundaries():
    valid, message, errors = check_column_geometry(300.0, 750.0)
    assert valid is True
    assert message == "OK"
    assert errors == []


@pytest.mark.parametrize(
    ("b_mm", "D_mm", "code"),
    [(299.999, 500.0, "E_DUCTILE_COL_001"), (300.0, 750.001, "E_DUCTILE_COL_002")],
)
def test_geometry_rejects_unsafe_boundary_inputs(b_mm: float, D_mm: float, code: str):
    valid, _message, errors = check_column_geometry(b_mm, D_mm)
    assert valid is False
    assert [error.code for error in errors] == [code]


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_geometry_rejects_non_finite_values(value: float):
    with pytest.raises(ValueError, match="finite"):
        check_column_geometry(value, 500.0)


def test_longitudinal_limits_are_truthfully_is456_companion_values():
    assert get_min_longitudinal_steel() == pytest.approx(0.8)
    assert get_max_longitudinal_steel() == pytest.approx(4.0)
    assert get_clause_refs(get_min_longitudinal_steel) == ["26.5.3.1(a)"]
    assert get_clause_refs(get_max_longitudinal_steel) == ["26.5.3.1(a)"]
    assert get_min_longitudinal_steel._clause_standard == "IS 456"  # type: ignore[attr-defined]
    assert get_max_longitudinal_steel._clause_standard == "IS 456"  # type: ignore[attr-defined]


def test_amended_confinement_spacing_and_length_benchmark():
    assert calculate_special_confining_spacing(400.0, 20.0) == pytest.approx(100.0)
    assert calculate_confining_length(500.0, 3000.0) == pytest.approx(500.0)
    assert get_clause_refs(calculate_special_confining_spacing) == ["7.6.1"]
    assert get_clause_refs(calculate_confining_length) == ["7.6.1"]


@pytest.mark.parametrize(
    ("function", "args"),
    [
        (calculate_special_confining_spacing, (math.nan, 20.0)),
        (calculate_confining_length, (500.0, math.inf)),
    ],
)
def test_confinement_limits_reject_non_finite_values(function, args):
    with pytest.raises(ValueError, match="finite"):
        function(*args)


def test_rectangular_ash_first_expression_governs_benchmark():
    ash = calculate_ash_required(100.0, 420.0, 25.0, 415.0, 200000.0, 134400.0)
    assert ash == pytest.approx(222.28915662650604)
    assert get_clause_refs(calculate_ash_required) == ["7.6.1(c)(2)"]


def test_rectangular_ash_second_expression_is_not_omitted():
    ash = calculate_ash_required(100.0, 920.0, 25.0, 415.0, 1_000_000.0, 846400.0)
    assert ash == pytest.approx(277.10843373493975)


@pytest.mark.parametrize(
    ("field", "value"),
    [("s_mm", math.nan), ("fck", math.inf), ("Ak_mm2", -1.0)],
)
def test_ash_rejects_invalid_numeric_inputs(field: str, value: float):
    kwargs = {
        "s_mm": 100.0,
        "h_mm": 420.0,
        "fck": 25.0,
        "fy": 415.0,
        "Ag_mm2": 200000.0,
        "Ak_mm2": 134400.0,
    }
    kwargs[field] = value
    with pytest.raises(ValueError):
        calculate_ash_required(**kwargs)


def test_explicit_benchmark_passes_bounded_contract():
    result = check_column_ductility(**_benchmark_kwargs())
    assert isinstance(result, DuctileColumnResult)
    assert result.is_geometry_valid is True
    assert result.confining_spacing_mm == pytest.approx(100.0)
    assert result.confining_length_mm == pytest.approx(500.0)
    assert result.ash_required_mm2 == pytest.approx(222.28915662650604)
    assert result.governing_ash_expression == "0.18_CORE_RATIO"
    assert result.spacing_passed is True
    assert result.length_passed is True
    assert result.ash_passed is True
    assert result.is_compliant is True
    assert result.errors == []


def test_second_expression_is_reported_as_governing():
    kwargs = _benchmark_kwargs()
    kwargs.update(
        b_mm=1000.0,
        D_mm=1000.0,
        clear_height_mm=3000.0,
        Ag_mm2=1_000_000.0,
        Ak_mm2=846400.0,
        h_mm=920.0,
        provided_confining_length_mm=1000.0,
        provided_ash_mm2=278.0,
    )
    result = check_column_ductility(**kwargs)
    assert result.ash_expression_2_mm2 == pytest.approx(277.10843373493975)
    assert result.ash_required_mm2 == pytest.approx(277.10843373493975)
    assert result.governing_ash_expression == "0.05_MINIMUM"
    assert result.is_compliant is True


@pytest.mark.parametrize(
    ("field", "value", "passed_field", "code"),
    [
        ("provided_confining_spacing_mm", 101.0, "spacing_passed", "E_DUCTILE_COL_006"),
        ("provided_confining_length_mm", 499.0, "length_passed", "E_DUCTILE_COL_007"),
        ("provided_ash_mm2", 222.0, "ash_passed", "E_DUCTILE_COL_005"),
    ],
)
def test_inadequate_provided_detail_fails_contract(
    field: str, value: float, passed_field: str, code: str
):
    kwargs = _benchmark_kwargs()
    kwargs[field] = value
    result = check_column_ductility(**kwargs)
    assert getattr(result, passed_field) is False
    assert result.is_compliant is False
    assert code in [error.code for error in result.errors]


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("is_is13920_applicable", False, "applicability"),
        ("is_rectangular_section", False, "rectangular"),
        ("applicability_basis", "  ", "applicability_basis"),
    ],
)
def test_applicability_and_topology_fail_closed(field: str, value: object, match: str):
    kwargs = _benchmark_kwargs()
    kwargs[field] = value
    with pytest.raises(ValueError, match=match):
        check_column_ductility(**kwargs)


def test_applicability_boolean_rejects_truthy_override():
    kwargs = _benchmark_kwargs()
    kwargs["is_is13920_applicable"] = 1
    with pytest.raises(TypeError, match="bool"):
        check_column_ductility(**kwargs)


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("Ag_mm2", 199999.0, "must equal"),
        ("Ak_mm2", 200000.0, "less than"),
        ("h_mm", 501.0, "cannot exceed"),
        ("provided_ash_mm2", math.nan, "finite"),
    ],
)
def test_actual_geometry_and_provided_inputs_are_validated(
    field: str, value: float, match: str
):
    kwargs = _benchmark_kwargs()
    kwargs[field] = value
    with pytest.raises(ValueError, match=match):
        check_column_ductility(**kwargs)


def test_invalid_geometry_returns_bounded_noncompliance():
    kwargs = _benchmark_kwargs()
    kwargs.update(
        b_mm=200.0,
        D_mm=500.0,
        Ag_mm2=100000.0,
        Ak_mm2=70000.0,
    )
    result = check_column_ductility(**kwargs)
    assert result.is_geometry_valid is False
    assert result.is_compliant is False
    assert result.governing_ash_expression == "NOT_EVALUATED_INVALID_GEOMETRY"
    assert [error.code for error in result.errors] == ["E_DUCTILE_COL_001"]


def test_result_provenance_and_compliance_scope_are_explicit():
    result = check_column_ductility(**_benchmark_kwargs())
    assert result.standard == "IS 13920:2016"
    assert "Amendment 1" in result.source_reference
    assert "Amendment 2" in result.source_reference
    assert result.clause_refs == ("7.1.1", "7.1.2", "7.6.1", "7.6.1(c)(2)")
    assert result.companion_standard == "IS 456:2000"
    assert result.companion_clause_refs == ("26.5.3.1(a)",)
    assert result.result_kind == "BOUNDED_RECTANGULAR_SPECIAL_CONFINEMENT_CHECK"
    assert result.compliance_scope == "GEOMETRY_AND_PROVIDED_SPECIAL_CONFINEMENT"
    assert result.longitudinal_reinforcement_status.startswith("NOT_EVALUATED")
    assert result.applicability_status == "CONFIRMED_BY_CALLER"
