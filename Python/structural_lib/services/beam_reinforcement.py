# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Evaluate explicitly supplied longitudinal reinforcement for rectangular beams.

This service deliberately keeps three different truths separate:

* flexural design calculates required ``Ast``/``Asc``;
* the maintained optimizer can recommend a preliminary arrangement; and
* only caller-supplied, source-referenced bars can receive a detailing result.

All dimensions are millimetres, steel areas are mm2, stresses are N/mm2, and
support shear is kN.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from structural_lib.codes.is456.beam.detailing import (
    AnchorageCheckResult,
    calculate_bar_spacing,
    check_anchorage_at_simple_support,
    check_min_spacing,
)
from structural_lib.services.rebar_optimizer import Objective, optimize_bar_arrangement

__all__ = [
    "BeamReinforcementEvaluationV1",
    "BeamReinforcementSelectionConstraintsV1",
    "LongitudinalBarLayersV1",
    "SuppliedBeamReinforcementV1",
    "evaluate_supplied_beam_reinforcement_v1",
]

ReinforcementStatus = Literal["PASS", "FAIL", "HOLD"]


def _finite_positive(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite positive real number")
    if not math.isfinite(float(value)) or value <= 0:
        raise ValueError(f"{name} must be a finite positive real number")


def _finite_non_negative(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite non-negative real number")
    if not math.isfinite(float(value)) or value < 0:
        raise ValueError(f"{name} must be a finite non-negative real number")


@dataclass(frozen=True)
class LongitudinalBarLayersV1:
    """One bar diameter arranged in explicit layers from the tension face inward."""

    diameter_mm: float
    bars_per_layer: tuple[int, ...]
    vertical_center_spacings_mm: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        _finite_positive("diameter_mm", self.diameter_mm)
        if not isinstance(self.bars_per_layer, tuple) or not isinstance(
            self.vertical_center_spacings_mm, tuple
        ):
            raise ValueError("bar layers and spacings must be immutable tuples")
        if not self.bars_per_layer or any(
            isinstance(count, bool) or not isinstance(count, int) or count < 2
            for count in self.bars_per_layer
        ):
            raise ValueError("bars_per_layer must contain at least two bars per layer")
        if len(self.vertical_center_spacings_mm) != len(self.bars_per_layer) - 1:
            raise ValueError(
                "vertical_center_spacings_mm must contain one value between layers"
            )
        for spacing in self.vertical_center_spacings_mm:
            _finite_positive("vertical_center_spacings_mm", spacing)

    @property
    def count(self) -> int:
        return sum(self.bars_per_layer)

    @property
    def layers(self) -> int:
        return len(self.bars_per_layer)

    @property
    def area_provided_mm2(self) -> float:
        return self.count * math.pi * self.diameter_mm**2 / 4.0


@dataclass(frozen=True)
class BeamReinforcementSelectionConstraintsV1:
    """Explicit bounded inputs for the preliminary bar recommendation."""

    permitted_diameters_mm: tuple[float, ...]
    maximum_layers: int
    maximum_bars_per_layer: int
    nominal_max_aggregate_size_mm: float
    effective_depth_tolerance_mm: float
    objective: Objective
    source_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.permitted_diameters_mm, tuple) or not (
            self.permitted_diameters_mm
        ):
            raise ValueError("permitted_diameters_mm must not be empty")
        for diameter in self.permitted_diameters_mm:
            _finite_positive("permitted_diameters_mm", diameter)
        normalized = tuple(float(value) for value in self.permitted_diameters_mm)
        if normalized != tuple(sorted(set(normalized))):
            raise ValueError(
                "permitted_diameters_mm must be unique and strictly increasing"
            )
        for name, value in (
            ("maximum_layers", self.maximum_layers),
            ("maximum_bars_per_layer", self.maximum_bars_per_layer),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        _finite_positive(
            "nominal_max_aggregate_size_mm", self.nominal_max_aggregate_size_mm
        )
        _finite_non_negative(
            "effective_depth_tolerance_mm", self.effective_depth_tolerance_mm
        )
        if self.objective not in {"min_area", "min_bar_count", "max_spacing"}:
            raise ValueError(f"unsupported reinforcement objective: {self.objective}")
        if not isinstance(self.source_reference, str) or not (
            self.source_reference.strip()
        ):
            raise ValueError("selection source_reference must not be empty")


@dataclass(frozen=True)
class SuppliedBeamReinforcementV1:
    """Exact supplied tension/top-bar layers and anchorage arrangement."""

    tension: LongitudinalBarLayersV1
    compression_or_hanger: LongitudinalBarLayersV1
    bar_type: Literal["deformed", "plain"]
    has_standard_bend_at_start: bool
    has_standard_bend_at_end: bool
    source_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.tension, LongitudinalBarLayersV1) or not isinstance(
            self.compression_or_hanger, LongitudinalBarLayersV1
        ):
            raise ValueError("supplied tension and top bars must be layer contracts")
        if self.bar_type not in {"deformed", "plain"}:
            raise ValueError("bar_type must be 'deformed' or 'plain'")
        if not isinstance(self.has_standard_bend_at_start, bool) or not isinstance(
            self.has_standard_bend_at_end, bool
        ):
            raise ValueError("support bend flags must be boolean")
        if not isinstance(self.source_reference, str) or not (
            self.source_reference.strip()
        ):
            raise ValueError(
                "supplied reinforcement source_reference must not be empty"
            )


@dataclass(frozen=True)
class BeamReinforcementEvaluationV1:
    """Bounded supplied-reinforcement result; not a professional approval."""

    status: ReinforcementStatus
    ast_required_mm2: float
    asc_required_mm2: float
    recommended_tension: dict[str, object] | None
    supplied_tension: dict[str, object] | None
    supplied_compression_or_hanger: dict[str, object] | None
    checks: dict[str, object]
    issues: tuple[dict[str, str], ...]
    clause_refs: dict[str, str]
    provenance: dict[str, str | None]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "beam-reinforcement-evaluation/v1",
            "status": self.status,
            "ast_required_mm2": self.ast_required_mm2,
            "asc_required_mm2": self.asc_required_mm2,
            "recommended_tension": self.recommended_tension,
            "supplied_tension": self.supplied_tension,
            "supplied_compression_or_hanger": (self.supplied_compression_or_hanger),
            "checks": self.checks,
            "issues": list(self.issues),
            "clause_refs": self.clause_refs,
            "provenance": self.provenance,
            "limitations": list(self.limitations),
            "qualified_review_required": True,
        }


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _arrangement_payload(arrangement: LongitudinalBarLayersV1) -> dict[str, object]:
    return {
        "diameter_mm": arrangement.diameter_mm,
        "bars_per_layer": list(arrangement.bars_per_layer),
        "vertical_center_spacings_mm": list(arrangement.vertical_center_spacings_mm),
        "count": arrangement.count,
        "layers": arrangement.layers,
        "area_provided_mm2": arrangement.area_provided_mm2,
    }


