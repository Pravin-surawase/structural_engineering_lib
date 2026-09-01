"""Source-based W3 regressions through real canonical and audit consumers.

IS 456:2000 Cl 26.5.1.6, 40.4, 41.4.2 and 41.4.3.
All inputs are authored software fixtures, not the actual ETABS building.
"""

import json
import math

import pytest

from structural_lib.codes.is456.beam import shear, torsion
from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam
from structural_lib.services import beam_audit
from structural_lib.services.bbs import parse_bar_mark
from tests.unit.test_beam_audit import _evaluate, _request
from tests.unit.test_etabs_w3_contracts import _present


def _canonical_payload():
    return {
        "identity": {"member_id": "authored:1", "story": "GF", "case_id": "ULS"},
        "section": {
            "span_mm": 3000,
            "b_mm": 300,
            "D_mm": 500,
            "effective_depth_basis": {"centroid_cover_mm": 58},
        },
        "materials": {"fck_nmm2": 25, "fy_nmm2": 500, "fy_transverse_nmm2": 415},
        "actions": {"mu_knm": 5, "vu_kn": 25, "tu_knm": 30},
        "calculation_basis": {
            "d_dash_mm": 56,
            "asv_mm2": 32 * math.pi,
            "pt_percent": 1.0,
        },
        "detailing": {
            "standard": "IS456",
            "clear_cover_mm": 40,
            "tension_bar_diameter_mm": 20,
            "compression_bar_diameter_mm": 16,
            "side_face_bar_diameter_mm": 16,
            "nominal_top_steel_ratio": 0.25,
            "stirrup_diameter_mm": 8,
            "stirrup_legs": 2,
            "stirrup_spacing_support_mm": 75,
            "stirrup_spacing_mid_mm": 75,
        },
        "source_provenance": "authored clause check; not installed reinforcement",
    }


def test_centroid_cover_and_separate_grades_survive_real_journey():
    request = beam.load(_canonical_payload())
    assert request.section.resolved_d_mm() == 442
    result = beam.check(request)
    data = result.to_dict()
    assert data["request"]["materials"]["fy_nmm2"] == 500
    assert data["request"]["materials"]["fy_transverse_nmm2"] == 415
    assert data["calculation"]["effective_depth_resolution"][
        "effective_depth_basis"
    ] == {"centroid_cover_mm": 58}
    assert data["request"]["detailing"]["clear_cover_mm"] == 40
    assert result.calculation.torsion.corner_bar_centres_mm == (184, 386)
    assert result.calculation.torsion.Me_opposite_knm == pytest.approx(42.0588235294)
    # Opposite-face tension stays distinct from compression steel.
    assert result.calculation.flexure.Asc_required == 0
    assert result.calculation.torsion.Ast_opposite_mm2 > 0
    assert result.is_ok
    detailed = beam.detail(result, detailing_standard=beam.DetailingStandard.IS456)
    assert detailed.is_ok
    assert detailed.detailing.torsion is not None
    assert detailed.detailing.torsion.primary_tension_face == "BOTTOM"
    assert detailed.detailing.torsion.primary_area_required == pytest.approx(
        result.calculation.flexure.Ast_required
    )
    assert detailed.detailing.torsion.opposite_area_required == pytest.approx(
        result.calculation.torsion.Ast_opposite_mm2
    )
    assert all(item.callout() == "2-20φ" for item in detailed.detailing.bottom_bars)
    assert all(item.callout() == "2-16φ" for item in detailed.detailing.top_bars)
    side = detailed.detailing.torsion.side_face_bars
    assert side is not None
    assert side.callout() == "1-16φ/face"
    assert side.area_provided_each_face >= side.area_required_each_face
    assert side.spacing <= side.max_spacing
    bbs = beam.bbs(detailed)
    bottom_items = [item for item in bbs.items if item.location == "bottom"]
    top_items = [item for item in bbs.items if item.location == "top"]
    assert len(bottom_items) == 1 and bottom_items[0].zone == "full"
    assert len(top_items) == 1 and top_items[0].zone == "full"
    side_items = [item for item in bbs.items if item.location == "side-face"]
    assert len(side_items) == 1
    assert side_items[0].zone == "full"
    assert side_items[0].no_of_bars == 2
    assert "-F-F-D16-" in side_items[0].bar_mark
    parsed_mark = parse_bar_mark(side_items[0].bar_mark)
    assert parsed_mark is not None
    assert parsed_mark["loc"] == "F"
    assert bbs.summary.total_items == 6
    assert beam.load(json.loads(request.model_dump_json())) == request


