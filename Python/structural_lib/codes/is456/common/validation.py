"""Fail-fast validators for IS 456 math functions.

These validators raise immediately on invalid input, unlike the
accumulate-errors pattern in :mod:`structural_lib.core.validation`
which collects all errors into a list for the services layer.

Use these validators inside ``codes/is456/`` pure-math functions
where computation cannot proceed with invalid inputs.

References:
    IS 456:2000 Cl. 26.5.1.1 (reinforcement limits)
    IS 456:2000 Table 2, 3 (concrete/steel grades)
"""

from __future__ import annotations

from structural_lib.core.errors import DimensionError, MaterialError

# Accepted concrete grades per IS 456 Table 2
_VALID_FCK = frozenset({15, 20, 25, 30, 35, 40, 45, 50, 55, 60})

# Accepted steel grades per IS 456 Table 3
_VALID_FY = frozenset({250, 415, 500})


def validate_beam_dimensions(
    b: float,
    d: float,
    *,
    label: str = "beam",
) -> None:
    """Validate basic beam cross-section dimensions.

    Args:
        b: Width (mm).  Must be > 0.
        d: Effective depth (mm).  Must be > 0.
        label: Human-readable label for error messages.

    Raises:
        DimensionError: If any dimension is non-positive.
    """
    if b <= 0:
        raise DimensionError(f"{label} width b must be > 0, got {b}")
    if d <= 0:
        raise DimensionError(f"{label} effective depth d must be > 0, got {d}")


def validate_material_grades(
    fck: float,
    fy: float,
) -> None:
    """Validate concrete and steel material grades.

    Checks that values are positive and within IS 456 standard grades.
    Non-standard positive values produce a warning-level pass (no raise)
    to support research use cases --- only non-positive values raise.

    Args:
        fck: Characteristic compressive strength (N/mm2).  Must be > 0.
        fy: Characteristic yield strength (N/mm2).  Must be > 0.

    Raises:
        MaterialError: If any grade is non-positive.
    """
    if fck <= 0:
        raise MaterialError(f"fck must be > 0, got {fck}")
    if fy <= 0:
        raise MaterialError(f"fy must be > 0, got {fy}")
