"""
Package:      structural_lib
Description:  IS 456:2000 Structural Engineering Library
Version:      0.9.0
License:      MIT
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Optional

# Expose key modules
from . import constants
from . import types
from . import tables
from . import utilities
from . import materials
from . import flexure
from . import shear
from . import ductile
from . import api
from . import detailing
from . import serviceability
from . import compliance

# DXF export is optional (requires ezdxf)
dxf_export: Optional[ModuleType]
try:
    dxf_export = importlib.import_module(f"{__name__}.dxf_export")
except ImportError:
    dxf_export = None

# Excel integration module
from . import excel_integration

__all__ = [
    "api",
    "compliance",
    "constants",
    "detailing",
    "ductile",
    "dxf_export",
    "excel_integration",
    "flexure",
    "materials",
    "serviceability",
    "shear",
    "tables",
    "types",
    "utilities",
]
