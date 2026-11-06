"""IS 456 shear resistance of declared reinforcement at one beam section."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456 import tables
from structural_lib.codes.is456.beam.shear import shear_reinforcement_component_kn

from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_applicable_result,
    rejected_result,
)

_OPERATION = "is456.beam.supplied_section_shear_capacity/v1"
_PROVENANCE = Provenance(
    "is456-2000-a5-section-shear-v1",
    "is456-supplied-section-shear-v1",
    (
        "IS 456:2000 Cl. 26.5.1.5–26.5.1.6",
        "IS 456:2000 Cl. 40.2, Cl. 40.4 and Tables 19–20",
    ),
)


@dataclass(frozen=True)
class SectionShearReinforcement:
    """One group of active stirrup legs or bent-up bars.

    Use the actual cross-sectional area normal to the steel. Spacing is measured
    along the member. Only a single bent-up group uses `spacing_mm=None`.
    """

    group_id: str
    area_mm2: float
    fy_nmm2: float
    inclination_deg: float
    spacing_mm: float | None


@dataclass(frozen=True)
class SuppliedSectionShearRequest:
    """Ordinary beam section, with at most one stirrup and one bent-up group.

    Supply the web width for a flanged section and the continuing longitudinal
    tension area eligible for Table 19. Declare only distinct groups effective
    at the same section. `None` declares zero provision for that group.
    """

    profile_id: str
    web_width_mm: float
    effective_depth_mm: float
    fck_nmm2: float
    longitudinal_tension_area_mm2: float
    stirrups: SectionShearReinforcement | None
    bent_up_bars: SectionShearReinforcement | None = None


def _diagnostic(code: str, field: str, message: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code, "error", message, _OPERATION, field, "is456-section-shear", remediation
    )


def _positive(value: float) -> bool:
    return type(value) in (float, int) and math.isfinite(value) and value > 0


def _valid_group(group: SectionShearReinforcement, *, stirrups: bool) -> bool:
    angle = group.inclination_deg
    spacing = group.spacing_mm
    return (
        bool(group.group_id.strip())
        and _positive(group.area_mm2)
        and _positive(group.fy_nmm2)
        and _positive(angle)
        and (angle in (45.0, 90.0) if stirrups else 45.0 <= angle <= 90.0)
        and (spacing is None and not stirrups or _positive(spacing))
    )


def supplied_section_shear_capacity(
    request: SuppliedSectionShearRequest,
) -> OperationResult:
    """Calculate raw, credited and limiting shear resistance in kN.

    The result checks stirrup spacing, minimum stirrup provision and the
    bent-up contribution limit. It carries no shear demand, layout or member
    detailing evidence. The existing vertical-link operation remains separate.
    """
    stirrups, bent = request.stirrups, request.bent_up_bars
    b, d, fck = request.web_width_mm, request.effective_depth_mm, request.fck_nmm2
    ast = request.longitudinal_tension_area_mm2
    invalid = []
    for field, value in (
        ("web_width_mm", b),
        ("effective_depth_mm", d),
        ("fck_nmm2", fck),
        ("longitudinal_tension_area_mm2", ast),
    ):
        if not _positive(value):
            invalid.append(
                _diagnostic(
                    "INPUT.RANGE",
                    field,
                    "A finite positive value is required.",
                    "Supply the value in the declared unit.",
                )
            )
    for field, group in (("stirrups", stirrups), ("bent_up_bars", bent)):
        if group is not None and not _valid_group(group, stirrups=field == "stirrups"):
            invalid.append(
                _diagnostic(
                    "INPUT.RANGE",
                    field,
                    "Invalid reinforcement group id, area, strength, inclination or spacing.",
                    "Use positive finite area and strength, 45° or 90° stirrups with positive spacing, and 45° to 90° bent-up bars. Omit spacing only for a single bent-up group.",
                )
            )
    if invalid:
        # Invalid values such as NaN cannot be hashed into a canonical result.
        return rejected_result(
            _OPERATION,
            effective_inputs(profile_id=request.profile_id),
            invalid,
            provenance=_PROVENANCE,
        )

    inputs = effective_inputs(
        profile_id=request.profile_id,
        web_width_mm=b,
        effective_depth_mm=d,
        fck_nmm2=fck,
        longitudinal_tension_area_mm2=ast,
        stirrups=stirrups,
        bent_up_bars=bent,
    )
    if (
        stirrups is not None
        and bent is not None
        and stirrups.group_id.strip() == bent.group_id.strip()
    ):
        return rejected_result(
            _OPERATION,
            inputs,
            (
                _diagnostic(
                    "INPUT.CONFLICT",
                    "bent_up_bars.group_id",
                    "Both groups identify the same reinforcement.",
                    "Provide distinct, non-overlapping reinforcement groups.",
                ),
            ),
            provenance=_PROVENANCE,
        )
    if not 15.0 <= fck <= 40.0:
        return not_applicable_result(
            _OPERATION,
            inputs,
            Diagnostic(
                "PROFILE.UNSUPPORTED",
                "information",
                "Concrete strength is outside the Table 19/20 profile.",
                _OPERATION,
                "fck_nmm2",
                "is456-section-shear",
                "Use fck from 15 through 40 N/mm².",
            ),
            provenance=_PROVENANCE,
        )

    bd = b * d
    pt = 100.0 * (ast / bd) if bd > 0 else math.inf
    pt_table = min(3.0, max(0.15, pt))
    tau_c = tables.get_tc_value(fck, pt_table)
    tau_max = tables.get_tc_max_value(fck)
    vc = tau_c * (bd / 1000.0)
    limiting = tau_max * (bd / 1000.0)
    stirrup_kn, bent_raw_kn = (
        (
            shear_reinforcement_component_kn(
                group.area_mm2,
                group.fy_nmm2,
                d,
                group.inclination_deg,
                group.spacing_mm,
            )
            if group is not None
            else 0.0
        )
        for group in (stirrups, bent)
    )
    bent_credited_kn = min(stirrup_kn, bent_raw_kn)
    total_kn = vc + stirrup_kn + bent_credited_kn
    if not _positive(vc) or not all(
        math.isfinite(v) for v in (pt, limiting, stirrup_kn, bent_raw_kn, total_kn)
    ):
        return rejected_result(
            _OPERATION,
            inputs,
            (
                _diagnostic(
                    "INPUT.RANGE",
                    "section",
                    "Inputs exceed the numeric range for shear resistance.",
                    "Check dimensions, areas and spacing in their declared units.",
                ),
            ),
            provenance=_PROVENANCE,
        )

    diagnostics = []
    maximum_spacing = None
    if stirrups is None:
        diagnostics.append(
            _diagnostic(
                "SHEAR.MINIMUM_REINFORCEMENT",
                "stirrups",
                "Ordinary beams require minimum stirrup reinforcement.",
                "Supply an effective stirrup group.",
            )
        )
    else:
        spacing = stirrups.spacing_mm
        assert spacing is not None
        maximum_spacing = min(
            300.0, 0.75 * d if stirrups.inclination_deg == 90.0 else d
        )
        if spacing > maximum_spacing + 1e-9:
            diagnostics.append(
                _diagnostic(
                    "SHEAR.SPACING",
                    "stirrups.spacing_mm",
                    "Stirrup spacing exceeds the permitted maximum.",
                    "Reduce the spacing.",
                )
            )
        if (stirrups.area_mm2 / b) / spacing + 1e-12 < 0.4 / (
            0.87 * min(415.0, stirrups.fy_nmm2)
        ):
            diagnostics.append(
                _diagnostic(
                    "SHEAR.MINIMUM_REINFORCEMENT",
                    "stirrups",
                    "Stirrup provision is below the minimum.",
                    "Increase the active area or reduce the spacing.",
                )
            )
    if bent_raw_kn > stirrup_kn and not math.isclose(
        bent_raw_kn, stirrup_kn, rel_tol=1e-12, abs_tol=1e-9
    ):
        diagnostics.append(
            _diagnostic(
                "SHEAR.BENT_UP_LIMIT",
                "bent_up_bars",
                "The raw bent-up contribution exceeds half the total reinforcement resistance.",
                "Base resistance only on the credited contribution and revise the reinforcement groups.",
            )
        )

    return completed_result(
        _OPERATION,
        inputs,
        {
            "longitudinal_percentage_actual": pt,
            "longitudinal_percentage_table": pt_table,
            "tau_c_n_per_mm2": tau_c,
            "tau_c_max_n_per_mm2": tau_max,
            "stirrup_maximum_spacing_mm": maximum_spacing,
            "concrete_capacity_kn": vc,
            "stirrup_capacity_kn": stirrup_kn,
            "bent_up_capacity_raw_kn": bent_raw_kn,
            "bent_up_capacity_credited_kn": bent_credited_kn,
            "limiting_capacity_kn": limiting,
            "provided_capacity_kn": min(total_kn, limiting),
        },
        engineering=EngineeringState.FAIL if diagnostics else EngineeringState.PASS,
        diagnostics=diagnostics,
        provenance=_PROVENANCE,
    )