def _recommendation(
    *,
    ast_required_mm2: float,
    b_mm: float,
    cover_mm: float,
    stirrup_dia_mm: float,
    selection: BeamReinforcementSelectionConstraintsV1,
) -> tuple[dict[str, object] | None, bool]:
    result = optimize_bar_arrangement(
        ast_required_mm2=ast_required_mm2,
        b_mm=b_mm,
        cover_mm=cover_mm,
        stirrup_dia_mm=stirrup_dia_mm,
        allowed_dia_mm=selection.permitted_diameters_mm,
        max_layers=selection.maximum_layers,
        objective=selection.objective,
        agg_size_mm=selection.nominal_max_aggregate_size_mm,
        min_total_bars=2,
        max_bars_per_layer=selection.maximum_bars_per_layer,
    )
    if not result.is_feasible or result.arrangement is None:
        return None, False
    arrangement = result.arrangement
    spacing_mm = arrangement.spacing if math.isfinite(arrangement.spacing) else None
    return (
        {
            "status": "PRELIMINARY_RECOMMENDATION_NOT_SUPPLIED_DETAILING",
            "count": arrangement.count,
            "diameter_mm": arrangement.diameter,
            "area_provided_mm2": (
                arrangement.count * math.pi * arrangement.diameter**2 / 4.0
            ),
            "horizontal_center_spacing_mm": spacing_mm,
            "layers": arrangement.layers,
            "objective": result.objective,
            "candidates_considered": result.candidates_considered,
            "limitations": [
                "Layer-by-layer distribution, vertical spacing, effective-depth identity, and anchorage remain to be supplied and checked."
            ],
        },
        True,
    )


