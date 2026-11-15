# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Check declared slab combinations using the existing single-row owners."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from typing import Literal

from structural_lib.codes.is456.slab._flexure import rectangular_limiting_moment_knm
from structural_lib.codes.is456.slab.built_in_coefficients import (
    resolve_builtin_one_way_continuous_coefficients,
    resolve_builtin_two_way_panel_coefficients,
)
from structural_lib.codes.is456.slab.coefficients import (
    OneWayContinuousCoefficientSet,
    TwoWayPanelCoefficientSet,
)
from structural_lib.codes.is456.slab.detailing import (
    ProvidedSlabBars,
    SlabReinforcementRegionResult,
)
from structural_lib.codes.is456.slab.models import (
    SlabCapacityFailureResult,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.slab.one_way_continuous import (
    ContinuousOneWaySlabInput,
    _ContinuousSlabCapacityExceededError,
)
from structural_lib.codes.is456.slab.serviceability import (
    SlabServiceabilityInput,
    SlabServiceabilityResult,
    check_slab_span_depth_serviceability,
)
from structural_lib.codes.is456.slab.shear import SlabShearResult
from structural_lib.codes.is456.slab.topology import (
    CornerLiftCondition,
    OrientedSlabPanelGeometry,
    SlabEdgeContinuity,
    SlabSupportTopology,
    SlabSupportTopologyKind,
)
from structural_lib.codes.is456.slab.two_way_complete import (
    TwoWayPanelDesignInput,
    _support_shear_demand_kn_per_m,
    design_two_way_slab_panel,
)
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    StructuralIssueV1,
)
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f1 import SlabServiceabilityEvidenceV1
from structural_lib.services.contracts.slab_action_set import (
    BuiltinOneWaySlabCoefficientBasisV1,
    BuiltinTwoWaySlabCoefficientBasisV1,
    ContinuousOneWaySlabActionSetInputV1,
    OneWaySlabActionRowInputV1,
    SlabActionSetInputV1,
    TwoWaySlabActionRowInputV1,
    TwoWaySlabActionSetInputV1,
)
from structural_lib.services.slab_api import (
    ContinuousOneWaySlabDesignResult,
    TwoWaySlabPanelWorkflowResult,
    _check_continuous_one_way_slab_strength,
    _ContinuousOneWaySlabStrengthResult,
)

_WORKFLOW = "is456.slab.supplied-action-set/v1"
_SERVICE = "reviewed_span_depth"
_CheckStatus = Literal["PASS", "FAIL", "HOLD", "NOT_APPLICABLE"]
_RowInput = OneWaySlabActionRowInputV1 | TwoWaySlabActionRowInputV1
_Coefficients = OneWayContinuousCoefficientSet | TwoWayPanelCoefficientSet
_OwnerResult = (
    ContinuousOneWaySlabDesignResult
    | _ContinuousOneWaySlabStrengthResult
    | TwoWaySlabPanelWorkflowResult
    | SlabCapacityFailureResult
)


@dataclass(frozen=True)
class SlabActionCheckV1:
    """Comparable utilization and the owning check's disposition."""

    demand: float | None
    limit: float | None
    utilization: float | None
    status: _CheckStatus
    reason: str | None = None


@dataclass(frozen=True)
class SlabActionRowResultV1:
    """One complete caller row and its checked actions and outcomes."""

    input: _RowInput
    coefficients: _Coefficients
    signed_moments_knm_per_m: dict[str, float]
    support_shear_magnitude_kn_per_m: float | None
    checks: dict[str, SlabActionCheckV1]
    uls: EngineeringStatus
    reviewed_service: EngineeringStatus
    owner_result: _OwnerResult


@dataclass(frozen=True)
class SlabActionSetResultV1:
    """Checked rows, declared coverage and per-check governing row IDs."""

    coverage: Literal["COMPLETE", "HOLD"]
    uls: EngineeringStatus
    reviewed_service: EngineeringStatus
    missing_required_row_ids: tuple[str, ...]
    rows: dict[str, SlabActionRowResultV1]
    governing_ids: dict[str, str | None]

    @property
    def governing_rows(self) -> dict[str, SlabActionRowResultV1 | None]:
        """Resolve each governing ID to its full row without recombining actions."""
        return {
            check: self.rows[row_id] if row_id is not None else None
            for check, row_id in self.governing_ids.items()
        }


