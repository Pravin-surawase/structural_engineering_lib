"""
Module:       api
Description:  Public facing API functions
"""

from . import ductile

def get_library_version() -> str:
    return "0.4.0"

def check_beam_ductility(b: float, D: float, d: float, fck: float, fy: float, min_long_bar_dia: float):
    """
    Wrapper for ductile.check_beam_ductility
    """
    return ductile.check_beam_ductility(b, D, d, fck, fy, min_long_bar_dia)

