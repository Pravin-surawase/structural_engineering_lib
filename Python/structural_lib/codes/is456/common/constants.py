"""IS 456:2000 named design constants.

Centralises magic numbers that appear across flexure, shear, torsion, and
detailing modules.  Every constant includes its IS 456 clause reference.

Usage::

    from structural_lib.codes.is456.common.constants import (
        STRESS_RATIO, STRESS_BLOCK_FACTOR, STRESS_BLOCK_DEPTH,
    )

.. note::
    ``IS456Code`` class in ``codes/is456/__init__.py`` also defines
    ``STRESS_BLOCK_FACTOR`` and ``STRESS_BLOCK_DEPTH`` as class attributes.
    In a future refactor those class attributes should import from this
    module to maintain a single source of truth.

.. note::
    General safety factors ``GAMMA_C`` and ``GAMMA_S`` live in
    ``core/constants.py`` because they apply across design codes.
"""

# ---------------------------------------------------------------------------
# Steel stress ratio --- IS 456 Cl. 36.1
# Design yield stress fd = 0.87 * fy  (i.e. fy / gamma_s where gamma_s = 1.15)
# ---------------------------------------------------------------------------
STRESS_RATIO: float = 0.87

# ---------------------------------------------------------------------------
# Rectangular stress-block coefficients --- IS 456 Cl. 38.1, Fig. 22
# Compressive force Cu = 0.36 * fck * b * xu
# Lever arm from top  = xu - 0.42 * xu = 0.58 * xu  (centroid at 0.42 xu)
# Peak stress in block = 0.446 * fck
# ---------------------------------------------------------------------------
STRESS_BLOCK_FACTOR: float = 0.36  # Force coefficient
STRESS_BLOCK_DEPTH: float = 0.42  # Centroid depth coefficient
STRESS_BLOCK_PEAK: float = 0.446  # Peak compressive stress ratio

# ---------------------------------------------------------------------------
# Limiting neutral-axis depth --- IS 456 Cl. 38.1, Table 4.1 (SP:16)
# xu_max / d = 700 / (1100 + 0.87 * fy)
# ---------------------------------------------------------------------------
XU_MAX_NUMERATOR: float = 700.0
XU_MAX_DENOM_BASE: float = 1100.0

# ---------------------------------------------------------------------------
# Flanged beam stress-block --- IS 456 Annex G, G-2.2
# Average stress in flange overhang = 0.45 * fck
# ---------------------------------------------------------------------------
FLANGE_STRESS_FACTOR: float = 0.45

# ---------------------------------------------------------------------------
# Minimum reinforcement --- IS 456 Cl. 26.5.1.1
# As_min = 0.85 * b * d / fy
# ---------------------------------------------------------------------------
MIN_STEEL_FACTOR: float = 0.85

# ---------------------------------------------------------------------------
# Maximum reinforcement --- IS 456 Cl. 26.5.1.1
# As_max = 0.04 * b * D  (4% of gross cross-sectional area)
# ---------------------------------------------------------------------------
MAX_STEEL_RATIO: float = 0.04

# ---------------------------------------------------------------------------
# Maximum stirrup spacing --- IS 456 Cl. 26.5.1.5
# s_max = min(0.75 * d, 300 mm)
# ---------------------------------------------------------------------------
MAX_SPACING_FACTOR: float = 0.75
MAX_SPACING_MM: float = 300.0

# ---------------------------------------------------------------------------
# Minimum shear reinforcement intensity --- IS 456 Cl. 26.5.1.6
# Asv / (b * sv) >= 0.4 / (0.87 * fy)
# ---------------------------------------------------------------------------
MIN_SHEAR_REINF_FACTOR: float = 0.4

# ---------------------------------------------------------------------------
# Torsion --- IS 456 Cl. 41.3.1 & 41.4.2
# Equivalent shear:   Ve = Vu + 1.6 * (Tu / b)
# Equivalent moment:  Me = Mu + Mt  where Mt = Tu * (1 + D/b) / 1.7
# ---------------------------------------------------------------------------
TORSION_SHEAR_FACTOR: float = 1.6
TORSION_MOMENT_DIVISOR: float = 1.7

# ---------------------------------------------------------------------------
# Concrete modulus of elasticity --- IS 456 Cl. 6.2.3.1
# Ec = 5000 * sqrt(fck)  (N/mm2)
# ---------------------------------------------------------------------------
CONCRETE_EC_FACTOR: float = 5000.0

# ---------------------------------------------------------------------------
# Flexural tensile strength --- IS 456 Cl. 6.2.2
# fcr = 0.7 * sqrt(fck)  (N/mm2)
# ---------------------------------------------------------------------------
CONCRETE_FCR_FACTOR: float = 0.7

# ---------------------------------------------------------------------------
# Side-face reinforcement --- IS 456 Cl. 26.5.1.3
# Required when web depth > 750 mm; area >= 0.1% of web area
# ---------------------------------------------------------------------------
SIDE_FACE_DEPTH_THRESHOLD_MM: float = 750.0
SIDE_FACE_AREA_RATIO: float = 0.001  # 0.1%

# ---------------------------------------------------------------------------
# Minimum clear cover --- IS 456 Cl. 26.4.1 (moderate exposure)
# ---------------------------------------------------------------------------
MIN_CLEAR_COVER_MM: float = 25.0

# ---------------------------------------------------------------------------
# Standard bar and stirrup diameters (mm)
# ---------------------------------------------------------------------------
STANDARD_BAR_DIAMETERS: tuple[int, ...] = (8, 10, 12, 16, 20, 25, 32)
STANDARD_STIRRUP_DIAMETERS: tuple[int, ...] = (6, 8, 10, 12)
STANDARD_STIRRUP_SPACINGS: tuple[int, ...] = (
    75,
    100,
    125,
    150,
    175,
    200,
    225,
    250,
    275,
    300,
)