def load_action_set(
    value: Mapping[str, object] | SlabActionSetInputV1,
) -> SlabActionSetInputV1:
    """Load one validated set of declared slab action rows.

    Parameters
    ----------
    value : Mapping[str, object] or SlabActionSetInputV1
        Decoded request or typed input for a continuous one-way strip or an
        oriented two-way panel. All rows share the same physical revisions.

    Returns
    -------
    SlabActionSetInputV1
        Strict request for :func:`check_action_set`.

    Raises
    ------
    InputContractError
        Invalid shape, duplicate row IDs, undeclared rows or unsupported input.

    Examples
    --------
    See the frozen B02 and B04 requests in the supplied slab action cookbook.

    Limitations
    -----------
    The continuous strip is one metre wide. The caller declares the required
    combination IDs and supplies each UDL and its applicable coefficient basis.

    Provenance
    ----------
    Preserves caller identities, revision fields, row order and typed
    coefficient basis for the existing slab owners.
    """
    if isinstance(
        value, (ContinuousOneWaySlabActionSetInputV1, TwoWaySlabActionSetInputV1)
    ):
        return value
    kind = value.get("kind") if isinstance(value, Mapping) else None
    if kind == "continuous_one_way":
        return model_validate_or_error(ContinuousOneWaySlabActionSetInputV1, value)
    if kind == "two_way_panel":
        return model_validate_or_error(TwoWaySlabActionSetInputV1, value)
    raise InputContractError(
        (
            InputIssueV1(
                code="ENUM_VALUE_INVALID",
                path="kind",
                message="kind must be continuous_one_way or two_way_panel",
            ),
        )
    )


def _ratio(demand: float, limit: float, passed: bool) -> SlabActionCheckV1:
    return SlabActionCheckV1(
        demand,
        limit,
        demand / limit if limit > 0 else None,
        "PASS" if passed else "FAIL",
    )


def _bar_checks(
    checks: dict[str, SlabActionCheckV1],
    region: str,
    value: SlabReinforcementRegionResult,
    diameter: float,
    spacing: float,
) -> None:
    checks[f"{region}.area"] = _ratio(
        value.governing_required_mm2_per_m, value.provided_mm2_per_m, value.area_passed
    )
    checks[f"{region}.diameter"] = _ratio(
        diameter, value.maximum_diameter_mm, value.diameter_passed
    )
    checks[f"{region}.spacing"] = _ratio(
        spacing, value.maximum_spacing_mm, value.spacing_passed
    )


def _shear_check(shear: SlabShearResult) -> SlabActionCheckV1:
    return _ratio(
        shear.tau_v_n_per_mm2,
        min(shear.design_tau_c_n_per_mm2, shear.tau_c_max_n_per_mm2),
        shear.is_safe_without_shear_reinforcement,
    )


def _reviewed_service(
    evidence: SlabServiceabilityEvidenceV1 | None, span_mm: float, depth_mm: float
) -> SlabServiceabilityResult | None:
    if evidence is None:
        return None
    return check_slab_span_depth_serviceability(
        SlabServiceabilityInput(
            effective_span_mm=span_mm,
            effective_depth_mm=depth_mm,
            reviewed_base_span_depth_limit=evidence.reviewed_base_span_depth_limit,
            reviewed_aggregate_modification_factor=evidence.reviewed_aggregate_modification_factor,
            limit_source_reference=evidence.serviceability_limit_source_reference,
            limit_source_is_approved=evidence.serviceability_limit_source_is_approved,
            qualified_acceptance_reference=evidence.qualified_serviceability_acceptance_reference,
            qualified_acceptance_acknowledged=evidence.qualified_serviceability_acceptance_acknowledged,
        )
    )


