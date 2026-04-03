# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for IS 13920:2016 Cl 7 — Ductile Detailing for Columns
(Special Confining Reinforcement).

Functions under test:
    - check_column_geometry (Cl 7.1)
    - get_min_longitudinal_steel (Cl 7.2.1)
    - get_max_longitudinal_steel (Cl 7.2.1)
    - calculate_special_confining_spacing (Cl 7.4.6)
    - calculate_confining_length (Cl 7.4.1)
    - calculate_ash_required (Cl 7.4.7/7.4.8)
    - check_column_ductility (Cl 7 orchestrator)

Test types per function-quality-pipeline Step 4:
    1. Unit tests (happy path) — 8 tests
    2. Edge-case / boundary tests — 3 tests
    3. Degenerate / error tests — 3 tests
    4. Orchestrator integration tests — 3 tests
    5. Known-value hand-calculation test — 1 test
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is13920.column import (
    DuctileColumnResult,
    calculate_ash_required,
    calculate_confining_length,
    calculate_special_confining_spacing,
    check_column_ductility,
    check_column_geometry,
    get_max_longitudinal_steel,
    get_min_longitudinal_steel,
)

# =============================================================================
# 1. Unit Tests — Happy Path (8 tests)
# =============================================================================


def test_check_column_geometry_valid():
    """300×500mm column passes geometry checks.

    IS 13920 Cl 7.1.2: min(300,500) = 300 >= 300 OK.
    IS 13920 Cl 7.1.3: 300/500 = 0.6 >= 0.4 OK.
    """
    is_valid, msg, errors = check_column_geometry(b_mm=300.0, D_mm=500.0)
    assert is_valid is True
    assert msg == "OK"
    assert len(errors) == 0


def test_check_column_geometry_width_too_small():
    """200×500mm fails: min dimension 200 < 300 mm.

    IS 13920 Cl 7.1.2: 200 < 300 → E_DUCTILE_COL_001
    """
    is_valid, msg, errors = check_column_geometry(b_mm=200.0, D_mm=500.0)
    assert is_valid is False
    assert any(e.code == "E_DUCTILE_COL_001" for e in errors)


def test_check_column_geometry_bad_aspect_ratio():
    """300×900mm fails: aspect ratio 300/900 = 0.333 < 0.4.

    IS 13920 Cl 7.1.3: ratio 0.33 < 0.4 → E_DUCTILE_COL_002
    """
    is_valid, msg, errors = check_column_geometry(b_mm=300.0, D_mm=900.0)
    assert is_valid is False
    assert any(e.code == "E_DUCTILE_COL_002" for e in errors)


def test_get_min_longitudinal_steel():
    """IS 13920 Cl 7.2.1: minimum longitudinal steel = 0.8%."""
    assert get_min_longitudinal_steel() == 0.8


def test_get_max_longitudinal_steel():
    """IS 13920 Cl 7.2.1: maximum longitudinal steel = 4.0%."""
    assert get_max_longitudinal_steel() == 4.0


def test_calculate_special_confining_spacing():
    """300mm column, 16mm bar: s = min(300/4=75, 6×16=96, 100) = 75 mm.

    IS 13920 Cl 7.4.6.
    """
    s = calculate_special_confining_spacing(b_mm=300.0, bar_dia_mm=16.0)
    assert s == pytest.approx(75.0)


def test_calculate_confining_length_takes_max():
    """500mm D, 3000mm clear_height: lo = max(500, 3000/6=500, 450) = 500 mm.

    IS 13920 Cl 7.4.1.
    """
    lo = calculate_confining_length(D_mm=500.0, clear_height_mm=3000.0)
    assert lo == pytest.approx(500.0)


