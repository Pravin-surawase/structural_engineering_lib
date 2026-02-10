"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.result_base
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.result_base."""

from __future__ import annotations

from structural_lib.core.result_base import (  # noqa: F401, E402
    BaseResult,
    CalculationResult,
    ComplianceResult,
)
