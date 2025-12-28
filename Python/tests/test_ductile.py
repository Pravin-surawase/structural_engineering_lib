import pytest
import sys
import os

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.ductile import (
    check_geometry,
    get_min_tension_steel_percentage,
    calculate_confinement_spacing,
    check_beam_ductility,
)


def test_geometry_checks():
    # Valid
    valid, msg, errors = check_geometry(230, 450)
    assert valid is True
    assert msg == "OK"
    assert errors == []

    # Invalid Width
    valid, msg, errors = check_geometry(150, 450)
    assert valid is False
    assert "Width" in msg
    assert len(errors) == 1
    assert errors[0].code == "E_DUCTILE_001"

    # Invalid Ratio (b/D < 0.3)
    # 200 / 700 = 0.285
    valid, msg, errors = check_geometry(200, 700)
    assert valid is False
    assert "Width/Depth ratio" in msg
    assert len(errors) == 1
    assert errors[0].code == "E_DUCTILE_002"


def test_min_steel():
    # fck=25, fy=500
    # rho = 0.24 * 5 / 500 = 0.0024 -> 0.24%
    pt = get_min_tension_steel_percentage(25, 500)
    assert pt == pytest.approx(0.24, rel=1e-4)

    # fck=30, fy=415
    # rho = 0.24 * 5.477 / 415 = 0.00316 -> 0.316%
    pt = get_min_tension_steel_percentage(30, 415)
    assert pt == pytest.approx(0.3168, rel=1e-3)


def test_min_steel_invalid_inputs():
    """Edge case: invalid inputs should return 0.0 (no crash)."""
    assert get_min_tension_steel_percentage(0, 500) == 0.0
    assert get_min_tension_steel_percentage(25, 0) == 0.0
    assert get_min_tension_steel_percentage(-25, 500) == 0.0
    assert get_min_tension_steel_percentage(25, -500) == 0.0


def test_confinement_spacing():
    # d=450, min_bar=12
    # 1. d/4 = 112.5
    # 2. 8*12 = 96
    # 3. 100
    # Min should be 96
    s = calculate_confinement_spacing(450, 12)
    assert s == 96

    # d=600, min_bar=20
    # 1. 150
    # 2. 160
    # 3. 100
    # Min should be 100
    s = calculate_confinement_spacing(600, 20)
    assert s == 100


def test_full_check():
    res = check_beam_ductility(230, 450, 410, 25, 500, 12)
    assert res.is_geometry_valid is True
    assert res.confinement_spacing <= 100
    assert res.remarks == "Compliant"
