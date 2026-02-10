"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.multi_objective_optimizer
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.multi_objective_optimizer."""

from __future__ import annotations

from structural_lib.services.multi_objective_optimizer import (  # noqa: F401, E402
    GOVERNING_CLAUSES,
    ParetoCandidate,
    ParetoOptimizationResult,
    get_design_explanation,
    optimize_pareto_front,
)
