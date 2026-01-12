# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       errors
Description:  Exception hierarchy and structured error types.

This module provides:
1. Exception hierarchy for raising errors (StructuralLibError and subclasses)
2. Structured error dataclasses for machine-readable error reporting (DesignError)

See:
- docs/guidelines/error-handling-standard.md for exception hierarchy
- docs/reference/error-schema.md for structured error specification

Related: TASK-212 (Create exception hierarchy)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# =============================================================================
# Exception Hierarchy (for raising errors)
# =============================================================================


class StructuralLibError(Exception):
    """
    Base exception for all structural_lib_is456 errors.

    All library exceptions should inherit from this class to allow users
    to catch all library-specific errors with a single except clause.

    Args:
        message: Human-readable error description
        details: Optional dict with additional context (values, constraints)
        suggestion: Optional actionable guidance for fixing the error
        clause_ref: Optional IS 456:2000 clause reference

    Example:
        >>> raise StructuralLibError(
        ...     "Beam width too small",
        ...     details={"b_mm": 150, "minimum": 200},
        ...     suggestion="Increase beam width to at least 200mm",
        ...     clause_ref="Cl. 26.5.1.1"
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        suggestion: str | None = None,
        clause_ref: str | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
        self.clause_ref = clause_ref

    def __str__(self) -> str:
        """Format exception with all context."""
        parts = [self.message]
        if self.clause_ref:
            parts.append(f"(Ref: IS 456:2000 {self.clause_ref})")
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(f"[{details_str}]")
        return " ".join(parts)


# -----------------------------------------------------------------------------
# Level 1: Primary exception categories
# -----------------------------------------------------------------------------


class ValidationError(StructuralLibError):
    """
    Raised when input validation fails.

    Use for: Invalid dimensions, materials, loads, or parameters provided by user.

    Example:
        >>> raise ValidationError(
        ...     "Beam width b=150mm is below minimum 200mm",
        ...     details={"b_mm": 150, "minimum": 200},
        ...     clause_ref="Cl. 26.5.1.1"
        ... )
    """


class DesignConstraintError(StructuralLibError):
    """
    Raised when design requirements cannot be satisfied within given constraints.

    Use for: Capacity exceeded, insufficient space for reinforcement,
    design not feasible with given section.

    Example:
        >>> raise DesignConstraintError(
        ...     "Moment Mu=250 kN·m exceeds section capacity Mu,lim=200 kN·m",
        ...     details={"mu_knm": 250, "mu_lim_knm": 200},
        ...     suggestion="Increase section depth or use compression reinforcement"
        ... )
    """


class ComplianceError(StructuralLibError):
    """
    Raised when IS 456:2000 code requirements are not met.

    Use for: Minimum reinforcement, spacing limits, detailing requirements,
    ductility criteria violations.

    Example:
        >>> raise ComplianceError(
        ...     "Steel ratio below minimum 0.85/fy",
        ...     details={"pt_actual": 0.12, "pt_min": 0.20},
        ...     clause_ref="Cl. 26.5.1.1"
        ... )
    """


class ConfigurationError(StructuralLibError):
    """
    Raised when library is misconfigured or in invalid state.

    Use for: Missing setup, invalid configuration, incompatible options.

    Example:
        >>> raise ConfigurationError(
        ...     "Invalid beam type specified",
        ...     details={"beam_type": "UNKNOWN"},
        ...     suggestion="Use 'RECTANGULAR', 'T_BEAM', or 'L_BEAM'"
        ... )
    """


class CalculationError(StructuralLibError):
    """
    Raised when calculation cannot complete due to numerical issues.

    Use for: Convergence failure, numerical instability, iteration limits exceeded.

    Example:
        >>> raise CalculationError(
        ...     "Iterative solution did not converge",
        ...     details={"iterations": 100, "tolerance": 0.001},
        ...     suggestion="Check input values or increase iteration limit"
        ... )
    """


# -----------------------------------------------------------------------------
# Level 2: Specific validation failures
# -----------------------------------------------------------------------------


class DimensionError(ValidationError):
    """
    Raised when dimensions are invalid or out of range.

    Use for: Negative dimensions, dimensions below code minimums,
    incompatible dimension relationships.
    """


class MaterialError(ValidationError):
    """
    Raised when material properties are invalid.

    Use for: Invalid concrete grade, invalid steel grade,
    material properties out of range.
    """


class LoadError(ValidationError):
    """
    Raised when loads are invalid.

    Use for: Negative loads (when not allowed), load combinations
    that don't make sense.
    """


# =============================================================================
# Structured Error Dataclasses (for machine-readable error reporting)
# =============================================================================


class Severity(str, Enum):
    """Error severity levels."""

    ERROR = "error"  # Design fails. Cannot proceed.
    WARNING = "warning"  # Design passes but has concerns.
    INFO = "info"  # Informational only.


@dataclass(frozen=True)
class DesignError:
    """
    Structured error dataclass for machine-readable error reporting.

    NOTE: This is a dataclass for structured error data, NOT an exception.
    For raising design-related exceptions, use DesignConstraintError instead.

    This dataclass is used in result objects to collect errors without raising exceptions,
    allowing batch processing and error collection.

    Note: This dataclass is frozen (immutable) to prevent accidental mutation
    of shared error constants.

    Attributes:
        code: Unique error code (e.g., E_FLEXURE_001)
        severity: One of: error, warning, info
        message: Human-readable error description
        field: Input field that caused the error (optional)
        hint: Actionable suggestion to fix the error (optional)
        clause: IS 456 clause reference (optional)
    """

    code: str
    severity: Severity
    message: str
    field: str | None = None
    hint: str | None = None
    clause: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
        }
        if self.field:
            result["field"] = self.field
        if self.hint:
            result["hint"] = self.hint
        if self.clause:
            result["clause"] = self.clause
        return result


# -----------------------------------------------------------------------------
# Pre-defined error codes (see docs/reference/error-schema.md for full catalog)
# -----------------------------------------------------------------------------

# Input Validation Errors
E_INPUT_001 = DesignError(
    code="E_INPUT_001",
    severity=Severity.ERROR,
    message="b must be > 0",
    field="b",
    hint="Check beam width input.",
)

E_INPUT_002 = DesignError(
    code="E_INPUT_002",
    severity=Severity.ERROR,
    message="d must be > 0",
    field="d",
    hint="Check effective depth input.",
)

E_INPUT_003 = DesignError(
    code="E_INPUT_003",
    severity=Severity.ERROR,
    message="d_total must be > d",
    field="d_total",
    hint="Ensure D > d + cover.",
)

# Note: E_INPUT_003a is for d_total <= 0, E_INPUT_003 is for d_total <= d
E_INPUT_003a = DesignError(
    code="E_INPUT_003a",
    severity=Severity.ERROR,
    message="d_total must be > 0",
    field="d_total",
    hint="Check overall depth input.",
)

E_INPUT_004 = DesignError(
    code="E_INPUT_004",
    severity=Severity.ERROR,
    message="fck must be > 0",
    field="fck",
    hint="Use valid concrete grade (15-80 N/mm²).",
)

E_INPUT_005 = DesignError(
    code="E_INPUT_005",
    severity=Severity.ERROR,
    message="fy must be > 0",
    field="fy",
    hint="Use valid steel grade (250/415/500/550).",
)

E_INPUT_006 = DesignError(
    code="E_INPUT_006",
    severity=Severity.ERROR,
    message="Mu must be >= 0",
    field="Mu",
    hint="Check moment input sign.",
)

E_INPUT_007 = DesignError(
    code="E_INPUT_007",
    severity=Severity.ERROR,
    message="Vu must be >= 0",
    field="Vu",
    hint="Check shear input sign.",
)

E_INPUT_008 = DesignError(
    code="E_INPUT_008",
    severity=Severity.ERROR,
    message="asv must be > 0",
    field="asv",
    hint="Provide stirrup area.",
)

E_INPUT_009 = DesignError(
    code="E_INPUT_009",
    severity=Severity.ERROR,
    message="pt must be >= 0",
    field="pt",
    hint="Check tension steel percentage.",
)

E_INPUT_010 = DesignError(
    code="E_INPUT_010",
    severity=Severity.ERROR,
    message="d_dash must be > 0",
    field="d_dash",
    hint="Check compression steel cover input.",
)

E_INPUT_011 = DesignError(
    code="E_INPUT_011",
    severity=Severity.ERROR,
    message="min_long_bar_dia must be > 0",
    field="min_long_bar_dia",
    hint="Provide smallest longitudinal bar diameter.",
)

E_INPUT_012 = DesignError(
    code="E_INPUT_012",
    severity=Severity.ERROR,
    message="bw must be > 0",
    field="bw",
    hint="Check web width input.",
)

E_INPUT_013 = DesignError(
    code="E_INPUT_013",
    severity=Severity.ERROR,
    message="bf must be > 0",
    field="bf",
    hint="Check flange width input.",
)

E_INPUT_014 = DesignError(
    code="E_INPUT_014",
    severity=Severity.ERROR,
    message="Df must be > 0",
    field="Df",
    hint="Check flange thickness input.",
)

E_INPUT_015 = DesignError(
    code="E_INPUT_015",
    severity=Severity.ERROR,
    message="bf must be >= bw",
    field="bf",
    hint="Ensure flange width is not smaller than web width.",
)

E_INPUT_016 = DesignError(
    code="E_INPUT_016",
    severity=Severity.ERROR,
    message="Df must be < d",
    field="Df",
    hint="Ensure flange thickness is less than effective depth.",
)

# Flexure Errors
E_FLEXURE_001 = DesignError(
    code="E_FLEXURE_001",
    severity=Severity.ERROR,
    message="Mu exceeds Mu_lim",
    field="Mu",
    hint="Use doubly reinforced or increase depth.",
    clause="Cl. 38.1",
)

E_FLEXURE_002 = DesignError(
    code="E_FLEXURE_002",
    severity=Severity.INFO,
    message="Ast < Ast_min. Minimum steel provided.",
    field="Ast",
    hint="Increase steel to meet minimum.",
    clause="Cl. 26.5.1.1",
)

E_FLEXURE_003 = DesignError(
    code="E_FLEXURE_003",
    severity=Severity.ERROR,
    message="Ast > Ast_max (4% bD)",
    field="Ast",
    hint="Reduce steel or increase section.",
    clause="Cl. 26.5.1.2",
)

E_FLEXURE_004 = DesignError(
    code="E_FLEXURE_004",
    severity=Severity.ERROR,
    message="d' too large for doubly reinforced design",
    field="d_dash",
    hint="Reduce compression steel cover.",
)

# Shear Errors
E_SHEAR_001 = DesignError(
    code="E_SHEAR_001",
    severity=Severity.ERROR,
    message="tv exceeds tc_max",
    field="tv",
    hint="Increase section size.",
    clause="Cl. 40.2.3",
)

# Note: E_SHEAR_002 is reserved for future use when spacing limits are exceeded.
# Currently, shear.py enforces max spacing internally, so this warning is not emitted.
# It will be used when we add explicit spacing limit warnings.
E_SHEAR_002 = DesignError(
    code="E_SHEAR_002",
    severity=Severity.WARNING,
    message="Spacing exceeds maximum",
    field="spacing",
    hint="Reduce stirrup spacing.",
    clause="Cl. 26.5.1.6",
)

E_SHEAR_003 = DesignError(
    code="E_SHEAR_003",
    severity=Severity.INFO,
    message="Nominal shear < Tc. Provide minimum shear reinforcement.",
    field="tv",
    hint="Minimum stirrups per Cl. 26.5.1.6.",
    clause="Cl. 26.5.1.6",
)

E_SHEAR_004 = DesignError(
    code="E_SHEAR_004",
    severity=Severity.WARNING,
    message="fck outside Table 19 range (15-40). Using nearest bound values.",
    field="fck",
    hint="Use fck within 15-40 for Table 19 or confirm conservative design.",
    clause="Table 19",
)

# Ductile Detailing Errors
E_DUCTILE_001 = DesignError(
    code="E_DUCTILE_001",
    severity=Severity.ERROR,
    message="Width < 200 mm",
    field="b",
    hint="Increase beam width to ≥ 200 mm.",
    clause="IS 13920 Cl. 6.1.1",
)

E_DUCTILE_002 = DesignError(
    code="E_DUCTILE_002",
    severity=Severity.ERROR,
    message="Width/Depth ratio < 0.3",
    field="b/D",
    hint="Increase width or reduce depth.",
    clause="IS 13920 Cl. 6.1.2",
)

E_DUCTILE_003 = DesignError(
    code="E_DUCTILE_003",
    severity=Severity.ERROR,
    message="Invalid depth",
    field="D",
    hint="Depth must be > 0.",
)


def make_error(
    code: str,
    severity: Severity,
    message: str,
    field: str | None = None,
    hint: str | None = None,
    clause: str | None = None,
) -> DesignError:
    """Factory function to create a DesignError."""
    return DesignError(
        code=code,
        severity=severity,
        message=message,
        field=field,
        hint=hint,
        clause=clause,
    )
