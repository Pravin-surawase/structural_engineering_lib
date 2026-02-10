"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.errors
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.errors."""

from __future__ import annotations

from structural_lib.core.errors import (  # noqa: F401, E402
    CalculationError,
    ComplianceError,
    ConfigurationError,
    DesignConstraintError,
    DesignError,
    DimensionError,
    E_DUCTILE_001,
    E_DUCTILE_002,
    E_DUCTILE_003,
    E_FLEXURE_001,
    E_FLEXURE_002,
    E_FLEXURE_003,
    E_FLEXURE_004,
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_003,
    E_INPUT_003a,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_006,
    E_INPUT_007,
    E_INPUT_008,
    E_INPUT_009,
    E_INPUT_010,
    E_INPUT_011,
    E_INPUT_012,
    E_INPUT_013,
    E_INPUT_014,
    E_INPUT_015,
    E_INPUT_016,
    E_SHEAR_001,
    E_SHEAR_002,
    E_SHEAR_003,
    E_SHEAR_004,
    E_TORSION_001,
    LoadError,
    MaterialError,
    Severity,
    StructuralLibError,
    ValidationError,
    make_error,
)
