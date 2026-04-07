"""
Tests for cross-field plausibility validators (TASK-729).

Each Pydantic model with a @model_validator is tested for:
  - Valid inputs accepted without error
  - Invalid cross-field combinations rejected with ValidationError
"""

import pytest
from pydantic import ValidationError

from fastapi_app.models.beam import (
    BeamCheckRequest,
    BeamDesignRequest,
    BeamDetailingRequest,
)
from fastapi_app.models.geometry import (
    BeamGeometryRequest,
    CrossSectionRequest,
)
from fastapi_app.models.analysis import SmartAnalysisRequest
from fastapi_app.models.column import (
    ColumnAxialRequest,
    ColumnUniaxialRequest,
    BiaxialCheckRequest,
    PMInteractionRequest,
    AdditionalMomentRequest,
    LongColumnRequest,
    ColumnDesignRequest,
    HelicalCheckRequest,
)

# =============================================================================
# BeamDesignRequest — effective_depth < depth, clear_cover < depth, depth/width <= 6
# =============================================================================


class TestBeamDesignRequestValidator:
    """Tests for BeamDesignRequest cross-field validators."""

    def test_valid_inputs(self):
        req = BeamDesignRequest(
            width=300,
            depth=500,
            moment=150,
            shear=75,
            fck=25,
            fy=415,
            clear_cover=25,
            effective_depth=450,
        )
        assert req.depth == 500
        assert req.effective_depth == 450

    def test_rejects_effective_depth_gte_depth(self):
        with pytest.raises(ValidationError, match="effective_depth"):
            BeamDesignRequest(
                width=300,
                depth=400,
                moment=100,
                shear=50,
                fck=25,
                fy=415,
                effective_depth=400,
            )

    def test_rejects_effective_depth_gt_depth(self):
        with pytest.raises(ValidationError, match="effective_depth"):
            BeamDesignRequest(
                width=300,
                depth=400,
                moment=100,
                shear=50,
                fck=25,
                fy=415,
                effective_depth=500,
            )

    def test_rejects_clear_cover_gte_depth(self):
        """clear_cover must be < depth. Field constraint ge=20 limits lower bound."""
        with pytest.raises(ValidationError, match="clear_cover"):
            BeamDesignRequest(
                width=300,
                depth=25,
                moment=10,
                shear=5,
                fck=25,
                fy=415,
                clear_cover=25,
            )

    def test_rejects_depth_width_ratio_gt_6(self):
        with pytest.raises(ValidationError, match="[Dd]epth.*width.*ratio"):
            BeamDesignRequest(
                width=100,
                depth=700,
                moment=100,
                shear=50,
                fck=25,
                fy=415,
            )

    def test_none_effective_depth_is_valid(self):
        """effective_depth=None means auto-calculated — should pass."""
        req = BeamDesignRequest(
            width=300,
            depth=500,
            moment=150,
            shear=75,
            fck=25,
            fy=415,
            effective_depth=None,
        )
        assert req.effective_depth is None


# =============================================================================
# BeamCheckRequest — effective_depth < depth, clear_cover < depth
# =============================================================================


class TestBeamCheckRequestValidator:
    """Tests for BeamCheckRequest cross-field validators."""

    def test_valid_inputs(self):
        req = BeamCheckRequest(
            width=230,
            depth=450,
            moment=100,
            shear=50,
            ast_provided=1200,
            fck=25,
            fy=415,
            clear_cover=25,
            effective_depth=400,
        )
        assert req.depth == 450

    def test_rejects_effective_depth_gte_depth(self):
        with pytest.raises(ValidationError, match="effective_depth"):
            BeamCheckRequest(
                width=230,
                depth=400,
                moment=100,
                shear=50,
                ast_provided=1200,
                fck=25,
                fy=415,
                clear_cover=25,
                effective_depth=500,
            )

    def test_rejects_effective_depth_equal_depth(self):
        with pytest.raises(ValidationError, match="effective_depth"):
            BeamCheckRequest(
                width=230,
                depth=400,
                moment=100,
                shear=50,
                ast_provided=1200,
                fck=25,
                fy=415,
                clear_cover=25,
                effective_depth=400,
            )

    def test_rejects_clear_cover_gte_depth(self):
        with pytest.raises(ValidationError, match="clear_cover"):
            BeamCheckRequest(
                width=230,
                depth=25,
                moment=10,
                shear=5,
                ast_provided=600,
                fck=25,
                fy=415,
                clear_cover=25,
            )

    def test_none_effective_depth_passes(self):
        req = BeamCheckRequest(
            width=230,
            depth=450,
            moment=100,
            shear=50,
            ast_provided=1200,
            fck=25,
            fy=415,
            clear_cover=25,
            effective_depth=None,
        )
        assert req.effective_depth is None


