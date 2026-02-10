"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.error_messages
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.error_messages."""

from __future__ import annotations

from structural_lib.core.error_messages import (  # noqa: F401, E402
    capacity_exceeded,
    convergence_failed,
    dimension_negative,
    dimension_relationship_invalid,
    dimension_too_large,
    dimension_too_small,
    format_list,
    format_value_with_unit,
    material_grade_invalid,
    material_property_out_of_range,
    maximum_reinforcement_exceeded,
    minimum_reinforcement_not_met,
    numerical_instability,
    reinforcement_spacing_insufficient,
    spacing_limit_exceeded,
)
