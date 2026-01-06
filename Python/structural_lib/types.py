# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Compatibility shim for the renamed data_types module.

This keeps historical imports like `structural_lib.types` working while the
project transitions to `structural_lib.data_types`.
"""

from __future__ import annotations

from .data_types import (
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

__all__ = [
    "BeamGeometry",
    "BeamType",
    "DesignSectionType",
    "ExposureClass",
    "FlexureResult",
    "JobSpec",
    "LoadCase",
    "ShearResult",
    "SupportCondition",
    "DeflectionResult",
    "DeflectionLevelBResult",
    "CrackWidthResult",
    "ComplianceCaseResult",
    "ComplianceReport",
    "ValidationReport",
    "CuttingAssignment",
    "CuttingPlan",
]
