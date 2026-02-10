"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.calculation_report

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.calculation_report is deprecated. "
    "Use structural_lib.services.calculation_report instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.calculation_report import (  # noqa: F401, E402
    CalculationReport,
    InputSection,
    ProjectInfo,
    ResultSection,
    generate_calculation_report,
)
