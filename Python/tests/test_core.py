"""Tests for structural_lib.core module.

Tests the new multi-code foundation:
- Base classes
- Materials
- Geometry
- Registry
"""

from __future__ import annotations

import pytest

from structural_lib.core import (
    CodeRegistry,
    Concrete,
    LSection,
    MaterialFactory,
    RectangularSection,
    Steel,
    TSection,
)
from structural_lib.core.base import DesignResult


class TestDesignResult:
    """Tests for DesignResult dataclass."""

    def test_success_result(self):
        result = DesignResult(success=True, value=123.45)
        assert result.success is True
        assert result.value == 123.45
        assert result.warnings == []

    def test_failure_result_with_warnings(self):
        result = DesignResult(success=False, value=None, warnings=["Section too small"])
        assert result.success is False
        assert len(result.warnings) == 1


class TestCodeRegistry:
    """Tests for CodeRegistry."""

    def test_is456_registered(self):
        """IS456 should be auto-registered on import."""
        from structural_lib.codes import is456  # noqa: F401

        assert CodeRegistry.is_registered("IS456")

    def test_get_is456(self):
        from structural_lib.codes import is456  # noqa: F401

        code = CodeRegistry.get("IS456")
        assert code.code_id == "IS456"
        assert code.code_name == "Indian Standard IS 456:2000"

    def test_list_codes(self):
        from structural_lib.codes import is456  # noqa: F401

        codes = CodeRegistry.list_codes()
        assert "IS456" in codes

    def test_get_unknown_code_raises(self):
        with pytest.raises(KeyError, match="not found"):
            CodeRegistry.get("UNKNOWN_CODE")


class TestMaterials:
    """Tests for material classes."""

    def test_concrete_creation(self):
        conc = Concrete(fck=30)
        assert conc.fck == 30
        assert conc.Ec == pytest.approx(5000 * 30**0.5, rel=0.01)
        assert conc.density == 25.0

    def test_concrete_fcm(self):
        conc = Concrete(fck=30)
        assert conc.fcm == 38.0  # fck + 8

    def test_steel_creation(self):
        steel = Steel(fy=500)
        assert steel.fy == 500
        assert steel.Es == 200000.0

    def test_steel_design_stress(self):
        steel = Steel(fy=500)
        assert steel.design_stress == pytest.approx(500 / 1.15, rel=0.01)

    def test_material_factory_is456(self):
        factory = MaterialFactory("IS456")
        conc = factory.concrete(fck=25)
        # IS 456: Ec = 5000 * sqrt(fck)
        assert conc.Ec == pytest.approx(5000 * 25**0.5, rel=0.01)

    def test_material_factory_aci318(self):
        factory = MaterialFactory("ACI318")
        conc = factory.concrete(fck=28)
        # ACI 318: Ec = 4700 * sqrt(fck)
        assert conc.Ec == pytest.approx(4700 * 28**0.5, rel=0.01)

    def test_material_factory_ec2(self):
        factory = MaterialFactory("EC2")
        conc = factory.concrete(fck=30)
        # EC2: Ec = 22000 * (fcm/10)^0.3
        fcm = 30 + 8
        expected = 22000 * ((fcm / 10) ** 0.3)
        assert conc.Ec == pytest.approx(expected, rel=0.01)


class TestRectangularSection:
    """Tests for RectangularSection geometry."""

    def test_creation(self):
        rect = RectangularSection(b=300, D=600)
        assert rect.b == 300
        assert rect.D == 600

    def test_area(self):
        rect = RectangularSection(b=300, D=600)
        assert rect.area == 300 * 600

    def test_centroid(self):
        rect = RectangularSection(b=300, D=600)
        assert rect.centroid_y == 300  # D/2

    def test_moment_of_inertia(self):
        rect = RectangularSection(b=300, D=600)
        expected = 300 * 600**3 / 12
        assert rect.moment_of_inertia == expected

    def test_effective_depth_auto_calculated(self):
        rect = RectangularSection(b=300, D=600, cover=40)
        # d = D - cover - stirrup(8) - bar/2(10)
        expected = 600 - 40 - 8 - 10
        assert rect.d == expected

    def test_effective_depth_explicit(self):
        rect = RectangularSection(b=300, D=600, d=540)
        assert rect.d == 540


class TestTSection:
    """Tests for T-beam geometry."""

    def test_creation(self):
        tsec = TSection(bf=1000, Df=120, bw=300, D=600)
        assert tsec.bf == 1000
        assert tsec.bw == 300

    def test_area(self):
        tsec = TSection(bf=1000, Df=120, bw=300, D=600)
        flange_area = 1000 * 120
        web_area = 300 * (600 - 120)
        expected = flange_area + web_area
        assert tsec.area == expected

    def test_centroid_above_mid_height(self):
        """T-beam centroid should be above mid-height due to flange."""
        tsec = TSection(bf=1000, Df=120, bw=300, D=600)
        assert tsec.centroid_y > 300  # Above mid-height


class TestLSection:
    """Tests for L-beam geometry."""

    def test_creation(self):
        lsec = LSection(bf=650, Df=120, bw=300, D=600)
        assert lsec.bf == 650

    def test_area_less_than_tsection(self):
        """L-section area should be less than equivalent T-section."""
        tsec = TSection(bf=1000, Df=120, bw=300, D=600)
        lsec = LSection(bf=650, Df=120, bw=300, D=600)
        assert lsec.area < tsec.area
