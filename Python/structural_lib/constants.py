"""
Module:       constants
Description:  Global constants for IS 456:2000 implementation
"""

import math

# Mathematical Constants
PI = math.pi

# Material Safety Factors (IS 456:2000, Cl. 36.4.2)
GAMMA_C = 1.5  # Partial safety factor for concrete
GAMMA_S = 1.15  # Partial safety factor for steel

# Design Constants
MIN_ECCENTRICITY_RATIO = 0.05  # min e = L/500 + D/30
MODULUS_ELASTICITY_STEEL = 200000  # N/mm^2 (Es)
