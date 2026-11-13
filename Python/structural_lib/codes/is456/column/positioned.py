"""Fixed-compression capacity for actual bars in a symmetric rectangle."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ._common import _calculate_puz
from ._layered_section import SectionResult, rectangular_layered_section
from .axial import min_eccentricity
from .biaxial import _calculate_alpha_n
from .four_corner import FourCornerBar, FourCornerCage


@dataclass(frozen=True)
class AxisBarResponse:
    """A positioned bar's response at the reported capacity plane."""

    bar_id: str
    depth_from_compression_face_mm: float
    strain: float
    net_force_kn: float
    centroid_moment_knm: float


@dataclass(frozen=True)
class PositionedAxisCapacity:
    """Moment magnitude and force residual at a fixed axial load."""

    compression_face: str
    xu_mm: float
    capacity_knm: float
    axial_residual_kn: float
    bars: tuple[AxisBarResponse, ...]


def fixed_compression_capacity(
    *,
    width_mm: float,
    depth_mm: float,
    pu_kn: float,
    fck_nmm2: float,
    fy_nmm2: float,
    bars: tuple[FourCornerBar, ...],
    depth_coordinates_mm: tuple[float, ...],
    compression_face: str,
) -> PositionedAxisCapacity | None:
    """Solve for equilibrium with the neutral axis strictly inside the section."""
    layers = tuple(
        (depth, bar.area_mm2)
        for depth, bar in zip(depth_coordinates_mm, bars, strict=True)
    )

    def response(xu_mm: float) -> SectionResult:
        return rectangular_layered_section(
            b_mm=width_mm,
            D_mm=depth_mm,
            xu_mm=xu_mm,
            fck_nmm2=fck_nmm2,
            fy_nmm2=fy_nmm2,
            layer_depths_and_areas=layers,
        )

    target_n = pu_kn * 1000
    lo, hi = depth_mm * 1e-6, depth_mm
    if not response(lo).axial_force_n < target_n < response(hi).axial_force_n:
        return None
    for _ in range(56):
        mid = (lo + hi) / 2
        if response(mid).axial_force_n < target_n:
            lo = mid
        else:
            hi = mid
    xu = (lo + hi) / 2
    solved = response(xu)
    residual_kn = (solved.axial_force_n - target_n) / 1000
    capacity_knm = solved.centroid_moment_nmm / 1e6
    if abs(residual_kn) > 0.01 or capacity_knm <= 0:
        return None
    return PositionedAxisCapacity(
        compression_face=compression_face,
        xu_mm=xu,
        capacity_knm=capacity_knm,
        axial_residual_kn=residual_kn,
        bars=tuple(
            AxisBarResponse(
                bar_id=bar.bar_id,
                depth_from_compression_face_mm=depth,
                strain=layer.strain,
                net_force_kn=layer.net_force_n / 1000,
                centroid_moment_knm=layer.centroid_moment_nmm / 1e6,
            )
            for bar, depth, layer in zip(
                bars, depth_coordinates_mm, solved.layers, strict=True
            )
        ),
    )


@dataclass(frozen=True)
class PositionedMemberStrength:
    """Separate the supplied contour check, eccentricity checks and axial limit."""

    pu_kn: float
    puz_kn: float
    alpha_n: float
    minimum_eccentricity_x_mm: float
    minimum_eccentricity_y_mm: float
    axes: dict[str, PositionedAxisCapacity | None]
    interaction_ratio: float | None = None
    minimum_eccentricity_ratio_x: float | None = None
    minimum_eccentricity_ratio_y: float | None = None
    governing_ratio: float | None = None
    governing_basis: str | None = None


def positioned_member_strength(
    *,
    b_mm: float,
    D_mm: float,
    unsupported_length_mm: float,
    pu_kn: float,
    mx_knm: float,
    my_knm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    cage: FourCornerCage,
) -> PositionedMemberStrength:
    """Apply Cl. 39.6 to the actual principal capacities at the supplied load."""
    puz = _calculate_puz(b_mm, D_mm, fck_nmm2, fy_nmm2, cage.supplied_steel_area_mm2)
    alpha = _calculate_alpha_n(pu_kn, puz)
    emin_x = min_eccentricity(unsupported_length_mm, D_mm)
    emin_y = min_eccentricity(unsupported_length_mm, b_mm)
    axes: dict[str, PositionedAxisCapacity | None] = {"x": None, "y": None}
    if pu_kn < puz:
        for axis, width, depth, moment, coordinate, faces in (
            ("x", b_mm, D_mm, mx_knm, "y_from_top_mm", ("top", "bottom")),
            ("y", D_mm, b_mm, my_knm, "x_from_left_mm", ("left", "right")),
        ):
            depths = tuple(getattr(bar, coordinate) for bar in cage.bars)
            axes[axis] = fixed_compression_capacity(
                width_mm=width,
                depth_mm=depth,
                pu_kn=pu_kn,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
                bars=cage.bars,
                depth_coordinates_mm=(
                    tuple(depth - distance for distance in depths)
                    if moment < 0
                    else depths
                ),
                compression_face=faces[moment < 0],
            )
    strength = PositionedMemberStrength(pu_kn, puz, alpha, emin_x, emin_y, axes)
    x, y = axes["x"], axes["y"]
    if x is None or y is None:
        return strength

    interaction = (abs(mx_knm) / x.capacity_knm) ** alpha + (
        abs(my_knm) / y.capacity_knm
    ) ** alpha
    minimum_x = pu_kn * emin_x / 1000 / x.capacity_knm
    minimum_y = pu_kn * emin_y / 1000 / y.capacity_knm
    ratios = {
        "supplied_cl39_6": interaction,
        "minimum_eccentricity_x": minimum_x,
        "minimum_eccentricity_y": minimum_y,
    }
    basis, governing = max(ratios.items(), key=lambda item: item[1])
    return replace(
        strength,
        interaction_ratio=interaction,
        minimum_eccentricity_ratio_x=minimum_x,
        minimum_eccentricity_ratio_y=minimum_y,
        governing_ratio=governing,
        governing_basis=basis,
    )