def _spacing_checks(
    *,
    arrangement: LongitudinalBarLayersV1,
    b_mm: float,
    cover_mm: float,
    stirrup_dia_mm: float,
    aggregate_size_mm: float,
) -> dict[str, object]:
    horizontal: list[dict[str, object]] = []
    for index, bar_count in enumerate(arrangement.bars_per_layer, start=1):
        center_spacing = calculate_bar_spacing(
            b_mm,
            cover_mm,
            stirrup_dia_mm,
            arrangement.diameter_mm,
            bar_count,
        )
        ok, message = check_min_spacing(
            center_spacing, arrangement.diameter_mm, aggregate_size_mm
        )
        horizontal.append(
            {
                "layer": index,
                "bar_count": bar_count,
                "center_spacing_mm": center_spacing,
                "clear_spacing_mm": center_spacing - arrangement.diameter_mm,
                "is_adequate": ok,
                "message": message,
            }
        )
    vertical: list[dict[str, object]] = []
    for index, center_spacing in enumerate(
        arrangement.vertical_center_spacings_mm, start=1
    ):
        ok, message = check_min_spacing(
            center_spacing, arrangement.diameter_mm, aggregate_size_mm
        )
        vertical.append(
            {
                "between_layers": [index, index + 1],
                "center_spacing_mm": center_spacing,
                "clear_spacing_mm": center_spacing - arrangement.diameter_mm,
                "is_adequate": ok,
                "message": message,
            }
        )
    return {
        "horizontal": horizontal,
        "vertical": vertical,
        "is_adequate": all(bool(item["is_adequate"]) for item in horizontal)
        and all(bool(item["is_adequate"]) for item in vertical),
    }


def _layer_centres_from_face_mm(
    arrangement: LongitudinalBarLayersV1,
    *,
    cover_mm: float,
    stirrup_dia_mm: float,
) -> tuple[float, ...]:
    centres = [cover_mm + stirrup_dia_mm + arrangement.diameter_mm / 2.0]
    for spacing in arrangement.vertical_center_spacings_mm:
        centres.append(centres[-1] + spacing)
    return tuple(centres)


def _weighted_centroid_from_face_mm(
    arrangement: LongitudinalBarLayersV1, centres_mm: tuple[float, ...]
) -> float:
    return (
        math.fsum(
            count * centre
            for count, centre in zip(
                arrangement.bars_per_layer, centres_mm, strict=True
            )
        )
        / arrangement.count
    )


def _anchorage_payload(result: AnchorageCheckResult) -> dict[str, object]:
    return {
        "is_adequate": result.is_adequate,
        "ld_required_mm": result.ld_required,
        "ld_available_mm": result.ld_available,
        "m1_enhancement": result.m1_enhancement,
        "utilization": result.utilization,
        "errors": list(result.errors),
        "warnings": list(result.warnings),
    }


