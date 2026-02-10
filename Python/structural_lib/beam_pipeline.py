"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.beam_pipeline
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.beam_pipeline."""

from __future__ import annotations

from structural_lib.services.beam_pipeline import (  # noqa: F401, E402
    IS456_UNITS,
    SCHEMA_VERSION,
    BeamDesignOutput,
    BeamGeometry,
    BeamLoads,
    BeamMaterials,
    DetailingOutput,
    FlexureOutput,
    MultiBeamOutput,
    ServiceabilityOutput,
    ShearOutput,
    UnitsValidationError,
    design_multiple_beams,
    design_single_beam,
    validate_units,
)
