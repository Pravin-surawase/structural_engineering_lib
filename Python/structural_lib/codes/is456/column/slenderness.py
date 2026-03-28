# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Column Slenderness Check — IS 456:2000 Cl 25.1.2

Classification of columns as short or long (slender) based on effective
length ratios. Includes IS 456 Table 28 effective length factors.

References:
- IS 456:2000, Cl 25.1.2 (Short and Slender columns)
- IS 456:2000, Table 28 (Effective length of columns)
- IS 456:2000, Cl 26.5.3.1 (Minimum column dimensions)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = [
    "ColumnType",
    "ColumnSlendernessResult",
    "check_column_slenderness",
    "get_effective_length_factor",
]


class ColumnType(Enum):
    """Classification of column by slenderness."""
    SHORT = "short"
    LONG = "long"


@dataclass
class ColumnSlendernessResult:
    """Result of column slenderness classification per IS 456 Cl 25.1.2.

    Attributes:
        is_ok: True if column is classified as short (le/b <= 12 AND le/D <= 12).
        is_slender: True if column is classified as long/slender.
        column_type: SHORT or LONG classification.
        slenderness_ratio: Governing le/dimension ratio (max of le/b and le/D).
        slenderness_limit: 12.0 per IS 456 Cl 25.1.2.
        utilization: slenderness_ratio / slenderness_limit (>1.0 means long).
        le_by_b: le / b ratio.
        le_by_D: le / D ratio.
        depth_to_width_ratio: D / b.
        remarks: Human-readable summary.
        assumptions: List of assumptions made.
        inputs: Input values used.
        computed: Intermediate computed values.
        errors: List of compliance errors.
        warnings: List of warnings.
    """
    is_ok: bool
    is_slender: bool
    column_type: ColumnType
    slenderness_ratio: float
    slenderness_limit: float
    utilization: float
    le_by_b: float
    le_by_D: float
    depth_to_width_ratio: float
    remarks: str
    assumptions: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    computed: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# IS 456 Table 28 — Effective length factors for columns
_EFFECTIVE_LENGTH_FACTORS: dict[tuple[str, str], float] = {
    ("fixed", "fixed"): 0.65,
    ("fixed", "hinged"): 0.80,
    ("hinged", "fixed"): 0.80,
    ("hinged", "hinged"): 1.00,
    ("fixed", "free"): 2.00,
    ("free", "fixed"): 2.00,
    ("fixed", "partial"): 0.80,
    ("partial", "fixed"): 0.80,
    ("hinged", "free"): 2.00,
    ("free", "hinged"): 2.00,
}

# IS 456 Cl 25.1.2 — Slenderness limit for short columns
_COLUMN_SLENDERNESS_LIMIT = 12.0

# IS 456 Cl 26.5.3.1 — Recommended minimum lateral dimension
_MIN_COLUMN_DIMENSION_MM = 200.0


def get_effective_length_factor(
    end_condition_top: str,
    end_condition_bottom: str,
) -> float:
    """Get effective length factor from IS 456 Table 28.

    Args:
        end_condition_top: End condition at top ('fixed', 'hinged', 'free', 'partial').
        end_condition_bottom: End condition at bottom ('fixed', 'hinged', 'free', 'partial').

    Returns:
        Effective length factor (k) such that le = k × unsupported_length.

    Raises:
        ValueError: If end conditions are not recognized.

    Example:
        >>> get_effective_length_factor("fixed", "fixed")
        0.65
        >>> get_effective_length_factor("fixed", "hinged")
        0.80
    """
    top = end_condition_top.strip().lower()
    bottom = end_condition_bottom.strip().lower()

    key = (top, bottom)
    if key in _EFFECTIVE_LENGTH_FACTORS:
        return _EFFECTIVE_LENGTH_FACTORS[key]

    valid = sorted(set(k for pair in _EFFECTIVE_LENGTH_FACTORS for k in pair))
    raise ValueError(
        f"Invalid end conditions: ({end_condition_top!r}, {end_condition_bottom!r}). "
        f"Valid conditions: {valid}"
    )


