"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.data_types
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.data_types."""

from __future__ import annotations

from structural_lib.core.data_types import (  # noqa: F401, E402
    BarDict,
    BeamGeometry,
    BeamType,
    ComplianceCaseResult,
    ComplianceReport,
    CrackWidthParams,
    CrackWidthResult,
    CriticalPoint,
    CuttingAssignment,
    CuttingPlan,
    DeflectionLevelBResult,
    DeflectionLevelCResult,
    DeflectionParams,
    DeflectionResult,
    DesignSectionType,
    ExposureClass,
    FlexureResult,
    JobSpec,
    LoadCase,
    LoadDefinition,
    LoadDiagramResult,
    LoadType,
    OptimizerCandidate,
    OptimizerChecks,
    OptimizerInputs,
    ShearResult,
    StirrupDict,
    SupportCondition,
    TorsionResult,
    ValidationReport,
)
