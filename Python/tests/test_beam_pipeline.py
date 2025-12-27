"""
Tests for the beam_pipeline module.

Tests cover:
- Units validation (TASK-061)
- Canonical schema structure (TASK-060)
- Single beam design (TASK-059)
- Multi-beam design
"""

import pytest
from structural_lib import beam_pipeline


class TestUnitsValidation:
    """Tests for units validation at application boundary (TASK-061)."""

    def test_validate_units_is456_valid(self):
        """IS456 units should be accepted."""
        result = beam_pipeline.validate_units("IS456")
        assert result == "IS456"

    def test_validate_units_is_456_space_valid(self):
        """IS 456 with space should be accepted."""
        result = beam_pipeline.validate_units("IS 456")
        assert result == "IS456"

    def test_validate_units_case_insensitive(self):
        """Units validation should be case-insensitive."""
        assert beam_pipeline.validate_units("is456") == "IS456"
        assert beam_pipeline.validate_units("IS456") == "IS456"

    def test_validate_units_mixed_case(self):
        """Mixed case units should be accepted (case-insensitive fix)."""
        assert beam_pipeline.validate_units("Is456") == "IS456"
        assert beam_pipeline.validate_units("iS456") == "IS456"
        assert beam_pipeline.validate_units("Is 456") == "IS456"
        assert beam_pipeline.validate_units("is 456") == "IS456"

    def test_validate_units_alternate_formats(self):
        """Alternate unit format strings should work."""
        # These are accepted per the implementation
        assert beam_pipeline.validate_units("mm,kN,kN-m,N/mm2") == "IS456"
        assert beam_pipeline.validate_units("mm-kN-kNm-Nmm2") == "IS456"

    def test_validate_units_empty_raises(self):
        """Empty units string should raise UnitsValidationError."""
        with pytest.raises(beam_pipeline.UnitsValidationError) as exc_info:
            beam_pipeline.validate_units("")
        assert "required" in str(exc_info.value).lower()

    def test_validate_units_none_raises(self):
        """None units should raise UnitsValidationError."""
        with pytest.raises(beam_pipeline.UnitsValidationError):
            beam_pipeline.validate_units(None)  # type: ignore

    def test_validate_units_invalid_raises(self):
        """Invalid units string should raise UnitsValidationError."""
        with pytest.raises(beam_pipeline.UnitsValidationError) as exc_info:
            beam_pipeline.validate_units("imperial")
        # Should mention what units are accepted
        error_msg = str(exc_info.value).lower()
        assert "expected" in error_msg or "invalid" in error_msg


class TestCanonicalSchema:
    """Tests for canonical BeamDesignOutput schema (TASK-060)."""

    def test_schema_version_is_1(self):
        """Schema version should be 1."""
        assert beam_pipeline.SCHEMA_VERSION == 1

    def test_beam_design_output_has_required_fields(self):
        """BeamDesignOutput should have all required fields."""
        # Check dataclass fields
        import dataclasses

        fields = {f.name for f in dataclasses.fields(beam_pipeline.BeamDesignOutput)}

        required_fields = {
            "schema_version",
            "units",
            "code",
            "geometry",
            "materials",
            "loads",
            "flexure",
            "shear",
            "serviceability",
            "detailing",
            "governing_check",
        }

        assert required_fields.issubset(
            fields
        ), f"Missing fields: {required_fields - fields}"

    def test_geometry_dataclass_has_required_fields(self):
        """BeamGeometry should have dimension fields."""
        import dataclasses

        fields = {f.name for f in dataclasses.fields(beam_pipeline.BeamGeometry)}

        # Using actual field names from implementation
        required_fields = {"b_mm", "D_mm", "d_mm", "cover_mm"}
        assert required_fields.issubset(
            fields
        ), f"Missing fields: {required_fields - fields}"

    def test_materials_dataclass_has_required_fields(self):
        """BeamMaterials should have material property fields."""
        import dataclasses

        fields = {f.name for f in dataclasses.fields(beam_pipeline.BeamMaterials)}

        # Using actual field names from implementation (N/mm2)
        required_fields = {"fck_nmm2", "fy_nmm2"}
        assert required_fields.issubset(
            fields
        ), f"Missing fields: {required_fields - fields}"

    def test_flexure_output_has_required_fields(self):
        """FlexureOutput should have steel area and status fields."""
        import dataclasses

        fields = {f.name for f in dataclasses.fields(beam_pipeline.FlexureOutput)}

        # Using lowercase as per implementation
        required_fields = {"ast_required_mm2", "is_safe"}
        assert required_fields.issubset(
            fields
        ), f"Missing fields: {required_fields - fields}"

    def test_detailing_output_has_ld_fields(self):
        """DetailingOutput should have development length fields."""
        import dataclasses

        fields = {f.name for f in dataclasses.fields(beam_pipeline.DetailingOutput)}

        required_fields = {"ld_tension_mm"}
        assert required_fields.issubset(
            fields
        ), f"Missing fields: {required_fields - fields}"