def _checked_row(
    row: _RowInput,
    coefficients: _Coefficients,
    moments: dict[str, float],
    shear: float | None,
    checks: dict[str, SlabActionCheckV1],
    owner: _OwnerResult,
    service: SlabServiceabilityResult | None,
) -> SlabActionRowResultV1:
    uls = _status(check.status for check in checks.values())
    service_check = (
        SlabActionCheckV1(
            None, None, None, "HOLD", "Reviewed span/depth evidence is unavailable."
        )
        if service is None
        else _ratio(
            service.actual_span_depth_ratio,
            service.reviewed_modified_span_depth_limit,
            service.is_satisfied,
        )
    )
    return SlabActionRowResultV1(
        row,
        coefficients,
        moments,
        shear,
        {**checks, _SERVICE: service_check},
        uls,
        EngineeringStatus(service_check.status),
        owner,
    )


def _capacity_failure(
    row: _RowInput,
    coefficients: _Coefficients,
    failure: SlabCapacityFailureResult,
    region: str,
) -> SlabActionRowResultV1:
    magnitude = failure.factored_moment_knm
    moment = -magnitude if "negative" in region else magnitude
    return _checked_row(
        row,
        coefficients,
        {region: moment},
        None,
        {
            f"{region}.section_flexure": SlabActionCheckV1(
                magnitude,
                failure.limiting_moment_knm,
                failure.utilization_ratio,
                "FAIL",
                failure.result_envelope.issues[0].message,
            )
        },
        failure,
        None,
    )


def _continuous_row(
    request: ContinuousOneWaySlabActionSetInputV1, row: OneWaySlabActionRowInputV1
) -> SlabActionRowResultV1:
    g, mat, r = request.geometry, request.materials, request.reinforcement
    basis = row.coefficient_basis
    if isinstance(basis, BuiltinOneWaySlabCoefficientBasisV1):
        nonfixed = basis.factored_nonfixed_imposed_load_kn_per_m2
        coefficients = resolve_builtin_one_way_continuous_coefficients(
            factored_dead_and_fixed_imposed_load_kn_per_m2=(
                row.factored_area_load_kn_per_m2 - nonfixed
            ),
            factored_nonfixed_imposed_load_kn_per_m2=nonfixed,
            positive_location=basis.positive_location,
            negative_location=basis.negative_location,
            shear_location=basis.shear_location,
        )
    else:
        coefficients = OneWayContinuousCoefficientSet(
            positive_midspan=basis.positive_moment_coefficient,
            negative_support=basis.negative_moment_coefficient,
            shear_support=basis.shear_coefficient,
            source_reference=basis.coefficient_source_reference,
            source_is_approved=basis.coefficient_source_is_approved,
            qualified_acceptance_reference=basis.qualified_coefficient_acceptance_reference,
            qualified_acceptance_acknowledged=basis.qualified_coefficient_acceptance_acknowledged,
        )
    try:
        strength = _check_continuous_one_way_slab_strength(
            ContinuousOneWaySlabInput(
                geometry=SolidRectangularSlabGeometry(
                    g.short_effective_span_mm,
                    g.long_effective_span_mm,
                    g.thickness_mm,
                    g.strip_width_mm,
                ),
                d_mm=g.effective_depth_mm,
                factored_area_load_kn_per_m2=row.factored_area_load_kn_per_m2,
                fck_n_per_mm2=mat.fck_nmm2,
                fy_n_per_mm2=mat.fy_nmm2,
                coefficients=coefficients,
                number_of_spans=g.number_of_spans,
                maximum_span_variation_percent=g.maximum_span_variation_percent,
                uniform_cross_section_acknowledged=g.uniform_cross_section_acknowledged,
                substantially_uniform_load_acknowledged=request.substantially_uniform_load_acknowledged,
                redistribution_applied=request.redistribution_applied,
            ),
            ProvidedSlabBars(r.positive_bar_diameter_mm, r.positive_bar_spacing_mm),
            ProvidedSlabBars(r.negative_bar_diameter_mm, r.negative_bar_spacing_mm),
            ProvidedSlabBars(
                r.distribution_bar_diameter_mm, r.distribution_bar_spacing_mm
            ),
        )
    except _ContinuousSlabCapacityExceededError as error:
        failure = error.result
        return _capacity_failure(
            row,
            coefficients,
            failure,
            failure.governing_region.removeprefix("continuous_"),
        )
    positive, negative = (
        strength.flexure.positive_midspan,
        strength.flexure.negative_support,
    )
    moments = {
        "positive_midspan": positive.factored_moment_knm_per_m,
        "negative_support": -negative.factored_moment_knm_per_m,
    }
    checks = {}
    for region, flexure in (
        ("positive_midspan", positive),
        ("negative_support", negative),
    ):
        checks[f"{region}.section_flexure"] = _ratio(
            flexure.factored_moment_knm_per_m,
            flexure.limiting_moment_knm_per_m,
            True,
        )
    for region, reinforcement, diameter, spacing in (
        (
            "positive_midspan",
            strength.positive_reinforcement,
            r.positive_bar_diameter_mm,
            r.positive_bar_spacing_mm,
        ),
        (
            "negative_support",
            strength.negative_reinforcement,
            r.negative_bar_diameter_mm,
            r.negative_bar_spacing_mm,
        ),
        (
            "distribution",
            strength.distribution_reinforcement,
            r.distribution_bar_diameter_mm,
            r.distribution_bar_spacing_mm,
        ),
    ):
        _bar_checks(checks, region, reinforcement, diameter, spacing)
    checks["support_shear"] = _shear_check(strength.shear)
    service = _reviewed_service(
        request.serviceability_evidence, g.short_effective_span_mm, g.effective_depth_mm
    )
    owner = (
        strength
        if service is None
        else ContinuousOneWaySlabDesignResult(
            flexure=strength.flexure,
            positive_reinforcement=strength.positive_reinforcement,
            negative_reinforcement=strength.negative_reinforcement,
            distribution_reinforcement=strength.distribution_reinforcement,
            shear=strength.shear,
            serviceability=service,
            punching_shear_disposition=strength.shear.punching_shear_disposition,
        )
    )
    return _checked_row(
        row,
        coefficients,
        moments,
        strength.flexure.factored_shear_kn_per_m,
        checks,
        owner,
        service,
    )