# =============================================================================
# BeamDetailingRequest — clear_cover < depth
# =============================================================================


class TestBeamDetailingRequestValidator:
    """Tests for BeamDetailingRequest cross-field validators."""

    def test_valid_inputs(self):
        req = BeamDetailingRequest(
            width=300,
            depth=500,
            ast_required=800,
            fck=25,
            fy=415,
            clear_cover=25,
        )
        assert req.clear_cover == 25

    def test_rejects_clear_cover_gte_depth(self):
        with pytest.raises(ValidationError, match="clear_cover"):
            BeamDetailingRequest(
                width=300,
                depth=25,
                ast_required=400,
                fck=25,
                fy=415,
                clear_cover=25,
            )


# =============================================================================
# BeamGeometryRequest — cover < depth
# =============================================================================


class TestBeamGeometryRequestValidator:
    """Tests for BeamGeometryRequest cross-field validators."""

    def test_valid_inputs(self):
        req = BeamGeometryRequest(
            beam_id="B1",
            story="GF",
            width=300,
            depth=500,
            span=6000,
            fck=25,
            fy=415,
            cover=40,
        )
        assert req.cover == 40

    def test_rejects_cover_gte_depth(self):
        with pytest.raises(ValidationError, match="cover"):
            BeamGeometryRequest(
                beam_id="B1",
                story="GF",
                width=300,
                depth=40,
                span=6000,
                fck=25,
                fy=415,
                cover=40,
            )

    def test_rejects_cover_gt_depth(self):
        with pytest.raises(ValidationError, match="cover"):
            BeamGeometryRequest(
                beam_id="B1",
                story="GF",
                width=300,
                depth=30,
                span=6000,
                fck=25,
                fy=415,
                cover=40,
            )


# =============================================================================
# CrossSectionRequest — cover < depth/2
# =============================================================================


class TestCrossSectionRequestValidator:
    """Tests for CrossSectionRequest cross-field validators."""

    def test_valid_inputs(self):
        req = CrossSectionRequest(
            width=300,
            depth=500,
            cover=40,
            tension_bars=3,
            compression_bars=2,
        )
        assert req.cover == 40

    def test_rejects_cover_gte_half_depth(self):
        with pytest.raises(ValidationError, match="cover"):
            CrossSectionRequest(
                width=300,
                depth=80,
                cover=40,
                tension_bars=3,
                compression_bars=2,
            )

    def test_cover_just_below_half_depth_passes(self):
        req = CrossSectionRequest(
            width=300,
            depth=500,
            cover=70,
            tension_bars=3,
            compression_bars=2,
        )
        assert req.cover == 70


# =============================================================================
# SmartAnalysisRequest — depth/width <= 6
# =============================================================================


class TestSmartAnalysisRequestValidator:
    """Tests for SmartAnalysisRequest cross-field validators."""

    def test_valid_inputs(self):
        req = SmartAnalysisRequest(
            width=300,
            depth=500,
            moment=150,
            shear=75,
            fck=25,
            fy=415,
        )
        assert req.depth == 500

    def test_rejects_depth_width_ratio_gt_6(self):
        with pytest.raises(ValidationError, match="[Dd]epth.*width.*ratio"):
            SmartAnalysisRequest(
                width=100,
                depth=700,
                moment=100,
                shear=50,
                fck=25,
                fy=415,
            )

    def test_depth_width_ratio_at_6_passes(self):
        req = SmartAnalysisRequest(
            width=100,
            depth=600,
            moment=100,
            shear=50,
            fck=25,
            fy=415,
        )
        assert req.depth == 600


# =============================================================================
# ColumnAxialRequest — Asc_mm2 < Ag_mm2
# =============================================================================


