# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Clause 32.2 geometry and empirical axial capacity for braced walls."""

from __future__ import annotations

from dataclasses import dataclass

from structural_lib.codes.is456.traceability import clause
from structural_lib.codes.is456.wall.models import (
    BracedWallAxialInput,
    BracedWallGeometry,
    WallAxialStatus,
    WallContractError,
    WallRotationRestraint,
)

__all__ = [
    "BracedWallAxialResult",
    "BracedWallGeometryResult",
    "check_braced_wall_axial_capacity",
    "resolve_braced_wall_geometry",
]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 32.2.1-32.2.5",
    "IS456-2000-A6",
)


@dataclass(frozen=True)
class BracedWallGeometryResult:
    """Resolved Clause 32.2.4 effective height and wall slenderness."""

    input: BracedWallGeometry
    height_effective_component_mm: float
    lateral_effective_component_mm: float
    effective_height_mm: float
    effective_height_to_thickness_ratio: float
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class BracedWallAxialResult:
    """Empirical axial-capacity check with explicit N/mm and kN outputs."""

    input: BracedWallAxialInput
    geometry: BracedWallGeometryResult
    minimum_eccentricity_mm: float
    design_eccentricity_mm: float
    additional_eccentricity_mm: float
    effective_compression_thickness_mm: float
    axial_capacity_n_per_mm: float
    axial_capacity_kn_per_m: float
    total_axial_capacity_kn: float
    axial_demand_n_per_mm: float
    axial_demand_kn_per_m: float
    utilization_ratio: float
    status: WallAxialStatus
    source_refs: tuple[str, ...]
    load_generation_status: str = "not_generated_caller_supplied_factored_action"


@clause("32.2.1", "32.2.3", "32.2.4")
def resolve_braced_wall_geometry(
    geometry: BracedWallGeometry,
) -> BracedWallGeometryResult:
    """Resolve effective height and enforce the Clause 32.2 slenderness limit."""
    if not isinstance(geometry, BracedWallGeometry):
        raise WallContractError("geometry must be a BracedWallGeometry")

    factor = (
        0.75
        if geometry.rotation_restraint is WallRotationRestraint.RESTRAINED_BOTH_ENDS
        else 1.0
    )
    height_component = factor * geometry.unsupported_height_mm
    lateral_component = factor * geometry.lateral_restraint_spacing_mm
    effective_height = min(height_component, lateral_component)
    slenderness_ratio = effective_height / geometry.wall_thickness_mm
    if slenderness_ratio > 30.0:
        raise WallContractError(
            "effective_height_mm / wall_thickness_mm must not exceed 30 "
            "for the Clause 32.2 empirical method"
        )

    return BracedWallGeometryResult(
        input=geometry,
        height_effective_component_mm=height_component,
        lateral_effective_component_mm=lateral_component,
        effective_height_mm=effective_height,
        effective_height_to_thickness_ratio=slenderness_ratio,
        source_refs=_SOURCE_REFS,
    )


@clause("32.2.2", "32.2.5")
def check_braced_wall_axial_capacity(
    design_input: BracedWallAxialInput,
) -> BracedWallAxialResult:
    """Check caller-supplied factored compression using Clause 32.2.5.

    The normalized empirical formula is evaluated per unit wall length in
    N/mm. The result also exposes the equivalent kN/m and full-wall kN values.
    """
    if not isinstance(design_input, BracedWallAxialInput):
        raise WallContractError("design_input must be a BracedWallAxialInput")

    geometry = resolve_braced_wall_geometry(design_input.geometry)
    thickness_mm = design_input.geometry.wall_thickness_mm
    minimum_eccentricity_mm = 0.05 * thickness_mm
    design_eccentricity_mm = max(
        design_input.supplied_eccentricity_mm,
        minimum_eccentricity_mm,
    )
    additional_eccentricity_mm = geometry.effective_height_mm**2 / (
        2500.0 * thickness_mm
    )
    effective_compression_thickness_mm = (
        thickness_mm - 1.2 * design_eccentricity_mm - 2.0 * additional_eccentricity_mm
    )
    if effective_compression_thickness_mm <= 0.0:
        raise WallContractError(
            "Clause 32.2.5 effective compression thickness must be positive; "
            "use the general combined compression/flexure path"
        )

    # IS 456:2000 Cl. 32.2.5, limit-state empirical capacity per unit length.
    axial_capacity_n_per_mm = (
        0.3 * effective_compression_thickness_mm * design_input.concrete_grade_nmm2
    )
    wall_length_mm = design_input.geometry.wall_length_mm
    axial_demand_n_per_mm = (
        design_input.factored_axial_load_kn * 1000.0 / wall_length_mm
    )
    utilization_ratio = axial_demand_n_per_mm / axial_capacity_n_per_mm
    status = WallAxialStatus.PASS if utilization_ratio <= 1.0 else WallAxialStatus.FAIL

    return BracedWallAxialResult(
        input=design_input,
        geometry=geometry,
        minimum_eccentricity_mm=minimum_eccentricity_mm,
        design_eccentricity_mm=design_eccentricity_mm,
        additional_eccentricity_mm=additional_eccentricity_mm,
        effective_compression_thickness_mm=effective_compression_thickness_mm,
        axial_capacity_n_per_mm=axial_capacity_n_per_mm,
        axial_capacity_kn_per_m=axial_capacity_n_per_mm,
        total_axial_capacity_kn=axial_capacity_n_per_mm * wall_length_mm / 1000.0,
        axial_demand_n_per_mm=axial_demand_n_per_mm,
        axial_demand_kn_per_m=axial_demand_n_per_mm,
        utilization_ratio=utilization_ratio,
        status=status,
        source_refs=_SOURCE_REFS
        + (
            design_input.geometry.bracing_basis_reference,
            design_input.action_basis_reference,
        ),
    )
