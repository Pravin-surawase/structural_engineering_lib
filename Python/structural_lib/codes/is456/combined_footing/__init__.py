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
    CombinedFootingDesignInput,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
    CombinedFootingMaterialInput,
    CombinedFootingPressureModel,
    CombinedFootingReinforcementInput,
    CombinedFootingSupportingAreaBasis,
    CombinedFootingTransferInput,
)
from structural_lib.codes.is456.combined_footing.strength import (
    CombinedFootingDesignDisposition,
    CombinedFootingFlexureResult,
    CombinedFootingLoadTransferResult,
    CombinedFootingOneWayShearResult,
    CombinedFootingPunchingResult,
    CombinedFootingStrengthResult,
    check_symmetric_combined_footing_strength,
)

__all__ = [
    "CombinedFootingActionInput",
    "CombinedFootingActionResult",
    "CombinedFootingAnalysisMethod",
    "CombinedFootingContractError",
    "CombinedFootingDesignDisposition",
    "CombinedFootingDesignInput",
    "CombinedFootingFlexureResult",
    "CombinedFootingGeometryInput",
    "CombinedFootingGeometryResult",
    "CombinedFootingInput",
    "CombinedFootingLoadTransferResult",
    "CombinedFootingMaterialInput",
    "CombinedFootingOneWayShearResult",
    "CombinedFootingPressureModel",
    "CombinedFootingPunchingResult",
    "CombinedFootingReinforcementInput",
    "CombinedFootingSectionAction",
    "CombinedFootingSectionKind",
    "CombinedFootingStrengthResult",
    "CombinedFootingSupportingAreaBasis",
    "CombinedFootingTensionFace",
    "CombinedFootingTransferInput",
    "CombinedFootingTransverseAction",
    "analyze_symmetric_combined_footing",
    "check_symmetric_combined_footing_strength",
    "resolve_symmetric_combined_footing_geometry",
]