class TestColumnAxialRequestValidator:
    """Tests for ColumnAxialRequest cross-field validators."""

    def test_valid_inputs(self):
        req = ColumnAxialRequest(fck=25, fy=415, Ag_mm2=120000, Asc_mm2=1885)
        assert req.Ag_mm2 == 120000

    def test_rejects_asc_gte_ag(self):
        with pytest.raises(ValidationError, match="Asc_mm2"):
            ColumnAxialRequest(fck=25, fy=415, Ag_mm2=1000, Asc_mm2=1000)

    def test_rejects_asc_gt_ag(self):
        with pytest.raises(ValidationError, match="Asc_mm2"):
            ColumnAxialRequest(fck=25, fy=415, Ag_mm2=1000, Asc_mm2=2000)


# =============================================================================
# ColumnUniaxialRequest — d_prime_mm < D_mm/2
# =============================================================================


class TestColumnUniaxialRequestValidator:
    """Tests for ColumnUniaxialRequest cross-field validators."""

    def test_valid_inputs(self):
        req = ColumnUniaxialRequest(
            Pu_kN=1200,
            Mu_kNm=150,
            b_mm=300,
            D_mm=400,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=2700,
            d_prime_mm=50,
        )
        assert req.d_prime_mm == 50

    def test_rejects_d_prime_gte_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            ColumnUniaxialRequest(
                Pu_kN=1200,
                Mu_kNm=150,
                b_mm=300,
                D_mm=400,
                le_mm=3000,
                fck=25,
                fy=415,
                Asc_mm2=2700,
                d_prime_mm=200,
            )

    def test_rejects_d_prime_equal_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            ColumnUniaxialRequest(
                Pu_kN=1200,
                Mu_kNm=150,
                b_mm=300,
                D_mm=400,
                le_mm=3000,
                fck=25,
                fy=415,
                Asc_mm2=2700,
                d_prime_mm=200,
            )


# =============================================================================
# BiaxialCheckRequest — d_prime_mm < D_mm/2
# =============================================================================


class TestBiaxialCheckRequestValidator:
    """Tests for BiaxialCheckRequest cross-field validators."""

    def test_valid_inputs(self):
        req = BiaxialCheckRequest(
            Pu_kN=1500,
            Mux_kNm=120,
            Muy_kNm=80,
            b_mm=300,
            D_mm=400,
            le_mm=3000,
            fck=25,
            fy=415,
            Asc_mm2=2400,
            d_prime_mm=50,
        )
        assert req.d_prime_mm == 50

    def test_rejects_d_prime_gte_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            BiaxialCheckRequest(
                Pu_kN=1500,
                Mux_kNm=120,
                Muy_kNm=80,
                b_mm=300,
                D_mm=400,
                le_mm=3000,
                fck=25,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=200,
            )


# =============================================================================
# PMInteractionRequest — d_prime_mm < D_mm/2
# =============================================================================


class TestPMInteractionRequestValidator:
    """Tests for PMInteractionRequest cross-field validators."""

    def test_valid_inputs(self):
        req = PMInteractionRequest(
            b_mm=300,
            D_mm=400,
            fck=25,
            fy=415,
            Asc_mm2=2400,
            d_prime_mm=50,
        )
        assert req.d_prime_mm == 50

    def test_rejects_d_prime_gte_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            PMInteractionRequest(
                b_mm=300,
                D_mm=400,
                fck=25,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=200,
            )


# =============================================================================
# AdditionalMomentRequest — d_prime_mm < D_mm/2, fck >= 15, fy >= 250
# =============================================================================


class TestAdditionalMomentRequestValidator:
    """Tests for AdditionalMomentRequest cross-field validators."""

    def test_valid_inputs(self):
        req = AdditionalMomentRequest(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            fck=25,
            fy=415,
            Asc_mm2=2400,
            d_prime_mm=50,
        )
        assert req.d_prime_mm == 50

    def test_rejects_d_prime_gte_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            AdditionalMomentRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                fck=25,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=225,
            )

    def test_rejects_fck_below_15(self):
        with pytest.raises(ValidationError, match="fck"):
            AdditionalMomentRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                fck=10,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=50,
            )

    def test_rejects_fy_below_250(self):
        with pytest.raises(ValidationError, match="fy"):
            AdditionalMomentRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                fck=25,
                fy=200,
                Asc_mm2=2400,
                d_prime_mm=50,
            )


