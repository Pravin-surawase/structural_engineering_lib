"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.beam_pipeline
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.beam_pipeline."""

from __future__ import annotations

from structural_lib.services.beam_pipeline import (  # noqa: F401, E402
    BeamDesignOutput,
    BeamGeometry,
    BeamLoads,
    BeamMaterials,
    DetailingOutput,
    FlexureOutput,
    IS456_UNITS,
    MultiBeamOutput,
    SCHEMA_VERSION,
    ServiceabilityOutput,
    ShearOutput,
    UnitsValidationError,
    design_multiple_beams,
    design_single_beam,
    validate_units,
)
