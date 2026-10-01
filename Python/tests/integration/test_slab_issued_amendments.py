# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Independent issued-amendment boundaries through supported slab callers.

Primary source SHA-256:
964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264.
A3 PDF 112 / printed 2: distribution spacing is min(5d, 300 mm).
A5 PDF 125 / printed 5: a solid slab uses half the Table 20 maximum.
Table 20 PDF 74 / printed 73: M20 has 2.8 N/mm2, hence a 1.4 N/mm2 slab cap.

The fixtures use a 1000 mm strip, D=150 mm, d=125 mm and Fe415. Fourteen-mm
distribution bars at 400 mm provide 384.84510006475 mm2/m, exceeding the
independent minimum 0.0012 * 1000 * 150 = 180 mm2/m. Their diameter is below
D/8=18.75 mm. The 300/301/400 mm cases therefore isolate the spacing limit.
D=75 mm, d=50 mm and eight-mm bars isolate the 5d=250 mm boundary.

For shear, Vu=175/250 kN gives tau=1.4/2.0 N/mm2. Short 500 mm spans keep
all composed moments below the independent rectangular M20/Fe415 limit
0.36 * 0.48 * (1 - 0.42 * 0.48) * 20 * 1000 * 125**2 / 1e6 = 43.1136 kNm.
No expected numerical value is obtained from a production table or solver.
These cases do not establish complete engineering or construction approval.
"""

from __future__ import annotations

from typing import Any

import pytest

from structural_lib.codes.is456 import tables
from structural_lib.codes.is456.slab.detailing import (
    ProvidedSlabBars,
    check_slab_reinforcement_region,
)
from structural_lib.codes.is456.slab.shear import (
    SlabShearInput,
    SlabShearStatus,
    check_solid_slab_one_way_shear,
)
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.design.is456 import slab as slab_facade
from structural_lib.services import api

_SPACING_SOURCE = "IS 456:2000 Cl. 26.3.3(b)(2), Amendment 3 (August 2007)"
_SHEAR_SOURCE = "IS 456:2000 Cl. 40.2.3.1, Amendment 5 (July 2019)"
_COMPOSED_EXPORTS = (
    "design_complete_one_way_slab_is456",
    "design_continuous_one_way_slab_is456",
    "design_continuous_one_way_slab_builtin_is456",
    "design_two_way_slab_panel_is456",
    "design_two_way_slab_panel_builtin_is456",
)
_FACADES = ("one_way", "continuous_one_way", "two_way")
_SPACING_BOUNDARIES = (
    (125.0, 150.0, 14.0, 300.0, 300.0, True),
    (125.0, 150.0, 14.0, 301.0, 300.0, False),
    (125.0, 150.0, 14.0, 400.0, 300.0, False),
    (50.0, 75.0, 8.0, 250.0, 250.0, True),
    (50.0, 75.0, 8.0, 251.0, 250.0, False),
)
_SHEAR_BOUNDARIES = (
    (1.4, 175.0, SlabShearStatus.INCREASE_DEPTH_OR_ENGINEER_REINFORCEMENT),
    (2.0, 250.0, SlabShearStatus.EXCEEDS_MAXIMUM_SHEAR_STRESS),
)


def _serviceability() -> dict[str, Any]:
    return {
        "reviewed_base_span_depth_limit": 20.0,
        "reviewed_aggregate_modification_factor": 1.0,
        "serviceability_limit_source_reference": "AMD-SLAB-BOUNDARY-SLS-01",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:AMD-SLAB-01",
        "qualified_serviceability_acceptance_acknowledged": True,
    }


def _one_way_arguments(
    *,
    spacing: float = 300.0,
    load: float = 10.0,
    depth: float = 125.0,
    thickness: float = 150.0,
    diameter: float = 14.0,
) -> dict[str, Any]:
    return {
        "short_effective_span_mm": 500.0,
        "long_effective_span_mm": 1500.0,
        "thickness_mm": thickness,
        "d_mm": depth,
        "strip_width_mm": 1000.0,
        "factored_area_load_kn_per_m2": load,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "main_bar_diameter_mm": diameter,
        "main_bar_spacing_mm": 100.0,
        "distribution_bar_diameter_mm": diameter,
        "distribution_bar_spacing_mm": spacing,
    }


def _continuous_arguments(
    *,
    spacing: float,
    load: float,
    builtin: bool,
) -> dict[str, Any]:
    values: dict[str, Any] = {
        "short_effective_span_mm": 500.0,
        "long_effective_span_mm": 1500.0,
        "thickness_mm": 150.0,
        "d_mm": 125.0,
        "strip_width_mm": 1000.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "number_of_spans": 3,
        "maximum_span_variation_percent": 0.0,
        "uniform_cross_section_acknowledged": True,
        "substantially_uniform_load_acknowledged": True,
        "redistribution_applied": False,
        "positive_bar_diameter_mm": 14.0,
        "positive_bar_spacing_mm": 100.0,
        "negative_bar_diameter_mm": 14.0,
        "negative_bar_spacing_mm": 100.0,
        "distribution_bar_diameter_mm": 14.0,
        "distribution_bar_spacing_mm": spacing,
        **_serviceability(),
    }
    if builtin:
        values.update(
            factored_dead_and_fixed_imposed_load_kn_per_m2=load,
            factored_nonfixed_imposed_load_kn_per_m2=0.0,
            positive_location="end_span_positive",
            negative_location="next_to_end_support_negative",
            shear_location="end_support",
        )
    else:
        values.update(
            factored_area_load_kn_per_m2=load,
            positive_moment_coefficient=1.0 / 12.0,
            negative_moment_coefficient=1.0 / 10.0,
            shear_coefficient=0.4,
            coefficient_source_reference="AMD-SLAB-TABLE12-13-01",
            coefficient_source_is_approved=True,
            qualified_coefficient_acceptance_reference="review:AMD-SLAB-COEFF-01",
            qualified_coefficient_acceptance_acknowledged=True,
        )
    return values


def _two_way_arguments(
    *,
    spacing: float,
    load: float,
    builtin: bool,
) -> dict[str, Any]:
    values: dict[str, Any] = {
        "x_effective_span_mm": 500.0,
        "y_effective_span_mm": 750.0,
        "thickness_mm": 150.0,
        "x_min_edge": "discontinuous",
        "x_max_edge": "continuous",
        "y_min_edge": "discontinuous",
        "y_max_edge": "continuous",
        "corner_lift_condition": "restrained",
        "factored_area_load_kn_per_m2": load,
        "d_x_mm": 125.0,
        "d_y_mm": 125.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "x_positive_bar_diameter_mm": 14.0,
        "x_positive_bar_spacing_mm": 100.0,
        "x_negative_bar_diameter_mm": 14.0,
        "x_negative_bar_spacing_mm": 100.0,
        "y_positive_bar_diameter_mm": 14.0,
        "y_positive_bar_spacing_mm": 100.0,
        "y_negative_bar_diameter_mm": 14.0,
        "y_negative_bar_spacing_mm": 100.0,
        "edge_strip_bar_diameter_mm": 14.0,
        "edge_strip_bar_spacing_mm": spacing,
        "torsion_bar_diameter_mm": 14.0,
        "torsion_bar_spacing_mm": 100.0,
        **_serviceability(),
    }
    if not builtin:
        values.update(
            support_topology_kind="two_adjacent_edges_discontinuous",
            alpha_x_negative=0.075,
            alpha_x_positive=0.056,
            alpha_y_negative=0.047,
            alpha_y_positive=0.035,
            coefficient_source_reference="AMD-SLAB-TABLE26-CASE4-01",
            coefficient_source_is_approved=True,
            qualified_coefficient_acceptance_reference="review:AMD-SLAB-COEFF-01",
            qualified_coefficient_acceptance_acknowledged=True,
        )
    return values


def _composed_case(export: str, *, spacing: float = 300.0, tau: float | None = None):
    if export == "design_complete_one_way_slab_is456":
        load = 10.0 if tau is None else {1.4: 700.0, 2.0: 1000.0}[tau]
        values = {**_one_way_arguments(spacing=spacing, load=load), **_serviceability()}
    elif "continuous" in export:
        # V=0.4*w*0.5, with w=875/1250, gives V=175/250 kN per metre.
        load = 10.0 if tau is None else {1.4: 875.0, 2.0: 1250.0}[tau]
        values = _continuous_arguments(
            spacing=spacing, load=load, builtin="builtin" in export
        )
    else:
        # V=w*0.5/2, with w=700/1000, gives V=175/250 kN per metre.
        load = 10.0 if tau is None else {1.4: 700.0, 2.0: 1000.0}[tau]
        values = _two_way_arguments(
            spacing=spacing, load=load, builtin="builtin" in export
        )
    return getattr(api, export)(**values)


def _distribution(result):
    if hasattr(result, "reinforcement"):
        return result.reinforcement.detailing
    if hasattr(result, "distribution_reinforcement"):
        return result.distribution_reinforcement
    return result.panel.edge_strip_reinforcement


def _spacing_source_refs(result) -> tuple[str, ...]:
    if hasattr(result, "reinforcement"):
        return result.reinforcement.detailing.source_refs
    if hasattr(result, "distribution_reinforcement"):
        return result.flexure.source_refs
    return result.panel.source_refs


def _shear(result):
    return result.panel.shear if hasattr(result, "panel") else result.shear


def _assert_distribution(result, *, spacing_passed: bool) -> None:
    distribution = _distribution(result)
    if hasattr(distribution, "governing_checks"):
        checks = {check.check_id: check for check in distribution.governing_checks}
        assert distribution.maximum_distribution_spacing_mm == 300.0
        assert checks["P8-DIST-STEEL-01"].passed is True
        assert checks["P8-DIST-DIA-01"].passed is True
        assert checks["P8-DIST-SPACING-01"].passed is spacing_passed
        assert all(
            check.passed
            for check in distribution.governing_checks
            if check.check_id != "P8-DIST-SPACING-01"
        )
        assert distribution.is_detailing_adequate is spacing_passed
    else:
        assert distribution.maximum_spacing_mm == 300.0
        assert distribution.area_passed is True
        assert distribution.diameter_passed is True
        assert distribution.spacing_passed is spacing_passed
        assert distribution.is_adequate is spacing_passed
    assert _SPACING_SOURCE in _spacing_source_refs(result)


def _facade_case(facade: str, *, spacing: float, tau: float | None = None):
    identity = {"family_id": "solid_slab", "case_id": f"AMD-SLAB-{facade}"}
    materials = {"fck_nmm2": 20.0, "fy_nmm2": 415.0}
    serviceability = _serviceability()
    if facade == "one_way":
        load = 10.0 if tau is None else {1.4: 700.0, 2.0: 1000.0}[tau]
        request = slab_facade.input_one_way(
            identity=identity,
            geometry={
                "short_effective_span_mm": 500.0,
                "long_effective_span_mm": 1500.0,
                "thickness_mm": 150.0,
                "effective_depth_mm": 125.0,
                "strip_width_mm": 1000.0,
            },
            actions={"factored_area_load_kn_per_m2": load},
            materials=materials,
            reinforcement={
                "main_bar_diameter_mm": 14.0,
                "main_bar_spacing_mm": 100.0,
                "distribution_bar_diameter_mm": 14.0,
                "distribution_bar_spacing_mm": spacing,
            },
            serviceability_evidence=serviceability,
        )
    elif facade == "continuous_one_way":
        load = 10.0 if tau is None else {1.4: 875.0, 2.0: 1250.0}[tau]
        values = _continuous_arguments(spacing=spacing, load=load, builtin=True)
        request = slab_facade.input_continuous_one_way(
            identity=identity,
            geometry={
                "short_effective_span_mm": 500.0,
                "long_effective_span_mm": 1500.0,
                "thickness_mm": 150.0,
                "effective_depth_mm": 125.0,
                "strip_width_mm": 1000.0,
                "number_of_spans": 3,
                "maximum_span_variation_percent": 0.0,
                "uniform_cross_section_acknowledged": True,
            },
            actions={
                key: values[key]
                for key in (
                    "factored_dead_and_fixed_imposed_load_kn_per_m2",
                    "factored_nonfixed_imposed_load_kn_per_m2",
                    "positive_location",
                    "negative_location",
                    "shear_location",
                    "substantially_uniform_load_acknowledged",
                    "redistribution_applied",
                )
            },
            materials=materials,
            reinforcement={
                key: values[key]
                for key in (
                    "positive_bar_diameter_mm",
                    "positive_bar_spacing_mm",
                    "negative_bar_diameter_mm",
                    "negative_bar_spacing_mm",
                    "distribution_bar_diameter_mm",
                    "distribution_bar_spacing_mm",
                )
            },
            serviceability_evidence=serviceability,
        )
    else:
        load = 10.0 if tau is None else {1.4: 700.0, 2.0: 1000.0}[tau]
        values = _two_way_arguments(spacing=spacing, load=load, builtin=True)
        request = slab_facade.input_two_way(
            identity=identity,
            geometry={
                key: values[key]
                for key in (
                    "x_effective_span_mm",
                    "y_effective_span_mm",
                    "thickness_mm",
                    "d_x_mm",
                    "d_y_mm",
                    "x_min_edge",
                    "x_max_edge",
                    "y_min_edge",
                    "y_max_edge",
                    "corner_lift_condition",
                )
            },
            actions={"factored_area_load_kn_per_m2": load},
            materials=materials,
            reinforcement={
                key: value for key, value in values.items() if "_bar_" in key
            },
            serviceability_evidence=serviceability,
        )
    return getattr(slab_facade, "design_" + facade)(request)


@pytest.mark.parametrize(
    "depth,thickness,diameter,spacing,limit,passed", _SPACING_BOUNDARIES
)
def test_basic_one_way_distribution_spacing_uses_issued_amendment(
    depth, thickness, diameter, spacing, limit, passed
) -> None:
    result = api.design_one_way_slab_is456(
        **_one_way_arguments(
            spacing=spacing, depth=depth, thickness=thickness, diameter=diameter
        )
    )
    detailing = result.detailing
    assert detailing is not None, "spacing benchmark must reach the detailing owner"
    checks = {check.check_id: check for check in detailing.governing_checks}
    assert detailing.maximum_distribution_spacing_mm == limit
    assert checks["P8-DIST-SPACING-01"].passed is passed
    assert all(
        check.passed
        for check in detailing.governing_checks
        if check.check_id != "P8-DIST-SPACING-01"
    )
    assert result.is_detailing_adequate is passed
    assert _SPACING_SOURCE in detailing.source_refs


@pytest.mark.parametrize(
    "depth,thickness,diameter,spacing,limit,passed", _SPACING_BOUNDARIES
)
def test_shared_distribution_region_retains_depth_and_absolute_limits(
    depth, thickness, diameter, spacing, limit, passed
) -> None:
    region = check_slab_reinforcement_region(
        region_id="AMD3-distribution-independent",
        required_for_moment_mm2_per_m=0.0,
        bars=ProvidedSlabBars(diameter, spacing),
        overall_depth_mm=thickness,
        effective_depth_mm=depth,
        fy_n_per_mm2=415.0,
        distribution_only=True,
    )
    assert region.maximum_spacing_mm == limit
    assert region.area_passed is True
    assert region.diameter_passed is True
    assert region.spacing_passed is passed
    assert region.is_adequate is passed
    if spacing == 400.0:
        assert region.minimum_required_mm2_per_m == 180.0
        assert region.provided_mm2_per_m == pytest.approx(384.84510006475)


@pytest.mark.parametrize("export", _COMPOSED_EXPORTS)
@pytest.mark.parametrize(
    "spacing,passed", ((300.0, True), (301.0, False), (400.0, False))
)
def test_all_composed_exports_propagate_distribution_spacing(
    export: str, spacing: float, passed: bool
) -> None:
    result = _composed_case(export, spacing=spacing)
    _assert_distribution(result, spacing_passed=passed)
    shear = _shear(result)
    assert shear.is_safe_without_shear_reinforcement is True
    assert shear.tau_c_max_n_per_mm2 == 1.4
    assert _SHEAR_SOURCE in shear.source_refs
    assert result.serviceability.is_satisfied is True
    assert result.complete_engineering_design_approved is False


@pytest.mark.parametrize("tau,force,status", _SHEAR_BOUNDARIES)
def test_solid_slab_shear_equality_and_exceedance_use_half_table_20(
    tau: float, force: float, status: SlabShearStatus
) -> None:
    result = check_solid_slab_one_way_shear(
        SlabShearInput(
            factored_shear_kn=force,
            strip_width_mm=1000.0,
            effective_depth_mm=125.0,
            overall_depth_mm=150.0,
            fck_n_per_mm2=20.0,
            tension_reinforcement_mm2=1539.380400259,
            uniformly_distributed_load_only=True,
            beam_or_wall_supported=True,
        )
    )
    assert result.tau_v_n_per_mm2 == pytest.approx(tau)
    assert result.tau_c_max_n_per_mm2 == 1.4
    assert result.status is status
    assert result.is_safe_without_shear_reinforcement is False
    assert result.shear_reinforcement_design_status == "not_automatically_designed"
    assert _SHEAR_SOURCE in result.source_refs


@pytest.mark.parametrize("export", _COMPOSED_EXPORTS)
@pytest.mark.parametrize("tau,force,status", _SHEAR_BOUNDARIES)
def test_all_composed_exports_reach_the_amended_shear_classification(
    export: str, tau: float, force: float, status: SlabShearStatus
) -> None:
    result = _composed_case(export, tau=tau)
    _assert_distribution(result, spacing_passed=True)
    shear = _shear(result)
    assert shear.tau_v_n_per_mm2 == pytest.approx(force * 1000.0 / 125000.0)
    assert shear.tau_c_max_n_per_mm2 == 1.4
    assert shear.status is status
    assert shear.is_safe_without_shear_reinforcement is False
    assert shear.shear_reinforcement_design_status == "not_automatically_designed"
    assert _SHEAR_SOURCE in shear.source_refs
    assert result.complete_engineering_design_approved is False


@pytest.mark.parametrize("facade", _FACADES)
@pytest.mark.parametrize(
    "spacing,passed", ((300.0, True), (301.0, False), (400.0, False))
)
def test_three_facades_propagate_spacing_into_engineering_disposition(
    facade: str, spacing: float, passed: bool
) -> None:
    result = _facade_case(facade, spacing=spacing)
    _assert_distribution(result.calculation, spacing_passed=passed)
    assert result.engineering_status is (
        EngineeringStatus.PASS if passed else EngineeringStatus.FAIL
    )
    assert result.is_safe is passed
    assert result.qualified_review_required is True
    assert "structural_lib.services.slab_api" in result.provenance
    serialized = result.to_dict()
    assert serialized["calculation"]["complete_engineering_design_approved"] is False
    assert _SPACING_SOURCE in _spacing_source_refs(result.calculation)
    assert _SHEAR_SOURCE in _shear(result.calculation).source_refs


@pytest.mark.parametrize("facade", _FACADES)
@pytest.mark.parametrize("tau,force,status", _SHEAR_BOUNDARIES)
def test_three_facades_preserve_unsafe_shear_and_amendment_provenance(
    facade: str, tau: float, force: float, status: SlabShearStatus
) -> None:
    result = _facade_case(facade, spacing=300.0, tau=tau)
    _assert_distribution(result.calculation, spacing_passed=True)
    shear = _shear(result.calculation)
    assert shear.tau_v_n_per_mm2 == pytest.approx(force * 1000.0 / 125000.0)
    assert shear.tau_c_max_n_per_mm2 == 1.4
    assert shear.status is status
    assert shear.is_safe_without_shear_reinforcement is False
    assert result.engineering_status is EngineeringStatus.FAIL
    assert result.is_safe is False
    assert result.calculation.complete_engineering_design_approved is False
    assert result.qualified_review_required is True
    assert _SHEAR_SOURCE in shear.source_refs
    assert "structural_lib.services.slab_api" in result.provenance
    serialized = result.to_dict()
    if facade == "two_way":
        serialized_shear = serialized["calculation"]["panel"]["shear"]
    else:
        serialized_shear = serialized["calculation"]["shear"]
    assert serialized_shear["tau_c_max_n_per_mm2"] == 1.4
    assert serialized_shear["status"] == status.value
    assert _SHEAR_SOURCE in serialized_shear["source_refs"]


def test_shared_table_20_retains_the_primary_m20_value() -> None:
    assert tables.get_tc_max_value(20.0) == 2.8