def test_calculate_ash_required():
    """Verify formula: Ash = 0.18 × s × h × (fck/fy) × (Ag/Ak - 1.0).

    IS 13920 Cl 7.4.8.
    s=75mm, h=220mm, fck=25, fy=415, Ag=90000, Ak=48400
    Ash = 0.18 × 75 × 220 × (25/415) × (90000/48400 - 1.0)
        = 0.18 × 75 × 220 × 0.060241 × 0.85950
        = 153.796 mm²
    """
    Ag = 300.0 * 300.0  # 90000 mm²
    Ak = 220.0 * 220.0  # 48400 mm²
    ash = calculate_ash_required(
        s_mm=75.0, h_mm=220.0, fck=25.0, fy=415.0, Ag_mm2=Ag, Ak_mm2=Ak
    )
    # Hand calculation:
    # 0.18 * 75 * 220 * (25/415) * (90000/48400 - 1)
    # = 0.18 * 75 * 220 * 0.06024096 * 0.85950413
    expected = 0.18 * 75.0 * 220.0 * (25.0 / 415.0) * (90000.0 / 48400.0 - 1.0)
    assert ash == pytest.approx(expected, rel=1e-6)


# =============================================================================
# 2. Edge-Case / Boundary Tests (3 tests)
# =============================================================================


def test_geometry_exactly_300mm():
    """Boundary: 300mm width is exactly the minimum — should pass.

    IS 13920 Cl 7.1.2: 300 >= 300 → valid.
    """
    is_valid, msg, errors = check_column_geometry(b_mm=300.0, D_mm=300.0)
    assert is_valid is True
    assert len(errors) == 0


def test_geometry_exactly_aspect_ratio_limit():
    """Boundary: b/D = 0.4 exactly — should pass.

    IS 13920 Cl 7.1.3: 300/750 = 0.4 exactly → valid.
    """
    is_valid, msg, errors = check_column_geometry(b_mm=300.0, D_mm=750.0)
    assert is_valid is True
    assert len(errors) == 0


def test_confining_length_450mm_minimum():
    """Small column where 450mm minimum governs.

    D=300mm, clear_height=2400mm: lo = max(300, 2400/6=400, 450) = 450 mm.
    IS 13920 Cl 7.4.1: 450mm minimum governs.
    """
    lo = calculate_confining_length(D_mm=300.0, clear_height_mm=2400.0)
    assert lo == pytest.approx(450.0)


# =============================================================================
# 3. Degenerate / Error Tests (3 tests)
# =============================================================================


def test_zero_dimension_raises():
    """Degenerate: 0mm width returns invalid with error code.

    IS 13920 Cl 7.1: dimensions must be positive.
    """
    is_valid, msg, errors = check_column_geometry(b_mm=0.0, D_mm=500.0)
    assert is_valid is False
    assert any(e.code == "E_DUCTILE_COL_001" for e in errors)


def test_negative_fck_raises():
    """Degenerate: negative fck raises ValueError.

    Input validation in calculate_ash_required.
    """
    with pytest.raises(ValueError, match="fck"):
        calculate_ash_required(
            s_mm=75.0,
            h_mm=220.0,
            fck=-25.0,
            fy=415.0,
            Ag_mm2=90000.0,
            Ak_mm2=48400.0,
        )


def test_zero_bar_dia_raises():
    """Degenerate: 0mm bar diameter raises ValueError.

    Input validation in calculate_special_confining_spacing.
    """
    with pytest.raises(ValueError, match="bar_dia_mm"):
        calculate_special_confining_spacing(b_mm=300.0, bar_dia_mm=0.0)


# =============================================================================
# 4. Orchestrator Tests — check_column_ductility (3 tests)
# =============================================================================


def test_check_column_ductility_compliant():
    """Full passing case: 400×400mm, 3000mm clear, 20mm bars, M25/Fe415.

    IS 13920 Cl 7: all sub-checks pass → is_compliant=True.
    """
    result = check_column_ductility(
        b_mm=400.0,
        D_mm=400.0,
        clear_height_mm=3000.0,
        bar_dia_mm=20.0,
        fck=25.0,
        fy=415.0,
    )
    assert isinstance(result, DuctileColumnResult)
    assert result.is_geometry_valid is True
    assert result.is_compliant is True
    assert result.min_pt == 0.8
    assert result.max_pt == 4.0
    assert result.confining_spacing_mm > 0
    assert result.confining_length_mm > 0
    assert len(result.errors) == 0