def _two_way_row(
    request: TwoWaySlabActionSetInputV1,
    row: TwoWaySlabActionRowInputV1,
) -> SlabActionRowResultV1:
    g, mat, r = request.geometry, request.materials, request.reinforcement
    geometry = OrientedSlabPanelGeometry(
        g.x_effective_span_mm, g.y_effective_span_mm, g.thickness_mm
    )
    topology = SlabSupportTopology(
        x_min=SlabEdgeContinuity(g.x_min_edge),
        x_max=SlabEdgeContinuity(g.x_max_edge),
        y_min=SlabEdgeContinuity(g.y_min_edge),
        y_max=SlabEdgeContinuity(g.y_max_edge),
        corner_lift_condition=CornerLiftCondition(g.corner_lift_condition),
    )
    basis = row.coefficient_basis
    if isinstance(basis, BuiltinTwoWaySlabCoefficientBasisV1):
        coefficients = resolve_builtin_two_way_panel_coefficients(
            geometry=geometry, topology=topology
        )
    else:
        coefficients = TwoWayPanelCoefficientSet(
            support_topology_kind=SlabSupportTopologyKind(basis.support_topology_kind),
            alpha_x_negative=basis.alpha_x_negative,
            alpha_x_positive=basis.alpha_x_positive,
            alpha_y_negative=basis.alpha_y_negative,
            alpha_y_positive=basis.alpha_y_positive,
            source_reference=basis.coefficient_source_reference,
            source_is_approved=basis.coefficient_source_is_approved,
            qualified_acceptance_reference=basis.qualified_coefficient_acceptance_reference,
            qualified_acceptance_acknowledged=basis.qualified_coefficient_acceptance_acknowledged,
        )
    panel = design_two_way_slab_panel(
        TwoWayPanelDesignInput(
            geometry=geometry,
            support_topology=topology,
            coefficients=coefficients,
            factored_area_load_kn_per_m2=row.factored_area_load_kn_per_m2,
            d_x_mm=g.d_x_mm,
            d_y_mm=g.d_y_mm,
            fck_n_per_mm2=mat.fck_nmm2,
            fy_n_per_mm2=mat.fy_nmm2,
            x_positive_bars=ProvidedSlabBars(
                r.x_positive_bar_diameter_mm, r.x_positive_bar_spacing_mm
            ),
            x_negative_bars=ProvidedSlabBars(
                r.x_negative_bar_diameter_mm, r.x_negative_bar_spacing_mm
            ),
            y_positive_bars=ProvidedSlabBars(
                r.y_positive_bar_diameter_mm, r.y_positive_bar_spacing_mm
            ),
            y_negative_bars=ProvidedSlabBars(
                r.y_negative_bar_diameter_mm, r.y_negative_bar_spacing_mm
            ),
            edge_strip_bars=ProvidedSlabBars(
                r.edge_strip_bar_diameter_mm, r.edge_strip_bar_spacing_mm
            ),
            torsion_bars_each_layer=ProvidedSlabBars(
                r.torsion_bar_diameter_mm, r.torsion_bar_spacing_mm
            ),
        )
    )
    if isinstance(panel, SlabCapacityFailureResult):
        failed_region = panel.governing_region.removesuffix(
            "_continuous_edge"
        ).removesuffix("_middle_strip")
        return _capacity_failure(row, coefficients, panel, failed_region)
    moments = {}
    checks = {}
    for name, region, depth, diameter, spacing in (
        (
            "x_negative",
            panel.x_negative,
            g.d_x_mm,
            r.x_negative_bar_diameter_mm,
            r.x_negative_bar_spacing_mm,
        ),
        (
            "x_positive",
            panel.x_positive,
            g.d_x_mm,
            r.x_positive_bar_diameter_mm,
            r.x_positive_bar_spacing_mm,
        ),
        (
            "y_negative",
            panel.y_negative,
            g.d_y_mm,
            r.y_negative_bar_diameter_mm,
            r.y_negative_bar_spacing_mm,
        ),
        (
            "y_positive",
            panel.y_positive,
            g.d_y_mm,
            r.y_positive_bar_diameter_mm,
            r.y_positive_bar_spacing_mm,
        ),
    ):
        moment = region.factored_moment_knm_per_m
        moments[name] = -moment if "negative" in name and moment else moment
        capacity = rectangular_limiting_moment_knm(
            b_mm=1000.0,
            d_mm=depth,
            fck_n_per_mm2=mat.fck_nmm2,
            fy_n_per_mm2=mat.fy_nmm2,
        )
        checks[f"{name}.section_flexure"] = _ratio(moment, capacity, True)
        _bar_checks(checks, name, region.reinforcement, diameter, spacing)
    _bar_checks(
        checks,
        "edge_strips",
        panel.edge_strip_reinforcement,
        r.edge_strip_bar_diameter_mm,
        r.edge_strip_bar_spacing_mm,
    )
    for corner in panel.corner_torsion:
        demand = corner.required_each_of_four_layers_mm2_per_m
        limit = corner.provided_each_layer_mm2_per_m
        checks[f"{corner.corner.value}.torsion_area_per_layer"] = (
            SlabActionCheckV1(demand, limit, None, "NOT_APPLICABLE")
            if demand == 0
            else _ratio(demand, limit, corner.is_adequate)
        )
    checks["support_shear"] = _shear_check(panel.shear)
    depth = min(g.d_x_mm, g.d_y_mm)
    service = _reviewed_service(
        request.serviceability_evidence, g.x_effective_span_mm, depth
    )
    if service is not None:
        panel = replace(
            panel,
            serviceability_dependency="evaluated_by_composed_workflow_with_reviewed_limit_carrier",
        )
    return _checked_row(
        row,
        coefficients,
        moments,
        _support_shear_demand_kn_per_m(panel.input),
        checks,
        TwoWaySlabPanelWorkflowResult(panel=panel, serviceability=service),
        service,
    )