# =============================================================================
# LongColumnRequest — d_prime_mm < D_mm/2, fck >= 15, fy >= 250
# =============================================================================


class TestLongColumnRequestValidator:
    """Tests for LongColumnRequest cross-field validators."""

    def test_valid_inputs(self):
        req = LongColumnRequest(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            fck=25,
            fy=415,
            Asc_mm2=2400,
            d_prime_mm=50,
        )
        assert req.d_prime_mm == 50

    def test_rejects_d_prime_gte_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            LongColumnRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                fck=25,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=225,
            )

    def test_rejects_fck_below_15(self):
        with pytest.raises(ValidationError, match="fck"):
            LongColumnRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                fck=10,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=50,
            )

    def test_rejects_fy_below_250(self):
        with pytest.raises(ValidationError, match="fy"):
            LongColumnRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                fck=25,
                fy=200,
                Asc_mm2=2400,
                d_prime_mm=50,
            )


# =============================================================================
# ColumnDesignRequest — d_prime_mm < D_mm/2, fck >= 15, fy >= 250
# =============================================================================


class TestColumnDesignRequestValidator:
    """Tests for ColumnDesignRequest cross-field validators."""

    def test_valid_inputs(self):
        req = ColumnDesignRequest(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            l_mm=3500,
            end_condition="FIXED_FIXED",
            fck=25,
            fy=415,
            Asc_mm2=2400,
            d_prime_mm=50,
        )
        assert req.d_prime_mm == 50

    def test_rejects_d_prime_gte_half_D(self):
        with pytest.raises(ValidationError, match="d_prime_mm"):
            ColumnDesignRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                l_mm=3500,
                end_condition="FIXED_FIXED",
                fck=25,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=225,
            )

    def test_rejects_fck_below_15(self):
        with pytest.raises(ValidationError, match="fck"):
            ColumnDesignRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                l_mm=3500,
                end_condition="FIXED_FIXED",
                fck=10,
                fy=415,
                Asc_mm2=2400,
                d_prime_mm=50,
            )

    def test_rejects_fy_below_250(self):
        with pytest.raises(ValidationError, match="fy"):
            ColumnDesignRequest(
                Pu_kN=1500,
                b_mm=300,
                D_mm=450,
                l_mm=3500,
                end_condition="FIXED_FIXED",
                fck=25,
                fy=200,
                Asc_mm2=2400,
                d_prime_mm=50,
            )


# =============================================================================
# HelicalCheckRequest — D_core_mm < D_mm, fck >= 15, fy >= 250
# =============================================================================


class TestHelicalCheckRequestValidator:
    """Tests for HelicalCheckRequest cross-field validators."""

    def test_valid_inputs(self):
        req = HelicalCheckRequest(
            D_mm=450,
            D_core_mm=350,
            fck=25,
            fy=415,
            d_helix_mm=8,
            pitch_mm=50,
            Pu_axial_kN=2000,
        )
        assert req.D_core_mm == 350

    def test_rejects_d_core_gte_d(self):
        with pytest.raises(ValidationError, match="D_core_mm"):
            HelicalCheckRequest(
                D_mm=450,
                D_core_mm=450,
                fck=25,
                fy=415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=2000,
            )

    def test_rejects_d_core_gt_d(self):
        with pytest.raises(ValidationError, match="D_core_mm"):
            HelicalCheckRequest(
                D_mm=350,
                D_core_mm=450,
                fck=25,
                fy=415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=2000,
            )

    def test_rejects_fck_below_15(self):
        with pytest.raises(ValidationError, match="fck"):
            HelicalCheckRequest(
                D_mm=450,
                D_core_mm=350,
                fck=10,
                fy=415,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=2000,
            )

    def test_rejects_fy_below_250(self):
        with pytest.raises(ValidationError, match="fy"):
            HelicalCheckRequest(
                D_mm=450,
                D_core_mm=350,
                fck=25,
                fy=200,
                d_helix_mm=8,
                pitch_mm=50,
                Pu_axial_kN=2000,
            )
