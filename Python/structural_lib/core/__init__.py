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
from structural_lib.core.geometry import LSection, RectangularSection, Section, TSection
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
]