def test_check_column_ductility_fails_geometry():
    """Geometry fails (200mm width) → overall is_compliant=False.

    IS 13920 Cl 7.1.2: 200 < 300 → fails early.
    """
    result = check_column_ductility(
        b_mm=200.0,
        D_mm=500.0,
        clear_height_mm=3000.0,
        bar_dia_mm=20.0,
        fck=25.0,
        fy=415.0,
    )
    assert result.is_geometry_valid is False
    assert result.is_compliant is False
    assert len(result.errors) > 0
    assert any(e.code == "E_DUCTILE_COL_001" for e in result.errors)


def test_check_column_ductility_returns_all_fields():
    """Verify all fields on DuctileColumnResult are populated for valid input."""
    result = check_column_ductility(
        b_mm=350.0,
        D_mm=500.0,
        clear_height_mm=3600.0,
        bar_dia_mm=16.0,
        fck=30.0,
        fy=500.0,
        Ag_mm2=350.0 * 500.0,
        Ak_mm2=270.0 * 420.0,
    )
    assert result.is_geometry_valid is True
    assert result.is_compliant is True
    assert result.min_pt == 0.8
    assert result.max_pt == 4.0
    # Spacing: min(350/4=87.5, 6×16=96, 100) = 87.5
    assert result.confining_spacing_mm == pytest.approx(87.5)
    # lo: max(500, 3600/6=600, 450) = 600
    assert result.confining_length_mm == pytest.approx(600.0)
    # Ash computed since Ag and Ak provided
    assert result.ash_required_mm2 > 0


# =============================================================================
# 5. Known-Value Hand-Calculation Test (IS 13920:2016)
# =============================================================================


def test_known_value_400x400_m25_fe415():
    """IS 13920 hand calculation: 400×400mm column, M25/Fe415, 20mm bars.

    Given:
        b=400mm, D=400mm, clear_height=3000mm, bar_dia=20mm
        fck=25 N/mm², fy=415 N/mm²
        Ag=160000 mm², Ak (core to hoop centreline) = 312×312 = 97344 mm²
        cover=40mm, hoop=8mm → core side = 400 - 2×(40+8/2) = 312mm
        h (hoop outer dimension) = 400 - 2×40 = 320mm

    Special confining spacing (Cl 7.4.6):
        s = min(400/4=100, 6×20=120, 100) = 100 mm

    Confinement length (Cl 7.4.1):
        lo = max(400, 3000/6=500, 450) = 500 mm

    Ash (Cl 7.4.8):
        Ash = 0.18 × 100 × 320 × (25/415) × (160000/97344 - 1.0)
            = 0.18 × 100 × 320 × 0.060241 × 0.64352
            = 223.21 mm²
    """
    # Verify individual functions first
    s = calculate_special_confining_spacing(b_mm=400.0, bar_dia_mm=20.0)
    assert s == pytest.approx(100.0)

    lo = calculate_confining_length(D_mm=400.0, clear_height_mm=3000.0)
    assert lo == pytest.approx(500.0)

    Ag = 400.0 * 400.0  # 160000 mm²
    Ak = 312.0 * 312.0  # 97344 mm²
    h = 400.0 - 2 * 40.0  # 320 mm (hoop outer dimension)

    ash = calculate_ash_required(
        s_mm=100.0,
        h_mm=320.0,
        fck=25.0,
        fy=415.0,
        Ag_mm2=Ag,
        Ak_mm2=Ak,
    )
    # Hand calc: 0.18 * 100 * 320 * (25/415) * (160000/97344 - 1)
    expected_ash = 0.18 * 100.0 * 320.0 * (25.0 / 415.0) * (Ag / Ak - 1.0)
    assert ash == pytest.approx(expected_ash, rel=1e-4)
    # Approximate sanity check
    assert ash == pytest.approx(223.21, rel=0.01)

    # Verify orchestrator with Ag/Ak provided
    result = check_column_ductility(
        b_mm=400.0,
        D_mm=400.0,
        clear_height_mm=3000.0,
        bar_dia_mm=20.0,
        fck=25.0,
        fy=415.0,
        Ag_mm2=Ag,
        Ak_mm2=Ak,
    )
    assert result.is_compliant is True
    assert result.confining_spacing_mm == pytest.approx(100.0)
    assert result.confining_length_mm == pytest.approx(500.0)
    assert result.ash_required_mm2 > 0