class TestDesignSingleBeam:
    """Tests for single beam design pipeline (TASK-059)."""

    @pytest.fixture
    def minimal_beam_params(self):
        """Minimal valid beam parameters for testing."""
        return {
            "beam_id": "B1",
            "story": "GF",
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "span_mm": 5000.0,
            "cover_mm": 25.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 415.0,
            "mu_knm": 150.0,
            "vu_kn": 100.0,
        }

    def test_design_single_beam_returns_output_object(self, minimal_beam_params):
        """design_single_beam should return BeamDesignOutput."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert isinstance(result, beam_pipeline.BeamDesignOutput)

    def test_design_single_beam_has_correct_schema_version(self, minimal_beam_params):
        """Output should have schema_version = 1."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.schema_version == 1

    def test_design_single_beam_has_units(self, minimal_beam_params):
        """Output should include the units used."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.units == "IS456"

    def test_design_single_beam_has_code(self, minimal_beam_params):
        """Output should include code = IS456."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.code == "IS456"

    def test_design_single_beam_geometry_populated(self, minimal_beam_params):
        """Geometry fields should be populated from inputs."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.geometry.b_mm == 300.0
        assert result.geometry.D_mm == 500.0
        assert result.geometry.cover_mm == 25.0

    def test_design_single_beam_materials_populated(self, minimal_beam_params):
        """Materials fields should be populated from inputs."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.materials.fck_nmm2 == 25.0
        assert result.materials.fy_nmm2 == 415.0

    def test_design_single_beam_flexure_has_result(self, minimal_beam_params):
        """Flexure result should have ast_required."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.flexure.ast_required_mm2 > 0
        assert hasattr(result.flexure, "is_safe")

    def test_design_single_beam_shear_has_result(self, minimal_beam_params):
        """Shear result should have stirrup specification."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.shear is not None

    def test_design_single_beam_detailing_has_ld(self, minimal_beam_params):
        """Detailing should have development length."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        assert result.detailing.ld_tension_mm > 0

    def test_design_single_beam_invalid_units_raises(self, minimal_beam_params):
        """Invalid units should raise UnitsValidationError."""
        with pytest.raises(beam_pipeline.UnitsValidationError):
            beam_pipeline.design_single_beam(units="imperial", **minimal_beam_params)

    def test_design_single_beam_to_dict_serializable(self, minimal_beam_params):
        """Output should be serializable to dict."""
        result = beam_pipeline.design_single_beam(units="IS456", **minimal_beam_params)
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["schema_version"] == 1
        assert result_dict["units"] == "IS456"
        assert "geometry" in result_dict
        assert "flexure" in result_dict
        assert "detailing" in result_dict


class TestDesignMultipleBeams:
    """Tests for multi-beam design pipeline."""

    @pytest.fixture
    def two_beam_cases(self):
        """Two beam cases for testing."""
        return [
            {
                "beam_id": "B1",
                "story": "GF",
                "b_mm": 300.0,
                "D_mm": 500.0,
                "d_mm": 450.0,
                "span_mm": 5000.0,
                "cover_mm": 25.0,
                "fck_nmm2": 25.0,
                "fy_nmm2": 415.0,
                "mu_knm": 150.0,
                "vu_kn": 100.0,
            },
            {
                "beam_id": "B2",
                "story": "1F",
                "b_mm": 350.0,
                "D_mm": 600.0,
                "d_mm": 550.0,
                "span_mm": 6000.0,
                "cover_mm": 30.0,
                "fck_nmm2": 30.0,
                "fy_nmm2": 500.0,
                "mu_knm": 200.0,
                "vu_kn": 120.0,
            },
        ]

    def test_design_multiple_beams_returns_multi_output(self, two_beam_cases):
        """design_multiple_beams should return MultiBeamOutput."""
        result = beam_pipeline.design_multiple_beams(
            units="IS456", beams=two_beam_cases
        )
        assert isinstance(result, beam_pipeline.MultiBeamOutput)

    def test_design_multiple_beams_has_all_results(self, two_beam_cases):
        """Should have result for each input beam."""
        result = beam_pipeline.design_multiple_beams(
            units="IS456", beams=two_beam_cases
        )
        assert len(result.beams) == 2

    def test_design_multiple_beams_preserves_beam_ids(self, two_beam_cases):
        """Beam IDs should be preserved in results."""
        result = beam_pipeline.design_multiple_beams(
            units="IS456", beams=two_beam_cases
        )
        beam_ids = [r.beam_id for r in result.beams]
        assert "B1" in beam_ids
        assert "B2" in beam_ids

    def test_design_multiple_beams_to_dict_serializable(self, two_beam_cases):
        """Multi-output should be serializable to dict."""
        result = beam_pipeline.design_multiple_beams(
            units="IS456", beams=two_beam_cases
        )
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "beams" in result_dict
        assert len(result_dict["beams"]) == 2
