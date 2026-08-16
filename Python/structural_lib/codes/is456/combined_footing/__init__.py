# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Bounded symmetric rigid combined-footing analysis for INDIA-2."""

from structural_lib.codes.is456.combined_footing.analysis import (
    CombinedFootingActionResult,
    CombinedFootingGeometryResult,
    CombinedFootingSectionAction,
    CombinedFootingSectionKind,
    CombinedFootingTensionFace,
    CombinedFootingTransverseAction,
    analyze_symmetric_combined_footing,
    resolve_symmetric_combined_footing_geometry,
)
from structural_lib.codes.is456.combined_footing.models import (
    CombinedFootingActionInput,
    CombinedFootingAnalysisMethod,
    CombinedFootingContractError,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
    CombinedFootingPressureModel,
)

__all__ = [
    "CombinedFootingActionInput",
    "CombinedFootingActionResult",
    "CombinedFootingAnalysisMethod",
    "CombinedFootingContractError",
    "CombinedFootingGeometryInput",
    "CombinedFootingGeometryResult",
    "CombinedFootingInput",
    "CombinedFootingPressureModel",
    "CombinedFootingSectionAction",
    "CombinedFootingSectionKind",
    "CombinedFootingTensionFace",
    "CombinedFootingTransverseAction",
    "analyze_symmetric_combined_footing",
    "resolve_symmetric_combined_footing_geometry",
]
