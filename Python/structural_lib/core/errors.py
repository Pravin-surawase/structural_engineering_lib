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
from enum import StrEnum
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


class Severity(StrEnum):
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
        recovery: Step-by-step recovery/fix instructions (optional)
    """

    code: str
    severity: Severity
    message: str
    field: str | None = None
    hint: str | None = None
    clause: str | None = None
    recovery: str | None = None

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
        if self.recovery:
            result["recovery"] = self.recovery
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
    recovery="Provide beam width b > 0 mm. Typical rectangular beams: 200\u2013500 mm.",
)

E_INPUT_002 = DesignError(
    code="E_INPUT_002",
    severity=Severity.ERROR,
    message="d must be > 0",
    field="d",
    hint="Check effective depth input.",
    recovery="Provide effective depth d > 0 mm. d = D \u2212 cover \u2212 stirrup_dia \u2212 bar_dia/2.",
)

E_INPUT_003 = DesignError(
    code="E_INPUT_003",
    severity=Severity.ERROR,
    message="d_total must be > d",
    field="d_total",
    hint="Ensure D > d + cover.",
    recovery="Ensure overall depth D > effective depth d. D = d + cover + stirrup_dia + bar_dia/2.",
)

# Note: E_INPUT_003a is for d_total <= 0, E_INPUT_003 is for d_total <= d
E_INPUT_003a = DesignError(
    code="E_INPUT_003a",
    severity=Severity.ERROR,
    message="d_total must be > 0",
    field="d_total",
    hint="Check overall depth input.",
    recovery="Provide overall depth D > 0 mm. Typical beams: 300\u2013900 mm.",
)

E_INPUT_004 = DesignError(
    code="E_INPUT_004",
    severity=Severity.ERROR,
    message="fck must be > 0",
    field="fck",
    hint="Use valid concrete grade (15-80 N/mm²).",
    recovery="Use standard IS 456 concrete grades: M15, M20, M25, M30, M35, M40 (fck = 15\u201340 N/mm\u00b2).",
)

E_INPUT_005 = DesignError(
    code="E_INPUT_005",
    severity=Severity.ERROR,
    message="fy must be > 0",
    field="fy",
    hint="Use valid steel grade (250/415/500/550).",
    recovery="Use standard IS 456 steel grades: Fe250, Fe415, Fe500, Fe550 (fy = 250/415/500/550 N/mm\u00b2).",
)

E_INPUT_006 = DesignError(
    code="E_INPUT_006",
    severity=Severity.ERROR,
    message="Mu must be >= 0",
    field="Mu",
    hint="Check moment input sign.",
    recovery="Provide non-negative factored moment Mu \u2265 0. For hogging, use absolute value.",
)

E_INPUT_007 = DesignError(
    code="E_INPUT_007",
    severity=Severity.ERROR,
    message="Vu must be >= 0",
    field="Vu",
    hint="Check shear input sign.",
    recovery="Provide non-negative factored shear Vu \u2265 0.",
)

E_INPUT_008 = DesignError(
    code="E_INPUT_008",
    severity=Severity.ERROR,
    message="asv must be > 0",
    field="asv",
    hint="Provide stirrup area.",
    recovery="Provide stirrup cross-sectional area asv > 0 mm\u00b2. For 2-legged 8mm stirrups: asv = 2 \u00d7 50.3 = 100.5 mm\u00b2.",
)

E_INPUT_009 = DesignError(
    code="E_INPUT_009",
    severity=Severity.ERROR,
    message="pt must be >= 0",
    field="pt",
    hint="Check tension steel percentage.",
    recovery="Provide non-negative tension steel percentage pt \u2265 0.",
)

E_INPUT_010 = DesignError(
    code="E_INPUT_010",
    severity=Severity.ERROR,
    message="d_dash must be > 0",
    field="d_dash",
    hint="Check compression steel cover input.",
    recovery="Provide compression steel cover d' > 0 mm. Typically 40\u201360 mm from compression face.",
)

E_INPUT_011 = DesignError(
    code="E_INPUT_011",
    severity=Severity.ERROR,
    message="min_long_bar_dia must be > 0",
    field="min_long_bar_dia",
    hint="Provide smallest longitudinal bar diameter.",
    recovery="Provide smallest longitudinal bar diameter > 0 mm. Minimum bar: 12 mm for beams.",
)

E_INPUT_012 = DesignError(
    code="E_INPUT_012",
    severity=Severity.ERROR,
    message="bw must be > 0",
    field="bw",
    hint="Check web width input.",
    recovery="Provide web width bw > 0 mm for flanged beam sections.",
)

E_INPUT_013 = DesignError(
    code="E_INPUT_013",
    severity=Severity.ERROR,
    message="bf must be > 0",
    field="bf",
    hint="Check flange width input.",
    recovery="Provide flange width bf > 0 mm. Per Cl 23.1.2: bf \u2264 L0/6 + bw + 6Df.",
)

E_INPUT_014 = DesignError(
    code="E_INPUT_014",
    severity=Severity.ERROR,
    message="Df must be > 0",
    field="Df",
    hint="Check flange thickness input.",
    recovery="Provide flange thickness Df > 0 mm. Typically equals slab thickness (100\u2013200 mm).",
)

E_INPUT_015 = DesignError(
    code="E_INPUT_015",
    severity=Severity.ERROR,
    message="bf must be >= bw",
    field="bf",
    hint="Ensure flange width is not smaller than web width.",
    recovery="Flange width bf must be \u2265 web width bw. Check flange effective width per Cl 23.1.2.",
)

E_INPUT_016 = DesignError(
    code="E_INPUT_016",
    severity=Severity.ERROR,
    message="Df must be < d",
    field="Df",
    hint="Ensure flange thickness is less than effective depth.",
    recovery="Flange thickness Df must be < effective depth d. If Df \u2265 d, section behaves as rectangular, not flanged.",
)

# Flexure Errors
E_FLEXURE_001 = DesignError(
    code="E_FLEXURE_001",
    severity=Severity.ERROR,
    message="Mu exceeds Mu_lim",
    field="Mu",
    hint="Use doubly reinforced or increase depth.",
    clause="Cl. 38.1",
    recovery="1. Increase depth D (Mu_lim \u221d d\u00b2, most economical). 2. Or use doubly reinforced design per Annex G-1.1. 3. Or increase concrete grade fck.",
)

E_FLEXURE_002 = DesignError(
    code="E_FLEXURE_002",
    severity=Severity.INFO,
    message="Ast < Ast_min. Minimum steel provided.",
    field="Ast",
    hint="Increase steel to meet minimum.",
    clause="Cl. 26.5.1.1",
    recovery="Increase steel to Ast_min = max(0.85\u00d7b\u00d7d/fy, 0.12%\u00d7b\u00d7D) per Cl 26.5.1.1.",
)

E_FLEXURE_003 = DesignError(
    code="E_FLEXURE_003",
    severity=Severity.ERROR,
    message="Ast > Ast_max (4% bD)",
    field="Ast",
    hint="Reduce steel or increase section.",
    clause="Cl. 26.5.1.2",
    recovery="Reduce steel below 4% of bD per Cl 26.5.1.2. Options: increase section, use higher fck, or split into multiple beams.",
)

E_FLEXURE_004 = DesignError(
    code="E_FLEXURE_004",
    severity=Severity.ERROR,
    message="d' too large for doubly reinforced design",
    field="d_dash",
    hint="Reduce compression steel cover.",
    recovery="Reduce compression steel cover d'. d' should be \u2264 0.2d for effective compression steel contribution.",
)

# Shear Errors
E_SHEAR_001 = DesignError(
    code="E_SHEAR_001",
    severity=Severity.ERROR,
    message="tv exceeds tc_max",
    field="tv",
    hint="Increase section size.",
    clause="Cl. 40.2.3",
    recovery="Redesign section \u2014 per Cl 40.2.3, no amount of shear reinforcement can fix this. Increase b or D.",
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
    recovery="Reduce stirrup spacing to \u2264 min(0.75d, 300 mm) per Cl 26.5.1.6.",
)

E_SHEAR_003 = DesignError(
    code="E_SHEAR_003",
    severity=Severity.INFO,
    message="Nominal shear < Tc. Provide minimum shear reinforcement.",
    field="tv",
    hint="Minimum stirrups per Cl. 26.5.1.6.",
    clause="Cl. 26.5.1.6",
    recovery="Provide minimum shear reinforcement per Cl 26.5.1.6: Asv_min/(b\u00d7sv) \u2265 0.4/0.87fy.",
)

E_SHEAR_004 = DesignError(
    code="E_SHEAR_004",
    severity=Severity.WARNING,
    message="fck outside Table 19 range (15-40). Using nearest bound values.",
    field="fck",
    hint="Use fck within 15-40 for Table 19 or confirm conservative design.",
    clause="Table 19",
    recovery="Use fck within 15\u201340 N/mm\u00b2 for IS 456 Table 19. For higher grades, \u03c4c values are conservative.",
)

E_SHEAR_005 = DesignError(
    code="E_SHEAR_005",
    severity=Severity.ERROR,
    message="av_mm must be > 0",
    field="av_mm",
    hint="Provide distance from face of support to nearest edge of concentrated load.",
    clause="Cl. 40.3",
    recovery="Provide distance from face of support to load point. For enhanced shear near supports per Cl 40.3.",
)

# Ductile Detailing Errors
E_DUCTILE_001 = DesignError(
    code="E_DUCTILE_001",
    severity=Severity.ERROR,
    message="Width < 200 mm",
    field="b",
    hint="Increase beam width to ≥ 200 mm.",
    clause="IS 13920 Cl. 6.1.1",
    recovery="Increase beam width to \u2265 200 mm per IS 13920 Cl 6.1.1 for seismic resistance.",
)

E_DUCTILE_002 = DesignError(
    code="E_DUCTILE_002",
    severity=Severity.ERROR,
    message="Width/Depth ratio < 0.3",
    field="b/D",
    hint="Increase width or reduce depth.",
    clause="IS 13920 Cl. 6.1.2",
    recovery="Increase width or reduce depth so that b/D \u2265 0.3 per IS 13920 Cl 6.1.2.",
)

E_DUCTILE_003 = DesignError(
    code="E_DUCTILE_003",
    severity=Severity.ERROR,
    message="Invalid depth",
    field="D",
    hint="Depth must be > 0.",
    recovery="Provide overall depth D > 0 mm.",
)

# Torsion Errors
E_TORSION_001 = DesignError(
    code="E_TORSION_001",
    severity=Severity.ERROR,
    message="Equivalent shear stress exceeds τc,max. Section must be redesigned.",
    field="tv_equiv",
    hint="Increase section size (b or D).",
    clause="Cl. 41.3",
    recovery="Increase section size. Per Cl 41.3, equivalent shear stress must not exceed \u03c4c,max from Table 20.",
)

# Column Errors --- IS 456 Cl. 25, 39
E_COLUMN_001 = DesignError(
    code="E_COLUMN_001",
    severity=Severity.ERROR,
    message="Column dimension must be positive",
    field="D_mm",
    hint="Provide positive column dimensions.",
    clause="Cl. 25",
    recovery="Provide positive column dimensions. Minimum per Cl 25: 300 mm for tied columns.",
)

E_COLUMN_002 = DesignError(
    code="E_COLUMN_002",
    severity=Severity.WARNING,
    message="Steel ratio below minimum 0.8% per Cl 26.5.3.1",
    field="Asc_mm2",
    hint="Increase longitudinal reinforcement to at least 0.8% of Ag.",
    clause="Cl. 26.5.3.1",
    recovery="Increase longitudinal steel to \u2265 0.8% of Ag per Cl 26.5.3.1.",
)

E_COLUMN_003 = DesignError(
    code="E_COLUMN_003",
    severity=Severity.WARNING,
    message="Steel ratio exceeds maximum 4% per Cl 26.5.3.1",
    field="Asc_mm2",
    hint="Reduce longitudinal reinforcement or increase section.",
    clause="Cl. 26.5.3.1",
    recovery="Reduce longitudinal steel to \u2264 4% (6% at laps) of Ag, or increase section per Cl 26.5.3.1.",
)

E_COLUMN_004 = DesignError(
    code="E_COLUMN_004",
    severity=Severity.WARNING,
    message="Slenderness ratio exceeds 60 per Cl 25.3.1",
    field="le_mm",
    hint="Reduce unsupported length or increase column dimensions.",
    clause="Cl. 25.3.1",
    recovery="Reduce unsupported length or increase column section so le/D \u2264 60 per Cl 25.3.1.",
)

E_COLUMN_005 = DesignError(
    code="E_COLUMN_005",
    severity=Severity.INFO,
    message="Cl 39.3 axial formula only applicable when e_min <= 0.05*D",
    field="e_min",
    hint="Use P-M interaction design for larger eccentricities.",
    clause="Cl. 39.3",
    recovery="For small eccentricities (e_min \u2264 0.05D), use Cl 39.3 axial formula. For larger, use P-M interaction design.",
)

E_COLUMN_006 = DesignError(
    code="E_COLUMN_006",
    severity=Severity.ERROR,
    message="Applied (Pu, Mu) exceeds P-M interaction envelope — section unsafe",
    field="Pu_kN",
    hint="Increase section size, concrete grade, or reinforcement.",
    clause="Cl. 39.5",
    recovery="Increase section, fck, or reinforcement. Use SP:16 Charts 27\u201362 to verify P-M interaction capacity.",
)

E_COLUMN_007 = DesignError(
    code="E_COLUMN_007",
    severity=Severity.WARNING,
    message="Column classified as slender — additional moment per Cl 39.7 required",
    field="le_mm",
    hint="Use design_long_column() for slender columns.",
    clause="Cl. 39.7",
    recovery="Apply additional moment per Cl 39.7.1: M_add = Pu \u00d7 (le\u00b2)/(2000\u00d7D). Use design_long_column().",
)

E_COLUMN_008 = DesignError(
    code="E_COLUMN_008",
    severity=Severity.WARNING,
    message="Eccentricity below 0.05D — pure axial formula (Cl 39.3) is more appropriate",
    field="Mu_kNm",
    hint="Consider using short_axial_capacity() for small eccentricities.",
    clause="Cl. 39.3",
    recovery="Consider using short_axial_capacity() for pure axial with small eccentricity per Cl 39.3.",
)

E_COLUMN_009 = DesignError(
    code="E_COLUMN_009",
    severity=Severity.ERROR,
    message="Cover to steel centroid d' must be > 0 and < D/2",
    field="d_prime_mm",
    hint="d_prime_mm should typically be 40-75mm.",
    clause="Cl. 26.4",
    recovery="Provide cover to steel centroid d' > 0 and < D/2. Typical values: 40\u201375 mm.",
)

E_COLUMN_010 = DesignError(
    code="E_COLUMN_010",
    severity=Severity.WARNING,
    message="Applied moment amplified to P_u × e_min per Cl 25.4",
    field="Mu_kNm",
    hint="Minimum eccentricity governs — design moment increased.",
    clause="Cl. 25.4",
    recovery="Design moment increased to Pu \u00d7 e_min per Cl 25.4. Minimum eccentricity = max(le/500 + D/30, 20 mm).",
)

E_COLUMN_011 = DesignError(
    code="E_COLUMN_011",
    severity=Severity.ERROR,
    message="Axial load Pu must be >= 0 for compression member",
    field="Pu_kN",
    hint="This function is for compression members. For pure tension, use a different design method.",
    clause="Cl. 39.5",
    recovery="This function is for compression members (Pu \u2265 0). For tension members, use different design methods.",
)

# Footing Errors --- IS 456 Cl. 34, 31.6
E_FOOTING_001 = DesignError(
    code="E_FOOTING_001",
    severity=Severity.ERROR,
    message="Footing dimensions must be positive",
    field="L_mm",
    hint="Provide positive footing dimensions.",
    clause="Cl. 34.1",
    recovery="Provide positive footing length and width. Minimum edge depth: 150mm per Cl 34.1.",
)

E_FOOTING_002 = DesignError(
    code="E_FOOTING_002",
    severity=Severity.ERROR,
    message="Bearing pressure exceeds safe bearing capacity",
    field="q_max_kPa",
    hint="Increase footing size or reduce load.",
    clause="Cl. 34.1",
    recovery="Increase footing area so q_max \u2264 q_safe. Use service (unfactored) loads for sizing.",
)

E_FOOTING_003 = DesignError(
    code="E_FOOTING_003",
    severity=Severity.ERROR,
    message="Punching shear exceeds capacity \u2014 increase depth or footing size",
    field="tau_v_nmm2",
    hint="Increase footing depth or plan dimensions. Shear reinforcement is not practical in footings.",
    clause="Cl. 31.6.1",
    recovery="Increase footing depth d or overall dimensions. Unlike beams, shear reinforcement is not practical in footings for punching.",
)

E_FOOTING_004 = DesignError(
    code="E_FOOTING_004",
    severity=Severity.ERROR,
    message="One-way shear exceeds capacity",
    field="tau_v_nmm2",
    hint="Increase footing depth.",
    clause="Cl. 34.2.4.1(a)",
    recovery="Increase footing depth d. One-way shear critical section is at distance d from column face.",
)

E_FOOTING_005 = DesignError(
    code="E_FOOTING_005",
    severity=Severity.WARNING,
    message="Footing depth less than minimum 150mm at edge per Cl 34.1",
    field="d_mm",
    hint="Minimum depth at edge is 150mm for footings on soil.",
    clause="Cl. 34.1",
    recovery="Increase footing depth to at least 150mm at edge (for soil) or 300mm (for piles) per Cl 34.1.",
)

E_FOOTING_006 = DesignError(
    code="E_FOOTING_006",
    severity=Severity.WARNING,
    message="Eccentricity exceeds L/6 \u2014 partial contact with soil (tension not permitted)",
    field="e_mm",
    hint="Increase footing size to keep eccentricity within kern.",
    clause="Cl. 34.1",
    recovery="Increase footing length L so eccentricity e \u2264 L/6. No tension at soil interface.",
)

E_FOOTING_007 = DesignError(
    code="E_FOOTING_007",
    severity=Severity.ERROR,
    message="Column dimensions exceed footing dimensions",
    field="a_mm",
    hint="Footing must be larger than the supported column.",
    clause="Cl. 34",
    recovery="Ensure footing L > column a and footing B > column b.",
)

E_FOOTING_008 = DesignError(
    code="E_FOOTING_008",
    severity=Severity.WARNING,
    message="Steel percentage below minimum 0.12% for HYSD bars",
    field="Ast_mm2",
    hint="Provide minimum reinforcement per Cl 26.5.2.1.",
    clause="Cl. 26.5.2.1",
    recovery="Increase reinforcement to at least 0.12% of b\u00d7d for HYSD (Fe 415/500) bars.",
)


def make_error(
    code: str,
    severity: Severity,
    message: str,
    field: str | None = None,
    hint: str | None = None,
    clause: str | None = None,
    recovery: str | None = None,
) -> DesignError:
    """Factory function to create a DesignError."""
    return DesignError(
        code=code,
        severity=severity,
        message=message,
        field=field,
        hint=hint,
        clause=clause,
        recovery=recovery,
    )