def test_top_primary_face_is_preserved_through_detailing_and_bbs():
    payload = _canonical_payload()
    payload["section"]["b_mm"] = 230
    payload["section"]["D_mm"] = 450
    payload["section"]["effective_depth_basis"] = {"centroid_cover_mm": 58}
    payload["actions"]["tu_knm"] = 10
    payload["actions"]["primary_tension_face"] = "TOP"
    payload["detailing"].pop("side_face_bar_diameter_mm")
    request = beam.load(payload)
    strength = beam.check(request)
    detailed = beam.detail(strength, detailing_standard=beam.DetailingStandard.IS456)
    assert detailed.detailing.torsion is not None
    assert detailed.detailing.torsion.primary_tension_face == "TOP"
    assert all(item.callout() == "2-20φ" for item in detailed.detailing.top_bars)
    assert all(item.callout() == "2-16φ" for item in detailed.detailing.bottom_bars)
    bbs = beam.bbs(detailed)
    bottom_items = [item for item in bbs.items if item.location == "bottom"]
    top_items = [item for item in bbs.items if item.location == "top"]
    assert len(bottom_items) == 1 and bottom_items[0].diameter_mm == 16
    assert len(top_items) == 1 and top_items[0].diameter_mm == 20
    assert bbs.summary.total_items == 5


def test_torsion_strength_stays_available_when_side_face_detailing_choice_is_missing():
    payload = _canonical_payload()
    payload["detailing"].pop("side_face_bar_diameter_mm")
    result = beam.design(beam.load(payload))
    assert result.is_ok
    with pytest.raises(InputContractError) as exc_info:
        beam.detail(result, detailing_standard=beam.DetailingStandard.IS456)
    assert exc_info.value.issues[0].path.endswith("side_face_bar_diameter_mm")
    assert "TORSION_SIDE_FACE_BAR_REQUIRED" in exc_info.value.issues[0].message


@pytest.mark.parametrize(
    ("mutation", "path", "message"),
    [
        (
            lambda payload: payload["section"].update({"b_mm": 500}),
            "request.section.b_mm",
            "TORSION_DETAILING_SECTION_UNSUPPORTED",
        ),
        (
            lambda payload: payload["detailing"].update(
                {"stirrup_spacing_mid_mm": 100}
            ),
            "request.detailing.stirrup_spacing_mid_mm",
            "TORSION_STIRRUP_SPACING_EXCEEDED",
        ),
    ],
)
def test_torsion_detailing_applicability_fails_closed(mutation, path, message):
    payload = _canonical_payload()
    mutation(payload)
    result = beam.design(beam.load(payload))
    with pytest.raises(InputContractError) as exc_info:
        beam.detail(result, detailing_standard=beam.DetailingStandard.IS456)
    assert exc_info.value.issues[0].path == path
    assert message in exc_info.value.issues[0].message


def test_etabs_40_centroid_is_not_40_clear_cover():
    payload = _canonical_payload()
    payload["actions"]["tu_knm"] = 0
    payload["section"]["effective_depth_basis"] = {"centroid_cover_mm": 40}
    with pytest.raises(InputContractError, match="centroid cover conflicts"):
        beam.load(payload)
    payload.pop("detailing")
    result = beam.design(beam.load(payload))
    assert result.calculation.effective_depth_resolution["d_mm"] == 460


def test_invalid_derived_depth_is_rejected_at_intake():
    payload = _canonical_payload()
    payload["section"]["effective_depth_basis"] = {"centroid_cover_mm": 500}
    with pytest.raises(InputContractError):
        beam.load(payload)


def test_shear_cap_and_constructibility_are_decisive():
    args = {"vu_kn": 150, "b": 300, "d": 442, "fck": 25, "pt": 1.0, "asv": 100}
    # tc=0.64 => Vus=65.136 kN. At capped fy=415, sv=245.002 mm => 225 mm.
    for fy in (415, 500):
        result = shear.design_shear(**args, fy=fy)
        assert result.Vus == pytest.approx(65.136)
        assert result.spacing == 225
    result = shear.design_shear(**{**args, "vu_kn": 300}, fy=250)
    assert not result.is_safe
    assert result.spacing == 0
    assert result.errors[0].code == "SHEAR_SPACING_NOT_CONSTRUCTIBLE"