def _status(values: Iterable[str]) -> EngineeringStatus:
    statuses = set(values)
    if "FAIL" in statuses:
        return EngineeringStatus.FAIL
    if not statuses or "HOLD" in statuses:
        return EngineeringStatus.HOLD
    return EngineeringStatus.PASS


def _governing_id(
    rows: dict[str, SlabActionRowResultV1],
    check_id: str,
) -> str | None:
    candidates = []
    for row_id, row in rows.items():
        check = row.checks.get(check_id)
        if check is None or check.status not in ("PASS", "FAIL"):
            continue
        candidates.append(
            (
                check.status != "FAIL",
                check.utilization is None,
                -(check.utilization or 0.0),
                row_id,
            )
        )
    return min(candidates)[-1] if candidates else None


def check_action_set(
    request: SlabActionSetInputV1,
) -> CanonicalFamilyResultV1[SlabActionSetResultV1]:
    """Check the supplied slab rows and select one governor per scoped check.

    Parameters
    ----------
    request : SlabActionSetInputV1
        Validated physical inputs and the declared ULS rows from
        :func:`load_action_set`.

    Returns
    -------
    CanonicalFamilyResultV1[SlabActionSetResultV1]
        Retained rows, per-check governing IDs, coverage and engineering
        disposition. A conclusive failure remains visible under partial coverage.

    Raises
    ------
    InputContractError
        Wrong request type or unsupported owner inputs.

    Examples
    --------
    See the executable B02 and B04 matrix in the supplied slab action cookbook.

    Limitations
    -----------
    Reviewed span/depth is the supported service check. Direct service
    calculations and load generation require their own workflows.

    Provenance
    ----------
    Reuses the continuous strip, two-way panel, slab detailing, shear and
    reviewed span/depth owners. Each result row retains its coefficient basis.
    """
    if not isinstance(
        request, (ContinuousOneWaySlabActionSetInputV1, TwoWaySlabActionSetInputV1)
    ):
        raise InputContractError(
            (
                InputIssueV1(
                    code="INPUT_TYPE_INVALID",
                    path="request",
                    message="Load a typed slab action set first.",
                ),
            )
        )
    rows: dict[str, SlabActionRowResultV1] = {}
    try:
        if isinstance(request, ContinuousOneWaySlabActionSetInputV1):
            for one_way in sorted(request.rows, key=lambda row: row.row_id):
                rows[one_way.row_id] = _continuous_row(request, one_way)
        else:
            for two_way in sorted(request.rows, key=lambda row: row.row_id):
                rows[two_way.row_id] = _two_way_row(request, two_way)
    except ValueError as error:
        translate_owner_input_error(error, path="rows")

    missing = tuple(sorted(set(request.required_row_ids) - rows.keys()))
    all_checks = sorted({check_id for row in rows.values() for check_id in row.checks})
    uls = _status(row.uls for row in rows.values())
    service = _status(row.reviewed_service for row in rows.values())
    result = canonical_family_result(
        request,
        SlabActionSetResultV1(
            coverage="HOLD" if missing else "COMPLETE",
            uls=uls,
            reviewed_service=service,
            missing_required_row_ids=missing,
            rows=rows,
            governing_ids={
                check_id: _governing_id(rows, check_id) for check_id in all_checks
            },
        ),
        workflow_id=_WORKFLOW,
        engineering_status=_status((uls, service, "HOLD" if missing else "PASS")),
        limitations=(
            "Checks the declared factored UDL rows on one supplied geometry and reinforcement revision.",
            "Reviewed span/depth is the admitted serviceability check. Direct deflection and crack width require separate evidence.",
        ),
        provenance=(
            "Existing IS 456 continuous strip and oriented panel slab checks.",
        ),
    )
    issues = [
        StructuralIssueV1(
            "SLAB_ACTION_CHECK_FAIL",
            f"rows.{row_id}.checks.{check_id}",
            check.reason or f"Row {row_id} fails {check_id}.",
        )
        for row_id, row in rows.items()
        for check_id, check in row.checks.items()
        if check.status == "FAIL"
    ]
    if missing:
        issues.append(
            StructuralIssueV1(
                "SLAB_REQUIRED_ROWS_MISSING",
                "rows",
                f"Required rows are missing: {', '.join(missing)}.",
            )
        )
    if request.serviceability_evidence is None:
        issues.append(
            StructuralIssueV1(
                "SLAB_REVIEWED_SERVICE_HELD",
                "serviceability_evidence",
                "Supply the shared reviewed span/depth basis.",
            )
        )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            intake_status=IntakeStatus.PARTIAL if missing else IntakeStatus.VALID,
            calculation_status=(
                CalculationStatus.COMPLETED if rows else CalculationStatus.NOT_EVALUATED
            ),
            issues=tuple(issues),
        ),
    )
