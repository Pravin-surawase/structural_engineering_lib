"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.optimization
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.optimization."""

from __future__ import annotations

from structural_lib.services.optimization import (  # noqa: F401, E402
    CostOptimizationResult,
    OptimizationCandidate,
    optimize_beam_cost,
)
