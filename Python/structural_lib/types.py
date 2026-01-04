"""
Compatibility shim for the renamed data_types module.

This keeps historical imports like `structural_lib.types` working while the
project transitions to `structural_lib.data_types`.
"""

from __future__ import annotations

from . import data_types as _data_types

__all__ = [name for name in dir(_data_types) if not name.startswith("_")]

globals().update({name: getattr(_data_types, name) for name in __all__})
