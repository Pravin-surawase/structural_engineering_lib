"""
Package:      structural_lib
Description:  IS 456:2000 Structural Engineering Library
Version:      0.8.0
License:      MIT
"""

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
try:
    from . import dxf_export
except ImportError:
    dxf_export = None  # ezdxf not installed

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
