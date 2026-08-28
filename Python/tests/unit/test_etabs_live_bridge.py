"""Deterministic tests for the optional live ETABS beam-pilot service."""

# ruff: noqa: N802 - fakes intentionally mirror the ETABS COM method names.

from __future__ import annotations

from contextlib import contextmanager

import pytest

from structural_lib.services import etabs_live_bridge as bridge


def _design_basis() -> bridge.ETABSPilotDesignBasisV1:
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
        }
    )


def _request(*, limit: int = 2) -> bridge.ETABSPilotRequestV1:
    return bridge.ETABSPilotRequestV1(
        result_selection=bridge.ETABSResultSelectionV1(
            kind=bridge.ETABSResultSelectionKind.COMBINATION,
            name="ULS-1",
        ),
        design_basis=_design_basis(),
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

    def FrameForce(self, frame_name, item_type):
        assert item_type == 0
        outputs = (
            3,
            (frame_name,) * 3,
            (0.0, 2500.0, 5000.0),
            (f"E-{frame_name}",) * 3,
            (0.0, 2500.0, 5000.0),
            ("ULS-1",) * 3,
            ("Max", "Max", "Min"),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (80.0, -110.0, 90.0),
            (5.0, 4.0, -6.0),
            (1000.0, -1500.0, 500.0),
            (10_000.0, 20_000.0, -15_000.0),
            (-150_000.0, 120_000.0, 100_000.0),
            0,
        )
        return self.output_container(outputs)


class _FakeFrameObj:
    def __init__(self, output_container=tuple) -> None:
        self.output_container = output_container

    def GetAllFrames(self, coordinate_system):
        assert coordinate_system == "Global"
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
    def __init__(self, output_container=tuple) -> None:
        self.output_container = output_container
        self.FrameObj = _FakeFrameObj(output_container)
        self.PropFrame = _FakePropFrame(output_container)
        self.Results = _FakeResults(output_container)
        self.unit_calls: list[int] = []

    def GetModelFilepath(self):
        return r"C:\Models\Pilot Copy.edb"

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
def test_pilot_extracts_sorted_beams_preserves_stations_and_restores_units(
    monkeypatch, output_container
):
    sap_model = _FakeSapModel(output_container)
    session = _FakeSession(sap_model)
    monkeypatch.setattr(bridge, "_library_identity", lambda: ("0.24.0", "a" * 64))

    result = bridge.run_etabs_beam_pilot_v1(_request(), session_factory=lambda: session)

    assert result.model.model_name == "Pilot Copy.edb"
    assert result.candidate_beam_count == 2
    assert result.designed_beam_count == 2
    assert [item.geometry.frame_name for item in result.beams] == ["B1", "B2"]
    assert result.beams[0].geometry.b_mm == 300.0
    assert result.beams[0].geometry.D_mm == 500.0
    assert result.beams[0].forces.result_row_count == 3
    assert result.beams[0].forces.governing_v2.signed_value == -110.0
    assert result.beams[0].forces.governing_m3.signed_value == -150.0
    assert result.beams[0].forces.governing_t.absolute_value == 1.5
    assert (
        result.beams[0].design_result["envelope"]["qualified_review_required"] is True
    )
    assert sap_model.unit_calls == [5, 6]
    assert sap_model.Results.Setup.calls == [
        ("deselect",),
        ("combo", "ULS-1", True),
    ]
    assert session.closed is True


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
    assert result.model.etabs_version == "ETABS 23.3.1"
    assert sap_model.unit_calls == []
    assert session.closed is True


def test_real_session_unit_context_restores_units_after_extraction_failure():
    sap_model = _FakeSapModel()
    session = object.__new__(bridge._ComtypesETABSSession)
    session.sap_model = sap_model

    with pytest.raises(RuntimeError, match="simulated extraction failure"):
        with session.normalized_kn_mm_units():
            raise RuntimeError("simulated extraction failure")

    assert sap_model.unit_calls == [5, 6]
