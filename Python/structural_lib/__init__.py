"""
Package:      structural_lib
Description:  IS 456:2000 Structural Engineering Library
License:      MIT

Version is read dynamically from pyproject.toml via importlib.metadata.
Use api.get_library_version() to get the current version.
"""

from __future__ import annotations

import importlib
from importlib.metadata import PackageNotFoundError, version as _get_version
from types import ModuleType
from typing import Optional

# Dynamic version from installed package metadata
try:
    __version__ = _get_version("structural-lib-is456")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"  # Not installed, development mode

# Expose key modules
from . import flexure
from . import shear
from . import api
from . import detailing
from . import serviceability
from . import compliance
from . import bbs

# DXF export is optional (requires ezdxf)
dxf_export: Optional[ModuleType]
try:
    dxf_export = importlib.import_module(f"{__name__}.dxf_export")
except ImportError:
    dxf_export = None

__all__ = [
    "__version__",
    "api",
    "bbs",
    "compliance",
    "detailing",
    "dxf_export",
    "flexure",
    "serviceability",
    "shear",
]
