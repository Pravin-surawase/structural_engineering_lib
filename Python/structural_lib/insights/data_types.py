"""
Compatibility shim for the renamed insights types module.

This preserves imports like `structural_lib.insights.data_types`.
"""

from __future__ import annotations

from . import types as _types

__all__ = [name for name in dir(_types) if not name.startswith("_")]

globals().update({name: getattr(_types, name) for name in __all__})
