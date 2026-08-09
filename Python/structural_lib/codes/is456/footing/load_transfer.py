# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
# ruff: noqa: N815
"""Bounded load-transfer check for an isolated footing (IS 456 Cl. 34.4).

This module deliberately accepts the effective supporting bearing area ``A1``
as an approved input.  It never substitutes the footing plan area for ``A1``:
the latter is the lower base of the applicable 1V:2H bearing frustum.

Supported case: concentric axial transfer from a rectangular/square column or
pedestal into an isolated rectangular/square footing using dowels.  It excludes
eccentric transfer, combined/strap/raft foundations, lateral transfer and the
special large-column-bar dowel arrangement of Cl. 34.4.4.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.beam.detailing import get_bond_stress
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.errors import ValidationError

__all__ = [
    "AMENDMENT_6_SOURCE_ID",
    "IS456_CONSOLIDATED_SOURCE_ID",
    "LoadTransferResult",
    "check_isolated_footing_load_transfer",
]


# Private source identities, retained as evidence identifiers only.
IS456_CONSOLIDATED_SOURCE_ID = (
    "is456_2000_amd5_reff2021.pdf:"
    "sha256:964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264"
)
AMENDMENT_6_SOURCE_ID = (
    "is456_amd_06_2024.pdf:"
    "sha256:4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881"
)

_A1_BASIS = "largest_frustum_1v_2h"
_SUPPORTED_CASE = "concentric_isolated_square_or_rectangular_footing_with_dowels"
_EXCLUSIONS = (
    "Eccentric or moment transfer is excluded.",
    "Combined, strap and raft footing geometries are excluded.",
    "Lateral load, geotechnical, settlement and footing flexure/shear checks are excluded.",
    "The Cl. 34.4.4 arrangement for column bars over 36 mm is excluded.",
)


@dataclass(frozen=True)
class LoadTransferResult:
    """Result of the bounded Cl. 34.4 bearing and dowel-transfer check.

    All force values are factored design actions/capacities.  ``is_safe`` is
    true only when the provided dowels meet the area, count, diameter and
    development-length conditions for this supported case.
    """

    source_ids: tuple[str, str]
    source_notes: tuple[str, str]
    clause_refs: tuple[str, str, str, str, str]
    supported_case: str
    exclusions: tuple[str, ...]
    units: dict[str, str]
    limits: dict[str, float | int | str]
    Pu_kN: float
    loaded_area_A2_mm2: float
    effective_supporting_area_A1_mm2: float
    effective_supporting_area_basis: str
    bearing_enhancement_factor: float
    actual_bearing_stress_nmm2: float
    supported_concrete_bearing_capacity_kN: float
    supporting_concrete_bearing_capacity_kN: float
    governing_concrete_member: str
    governing_concrete_bearing_capacity_kN: float
    concrete_bearing_without_transfer_is_safe: bool
    excess_force_kN: float
    excess_transfer_steel_area_mm2: float
    minimum_transfer_steel_area_mm2: float
    required_transfer_steel_area_mm2: float
    provided_transfer_steel_area_mm2: float
    transfer_steel_capacity_kN: float
    minimum_bar_count: int
    provided_bar_count: int
    maximum_dowel_diameter_mm: float
    provided_dowel_diameter_mm: float
    supporting_concrete_design_bond_stress_nmm2: float
    supported_concrete_design_bond_stress_nmm2: float
    required_dowel_development_length_into_footing_mm: float
    required_dowel_development_length_into_supported_member_mm: float
    available_dowel_development_length_into_footing_mm: float
    available_dowel_development_length_into_supported_member_mm: float
    reinforcement_area_is_safe: bool
    bar_count_is_safe: bool
    dowel_diameter_is_safe: bool
    footing_development_length_is_safe: bool
    supported_member_development_length_is_safe: bool
    development_lengths_are_safe: bool
    is_safe: bool
    reasons: tuple[str, ...]


def _positive(name: str, value: float, clause_ref: str = "Cl. 34.4") -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValidationError(
            f"{name} must be positive",
            details={name: value},
            clause_ref=clause_ref,
        )


@clause("34.4", "34.4.1", "34.4.2", "34.4.3", "26.2.1")
def check_isolated_footing_load_transfer(
    *,
    Pu_kN: float,
    loaded_area_A2_mm2: float,
    effective_supporting_area_A1_mm2: float,
    effective_supporting_area_basis: str,
    effective_supporting_area_is_approved: bool,
    supporting_concrete_fck_nmm2: float,
    supported_concrete_fck_nmm2: float,
    steel_fy_nmm2: float,
    dowel_count: int,
    dowel_diameter_mm: float,
    column_longitudinal_bar_diameter_mm: float,
    available_dowel_development_length_into_footing_mm: float,
    available_dowel_development_length_into_supported_member_mm: float,
    dowel_bar_type: str = "deformed",
) -> LoadTransferResult:
    """Check Cl. 34.4 bearing transfer and dowels for the supported case.

    ``Pu_kN`` is the factored concentric axial action in kN.
    ``effective_supporting_area_A1_mm2`` must be an independently established
    lower-base area of a 1V:2H frustum wholly contained by the footing.  Plan
    dimensions are intentionally absent, so this API cannot infer ``A1`` from
    the full footing plan.  ``effective_supporting_area_is_approved`` is an
    explicit fail-closed acknowledgement of that geometry verification.

    The supported concrete has no submitted enlargement beyond the loaded
    section, so its bearing factor is one.  The supporting concrete uses
    ``min(sqrt(A1/A2), 2)``.  The governing concrete capacity determines the
    force that must be developed by transfer reinforcement.
    """
    _positive("Pu_kN", Pu_kN)
    _positive("loaded_area_A2_mm2", loaded_area_A2_mm2)
    _positive("effective_supporting_area_A1_mm2", effective_supporting_area_A1_mm2)
    _positive("supporting_concrete_fck_nmm2", supporting_concrete_fck_nmm2)
    _positive("supported_concrete_fck_nmm2", supported_concrete_fck_nmm2)
    _positive("steel_fy_nmm2", steel_fy_nmm2)
    _positive("dowel_diameter_mm", dowel_diameter_mm)
    _positive(
        "column_longitudinal_bar_diameter_mm", column_longitudinal_bar_diameter_mm
    )
    _positive(
        "available_dowel_development_length_into_footing_mm",
        available_dowel_development_length_into_footing_mm,
        "Cl. 34.4.2",
    )
    _positive(
        "available_dowel_development_length_into_supported_member_mm",
        available_dowel_development_length_into_supported_member_mm,
        "Cl. 34.4.2",
    )
    if isinstance(dowel_count, bool) or not isinstance(dowel_count, int):
        raise ValidationError(
            "dowel_count must be a positive integer",
            details={"dowel_count": dowel_count},
            clause_ref="Cl. 34.4.3",
        )
    if dowel_count <= 0:
        raise ValidationError(
            "dowel_count must be a positive integer",
            details={"dowel_count": dowel_count},
            clause_ref="Cl. 34.4.3",
        )
    if effective_supporting_area_A1_mm2 < loaded_area_A2_mm2:
        raise ValidationError(
            "effective supporting area A1 must be at least loaded area A2",
            details={
                "effective_supporting_area_A1_mm2": effective_supporting_area_A1_mm2,
                "loaded_area_A2_mm2": loaded_area_A2_mm2,
            },
            clause_ref="Cl. 34.4",
        )
    if effective_supporting_area_basis != _A1_BASIS:
        raise ValidationError(
            "effective A1 must be supplied as the approved 1V:2H largest-frustum lower base",
            details={
                "effective_supporting_area_basis": effective_supporting_area_basis,
                "required_basis": _A1_BASIS,
            },
            clause_ref="Cl. 34.4",
        )
    if not effective_supporting_area_is_approved:
        raise ValidationError(
            "effective A1 geometry is not approved; full footing plan area cannot be assumed",
            details={"effective_supporting_area_is_approved": False},
            clause_ref="Cl. 34.4",
        )
    if dowel_bar_type not in {"deformed", "plain"}:
        raise ValidationError(
            "dowel_bar_type must be 'deformed' or 'plain'",
            details={"dowel_bar_type": dowel_bar_type},
            clause_ref="Cl. 26.2.1",
        )
    if column_longitudinal_bar_diameter_mm > 36.0:
        raise ValidationError(
            "Column bars over 36 mm require the separate Cl. 34.4.4 dowel arrangement",
            details={
                "column_longitudinal_bar_diameter_mm": column_longitudinal_bar_diameter_mm
            },
            clause_ref="Cl. 34.4.4",
        )

    # N/mm2 times mm2 gives N.  Pu is converted once from kN to N.
    pu_n = Pu_kN * 1_000.0
    bearing_enhancement_factor = min(
        math.sqrt(effective_supporting_area_A1_mm2 / loaded_area_A2_mm2), 2.0
    )
    actual_bearing_stress_nmm2 = pu_n / loaded_area_A2_mm2
    supported_capacity_n = 0.45 * supported_concrete_fck_nmm2 * loaded_area_A2_mm2
    supporting_capacity_n = (
        0.45
        * supporting_concrete_fck_nmm2
        * bearing_enhancement_factor
        * loaded_area_A2_mm2
    )
    if supported_capacity_n <= supporting_capacity_n:
        governing_member = "supported_column_or_pedestal"
        governing_capacity_n = supported_capacity_n
    else:
        governing_member = "supporting_footing"
        governing_capacity_n = supporting_capacity_n

    excess_force_n = max(0.0, pu_n - governing_capacity_n)
    steel_design_stress_nmm2 = 0.87 * steel_fy_nmm2
    excess_transfer_steel_area_mm2 = excess_force_n / steel_design_stress_nmm2
    minimum_transfer_steel_area_mm2 = 0.005 * loaded_area_A2_mm2
    required_transfer_steel_area_mm2 = max(
        excess_transfer_steel_area_mm2, minimum_transfer_steel_area_mm2
    )
    provided_transfer_steel_area_mm2 = (
        dowel_count * math.pi * dowel_diameter_mm**2 / 4.0
    )
    transfer_steel_capacity_n = (
        provided_transfer_steel_area_mm2 * steel_design_stress_nmm2
    )

    supporting_bond_stress_nmm2 = get_bond_stress(
        supporting_concrete_fck_nmm2, dowel_bar_type
    )
    supported_bond_stress_nmm2 = get_bond_stress(
        supported_concrete_fck_nmm2, dowel_bar_type
    )
    required_footing_development_length_mm = (
        dowel_diameter_mm
        * steel_design_stress_nmm2
        / (4.0 * supporting_bond_stress_nmm2)
    )
    required_supported_development_length_mm = (
        dowel_diameter_mm
        * steel_design_stress_nmm2
        / (4.0 * supported_bond_stress_nmm2)
    )
    maximum_dowel_diameter_mm = column_longitudinal_bar_diameter_mm + 3.0

    reinforcement_area_is_safe = (
        provided_transfer_steel_area_mm2 >= required_transfer_steel_area_mm2
    )
    bar_count_is_safe = dowel_count >= 4
    dowel_diameter_is_safe = dowel_diameter_mm <= maximum_dowel_diameter_mm
    footing_development_length_is_safe = (
        available_dowel_development_length_into_footing_mm
        >= required_footing_development_length_mm
    )
    supported_member_development_length_is_safe = (
        available_dowel_development_length_into_supported_member_mm
        >= required_supported_development_length_mm
    )
    development_lengths_are_safe = (
        footing_development_length_is_safe
        and supported_member_development_length_is_safe
    )
    concrete_bearing_without_transfer_is_safe = pu_n <= governing_capacity_n
    is_safe = (
        reinforcement_area_is_safe
        and bar_count_is_safe
        and dowel_diameter_is_safe
        and development_lengths_are_safe
    )

    reasons = [f"Concrete bearing is governed by {governing_member}."]
    if concrete_bearing_without_transfer_is_safe:
        reasons.append(
            "Concrete bearing capacity alone carries the factored axial load."
        )
    else:
        reasons.append("Excess factored load requires transfer reinforcement.")
    if not reinforcement_area_is_safe:
        reasons.append("Provided dowel area is below the required transfer-steel area.")
    if not bar_count_is_safe:
        reasons.append("At least four transfer bars are required.")
    if not dowel_diameter_is_safe:
        reasons.append("Dowel diameter exceeds the column-bar diameter limit.")
    if not footing_development_length_is_safe:
        reasons.append(
            "Available dowel embedment into the footing is below required development length."
        )
    if not supported_member_development_length_is_safe:
        reasons.append(
            "Available dowel embedment into the supported member is below required development length."
        )
    if is_safe:
        reasons.append("Provided dowels satisfy the bounded Cl. 34.4 transfer check.")

    return LoadTransferResult(
        source_ids=(IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID),
        source_notes=(
            "IS 456 consolidated source used for Clauses 34.4 and 26.2.1.",
            "Supplied Amendment 6 has no footing load-transfer change.",
        ),
        clause_refs=(
            "Cl. 34.4",
            "Cl. 34.4.1",
            "Cl. 34.4.2",
            "Cl. 34.4.3",
            "Cl. 26.2.1",
        ),
        supported_case=_SUPPORTED_CASE,
        exclusions=_EXCLUSIONS,
        units={
            "force": "kN",
            "area": "mm2",
            "stress": "N/mm2",
            "length": "mm",
        },
        limits={
            "maximum_bearing_enhancement_factor": 2.0,
            "minimum_transfer_steel_ratio": 0.005,
            "minimum_transfer_bar_count": 4,
            "maximum_dowel_diameter_increment_over_column_bar_mm": 3.0,
            "effective_A1_basis": _A1_BASIS,
        },
        Pu_kN=Pu_kN,
        loaded_area_A2_mm2=loaded_area_A2_mm2,
        effective_supporting_area_A1_mm2=effective_supporting_area_A1_mm2,
        effective_supporting_area_basis=effective_supporting_area_basis,
        bearing_enhancement_factor=bearing_enhancement_factor,
        actual_bearing_stress_nmm2=actual_bearing_stress_nmm2,
        supported_concrete_bearing_capacity_kN=supported_capacity_n / 1_000.0,
        supporting_concrete_bearing_capacity_kN=supporting_capacity_n / 1_000.0,
        governing_concrete_member=governing_member,
        governing_concrete_bearing_capacity_kN=governing_capacity_n / 1_000.0,
        concrete_bearing_without_transfer_is_safe=concrete_bearing_without_transfer_is_safe,
        excess_force_kN=excess_force_n / 1_000.0,
        excess_transfer_steel_area_mm2=excess_transfer_steel_area_mm2,
        minimum_transfer_steel_area_mm2=minimum_transfer_steel_area_mm2,
        required_transfer_steel_area_mm2=required_transfer_steel_area_mm2,
        provided_transfer_steel_area_mm2=provided_transfer_steel_area_mm2,
        transfer_steel_capacity_kN=transfer_steel_capacity_n / 1_000.0,
        minimum_bar_count=4,
        provided_bar_count=dowel_count,
        maximum_dowel_diameter_mm=maximum_dowel_diameter_mm,
        provided_dowel_diameter_mm=dowel_diameter_mm,
        supporting_concrete_design_bond_stress_nmm2=supporting_bond_stress_nmm2,
        supported_concrete_design_bond_stress_nmm2=supported_bond_stress_nmm2,
        required_dowel_development_length_into_footing_mm=(
            required_footing_development_length_mm
        ),
        required_dowel_development_length_into_supported_member_mm=(
            required_supported_development_length_mm
        ),
        available_dowel_development_length_into_footing_mm=(
            available_dowel_development_length_into_footing_mm
        ),
        available_dowel_development_length_into_supported_member_mm=(
            available_dowel_development_length_into_supported_member_mm
        ),
        reinforcement_area_is_safe=reinforcement_area_is_safe,
        bar_count_is_safe=bar_count_is_safe,
        dowel_diameter_is_safe=dowel_diameter_is_safe,
        footing_development_length_is_safe=footing_development_length_is_safe,
        supported_member_development_length_is_safe=(
            supported_member_development_length_is_safe
        ),
        development_lengths_are_safe=development_lengths_are_safe,
        is_safe=is_safe,
        reasons=tuple(reasons),
    )
