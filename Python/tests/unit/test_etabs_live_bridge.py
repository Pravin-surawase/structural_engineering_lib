"""Deterministic tests for the optional live ETABS beam-pilot service."""

# ruff: noqa: N802 - fakes intentionally mirror the ETABS COM method names.

from __future__ import annotations

from contextlib import contextmanager

import pytest

from structural_lib.services import etabs_live_bridge as bridge


def _design_basis(*, with_provenance: bool = True) -> bridge.ETABSPilotDesignBasisV1:
    audit_provenance = (
        {
            "model_identity_sha256": "1" * 64,
            "baseline_sha256": "2" * 64,
            "catalogue_sha256": "3" * 64,
            "selection_id": "selection:uls",
            "scenario_id": "scenario:pilot-strength",
            "local_axis_basis": "Retained ETABS frame local axes; no transformation.",
            "factored_action_basis": "Explicit synthetic ULS fixture.",
            "max_abs_axial_kn": 1.0,
            "max_abs_minor_shear_kn": 10.0,
            "max_abs_minor_moment_knm": 25.0,
            "positive_m3_tension_face": "BOTTOM",
            "negative_m3_tension_face": "TOP",
            "source_references": ("synthetic:pilot-provenance",),
        }
        if with_provenance
        else None
    )
    return bridge.ETABSPilotDesignBasisV1.model_validate(
        {
            "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
            "effective_depth_basis": {
                "clear_cover_mm": 40.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 20.0,
            },
            "d_dash_mm": 40.0,
            "detailing": {
                "standard": "IS456",
                "clear_cover_mm": 40.0,
                "tension_bar_diameter_mm": 20.0,
                "compression_bar_diameter_mm": 16.0,
                "nominal_top_steel_ratio": 0.25,
                "stirrup_diameter_mm": 8.0,
                "stirrup_legs": 2,
                "stirrup_spacing_support_mm": 150.0,
                "stirrup_spacing_mid_mm": 200.0,
            },
            "audit_provenance": audit_provenance,
        }
    )


def _request(
    *, limit: int = 2, with_provenance: bool = True
) -> bridge.ETABSPilotRequestV1:
    return bridge.ETABSPilotRequestV1(
        result_selection=bridge.ETABSResultSelectionV1(
            kind=bridge.ETABSResultSelectionKind.COMBINATION,
            name="117.(1.5DL+1.5LL)",
        ),
        design_basis=_design_basis(with_provenance=with_provenance),
        limit=limit,
    )


class _FakeSetup:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def DeselectAllCasesAndCombosForOutput(self):
        self.calls.append(("deselect",))
        return 0

    def SetComboSelectedForOutput(self, name, selected):
        self.calls.append(("combo", name, selected))
        return 0

    def SetCaseSelectedForOutput(self, name, selected):
        self.calls.append(("case", name, selected))
        return 0


class _FakeResults:
    def __init__(self, output_container=tuple) -> None:
        self.Setup = _FakeSetup()
        self.output_container = output_container
        self.torsion_values = (1000.0, -1500.0, 500.0)
        self.m3_values = (-150_000.0, 120_000.0, 100_000.0)

    def FrameForce(self, frame_name, item_type):
        assert item_type == 0
        outputs = (
            3,
            (frame_name,) * 3,
            (0.0, 2500.0, 5000.0),
            (f"E-{frame_name}",) * 3,
            (0.0, 2500.0, 5000.0),
            ("117.(1.5DL+1.5LL)",) * 3,
            ("Max", "Max", "Min"),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (80.0, -110.0, 90.0),
            (5.0, 4.0, -6.0),
            self.torsion_values,
            (10_000.0, 20_000.0, -15_000.0),
            self.m3_values,
            0,
        )
        return self.output_container(outputs)