def test_torsion_equation_and_equivalent_stress_floor_independently():
    # Published 41.4.3 uses total Vu/(2.5*d1*.87*fy), even below Vc.
    at, av, total = torsion.calculate_torsion_stirrup_area(
        10, 50, 300, 450, 200, 400, 415, 0.64
    )
    assert at == pytest.approx(0.34621243595)
    assert av == pytest.approx(0.13848497438)
    assert total == pytest.approx(0.48469741033)
    # High Vu makes the equivalent-stress lower bound govern, not the sum.
    at, av, total = torsion.calculate_torsion_stirrup_area(
        10, 250, 300, 450, 200, 400, 415, 0.64
    )
    assert total == pytest.approx(1.33520031595)
    assert total > at + av


def test_torsion_does_not_invent_longitudinal_geometry_or_steel():
    with pytest.raises(ValueError, match="TORSION_CORNER_GEOMETRY_REQUIRED"):
        torsion.design_torsion(10, 100, 150, 300, 500, 450, 25, 500, 40)
    with pytest.raises(ValueError, match="TORSION_LONGITUDINAL_BASIS_REQUIRED"):
        torsion.calculate_longitudinal_torsion_steel(10, 100, 200, 400, 500, 150)


def test_transverse_grade_changes_stirrups_and_evidence_not_longitudinal_flexure():
    payload = _canonical_payload()
    original = beam.design(beam.load(payload))
    payload["materials"]["fy_transverse_nmm2"] = 250
    changed = beam.design(beam.load(payload))
    assert (
        changed.calculation.flexure.Ast_required
        == original.calculation.flexure.Ast_required
    )
    assert (
        changed.calculation.torsion.Asv_total > original.calculation.torsion.Asv_total
    )
    assert (
        changed.calculation.result_envelope["result_identity"]["input_hash"]
        != original.calculation.result_envelope["result_identity"]["input_hash"]
    )


def test_w3_audit_retains_mixed_material_and_centroid_basis():
    request = _request()
    source = request.member_bases[0]
    basis = source.model_copy(
        update={
            "materials": _present(
                beam.IS456ReinforcementMaterialsV1(
                    fck_nmm2=25, fy_nmm2=500, fy_transverse_nmm2=415
                )
            ),
            "section": _present(
                beam.RectangularBeamSectionV1(
                    b_mm=300,
                    D_mm=500,
                    span_mm=3000,
                    effective_depth_basis=beam.CentroidCoverDepthRequestV1(
                        centroid_cover_mm=58
                    ),
                )
            ),
            "calculation_basis": _present(
                source.calculation_basis.value.model_copy(update={"d_dash_mm": 56.0})
            ),
        }
    )
    updated = beam_audit.BeamAuditInputBuildRequestV1.model_validate(
        {**request.model_dump(), "member_bases": (basis,)}
    )
    result = _evaluate(updated)
    assert len(result.rows) == 3
    for row in result.rows:
        assert row.input.canonical_request.materials.fy_transverse_nmm2 == 415
        assert json.loads(row.canonical_result_json)["request"]["section"][
            "effective_depth_basis"
        ] == {"centroid_cover_mm": 58}
    assert _evaluate(updated) == result


def test_legacy_single_grade_and_clear_cover_shape_remains_unchanged():
    payload = _canonical_payload()
    payload["actions"]["tu_knm"] = 0
    payload["materials"].pop("fy_transverse_nmm2")
    payload["section"]["effective_depth_basis"] = {
        "clear_cover_mm": 40,
        "stirrup_diameter_mm": 8,
        "tension_bar_diameter_mm": 20,
    }
    request = beam.load(payload)
    assert type(request.materials) is beam.IS456MaterialsV1
    assert request.model_dump()["materials"] == {"fck_nmm2": 25, "fy_nmm2": 500}
    assert request.section.resolved_d_mm() == 442
    assert beam.design(request).calculation.torsion is None
