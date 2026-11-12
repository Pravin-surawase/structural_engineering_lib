"""Slender-member actions for the actual-bar section check."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from structural_lib.core.data_types import ColumnClassification

from .axial import classify_column, min_eccentricity
from .long_column import _initial_moment
from .slenderness import _additional_eccentricity


@dataclass(frozen=True)
class SlenderPlaneDemand:
    """One plane's member checks and signed bounds for equivalent pairs."""

    unsupported_length_mm: float
    effective_length_mm: float
    slenderness: float
    classification: str
    minimum_eccentricity_mm: float
    initial_moment_knm: float
    end_floor_knm: float
    additional_moment_knm: float
    component_options_knm: tuple[float, ...]


def slender_plane_demand(
    *,
    dimension_mm: float,
    unsupported_mm: float,
    effective_mm: float,
    pu_kn: float,
    end_moments_knm: tuple[float, float] | None,
) -> SlenderPlaneDemand:
    """Apply the unreduced additional moment for admitted first-order actions."""
    classification = classify_column(effective_mm, dimension_mm)
    initial = floor = additional = 0.0
    options: tuple[float, ...] = ()
    if end_moments_knm is not None:
        small, large = sorted(end_moments_knm, key=abs)
        floor = abs(large)
        initial = _initial_moment(small, large, braced=True)
        if classification is ColumnClassification.SLENDER:
            additional = (
                pu_kn * _additional_eccentricity(effective_mm, dimension_mm) / 1000
            )
        bound = max(floor, initial + additional)
        signs = {1 if moment > 0 else -1 for moment in end_moments_knm if moment}
        # Reverse curvature retains both compression sides. An unknown
        # direction with a nonzero addition also checks both sides.
        options = (
            tuple(sorted(sign * bound for sign in (signs or {-1, 1})))
            if bound
            else (0.0,)
        )
    return SlenderPlaneDemand(
        unsupported_mm,
        effective_mm,
        effective_mm / dimension_mm,
        classification.name,
        min_eccentricity(unsupported_mm, dimension_mm),
        initial,
        floor,
        additional,
        options,
    )


def equivalent_slender_pairs(
    x: SlenderPlaneDemand, y: SlenderPlaneDemand
) -> tuple[tuple[str, float, float], ...]:
    """Return conservative signed equivalent pairs without physical station IDs."""
    return tuple(
        (
            "EQUIVALENT-"
            + "".join("N" if m < 0 else "P" if m > 0 else "0" for m in (mx, my)),
            mx,
            my,
        )
        for mx, my in product(x.component_options_knm, y.component_options_knm)
    )
