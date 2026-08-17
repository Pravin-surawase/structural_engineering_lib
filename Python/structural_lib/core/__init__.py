"""Core module - Code-agnostic base classes and utilities.

This module provides the foundation for multi-code support:
- Abstract base classes for design calculations
- Universal material models
- Code-agnostic geometry definitions
- Unit handling utilities

All code-specific implementations (IS 456, ACI 318, EC2) inherit from these bases.
"""

from __future__ import annotations

from structural_lib.core.base import (
    DesignCode,
    DetailingRules,
    FlexureDesigner,
    ShearDesigner,
)
from structural_lib.core.building_gravity import (
    BuildingModelV1,
    BuildingSourceRecordV1,
    ExcludedGravityActionV1,
    GravityActionCategoryV1,
    GravityApprovedExclusionV1,
    GravityCombinationFactorV1,
    GravityCombinationV1,
    GravityFootingDestinationV1,
    GravityInclusionDispositionV1,
    GravityInclusionRuleV1,
    GravityLoadCaseV1,
    GravityLoadStateV1,
    GravityMaterialV1,
    GravityMemberKindV1,
    GravityMemberV1,
    GravityNodeV1,
    GravityPanelV1,
    GravitySectionKindV1,
    GravitySectionV1,
    GravitySourceReferenceV1,
    GravitySupportIdealizationV1,
    LoadModelV1,
    SourceDispositionV1,
    canonical_building_model_hash_v1,
    canonical_load_model_hash_v1,
)
from structural_lib.core.geometry import LSection, RectangularSection, Section, TSection
from structural_lib.core.gravity_workflow import (
    ComponentApplicabilityMatrixV1,
    GravityBeamDesignBasisV1,
    GravityColumnDesignBasisV1,
    GravityComponentApplicabilityV1,
    GravityComponentKindV1,
    GravityComponentResultV1,
    GravityFootingDesignBasisV1,
    GravityMemberActionV1,
    GravityPrerequisiteDispositionV1,
    GravitySlabDesignBasisV1,
    GravityWorkflowRequestV1,
    GravityWorkflowResultV1,
)
from structural_lib.core.materials import Concrete, MaterialFactory, Steel
from structural_lib.core.registry import CodeRegistry

__all__ = [
    # Base classes
    "DesignCode",
    "FlexureDesigner",
    "ShearDesigner",
    "DetailingRules",
    # Materials
    "Concrete",
    "Steel",
    "MaterialFactory",
    # Geometry
    "Section",
    "RectangularSection",
    "TSection",
    "LSection",
    # Registry
    "CodeRegistry",
    # Building gravity V1 contracts
    "BuildingModelV1",
    "BuildingSourceRecordV1",
    "ExcludedGravityActionV1",
    "GravityActionCategoryV1",
    "GravityApprovedExclusionV1",
    "GravityCombinationFactorV1",
    "GravityCombinationV1",
    "GravityFootingDestinationV1",
    "GravityInclusionDispositionV1",
    "GravityInclusionRuleV1",
    "GravityLoadCaseV1",
    "GravityLoadStateV1",
    "GravityMaterialV1",
    "GravityMemberKindV1",
    "GravityMemberV1",
    "GravityNodeV1",
    "GravityPanelV1",
    "GravitySectionKindV1",
    "GravitySectionV1",
    "GravitySourceReferenceV1",
    "GravitySupportIdealizationV1",
    "LoadModelV1",
    "SourceDispositionV1",
    "canonical_building_model_hash_v1",
    "canonical_load_model_hash_v1",
    # Building Gravity Workflow V1 contracts
    "ComponentApplicabilityMatrixV1",
    "GravityBeamDesignBasisV1",
    "GravityColumnDesignBasisV1",
    "GravityComponentApplicabilityV1",
    "GravityComponentKindV1",
    "GravityComponentResultV1",
    "GravityFootingDesignBasisV1",
    "GravityMemberActionV1",
    "GravityPrerequisiteDispositionV1",
    "GravitySlabDesignBasisV1",
    "GravityWorkflowRequestV1",
    "GravityWorkflowResultV1",
]
