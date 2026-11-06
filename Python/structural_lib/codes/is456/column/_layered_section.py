"""Pure IS 456 resultants for depth-wise reinforcement in a solid rectangle."""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum

from structural_lib.codes.is456.column._strain_compatibility import (
    concrete_stress_at_strain,
    extreme_compression_strain,
    rectangular_concrete_resultants,
)
from structural_lib.codes.is456.section_materials import section_steel_stress


@dataclass(frozen=True)
class LayerResult:
    strain: float
    steel_stress_nmm2: float
    displaced_concrete_stress_nmm2: float
    net_force_n: float
    centroid_moment_nmm: float


@dataclass(frozen=True)
class SectionResult:
    top_strain: float
    far_face_strain: float
    gross_concrete_force_n: float
    gross_concrete_centroid_moment_nmm: float
    axial_force_n: float
    centroid_moment_nmm: float
    layers: tuple[LayerResult, ...]


def rectangular_layered_section(
    *,
    b_mm: float,
    D_mm: float,
    xu_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    layer_depths_and_areas: tuple[tuple[float, float], ...],
) -> SectionResult:
    """Evaluate a validated strain plane in N and Nmm, with compression positive."""
    top_strain = extreme_compression_strain(xu_mm, D_mm)
    concrete_force, concrete_moment = rectangular_concrete_resultants(
        xu_mm, b_mm, D_mm, fck_nmm2
    )
    layers = []
    for depth_mm, area_mm2 in layer_depths_and_areas:
        strain = top_strain * (1 - depth_mm / xu_mm)
        steel_stress = section_steel_stress(strain, fy_nmm2)
        concrete_stress = concrete_stress_at_strain(strain, fck_nmm2)
        net_force = area_mm2 * (steel_stress - concrete_stress)
        layers.append(
            LayerResult(
                strain=strain,
                steel_stress_nmm2=steel_stress,
                displaced_concrete_stress_nmm2=concrete_stress,
                net_force_n=net_force,
                centroid_moment_nmm=net_force * (D_mm / 2 - depth_mm),
            )
        )
    return SectionResult(
        top_strain=top_strain,
        far_face_strain=top_strain * (1 - D_mm / xu_mm),
        gross_concrete_force_n=concrete_force,
        gross_concrete_centroid_moment_nmm=concrete_moment,
        axial_force_n=concrete_force + fsum(layer.net_force_n for layer in layers),
        centroid_moment_nmm=concrete_moment
        + fsum(layer.centroid_moment_nmm for layer in layers),
        layers=tuple(layers),
    )
