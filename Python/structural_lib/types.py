"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.types
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.types."""

from __future__ import annotations

from structural_lib.core.types import (  # noqa: F401, E402
    BeamGeometry,
    BeamType,
    ComplianceCaseResult,
    ComplianceReport,
    CrackWidthResult,
    CuttingAssignment,
    CuttingPlan,
    DeflectionLevelBResult,
    DeflectionResult,
    DesignSectionType,
    ExposureClass,
    FlexureResult,
    JobSpec,
    LoadCase,
    ShearResult,
    SupportCondition,
    ValidationReport,
)
