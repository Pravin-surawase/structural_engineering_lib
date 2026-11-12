"""Physical restraint and local quantities for a circular bar ring."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, pi, sin

from .circular import circular_bars
from .detailing import (
    calculate_tie_spacing,
    check_longitudinal_limits,
    check_min_bar_diameter,
    get_min_bar_count,
    minimum_tie_diameter,
)
from .four_corner import ColumnCageCheck
from .helical import enhancement_pitch_limits, minimum_helical_ratio
from .positioned_biaxial import PositionedColumnBar

_RESTRAINT = "IS 456:2000 Cl. 26.5.3"
_COVER = "IS 456:2000 Cl. 26.4 and declared cover requirement"
_HELIX = "IS 456:2000 Cl. 26.5.3.2(d) and 39.4.1"


@dataclass(frozen=True)
class CircularTransverse:
    """Size and axial spacing of the supplied transverse steel."""

    tie_id: str
    diameter_mm: float
    pitch_mm: float


@dataclass(frozen=True)
class CircularRing(CircularTransverse):
    """Closed ring and supplied circumferential closure detail."""

    closed: bool
    closure_reference: str | None


@dataclass(frozen=True)
class CircularSpiral(CircularTransverse):
    """Uniform helix, end turns and requested axial enhancement."""

    fy_nmm2: float
    start_extra_turns: float | None
    end_extra_turns: float | None
    axial_enhancement: bool


@dataclass(frozen=True)
class CircularCage:
    """Checked actual bar and transverse geometry for one section."""

    bars: tuple[PositionedColumnBar, ...]
    gross_area_mm2: float
    steel_area_mm2: float
    gross_inertia_mm4: float
    steel_ratio: float
    section_admitted: bool
    detail: dict[str, float]
    checks: tuple[ColumnCageCheck, ...]
    missing_evidence: tuple[tuple[str, str], ...]
    spiral_enhancement_eligible: bool


def check_circular_cage(
    *,
    diameter_mm: float,
    count: int,
    bar_diameter_mm: float,
    ring_radius_mm: float,
    first_angle_deg: float,
    aggregate_size_mm: float,
    nominal_cover_mm: float,
    project_cover_mm: float,
    fck: float,
    transverse: CircularRing | CircularSpiral | None,
) -> CircularCage:
    """Check local fit, continuous restraint and any requested enhancement."""
    bars = circular_bars(
        diameter_mm, count, bar_diameter_mm, ring_radius_mm, first_angle_deg
    )
    gross = pi * diameter_mm**2 / 4
    steel = sum(bar.area_mm2 for bar in bars)
    ratio, minimum_ok, maximum_ok, _ = check_longitudinal_limits(gross, steel)
    detail = {
        "clear_spacing_mm": 2 * ring_radius_mm * sin(pi / count) - bar_diameter_mm,
        "minimum_clear_spacing_mm": max(bar_diameter_mm, aggregate_size_mm + 5),
        "periphery_spacing_mm": pi * diameter_mm / count,
        "required_cover_mm": max(40.0, bar_diameter_mm, project_cover_mm),
        "longitudinal_cover_mm": diameter_mm / 2 - ring_radius_mm - bar_diameter_mm / 2,
        "ordinary_pitch_limit_mm": calculate_tie_spacing(
            diameter_mm, diameter_mm, bar_diameter_mm
        ),
        "minimum_transverse_diameter_mm": minimum_tie_diameter(bar_diameter_mm),
    }
    checks: list[ColumnCageCheck] = []
    missing: list[tuple[str, str]] = []

    def record(
        code: str,
        passed: bool,
        actual: float | bool,
        limit: float | bool,
        source: str = _RESTRAINT,
    ) -> None:
        checks.append(ColumnCageCheck(f"COLUMN.{code}", passed, actual, limit, source))

    count_min = get_min_bar_count(is_circular=True)
    record("BAR_COUNT", count >= count_min, count, count_min)
    record(
        "LONGITUDINAL_DIAMETER",
        check_min_bar_diameter(bar_diameter_mm),
        bar_diameter_mm,
        12,
    )
    record("STEEL_RATIO_MIN", minimum_ok, ratio, 0.008)
    record(
        "STEEL_RATIO_MAX",
        maximum_ok,
        ratio,
        0.04,
        "Admitted section model and IS 456 Cl. 26.5.3.1",
    )
    clear, minimum_clear = (
        detail["clear_spacing_mm"],
        detail["minimum_clear_spacing_mm"],
    )
    record(
        "CLEAR_SPACING",
        clear >= minimum_clear,
        clear,
        minimum_clear,
        "IS 456:2000 Cl. 26.3.2",
    )
    periphery = detail["periphery_spacing_mm"]
    record("PERIPHERAL_SPACING", periphery <= 300, periphery, 300)
    required_cover, longitudinal_cover = (
        detail["required_cover_mm"],
        detail["longitudinal_cover_mm"],
    )
    record(
        "LONGITUDINAL_COVER",
        longitudinal_cover >= required_cover,
        longitudinal_cover,
        required_cover,
        _COVER,
    )

    eligible = False
    if transverse is None:
        missing.append(
            (
                "COLUMN.CIRCULAR_TRANSVERSE_REQUIRED",
                "Supply a closed ring or regular spiral.",
            )
        )
    else:
        dt, pitch = transverse.diameter_mm, transverse.pitch_mm
        core = diameter_mm - 2 * nominal_cover_mm
        centreline = core - dt
        radial_gap = core / 2 - dt - ring_radius_mm - bar_diameter_mm / 2
        detail.update(
            core_outside_mm=core,
            transverse_centreline_diameter_mm=centreline,
            radial_gap_mm=radial_gap,
        )
        record(
            "TRANSVERSE_COVER",
            nominal_cover_mm >= required_cover,
            nominal_cover_mm,
            required_cover,
            _COVER,
        )
        record("CIRCULAR_CONTACT", abs(radial_gap) <= 1e-6, radial_gap, 0)
        minimum_diameter, pitch_limit = (
            detail["minimum_transverse_diameter_mm"],
            detail["ordinary_pitch_limit_mm"],
        )
        record("TRANSVERSE_DIAMETER", dt >= minimum_diameter, dt, minimum_diameter)
        record("TRANSVERSE_PITCH", pitch <= pitch_limit, pitch, pitch_limit)
        turn = pi * centreline
        if isinstance(transverse, CircularRing):
            record("RING_CLOSED", transverse.closed, transverse.closed, True)
            if (
                not transverse.closure_reference
                or not transverse.closure_reference.strip()
            ):
                missing.append(
                    (
                        "COLUMN.RING_CLOSURE_EVIDENCE",
                        "Identify the ring closure detail that develops circumferential tension.",
                    )
                )
            separation = pitch
        else:
            # A chord lower bound over ±half a turn gives a conservative
            # lower bound on separation between adjacent turns in 3D.
            separation = pitch / hypot(1, pitch / (2 * centreline))
            turn = hypot(turn, pitch)
            used_fy = min(transverse.fy_nmm2, 415.0)
            core_area = pi * core**2 / 4
            provided = (pi * dt**2 / 4) * turn / (core_area * pitch)
            required = minimum_helical_ratio(gross, core_area, fck, used_fy)
            low, high = enhancement_pitch_limits(core, dt)
            detail.update(
                spiral_ratio_provided=provided,
                spiral_ratio_required=required,
                spiral_fy_used_nmm2=used_fy,
                enhanced_min_pitch_mm=low,
                enhanced_max_pitch_mm=high,
            )
            for side, turns in (
                ("START", transverse.start_extra_turns),
                ("END", transverse.end_extra_turns),
            ):
                if turns is None:
                    missing.append(
                        (
                            f"COLUMN.SPIRAL_{side}_ANCHORAGE_EVIDENCE",
                            f"Supply the extra anchorage turns at the spiral {side.lower()}.",
                        )
                    )
                else:
                    record(f"SPIRAL_{side}_ANCHORAGE", turns >= 1.5, turns, 1.5, _HELIX)
            if transverse.axial_enhancement:
                record("SPIRAL_ENHANCED_MIN_PITCH", pitch >= low, pitch, low, _HELIX)
                record("SPIRAL_ENHANCED_MAX_PITCH", pitch <= high, pitch, high, _HELIX)
                record("SPIRAL_RATIO", provided >= required, provided, required, _HELIX)
                eligible = True
        detail["centreline_length_per_pitch_mm"] = turn
        record(
            "TRANSVERSE_NONOVERLAP",
            separation >= dt,
            separation,
            dt,
            "Physical separation of consecutive levels",
        )

    return CircularCage(
        bars,
        gross,
        steel,
        pi * diameter_mm**4 / 64,
        ratio,
        minimum_ok and maximum_ok and clear >= 0,
        detail,
        tuple(checks),
        tuple(missing),
        eligible and not missing and all(check.passed for check in checks),
    )