class _FakeFrameObj:
    def __init__(self, output_container=tuple) -> None:
        self.output_container = output_container

    def GetAllFrames(self):
        # Installed ETABS exposes CSys="Global" as the optional final input;
        # callers omit all preceding COM output parameters and use that default.
        # B2 is intentionally listed first; deterministic story/name sorting picks B1.
        outputs = (
            3,
            ("B2", "C1", "B1"),
            ("R300x500", "R400x400", "R300x500"),
            ("L2", "L1", "L1"),
            ("P3", "P5", "P1"),
            ("P4", "P6", "P2"),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (3000.0, 0.0, 0.0),
            (5000.0, 0.0, 5000.0),
            (0.0, 0.0, 0.0),
            (3000.0, 3000.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (5, 5, 5),
            0,
        )
        return self.output_container(outputs)


class _FakePropFrame:
    def __init__(self, output_container=tuple) -> None:
        self.output_container = output_container

    def GetRectangle(self, name):
        assert name == "R300x500"
        return self.output_container(("", "M25", 500.0, 300.0, 1, "", "guid", 0))


class _FakeSapModel:
    def __init__(
        self,
        output_container=tuple,
        *,
        model_filename: str = r"C:\Models\Pilot Copy.EDB",
    ) -> None:
        self.output_container = output_container
        self.model_filename = model_filename
        self.FrameObj = _FakeFrameObj(output_container)
        self.PropFrame = _FakePropFrame(output_container)
        self.Results = _FakeResults(output_container)
        self.unit_calls: list[int] = []
        self.model_filename_calls: list[bool] = []
        self.model_filepath_calls = 0

    def GetModelFilepath(self):
        self.model_filepath_calls += 1
        return "C:\\Models\\"

    def GetModelFilename(self, include_path):
        self.model_filename_calls.append(include_path)
        return self.model_filename

    def GetVersion(self):
        return self.output_container(("ETABS 23.3.1", 23.31, 0))

    def GetPresentUnits(self):
        return 6

    def SetPresentUnits(self, units):
        self.unit_calls.append(units)
        return 0


class _FakeSession:
    def __init__(self, sap_model: _FakeSapModel) -> None:
        self.sap_model = sap_model
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.closed = True

    @contextmanager
    def normalized_kn_mm_units(self):
        original = self.sap_model.GetPresentUnits()
        assert self.sap_model.SetPresentUnits(5) == 0
        try:
            yield
        finally:
            assert self.sap_model.SetPresentUnits(original) == 0


@pytest.mark.parametrize("output_container", [tuple, list], ids=["tuple", "list"])
def test_zero_torsion_pilot_preserves_sorted_beams_stations_and_units(
    monkeypatch, output_container
):
    sap_model = _FakeSapModel(output_container)
    # Pilot includes detailing, which deliberately excludes torsion distribution.
    sap_model.Results.torsion_values = (0.0, 0.0, 0.0)
    session = _FakeSession(sap_model)
    monkeypatch.setattr(bridge, "_library_identity", lambda: ("0.24.0", "a" * 64))

    result = bridge.run_etabs_beam_pilot_v1(_request(), session_factory=lambda: session)

    assert result.model.model_name == "Pilot Copy.EDB"
    assert result.model.model_path == r"C:\Models\Pilot Copy.EDB"
    assert result.candidate_beam_count == 2
    assert result.designed_beam_count == 2
    assert [item.geometry.frame_name for item in result.beams] == ["B1", "B2"]
    assert result.beams[0].geometry.b_mm == 300.0
    assert result.beams[0].geometry.D_mm == 500.0
    assert result.beams[0].forces.result_row_count == 3
    assert result.beams[0].forces.governing_v2.signed_value == -110.0
    assert result.beams[0].forces.governing_m3.signed_value == -150.0
    assert result.beams[0].forces.governing_t.absolute_value == 0.0
    delegated = result.beams[0].design_result
    assert delegated["compatibility_status"] == "DELEGATED"
    assert delegated["tension_face"] == "TOP"
    assert delegated["same_row_actions"] == {
        "p_kn": 0.0,
        "v2_kn": 80.0,
        "v3_kn": 5.0,
        "t_knm": 0.0,
        "m2_knm": 10.0,
        "m3_knm": -150.0,
    }
    canonical_actions = delegated["audit_evaluation"]["row"]["input"][
        "canonical_request"
    ]["actions"]
    assert canonical_actions["mu_knm"] == 150.0
    assert canonical_actions["vu_kn"] == 80.0
    assert canonical_actions["primary_tension_face"] == "TOP"
    assert result.held_beam_count == 0
    assert result.calculation_owner == "beam-audit-row/v1"
    assert sap_model.unit_calls == [5, 6]
    assert sap_model.Results.Setup.calls == [
        ("deselect",),
        ("combo", "117.(1.5DL+1.5LL)", True),
    ]
    assert sap_model.model_filename_calls == [True]
    assert sap_model.model_filepath_calls == 0
    assert session.closed is True


def test_positive_and_negative_m3_map_to_opposite_physical_faces(monkeypatch):
    negative_model = _FakeSapModel()
    negative_model.Results.torsion_values = (0.0, 0.0, 0.0)
    positive_model = _FakeSapModel()
    positive_model.Results.torsion_values = (0.0, 0.0, 0.0)
    positive_model.Results.m3_values = (150_000.0, -120_000.0, -100_000.0)
    monkeypatch.setattr(bridge, "_library_identity", lambda: ("0.24.0", "a" * 64))

    negative = bridge.run_etabs_beam_pilot_v1(
        _request(limit=1),
        session_factory=lambda: _FakeSession(negative_model),
    )
    positive = bridge.run_etabs_beam_pilot_v1(
        _request(limit=1),
        session_factory=lambda: _FakeSession(positive_model),
    )

    negative_result = negative.beams[0].design_result
    positive_result = positive.beams[0].design_result
    assert negative_result["tension_face"] == "TOP"
    assert positive_result["tension_face"] == "BOTTOM"
    assert negative_result["same_row_actions"]["m3_knm"] == -150.0
    assert positive_result["same_row_actions"]["m3_knm"] == 150.0
    assert (
        negative_result["audit_evaluation"]["row"]["input"]["canonical_request"][
            "actions"
        ]["mu_knm"]
        == positive_result["audit_evaluation"]["row"]["input"]["canonical_request"][
            "actions"
        ]["mu_knm"]
        == 150.0
    )


def test_missing_signed_face_provenance_holds_without_design(monkeypatch):
    sap_model = _FakeSapModel()
    session = _FakeSession(sap_model)
    monkeypatch.setattr(bridge, "_library_identity", lambda: ("0.24.0", "a" * 64))

    result = bridge.run_etabs_beam_pilot_v1(
        _request(limit=1, with_provenance=False),
        session_factory=lambda: session,
    )

    assert result.pilot_status == "HELD"
    assert result.designed_beam_count == 0
    assert result.held_beam_count == 1
    assert result.beams[0].design_result["compatibility_status"] == "HELD"
    assert result.beams[0].design_result["issues"][0]["code"] == (
        "ETABS_PILOT_FACE_PROVENANCE_REQUIRED"
    )


def test_pilot_limit_is_enforced_before_etabs_calls():
    with pytest.raises(ValueError):
        bridge.ETABSPilotRequestV1(
            result_selection=bridge.ETABSResultSelectionV1(
                kind=bridge.ETABSResultSelectionKind.CASE,
                name="DEAD",
            ),
            design_basis=_design_basis(),
            limit=6,
        )


def test_status_is_truthful_on_non_windows(monkeypatch):
    monkeypatch.setattr(bridge.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(bridge, "_library_identity", lambda: ("0.24.0", "b" * 64))

    status = bridge.get_etabs_bridge_status_v1()

    assert status.bridge_status == "PLATFORM_UNSUPPORTED"
    assert status.com_dependency == "NOT_APPLICABLE"
    assert status.model is None


def test_com_signature_mismatch_is_a_stable_data_error():
    with pytest.raises(bridge.ETABSDataError) as exc_info:
        bridge._decode_com_outputs("FrameObj.GetAllFrames", (1, 0), output_count=20)
    assert exc_info.value.code == "ETABS_COM_SIGNATURE_MISMATCH"


@pytest.mark.parametrize("output_container", [tuple, list], ids=["tuple", "list"])
def test_connect_returns_exact_open_model_without_unit_change(
    monkeypatch, output_container
):
    sap_model = _FakeSapModel(output_container)
    session = _FakeSession(sap_model)
    monkeypatch.setattr(bridge, "_library_identity", lambda: ("0.24.0", "c" * 64))

    result = bridge.connect_etabs_v1(session_factory=lambda: session)

    assert result.bridge_status == "CONNECTED"
    assert result.model.model_name == "Pilot Copy.EDB"
    assert result.model.model_path == r"C:\Models\Pilot Copy.EDB"
    assert result.model.etabs_version == "ETABS 23.3.1"
    assert sap_model.model_filename_calls == [True]
    assert sap_model.model_filepath_calls == 0
    assert sap_model.unit_calls == []
    assert session.closed is True


@pytest.mark.parametrize(
    ("model_filename", "expected_code"),
    [
        ("", "ETABS_MODEL_PATH_MISSING"),
        ("C:\\Models\\", "ETABS_MODEL_PATH_INVALID"),
        ("Pilot Copy.edb", "ETABS_MODEL_PATH_INVALID"),
        (r"C:\Models\Pilot Copy.e2k", "ETABS_MODEL_PATH_INVALID"),
    ],
)
def test_connect_rejects_missing_or_non_edb_model_identity(
    model_filename, expected_code
):
    sap_model = _FakeSapModel(model_filename=model_filename)
    session = _FakeSession(sap_model)

    with pytest.raises(bridge.ETABSConnectionError) as exc_info:
        bridge.connect_etabs_v1(session_factory=lambda: session)

    assert exc_info.value.code == expected_code
    assert sap_model.model_filename_calls == [True]
    assert sap_model.model_filepath_calls == 0
    assert session.closed is True


def test_real_session_unit_context_restores_units_after_extraction_failure():
    sap_model = _FakeSapModel()
    session = object.__new__(bridge._ComtypesETABSSession)
    session.sap_model = sap_model

    with pytest.raises(RuntimeError, match="simulated extraction failure"):
        with session.normalized_kn_mm_units():
            raise RuntimeError("simulated extraction failure")

    assert sap_model.unit_calls == [5, 6]
