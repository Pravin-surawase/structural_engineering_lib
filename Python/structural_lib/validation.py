"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.validation
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.validation."""

from __future__ import annotations

from structural_lib.core.validation import (  # noqa: F401, E402
    validate_all_positive,
    validate_beam_inputs,
    validate_cover,
    validate_dimensions,
    validate_geometry_relationship,
    validate_loads,
    validate_material_grades,
    validate_materials,
    validate_positive,
    validate_range,
    validate_reinforcement,
    validate_span,
    validate_stirrup_parameters,
)