def check_column_slenderness(
    b_mm: float,
    D_mm: float,
    unsupported_length_mm: float,
    effective_length_factor: float = 1.0,
) -> ColumnSlendernessResult:
    """Classify column as short or long per IS 456 Cl 25.1.2.

    A column is SHORT if both le/b <= 12 AND le/D <= 12.
    Otherwise it is LONG (slender) and additional moment must be considered.

    Args:
        b_mm: Width (least lateral dimension) in mm.
        D_mm: Depth (other lateral dimension) in mm.
        unsupported_length_mm: Unsupported length of column in mm.
        effective_length_factor: Factor k from IS 456 Table 28 (default 1.0).

    Returns:
        ColumnSlendernessResult with classification and details.

    Example:
        >>> result = check_column_slenderness(300, 300, 3000, 1.0)
        >>> result.is_ok
        True
        >>> result.column_type
        ColumnType.SHORT
    """
    errors: list[str] = []
    warnings: list[str] = []
    assumptions: list[str] = []

    if b_mm <= 0:
        errors.append(f"Column width must be positive, got {b_mm} mm")
    if D_mm <= 0:
        errors.append(f"Column depth must be positive, got {D_mm} mm")
    if unsupported_length_mm <= 0:
        errors.append(f"Unsupported length must be positive, got {unsupported_length_mm} mm")
    if effective_length_factor <= 0:
        errors.append(f"Effective length factor must be positive, got {effective_length_factor}")

    if errors:
        return ColumnSlendernessResult(
            is_ok=False,
            is_slender=False,
            column_type=ColumnType.SHORT,
            slenderness_ratio=0.0,
            slenderness_limit=_COLUMN_SLENDERNESS_LIMIT,
            utilization=0.0,
            le_by_b=0.0,
            le_by_D=0.0,
            depth_to_width_ratio=0.0,
            remarks="Invalid inputs: " + "; ".join(errors),
            assumptions=assumptions,
            inputs={
                "b_mm": b_mm, "D_mm": D_mm,
                "unsupported_length_mm": unsupported_length_mm,
                "effective_length_factor": effective_length_factor,
            },
            computed={},
            errors=errors,
            warnings=warnings,
        )

    # Calculate effective length
    le_mm = effective_length_factor * unsupported_length_mm

    # Calculate slenderness ratios
    le_by_b = le_mm / b_mm
    le_by_D = le_mm / D_mm
    governing_ratio = max(le_by_b, le_by_D)
    depth_to_width = D_mm / b_mm

    utilization = governing_ratio / _COLUMN_SLENDERNESS_LIMIT

    # Classify
    is_short = (le_by_b <= _COLUMN_SLENDERNESS_LIMIT) and (le_by_D <= _COLUMN_SLENDERNESS_LIMIT)
    column_type = ColumnType.SHORT if is_short else ColumnType.LONG

    inputs = {
        "b_mm": b_mm,
        "D_mm": D_mm,
        "unsupported_length_mm": unsupported_length_mm,
        "effective_length_factor": effective_length_factor,
    }
    computed = {
        "le_mm": round(le_mm, 2),
        "le_by_b": round(le_by_b, 2),
        "le_by_D": round(le_by_D, 2),
        "governing_ratio": round(governing_ratio, 2),
        "utilization": round(utilization, 3),
    }

    # Minimum dimension warning
    min_dim = min(b_mm, D_mm)
    if min_dim < _MIN_COLUMN_DIMENSION_MM:
        warnings.append(
            f"Minimum lateral dimension ({min_dim:.0f} mm) is below recommended "
            f"{_MIN_COLUMN_DIMENSION_MM:.0f} mm (IS 456 Cl 26.5.3.1)."
        )

    if not is_short:
        warnings.append(
            f"Column is LONG/SLENDER (le/b={le_by_b:.1f} or le/D={le_by_D:.1f} > 12). "
            "Additional moment per IS 456 Cl 39.7.1 must be considered."
        )

    if is_short:
        remarks = (
            f"SHORT column (IS 456 Cl 25.1.2): le/b={le_by_b:.2f}, "
            f"le/D={le_by_D:.2f}, both ≤ 12."
        )
    else:
        remarks = (
            f"LONG/SLENDER column (IS 456 Cl 25.1.2): governing ratio "
            f"{governing_ratio:.2f} > 12. Additional moment required."
        )

    return ColumnSlendernessResult(
        is_ok=is_short,
        is_slender=not is_short,
        column_type=column_type,
        slenderness_ratio=round(governing_ratio, 2),
        slenderness_limit=_COLUMN_SLENDERNESS_LIMIT,
        utilization=round(utilization, 3),
        le_by_b=round(le_by_b, 2),
        le_by_D=round(le_by_D, 2),
        depth_to_width_ratio=round(depth_to_width, 2),
        remarks=remarks,
        assumptions=assumptions,
        inputs=inputs,
        computed=computed,
        errors=errors,
        warnings=warnings,
    )
