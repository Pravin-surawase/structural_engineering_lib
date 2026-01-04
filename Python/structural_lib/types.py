"""
Compatibility shim for the renamed data_types module.

This keeps historical imports like `structural_lib.types` working while the
project transitions to `structural_lib.data_types`.
"""

from __future__ import annotations

from .data_types import (
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
    ShearResult,
    SupportCondition,
    ValidationReport,
)

__all__ = [
    "BeamType",
    "DesignSectionType",
    "SupportCondition",
    "ExposureClass",
    "FlexureResult",
    "ShearResult",
    "DeflectionResult",
    "DeflectionLevelBResult",
    "CrackWidthResult",
    "ComplianceCaseResult",
    "ComplianceReport",
    "ValidationReport",
    "CuttingAssignment",
    "CuttingPlan",
]