def evaluate_supplied_beam_reinforcement_v1(
    *,
    ast_required_mm2: float,
    asc_required_mm2: float,
    b_mm: float,
    D_mm: float,
    d_design_mm: float,
    d_dash_design_mm: float | None,
    cover_mm: float,
    stirrup_dia_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    vu_kn: float,
    support_width_start_mm: float | None,
    support_width_end_mm: float | None,
    support_width_source_reference: str | None,
    selection: BeamReinforcementSelectionConstraintsV1,
    supplied: SuppliedBeamReinforcementV1 | None,
) -> BeamReinforcementEvaluationV1:
    """Recommend bars, then independently evaluate the exact supplied arrangement."""

    if not isinstance(selection, BeamReinforcementSelectionConstraintsV1):
        raise TypeError("selection must be BeamReinforcementSelectionConstraintsV1")
    if supplied is not None and not isinstance(supplied, SuppliedBeamReinforcementV1):
        raise TypeError("supplied must be SuppliedBeamReinforcementV1 or None")
    for name, value in (
        ("ast_required_mm2", ast_required_mm2),
        ("b_mm", b_mm),
        ("D_mm", D_mm),
        ("d_design_mm", d_design_mm),
        ("cover_mm", cover_mm),
        ("stirrup_dia_mm", stirrup_dia_mm),
        ("fck_nmm2", fck_nmm2),
        ("fy_nmm2", fy_nmm2),
        ("vu_kn", vu_kn),
    ):
        _finite_positive(name, value)
    _finite_non_negative("asc_required_mm2", asc_required_mm2)
    if not 0 < d_design_mm < D_mm:
        raise ValueError("d_design_mm must lie within the overall depth")
    if d_dash_design_mm is not None:
        _finite_positive("d_dash_design_mm", d_dash_design_mm)
        if d_dash_design_mm >= D_mm:
            raise ValueError("d_dash_design_mm must lie within the overall depth")
    if support_width_start_mm is not None:
        _finite_positive("support_width_start_mm", support_width_start_mm)
    if support_width_end_mm is not None:
        _finite_positive("support_width_end_mm", support_width_end_mm)
    if supplied is not None and any(
        diameter not in selection.permitted_diameters_mm
        for diameter in (
            supplied.tension.diameter_mm,
            supplied.compression_or_hanger.diameter_mm,
        )
    ):
        raise ValueError("supplied bar diameters must be in permitted_diameters_mm")
    if supplied is not None:
        for name, arrangement in (
            ("tension", supplied.tension),
            ("compression_or_hanger", supplied.compression_or_hanger),
        ):
            if arrangement.layers > selection.maximum_layers:
                raise ValueError(f"{name} layers exceed maximum_layers")
            if max(arrangement.bars_per_layer) > selection.maximum_bars_per_layer:
                raise ValueError(f"{name} bars per layer exceed the explicit maximum")

    recommendation, recommendation_feasible = _recommendation(
        ast_required_mm2=ast_required_mm2,
        b_mm=b_mm,
        cover_mm=cover_mm,
        stirrup_dia_mm=stirrup_dia_mm,
        selection=selection,
    )
    base_provenance = {
        "selection_constraints": selection.source_reference,
        "supplied_reinforcement": (
            supplied.source_reference if supplied is not None else None
        ),
        "support_width": support_width_source_reference,
    }
    limitations = (
        "Rectangular, non-bundled bars of one diameter per tension/top group only.",
        "No curtailment, lap location, joint congestion, construction sequence, or seismic capacity-design claim.",
        "Anchorage uses the maintained conservative simple-support check with zero M1/V enhancement.",
        "Qualified structural-engineering review remains required.",
    )
    clause_refs = {
        "minimum_clear_spacing": "IS 456:2000 Cl 26.3.2",
        "longitudinal_reinforcement": "IS 456:2000 Cl 26.5.1",
        "simple_support_anchorage": "IS 456:2000 Cl 26.2.3.3",
    }
    if supplied is None:
        missing_supply_issues = [
            _issue(
                "BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED",
                "Required steel was calculated, but no source-referenced longitudinal bar arrangement was supplied.",
            )
        ]
        if not recommendation_feasible:
            missing_supply_issues.append(
                _issue(
                    "BEAM_REINFORCEMENT_RECOMMENDATION_INFEASIBLE",
                    "No preliminary tension-bar recommendation satisfies the explicit selection constraints.",
                )
            )
        return BeamReinforcementEvaluationV1(
            status="HOLD",
            ast_required_mm2=ast_required_mm2,
            asc_required_mm2=asc_required_mm2,
            recommended_tension=recommendation,
            supplied_tension=None,
            supplied_compression_or_hanger=None,
            checks={"supply_complete": False},
            issues=tuple(missing_supply_issues),
            clause_refs=clause_refs,
            provenance=base_provenance,
            limitations=limitations,
        )

    tension = supplied.tension
    compression = supplied.compression_or_hanger
    tension_spacing = _spacing_checks(
        arrangement=tension,
        b_mm=b_mm,
        cover_mm=cover_mm,
        stirrup_dia_mm=stirrup_dia_mm,
        aggregate_size_mm=selection.nominal_max_aggregate_size_mm,
    )
    compression_spacing = _spacing_checks(
        arrangement=compression,
        b_mm=b_mm,
        cover_mm=cover_mm,
        stirrup_dia_mm=stirrup_dia_mm,
        aggregate_size_mm=selection.nominal_max_aggregate_size_mm,
    )

    tension_centres = _layer_centres_from_face_mm(
        tension, cover_mm=cover_mm, stirrup_dia_mm=stirrup_dia_mm
    )
    compression_centres = _layer_centres_from_face_mm(
        compression, cover_mm=cover_mm, stirrup_dia_mm=stirrup_dia_mm
    )
    d_supplied_mm = D_mm - _weighted_centroid_from_face_mm(tension, tension_centres)
    d_difference_mm = abs(d_supplied_mm - d_design_mm)
    d_ok = d_difference_mm <= selection.effective_depth_tolerance_mm
    d_dash_supplied_mm = _weighted_centroid_from_face_mm(
        compression, compression_centres
    )
    d_dash_difference_mm = (
        abs(d_dash_supplied_mm - d_dash_design_mm)
        if asc_required_mm2 > 0 and d_dash_design_mm is not None
        else None
    )
    d_dash_ok = asc_required_mm2 <= 0 or (
        d_dash_difference_mm is not None
        and d_dash_difference_mm <= selection.effective_depth_tolerance_mm
    )
    compression_depth_complete = asc_required_mm2 <= 0 or d_dash_design_mm is not None
    group_clear_spacing_mm = (
        D_mm
        - (tension_centres[-1] + tension.diameter_mm / 2.0)
        - (compression_centres[-1] + compression.diameter_mm / 2.0)
    )
    group_min_clear_spacing_mm = max(
        tension.diameter_mm,
        compression.diameter_mm,
        selection.nominal_max_aggregate_size_mm + 5.0,
        25.0,
    )
    group_clear_ok = group_clear_spacing_mm >= group_min_clear_spacing_mm

    tension_area_ok = tension.area_provided_mm2 + 1e-9 >= ast_required_mm2
    compression_area_ok = compression.area_provided_mm2 + 1e-9 >= asc_required_mm2
    support_complete = (
        support_width_start_mm is not None
        and support_width_end_mm is not None
        and support_width_source_reference is not None
        and support_width_source_reference.strip() != ""
    )
    start_anchorage: AnchorageCheckResult | None = None
    end_anchorage: AnchorageCheckResult | None = None
    if support_complete:
        assert support_width_start_mm is not None
        assert support_width_end_mm is not None
        start_anchorage = check_anchorage_at_simple_support(
            bar_dia=tension.diameter_mm,
            fck=fck_nmm2,
            fy=fy_nmm2,
            vu_kn=vu_kn,
            support_width=support_width_start_mm,
            cover=cover_mm,
            bar_type=supplied.bar_type,
            has_standard_bend=supplied.has_standard_bend_at_start,
        )
        end_anchorage = check_anchorage_at_simple_support(
            bar_dia=tension.diameter_mm,
            fck=fck_nmm2,
            fy=fy_nmm2,
            vu_kn=vu_kn,
            support_width=support_width_end_mm,
            cover=cover_mm,
            bar_type=supplied.bar_type,
            has_standard_bend=supplied.has_standard_bend_at_end,
        )

    issues: list[dict[str, str]] = []
    if not tension_area_ok:
        issues.append(
            _issue(
                "BEAM_TENSION_REINFORCEMENT_AREA_INSUFFICIENT",
                "Supplied tension-bar area is below calculated Ast.",
            )
        )
    if not compression_area_ok:
        issues.append(
            _issue(
                "BEAM_COMPRESSION_REINFORCEMENT_AREA_INSUFFICIENT",
                "Supplied compression-bar area is below calculated Asc.",
            )
        )
    if not bool(tension_spacing["is_adequate"]):
        issues.append(
            _issue(
                "BEAM_TENSION_BAR_SPACING_INADEQUATE",
                "Supplied tension-bar horizontal or vertical spacing is inadequate.",
            )
        )
    if not bool(compression_spacing["is_adequate"]):
        issues.append(
            _issue(
                "BEAM_COMPRESSION_BAR_SPACING_INADEQUATE",
                "Supplied top-bar horizontal or vertical spacing is inadequate.",
            )
        )
    if not d_ok:
        issues.append(
            _issue(
                "BEAM_SUPPLIED_EFFECTIVE_DEPTH_MISMATCH",
                "The supplied tension-layer centroid does not match the design effective depth within tolerance.",
            )
        )
    if not d_dash_ok:
        if compression_depth_complete:
            issues.append(
                _issue(
                    "BEAM_SUPPLIED_COMPRESSION_DEPTH_MISMATCH",
                    "The supplied compression-layer centroid does not match the design compression depth within tolerance.",
                )
            )
        else:
            issues.append(
                _issue(
                    "BEAM_COMPRESSION_DEPTH_BASIS_NOT_SUPPLIED",
                    "Calculated compression reinforcement requires a supplied design compression-depth basis.",
                )
            )
    if not group_clear_ok:
        issues.append(
            _issue(
                "BEAM_LONGITUDINAL_GROUP_CLEARANCE_INADEQUATE",
                "Tension and top reinforcement groups do not retain the required clear vertical separation.",
            )
        )
    if not support_complete:
        issues.append(
            _issue(
                "BEAM_SUPPORT_WIDTH_BASIS_NOT_SUPPLIED",
                "Both support widths and their source reference are required for anchorage evaluation.",
            )
        )
    else:
        if start_anchorage is not None and not start_anchorage.is_adequate:
            issues.append(
                _issue(
                    "BEAM_START_SUPPORT_ANCHORAGE_INADEQUATE",
                    "Supplied tension bars fail the maintained start-support anchorage check.",
                )
            )
        if end_anchorage is not None and not end_anchorage.is_adequate:
            issues.append(
                _issue(
                    "BEAM_END_SUPPORT_ANCHORAGE_INADEQUATE",
                    "Supplied tension bars fail the maintained end-support anchorage check.",
                )
            )

    status: ReinforcementStatus
    if not support_complete or not compression_depth_complete:
        status = "HOLD"
    elif issues:
        status = "FAIL"
    else:
        status = "PASS"
    return BeamReinforcementEvaluationV1(
        status=status,
        ast_required_mm2=ast_required_mm2,
        asc_required_mm2=asc_required_mm2,
        recommended_tension=recommendation,
        supplied_tension=_arrangement_payload(tension),
        supplied_compression_or_hanger=_arrangement_payload(compression),
        checks={
            "supply_complete": True,
            "tension_area": {
                "required_mm2": ast_required_mm2,
                "provided_mm2": tension.area_provided_mm2,
                "is_adequate": tension_area_ok,
            },
            "compression_area": {
                "required_mm2": asc_required_mm2,
                "provided_mm2": compression.area_provided_mm2,
                "is_adequate": compression_area_ok,
            },
            "tension_spacing": tension_spacing,
            "compression_spacing": compression_spacing,
            "effective_depth": {
                "design_mm": d_design_mm,
                "supplied_centroid_mm": d_supplied_mm,
                "absolute_difference_mm": d_difference_mm,
                "tolerance_mm": selection.effective_depth_tolerance_mm,
                "is_adequate": d_ok,
            },
            "compression_depth": {
                "design_mm": d_dash_design_mm,
                "supplied_centroid_mm": d_dash_supplied_mm,
                "absolute_difference_mm": d_dash_difference_mm,
                "tolerance_mm": selection.effective_depth_tolerance_mm,
                "is_adequate": d_dash_ok,
                "required": asc_required_mm2 > 0,
            },
            "between_groups_clearance": {
                "clear_spacing_mm": group_clear_spacing_mm,
                "minimum_clear_spacing_mm": group_min_clear_spacing_mm,
                "is_adequate": group_clear_ok,
            },
            "start_anchorage": (
                _anchorage_payload(start_anchorage)
                if start_anchorage is not None
                else None
            ),
            "end_anchorage": (
                _anchorage_payload(end_anchorage) if end_anchorage is not None else None
            ),
        },
        issues=tuple(issues),
        clause_refs=clause_refs,
        provenance=base_provenance,
        limitations=limitations,
    )
