# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Package:      structural_lib
Description:  IS 456:2000 Structural Engineering Library
License:      MIT

Version is read dynamically from pyproject.toml via importlib.metadata.
Use api.get_library_version() to get the current version.
"""

from __future__ import annotations

import importlib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version
from types import ModuleType as _ModuleType

# Dynamic version from installed package metadata
try:
    __version__ = _get_version("structural-lib-is456")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"  # Not installed, development mode

# Expose key modules
from . import (
    adapters,
    api,
    audit,
    bbs,
    calculation_report,
    compliance,
    costing,
    detailing,
    etabs_import,
    flexure,
    inputs,
    models,
    result_base,
    serialization,
    serviceability,
    shear,
    testing_strategies,
    types,
)

# DXF export is optional (requires ezdxf)
dxf_export: _ModuleType | None
try:
    dxf_export = importlib.import_module(f"{__name__}.dxf_export")
except ImportError:
    dxf_export = None

# Reports module is optional (requires jinja2)
reports: _ModuleType | None
try:
    reports = importlib.import_module(f"{__name__}.reports")
except ImportError:
    reports = None

__all__ = [
    "__version__",
    "adapters",
    "api",
    "audit",
    "bbs",
    "calculation_report",
    "compliance",
    "costing",
    "detailing",
    "dxf_export",
    "etabs_import",
    "flexure",
    "inputs",
    "models",
    "reports",
    "result_base",
    "serialization",
    "serviceability",
    "shear",
    "testing_strategies",
    "types",
]
