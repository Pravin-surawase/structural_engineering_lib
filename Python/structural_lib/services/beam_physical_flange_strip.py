"""Bounded physical slab-strip evidence for the BEAM05 T-flange packet."""

from __future__ import annotations

import math
from typing import Any

from pydantic import Field, field_validator, model_validator

from structural_lib.beam.detailing import (
    BarSurface,
    DevelopmentLengthRequest,
    StressState,
    development_length,
)
from structural_lib.beam.flexure import (
    FlexuralCapacityRequest,
    SectionKind,
    flexural_capacity,
)
from structural_lib.beam.reinforcement import BarPosition, Face
from structural_lib.beam.semantics import EngineeringState
from structural_lib.codes.is456.beam.flanged_serviceability import (
    conservative_strip_shear,
    flange_strip_limits,
)
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
)
from structural_lib.services.contracts.common import StrictPublicModel


class BeamPhysicalFlangeMainV1(StrictPublicModel):
    owner: str = Field(min_length=1, max_length=80)
    top_axis_mm: float = Field(gt=0, le=1000)
    bottom_axis_mm: float = Field(gt=0, le=1000)
    stations_mm: tuple[float, ...] = Field(min_length=4, max_length=300)
    x_ends_mm: tuple[float, float]
    diameter_mm: float = Field(ge=6, le=40)

    @field_validator("stations_mm", "x_ends_mm", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class BeamPhysicalFlangeDistributionV1(StrictPublicModel):
    owner: str = Field(min_length=1, max_length=80)
    top_axis_mm: float = Field(gt=0, le=1000)
    bottom_axis_mm: float = Field(gt=0, le=1000)
    x_axes_mm: tuple[float, ...] = Field(min_length=3, max_length=100)
    end_stations_mm: tuple[float, float]
    diameter_mm: float = Field(ge=6, le=40)

    @field_validator("x_axes_mm", "end_stations_mm", mode="before")
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class BeamPhysicalFlangeCombinationV1(StrictPublicModel):
    combination_id: str = Field(min_length=1, max_length=80)
    beam_udl_kn_per_m: float = Field(ge=0, le=10000)
    slab_udl_kn_per_m2: float = Field(ge=0, le=10000)
    other_beam_line_load_kn_per_m: float = Field(ge=0, le=10000)


class BeamPhysicalFlangeStripV1(StrictPublicModel):
    geometry_revision: str = Field(min_length=1, max_length=160)
    transverse_support_x_mm: tuple[float, float, float]
    transverse_support_widths_mm: tuple[float, float, float]
    transverse_edge_x_mm: tuple[float, float]
    width_between_stations_mm: tuple[float, float]
    main: BeamPhysicalFlangeMainV1
    distribution: BeamPhysicalFlangeDistributionV1
    combinations: tuple[BeamPhysicalFlangeCombinationV1, ...] | None = None

    @field_validator(
        "transverse_support_x_mm",
        "transverse_support_widths_mm",
        "transverse_edge_x_mm",
        "width_between_stations_mm",
        "combinations",
        mode="before",
    )
    @classmethod
    def _tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def _finite_and_ordered(self) -> BeamPhysicalFlangeStripV1:
        values = (
            *self.transverse_support_x_mm,
            *self.transverse_support_widths_mm,
            *self.transverse_edge_x_mm,
            *self.width_between_stations_mm,
            *self.main.stations_mm,
            *self.main.x_ends_mm,
            *self.distribution.x_axes_mm,
            *self.distribution.end_stations_mm,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Physical strip coordinates must be finite.")
        if any(
            b <= a
            for a, b in zip(
                self.main.stations_mm, self.main.stations_mm[1:], strict=False
            )
        ):
            raise ValueError("Main-bar stations must be strictly increasing.")
        if any(
            b <= a
            for a, b in zip(
                self.distribution.x_axes_mm,
                self.distribution.x_axes_mm[1:],
                strict=False,
            )
        ):
            raise ValueError("Distribution-bar axes must be strictly increasing.")
        return self


def _issue(code: str, field: str, message: str) -> StructuralIssueV1:
    return StructuralIssueV1(
        "BEAM.FLANGE_STRIP_" + code, "physical_flange.slab_strip." + field, message
    )


def _uniform_pitch(points: tuple[float, ...]) -> float | None:
    pitch = points[1] - points[0]
    if pitch <= 0 or not all(
        math.isclose(b - a, pitch, rel_tol=0, abs_tol=1e-8)
        for a, b in zip(points, points[1:], strict=False)
    ):
        return None
    return pitch


def check_physical_flange_strip(
    strip: BeamPhysicalFlangeStripV1,
    member: BeamLayeredContinuousCheckRequestV1,
    *,
    placement_tolerance_mm: float = 0,
) -> tuple[dict[str, Any], tuple[StructuralIssueV1, ...]]:
    """Check the two equal pinned spans of the independently owned slab strip."""
    flange = member.flange
    assert flange is not None
    if not strip.combinations:
        return {}, (
            _issue(
                "ACTIONS_HELD",
                "combinations",
                "Supply current slab and concurrent beam loads for each ULS combination.",
            ),
        )

    supports, widths = strip.transverse_support_x_mm, strip.transverse_support_widths_mm
    span = supports[1] - supports[0]
    transverse_start, transverse_end = strip.transverse_edge_x_mm
    axial_start, axial_end = strip.width_between_stations_mm
    tol = placement_tolerance_mm
    main, dist = strip.main, strip.distribution
    main_pitch, dist_pitch = _uniform_pitch(main.stations_mm), _uniform_pitch(
        dist.x_axes_mm
    )
    depth = flange.thickness_mm
    effective_depth = min(depth - main.top_axis_mm, main.bottom_axis_mm)
    adverse_depth = effective_depth - tol
    if not (
        span > 0
        and axial_start < axial_end
        and all(width > 0 for width in widths)
        and math.isclose(supports[2] - supports[1], span, abs_tol=1e-8, rel_tol=0)
        and transverse_start <= supports[0] - widths[0] / 2
        and supports[2] + widths[2] / 2 <= transverse_end
        and 0 < adverse_depth <= effective_depth < depth
        and main_pitch is not None
        and dist_pitch is not None
    ):
        return {}, (
            _issue(
                "GEOMETRY_FAIL",
                "transverse_support_x_mm",
                "Supply two equal transverse spans, supported slab ends and ordered steel grids within the slab.",
            ),
        )

    limits = flange_strip_limits(depth, adverse_depth)
    main_area = math.pi * main.diameter_mm**2 / 4 * 1000 / main_pitch
    dist_area = math.pi * dist.diameter_mm**2 / 4 * 1000 / dist_pitch
    aggregate = member.aggregate_size_mm
    issues = []
    if not (
        main.owner == dist.owner == "SLAB"
        and main_pitch + 2 * tol <= limits["maximum_main_spacing_mm"]
        and dist_pitch + 2 * tol <= limits["maximum_distribution_spacing_mm"]
        and max(main.diameter_mm, dist.diameter_mm) <= limits["maximum_bar_diameter_mm"]
        and min(main_area, dist_area) >= limits["minimum_area_per_m_each_direction_mm2"]
        and all(
            steel.bottom_axis_mm - steel.top_axis_mm - steel.diameter_mm - 2 * tol
            >= max(steel.diameter_mm, 15, 2 * aggregate / 3)
            and pitch - steel.diameter_mm - 2 * tol
            >= max(steel.diameter_mm, aggregate + 5)
            for steel, pitch in ((main, main_pitch), (dist, dist_pitch))
        )
        and main.stations_mm[0] - axial_start <= main_pitch / 2
        and axial_end - main.stations_mm[-1] <= main_pitch / 2
        and dist.x_axes_mm[0] - supports[0] <= dist_pitch / 2
        and supports[2] - dist.x_axes_mm[-1] <= dist_pitch / 2
        and dist.end_stations_mm[0] + 2 * tol <= main.stations_mm[0]
        and main.stations_mm[-1] + 2 * tol <= dist.end_stations_mm[-1]
    ):
        issues.append(
            _issue(
                "REINFORCEMENT_FAIL",
                "main",
                "Verify the two slab faces, bar size, spacing, minimum steel and actual strip coverage.",
            )
        )

    development = development_length(
        DevelopmentLengthRequest(
            member.schema_version,
            main.diameter_mm,
            0.87 * member.fy_nmm2,
            member.fy_nmm2,
            member.fck_nmm2,
            BarSurface.DEFORMED,
            StressState.TENSION,
        )
    )
    required = float(development.outputs["required_development_length_mm"])
    internal = min(
        supports[1] - widths[1] / 2 - main.x_ends_mm[0],
        main.x_ends_mm[1] - supports[1] - widths[1] / 2,
    )
    outer = min(
        supports[0] + widths[0] / 2 - main.x_ends_mm[0],
        main.x_ends_mm[1] - (supports[2] - widths[2] / 2),
    )
    if internal - tol < required or outer - tol < required / 3:
        issues.append(
            _issue(
                "DEVELOPMENT_FAIL",
                "main.x_ends_mm",
                "The slab main bars lack straight development beyond a transverse support face.",
            )
        )

    reference_width = 4 * main_pitch
    pieces = tuple(
        BarPosition(
            f"SM{main.diameter_mm:g}-{face.name}-{i}",
            main.diameter_mm,
            (i - 0.5) * main_pitch,
            y,
            face,
        )
        for face, y in (
            (Face.TOP, main.top_axis_mm),
            (Face.BOTTOM, main.bottom_axis_mm),
        )
        for i in range(1, 5)
    )
    capacities = {}
    for key, shift in (("nominal", 0.0), ("adverse", tol)):
        actual = tuple(
            BarPosition(
                bar.bar_id,
                bar.diameter_mm,
                bar.x_from_left_mm,
                bar.y_from_top_mm + (shift if bar.face is Face.TOP else -shift),
                bar.face,
            )
            for bar in pieces
        )
        capacities[key] = {
            face.value: flexural_capacity(
                FlexuralCapacityRequest(
                    member.schema_version,
                    SectionKind.RECTANGULAR,
                    reference_width,
                    depth,
                    member.fck_nmm2,
                    member.fy_nmm2,
                    actual,
                    face,
                )
            )
            for face in Face
        }
    if any(
        result.engineering is not EngineeringState.PASS
        for basis in capacities.values()
        for result in basis.values()
    ):
        return {}, (
            *issues,
            _issue(
                "FLEXURE_FAIL",
                "main",
                "The actual strip axes do not provide a qualifying section.",
            ),
        )

    strip_rows = []
    for case in strip.combinations:
        q = case.slab_udl_kn_per_m2 * reference_width / 1000
        m_neg = -q * (span / 1000) ** 2 / 8
        m_pos = 9 * q * (span / 1000) ** 2 / 128
        v = 5 * q * span / 8000
        area = math.pi * main.diameter_mm**2  # Four bars, area pi*d²/4 each.
        tau, tau_c = conservative_strip_shear(
            q * 5 / 8, span, reference_width, effective_depth, area
        )
        tau_adverse, tau_c_adverse = conservative_strip_shear(
            q * 5 / 8, span, reference_width, adverse_depth, area
        )
        accepted = (
            abs(m_neg) <= float(capacities["adverse"]["top"].outputs["capacity_knm"])
            and m_pos <= float(capacities["adverse"]["bottom"].outputs["capacity_knm"])
            and tau_adverse <= tau_c_adverse
        )
        if not accepted:
            issues.append(
                _issue(
                    "STRENGTH_FAIL",
                    "combinations",
                    f"The transverse strip does not resist the signed actions for {case.combination_id}.",
                )
            )
        strip_rows.append(
            {
                "combination_id": case.combination_id,
                "interior_support_moment_knm": m_neg,
                "same_span_positive_peak_knm": m_pos,
                "support_shear_magnitude_kn": v,
                "tau_v_nmm2": tau,
                "tau_c_nmm2": tau_c,
                "adverse_tau_v_nmm2": tau_adverse,
                "adverse_tau_c_nmm2": tau_c_adverse,
                "passes": accepted,
            }
        )

    return {
        "owner": "SLAB",
        "geometry_revision": strip.geometry_revision,
        "transverse_span_mm": span,
        "reference_width_mm": reference_width,
        "main_area_per_m_mm2": main_area,
        "distribution_area_per_m_mm2": dist_area,
        "minimum_area_per_m_mm2": limits["minimum_area_per_m_each_direction_mm2"],
        "required_main_development_mm": required,
        "available_main_development_mm": internal,
        "minimum_outer_development_mm": outer,
        "strip_checks": strip_rows,
        "capacity_knm": {
            basis: {
                face: float(result.outputs["capacity_knm"])
                for face, result in leaves.items()
            }
            for basis, leaves in capacities.items()
        },
    }, tuple(issues)
