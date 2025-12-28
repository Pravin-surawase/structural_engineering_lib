"""
Module:       errors
Description:  Structured error types for machine-readable, traceable errors.

See docs/reference/error-schema.md for full specification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    """Error severity levels."""

    ERROR = "error"  # Design fails. Cannot proceed.
    WARNING = "warning"  # Design passes but has concerns.
    INFO = "info"  # Informational only.


@dataclass(frozen=True)
class DesignError:
    """
    Structured error for machine-readable and human-friendly error reporting.

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
    field: Optional[str] = None
    hint: Optional[str] = None
    clause: Optional[str] = None

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
    field: Optional[str] = None,
    hint: Optional[str] = None,
    clause: Optional[str] = None,
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
