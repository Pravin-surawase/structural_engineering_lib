"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.costing
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.costing."""

from __future__ import annotations

from structural_lib.services.costing import (  # noqa: F401, E402
    DEFAULT_CONCRETE_GRADE,
    STEEL_DENSITY_KG_PER_M3,
    CostBreakdown,
    CostProfile,
    calculate_beam_cost,
    calculate_concrete_cost,
    calculate_concrete_volume,
    calculate_formwork_area,
    calculate_formwork_cost,
    calculate_steel_cost,
    calculate_steel_weight,
    calculate_total_beam_cost,
)
