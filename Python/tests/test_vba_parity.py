"""
VBA Parity Tests — Golden Vectors for Python ↔ VBA Alignment

This module defines 10 golden test vectors that MUST produce identical
results in both Python and VBA implementations. These vectors cover:
- Flexure: singly, doubly, flanged beams
- Shear: safe, min reinforcement, unsafe
- Materials: xu_max, Table 19 lookup
- Detailing: Ld, lap length

TOLERANCES (per docs/reference/known-pitfalls.md):
- Areas: ±1 mm²
- Stresses: ±0.01 N/mm²
- Lengths: ±1 mm
- Ratios: ±0.0001

USAGE:
    pytest tests/test_vba_parity.py -v

VBA COUNTERPART:
    VBA/Tests/Test_Parity.bas contains corresponding tests (FSR-001, SHR-001, etc.)
    Both test files use parity_test_vectors.json as the source of truth.

PARITY WORKFLOW:
    1. Update Python → run pytest → capture expected values
    2. Update VBA → run Test_Parity.Run_All_Parity_Tests → compare
    3. If values differ beyond tolerance, investigate and fix
"""

import pytest
from dataclasses import dataclass
from typing import Any

from structural_lib import flexure, shear, materials, tables, detailing


@dataclass
class GoldenVector:
    """A test case that must match between Python and VBA."""

    id: str
    description: str
    function: str
    inputs: dict
    expected: dict
    tolerances: dict


# =============================================================================
# GOLDEN VECTORS — 10 cases covering critical parity paths
# =============================================================================

GOLDEN_VECTORS = [
    # --- Flexure ---
    GoldenVector(
        id="GV-01",
        description="Singly reinforced beam - Mu_lim",
        function="flexure.calculate_mu_lim",
        inputs={"b": 300, "d": 450, "fck": 25, "fy": 500},
        expected={"mu_lim_knm": 202.91},
        tolerances={"mu_lim_knm": 0.1},
    ),
    GoldenVector(
        id="GV-02",
        description="Ast required - under-reinforced",
        function="flexure.calculate_ast_required",
        inputs={"b": 300, "d": 450, "mu_knm": 150, "fck": 25, "fy": 500},
        expected={"ast_mm2": 881.88},
        tolerances={"ast_mm2": 1.0},
    ),
    GoldenVector(
        id="GV-03",
        description="Ast required - over-reinforced returns -1",
        function="flexure.calculate_ast_required",
        inputs={"b": 300, "d": 450, "mu_knm": 250, "fck": 25, "fy": 500},
        expected={"ast_mm2": -1.0},
        tolerances={"ast_mm2": 0.0},
    ),
    GoldenVector(
        id="GV-04",
        description="Design singly reinforced - full result",
        function="flexure.design_singly_reinforced",
        inputs={
            "b": 300,
            "d": 450,
            "d_total": 500,
            "mu_knm": 100,
            "fck": 25,
            "fy": 500,
        },
        expected={
            "ast_required": 557.09,
            "is_safe": True,
            "mu_lim": 202.91,
        },
        tolerances={"ast_required": 1.0, "mu_lim": 0.1},
    ),
    # --- Shear ---
    GoldenVector(
        id="GV-05",
        description="Shear stress calculation",
        function="shear.calculate_tv",
        inputs={"vu_kn": 150, "b": 300, "d": 450},
        expected={"tv": 1.111},
        tolerances={"tv": 0.01},
    ),
    GoldenVector(
        id="GV-06",
        description="Table 19 - Tc lookup with interpolation",
        function="tables.get_tc_value",
        inputs={"pt": 0.75, "fck": 25},
        expected={"tc": 0.57},
        tolerances={"tc": 0.01},
    ),
    GoldenVector(
        id="GV-07",
        description="Shear design - safe with stirrups",
        function="shear.design_shear",
        inputs={
            "vu_kn": 150,
            "b": 300,
            "d": 450,
            "fck": 25,
            "fy": 500,
            "asv": 100.5,  # 2-leg 8mm stirrup
            "pt": 0.698,  # 942 / (300*450) * 100
        },
        expected={
            "is_safe": True,
            "tv": 1.111,
        },
        tolerances={"tv": 0.01},
    ),
    # --- Materials ---
    GoldenVector(
        id="GV-08",
        description="xu_max/d ratio for Fe500",
        function="materials.get_xu_max_d",
        inputs={"fy": 500},
        expected={"xu_max_d": 0.46},
        tolerances={"xu_max_d": 0.001},
    ),
    GoldenVector(
        id="GV-09",
        description="xu_max/d ratio for Fe415",
        function="materials.get_xu_max_d",
        inputs={"fy": 415},
        expected={"xu_max_d": 0.48},
        tolerances={"xu_max_d": 0.001},
    ),
    # --- Detailing ---
    GoldenVector(
        id="GV-10",
        description="Development length calculation",
        function="detailing.calculate_development_length",
        inputs={"bar_dia": 20, "fy": 500, "fck": 25},
        expected={"ld_mm": 971.0},
        tolerances={"ld_mm": 1.0},
    ),
]


# =============================================================================
# Helper to call functions dynamically
# =============================================================================


def call_function(func_path: str, inputs: dict) -> Any:
    """Call a function by its dotted path and return the result."""
    module_name, func_name = func_path.rsplit(".", 1)

    if module_name == "flexure":
        module = flexure
    elif module_name == "shear":
        module = shear
    elif module_name == "materials":
        module = materials
    elif module_name == "tables":
        module = tables
    elif module_name == "detailing":
        module = detailing
    else:
        raise ValueError(f"Unknown module: {module_name}")

    func = getattr(module, func_name)
    return func(**inputs)


def extract_value(result: Any, key: str) -> Any:
    """Extract a value from a result (scalar or dataclass)."""
    # For scalar functions, the result IS the value
    if isinstance(result, (int, float)):
        return result

    # For dataclass results
    if hasattr(result, key):
        return getattr(result, key)
    elif isinstance(result, dict):
        return result[key]

    # Fallback
    return result


# =============================================================================
# Parametrized Tests
# =============================================================================


@pytest.mark.parametrize(
    "vector",
    GOLDEN_VECTORS,
    ids=[v.id for v in GOLDEN_VECTORS],
)
def test_golden_vector(vector: GoldenVector):
    """Test a golden vector against expected values."""
    result = call_function(vector.function, vector.inputs)

    for key, expected_value in vector.expected.items():
        if key == "is_safe":
            # Boolean check
            actual = extract_value(result, key)
            assert (
                actual == expected_value
            ), f"{vector.id}: {key} expected {expected_value}, got {actual}"
        else:
            # Numeric check with tolerance
            actual = extract_value(result, key)
            tolerance = vector.tolerances.get(key, 0.01)
            assert abs(actual - expected_value) <= tolerance, (
                f"{vector.id}: {key} expected {expected_value} ± {tolerance}, "
                f"got {actual} (diff: {abs(actual - expected_value):.4f})"
            )


# =============================================================================
# Export for VBA comparison
# =============================================================================


def print_golden_vectors_for_vba():
    """Print golden vectors in a format that can be used in VBA tests."""
    print("=" * 70)
    print("GOLDEN VECTORS FOR VBA PARITY TESTING")
    print("=" * 70)
    print()

    for v in GOLDEN_VECTORS:
        print(f"' {v.id}: {v.description}")
        print(f"' Function: {v.function}")
        print(f"' Inputs: {v.inputs}")
        print(f"' Expected: {v.expected}")
        print(f"' Tolerances: {v.tolerances}")
        print()

    print("=" * 70)


if __name__ == "__main__":
    print_golden_vectors_for_vba()
