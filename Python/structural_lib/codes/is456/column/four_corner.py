"""Physical ordinary four-corner cage geometry and IS 456 detailing checks."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Literal

from structural_lib.codes.is456.beam.detailing import check_min_spacing
from structural_lib.core.geometry import circle_inside_rounded_rectangle

from .detailing import (
    calculate_tie_spacing,
    check_longitudinal_limits,
    check_min_bar_diameter,
)


@dataclass(frozen=True)
class ColumnCageCheck:
    code: str
    passed: bool
    actual: float | bool
    limit: float | bool
    source_reference: str


@dataclass(frozen=True)
class FourCornerBar:
    bar_id: str
    diameter_mm: float
    area_mm2: float
    x_from_left_mm: float
    y_from_top_mm: float


@dataclass(frozen=True)
class FourCornerCage:
    supplied_steel_area_mm2: float
    steel_ratio: float
    bar_centroid_offset_mm: float
    bars: tuple[FourCornerBar, ...]
    tie_centreline_width_mm: float
    tie_centreline_depth_mm: float
    minimum_tie_diameter_mm: float
    maximum_tie_spacing_mm: float
    checks: tuple[ColumnCageCheck, ...]


def evaluate_four_corner_cage(
    *,
    b_mm: float,
    D_mm: float,
    bar_diameter_mm: float,
    nominal_cover_mm: float,
    corner_inset_mm: float,
    aggregate_size_mm: float,
    project_required_cover_mm: float,
    project_required_bend_radius_mm: float,
    tie_diameter_mm: float,
    tie_spacing_mm: float,
    tie_internal_bend_radius_mm: float,
    tie_closed: bool,
    tie_hook_angle_deg: float,
    tie_hook_tail_mm: float,
    midpoint_axes: tuple[Literal["x", "y"], ...] = (),
) -> FourCornerCage:
    """Resolve the perimeter tie's corners and any selected face-midpoint pairs.

    This checks enclosure and spacing. A separate check must establish
    restraint for the midpoint bars.
    """
    area = pi * bar_diameter_mm**2 / 4
    offset = nominal_cover_mm + tie_diameter_mm + bar_diameter_mm / 2 + corner_inset_mm
    bar_coordinates = [
        ("C1", offset, offset),
        ("C2", b_mm - offset, offset),
        ("C3", b_mm - offset, D_mm - offset),
        ("C4", offset, D_mm - offset),
    ]
    if "x" in midpoint_axes:
        bar_coordinates.extend(
            (("M_LEFT", offset, D_mm / 2), ("M_RIGHT", b_mm - offset, D_mm / 2))
        )
    if "y" in midpoint_axes:
        bar_coordinates.extend(
            (("M_TOP", b_mm / 2, offset), ("M_BOTTOM", b_mm / 2, D_mm - offset))
        )
    bars = tuple(
        FourCornerBar(bar_id, bar_diameter_mm, area, x, y)
        for bar_id, x, y in bar_coordinates
    )
    steel = len(bars) * area
    ratio, minimum_ok, maximum_ok, _ = check_longitudinal_limits(b_mm * D_mm, steel)
    centre_gaps = (
        (b_mm - 2 * offset) / (2 if "y" in midpoint_axes else 1),
        (D_mm - 2 * offset) / (2 if "x" in midpoint_axes else 1),
    )
    required_cover = max(40.0, bar_diameter_mm, project_required_cover_mm)
    minimum_clear = max(bar_diameter_mm, aggregate_size_mm + 5, 25.0)
    min_spacing_ok = all(
        check_min_spacing(gap, bar_diameter_mm, aggregate_size_mm)[0]
        for gap in centre_gaps
    )
    maximum_spacing = calculate_tie_spacing(b_mm, D_mm, bar_diameter_mm)
    minimum_tie_dia = max(6.0, bar_diameter_mm / 4)
    centre_width = b_mm - 2 * nominal_cover_mm - tie_diameter_mm
    centre_depth = D_mm - 2 * nominal_cover_mm - tie_diameter_mm
    minimum_bend_extent = 2 * tie_internal_bend_radius_mm + tie_diameter_mm
    bend_fits = min(centre_width, centre_depth) + 1e-9 >= minimum_bend_extent
    available_hook_tail = max(
        0.0, min(centre_width, centre_depth) - minimum_bend_extent
    )
    inner_face = nominal_cover_mm + tie_diameter_mm
    enclosure_ok = bend_fits and all(
        circle_inside_rounded_rectangle(
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            bar_diameter_mm / 2,
            inner_face,
            b_mm - inner_face,
            inner_face,
            D_mm - inner_face,
            tie_internal_bend_radius_mm,
        )
        for bar in bars
    )
    checks = (
        ColumnCageCheck(
            "COLUMN.STEEL_MIN", minimum_ok, ratio, 0.008, "IS 456:2000 Cl. 26.5.3.1"
        ),
        ColumnCageCheck(
            "COLUMN.STEEL_MAX",
            maximum_ok,
            ratio,
            0.04,
            "Supported 0.8–4% supplied-steel member profile",
        ),
        ColumnCageCheck(
            "COLUMN.BAR_DIAMETER",
            check_min_bar_diameter(bar_diameter_mm),
            bar_diameter_mm,
            12,
            "IS 456:2000 Cl. 26.5.3.1",
        ),
        ColumnCageCheck(
            "COLUMN.COVER",
            nominal_cover_mm >= required_cover,
            nominal_cover_mm,
            required_cover,
            "IS 456:2000 Cl. 26.4.2.1 and project cover requirement",
        ),
        ColumnCageCheck(
            "COLUMN.BAR_CENTRES",
            min(centre_gaps) > 0,
            min(centre_gaps),
            0,
            "Four distinct ordered corner centres",
        ),
        ColumnCageCheck(
            "COLUMN.CLEAR_SPACING",
            min_spacing_ok,
            min(centre_gaps) - bar_diameter_mm,
            minimum_clear,
            "IS 456:2000 Cl. 26.3.2; supported minimum 25 mm",
        ),
        ColumnCageCheck(
            "COLUMN.PERIPHERAL_SPACING",
            max(centre_gaps) <= 300,
            max(centre_gaps),
            300,
            "IS 456:2000 Cl. 26.5.3.1",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_DIAMETER",
            tie_diameter_mm >= minimum_tie_dia,
            tie_diameter_mm,
            minimum_tie_dia,
            "IS 456:2000 Cl. 26.5.3.2",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_SPACING",
            tie_spacing_mm <= maximum_spacing,
            tie_spacing_mm,
            maximum_spacing,
            "IS 456:2000 Cl. 26.5.3.2",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_CLOSED",
            tie_closed,
            tie_closed,
            True,
            "IS 456:2000 Cl. 26.5.3.2",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_BEND_RADIUS",
            tie_internal_bend_radius_mm >= project_required_bend_radius_mm,
            tie_internal_bend_radius_mm,
            project_required_bend_radius_mm,
            "Declared project bend schedule",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_BEND_FIT",
            bend_fits,
            min(centre_width, centre_depth),
            minimum_bend_extent,
            "Rounded tie centreline geometry",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_ENCLOSURE",
            enclosure_ok,
            enclosure_ok,
            True,
            "Whole bar circles inside the rounded tie",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_HOOK_ANGLE",
            tie_hook_angle_deg == 135,
            tie_hook_angle_deg,
            135,
            "Supported IS 456:2000 Cl. 26.2.2.4(b) hook",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_HOOK_TAIL",
            tie_hook_tail_mm >= 6 * tie_diameter_mm,
            tie_hook_tail_mm,
            6 * tie_diameter_mm,
            "IS 456:2000 Cl. 26.2.2.4(b)",
        ),
        ColumnCageCheck(
            "COLUMN.TIE_HOOK_FIT",
            tie_hook_tail_mm <= available_hook_tail,
            tie_hook_tail_mm,
            available_hook_tail,
            "Supported hook continuation within the shortest straight leg between bend tangencies",
        ),
    )
    return FourCornerCage(
        steel,
        ratio,
        offset,
        bars,
        centre_width,
        centre_depth,
        minimum_tie_dia,
        maximum_spacing,
        checks,
    )
