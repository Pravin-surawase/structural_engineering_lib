"""W2A transport-neutral ETABS beam-baseline contract tests."""

# ruff: noqa: N802 - fake methods intentionally mirror ETABS COM names.

from __future__ import annotations

import platform
from hashlib import sha256

import pytest
from pydantic import ValidationError

from structural_lib.services import etabs_beam_baseline as baseline
from structural_lib.services import etabs_beam_bridge as beam_bridge
from structural_lib.services.etabs_live_bridge import (
    ETABSDataError,
    ETABSResultSelectionKind,
    ETABSResultSelectionV1,
)


def _file_snapshot(observed_at: str) -> baseline.ETABSModelFileSnapshotV1:
    return baseline.ETABSModelFileSnapshotV1(
        model_path=r"C:\Models\W2 Authorized Copy.edb",
        model_name="W2 Authorized Copy.edb",
        sha256="a" * 64,
        byte_count=12_345,
        modified_at_utc="2026-08-29T05:00:00Z",
        observed_at_utc=observed_at,
    )


def _request() -> baseline.ETABSBeamBaselineRequestV1:
    return baseline.ETABSBeamBaselineRequestV1(
        authorized_model_file=_file_snapshot("2026-08-29T05:00:30Z"),
        runtime_provenance=baseline.ETABSRuntimeProvenanceV1(
            library_version="0.24.0",
            library_content_identity="b" * 64,
            python_version="3.11.15",
            platform="Windows-11",
            com_provider="fake-com/v1",
        ),
        result_selections=(
            ETABSResultSelectionV1(
                kind=ETABSResultSelectionKind.CASE,
                name="DEAD",
            ),
            ETABSResultSelectionV1(
                kind=ETABSResultSelectionKind.COMBINATION,
                name="ULS-1",
            ),
        ),
    )


class _FakeFileObserver:
    def __init__(
        self, *, after_read: baseline.ETABSModelFileSnapshotV1 | None = None
    ) -> None:
        self.before_read = _file_snapshot("2026-08-29T05:01:00Z")
        self.after_read = after_read or _file_snapshot("2026-08-29T05:02:00Z")
        self.calls: list[str] = []

    def __call__(self, model_path: str) -> baseline.ETABSModelFileSnapshotV1:
        self.calls.append(model_path)
        return self.before_read if len(self.calls) == 1 else self.after_read


def _extract(
    sap_model: _FakeSapModel,
    request: baseline.ETABSBeamBaselineRequestV1 | None = None,
    *,
    observer: _FakeFileObserver | None = None,
) -> baseline.ETABSBaselineBuildResultV1:
    return baseline.extract_etabs_beam_baseline_v1(
        sap_model,
        request or _request(),
        observe_model_file=observer or _FakeFileObserver(),
    )


class _FakeStory:
    def __init__(self, pack) -> None:
        self.pack = pack

    def GetStories(self):
        return self.pack(
            (
                2,
                self.pack(("Base", "L1", "L2")),
                self.pack((0.0, 0.0, 3000.0)),
                self.pack((0.0, 3000.0, 3000.0)),
                self.pack((False, True, False)),
                self.pack(("", "", "L1")),
                self.pack((False, False, False)),
                self.pack((0.0, 0.0, 0.0)),
                0,
            )
        )


class _FakePointObj:
    COORDINATES = {
        "P1": (0.0, 0.0, 3000.0),
        "P2": (5000.0, 0.0, 3000.0),
        "P3": (10_000.0, 0.0, 3000.0),
        "P4": (5000.0, 0.0, 0.0),
        "P5": (0.0, 5000.0, 0.0),
        "P6": (2000.0, 6000.0, 1000.0),
    }

    def __init__(self, pack) -> None:
        self.pack = pack

    def GetCoordCartesian(self, name):
        return self.pack((*self.COORDINATES[name], 0))


class _FakeFrameObj:
    FRAMES = {
        "B1": ("B1-L1", "L1", "P1", "P2", "R300x500", ""),
        "B2": ("B2-L1", "L1", "P2", "P3", "R300x500", ""),
        "C1": ("C1-L1", "L1", "P4", "P2", "R400x400", ""),
        "D1": ("D1-L1", "L1", "P5", "P6", "R250x350", ""),
    }

    def __init__(
        self,
        pack,
        *,
        bad_column_section: bool = False,
        advanced_axes_frame: str | None = None,
    ) -> None:
        self.pack = pack
        self.bad_column_section = bad_column_section
        self.advanced_axes_frame = advanced_axes_frame

    def GetNameList(self):
        return self.pack((4, self.pack(("D1", "C1", "B2", "B1")), 0))

    def GetLabelFromName(self, name):
        label, story, *_rest = self.FRAMES[name]
        return self.pack((label, story, 0))

    def GetPoints(self, name):
        _label, _story, point_i, point_j, _section, _auto = self.FRAMES[name]
        return self.pack((point_i, point_j, 0))

    def GetSection(self, name):
        _label, _story, _point_i, _point_j, section, auto = self.FRAMES[name]
        if name == "C1" and self.bad_column_section:
            section = "UNSUPPORTED"
        return self.pack((section, auto, 0))

    def GetLocalAxes(self, name):
        return self.pack(
            (
                15.0 if name == "B2" else 0.0,
                name == self.advanced_axes_frame,
                0,
            )
        )


class _FakePropFrame:
    def __init__(self, pack) -> None:
        self.pack = pack

    def GetRectangle(self, name):
        if name == "UNSUPPORTED":
            return self.pack(("", "", 0.0, 0.0, 0, "", "", 1))
        depth, width = {
            "R300x500": (500.0, 300.0),
            "R400x400": (400.0, 400.0),
            "R250x350": (350.0, 250.0),
        }[name]
        return self.pack(("", "M25-LABEL", depth, width, 1, "", "guid", 0))


class _FakeNameList:
    def __init__(self, pack, names: tuple[str, ...]) -> None:
        self.pack = pack
        self.names = names

    def GetNameList(self):
        return self.pack((len(self.names), self.pack(self.names), 0))


class _FakeAnalyze:
    def __init__(self, pack) -> None:
        self.pack = pack

    def GetCaseStatus(self):
        return self.pack((2, self.pack(("DEAD", "LIVE")), self.pack((4, 4)), 0))


class _FakeSetup:
    def __init__(self, pack, *, case_selected: bool = True) -> None:
        self.pack = pack
        self.case_selected = case_selected
        self.calls: list[tuple[str, str]] = []

    def GetCaseSelectedForOutput(self, name):
        self.calls.append(("case", name))
        return self.pack((self.case_selected, 0))

    def GetComboSelectedForOutput(self, name):
        self.calls.append(("combo", name))
        return self.pack((True, 0))


class _FakeResults:
    def __init__(self, pack, *, case_selected: bool = True) -> None:
        self.pack = pack
        self.Setup = _FakeSetup(pack, case_selected=case_selected)
        self.frame_force_calls: list[str] = []

    def FrameForce(self, frame_name, item_type):
        assert item_type == 0
        self.frame_force_calls.append(frame_name)
        load_cases = ("DEAD", "ULS-1", "DEAD", "ULS-1", "EXTRA")
        return self.pack(
            (
                5,
                self.pack((frame_name,) * 5),
                self.pack((0.0, 0.0, 2500.0, 2500.0, 5000.0)),
                self.pack(tuple(f"E-{frame_name}" for _ in range(5))),
                self.pack((0.0, 0.0, 2500.0, 2500.0, 5000.0)),
                self.pack(load_cases),
                self.pack(("", "Max", "", "Max", "")),
                self.pack((0.0, 0.0, 0.0, 0.0, 0.0)),
                self.pack((0.0, 0.0, 0.0, 0.0, 0.0)),
                self.pack((10.0, 20.0, 30.0, 40.0, 50.0)),
                self.pack((1.0, 2.0, 3.0, 4.0, 5.0)),
                self.pack((1000.0, 2000.0, 3000.0, 4000.0, 5000.0)),
                self.pack((6000.0, 7000.0, 8000.0, 9000.0, 10_000.0)),
                self.pack((11_000.0, 12_000.0, 13_000.0, 14_000.0, 15_000.0)),
                0,
            )
        )


class _FakeSapModel:
    def __init__(
        self,
        output_container=tuple,
        *,
        case_selected: bool = True,
        bad_column_section: bool = False,
        advanced_axes_frame: str | None = None,
    ) -> None:
        self.pack = output_container
        self.Story = _FakeStory(output_container)
        self.PointObj = _FakePointObj(output_container)
        self.FrameObj = _FakeFrameObj(
            output_container,
            bad_column_section=bad_column_section,
            advanced_axes_frame=advanced_axes_frame,
        )
        self.PropFrame = _FakePropFrame(output_container)
        self.LoadCases = _FakeNameList(output_container, ("DEAD", "LIVE"))
        self.RespCombo = _FakeNameList(output_container, ("ULS-1",))
        self.Analyze = _FakeAnalyze(output_container)
        self.Results = _FakeResults(output_container, case_selected=case_selected)
        self.unit_calls: list[int] = []

    def GetModelFilename(self, include_path):
        assert include_path is True
        return r"C:\Models\W2 Authorized Copy.edb"

    def GetVersion(self):
        return self.pack(("ETABS 23.3.1", 23.31, 0))

    def GetModelIsLocked(self):
        return True

    def GetPresentUnits(self):
        return 6

    def SetPresentUnits(self, units):
        self.unit_calls.append(units)
        return 0


class _FakeSession:
    def __init__(self, sap_model: _FakeSapModel) -> None:
        self.sap_model = sap_model

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


def _w2b_run_request(
    runtime: baseline.ETABSRuntimeProvenanceV1,
) -> beam_bridge.ETABSBeamBaselineRunRequestV1:
    return beam_bridge.ETABSBeamBaselineRunRequestV1(
        authorized_model_file=_file_snapshot("2026-08-29T05:00:30Z"),
        expected_etabs_version="ETABS 23.3.1",
        expected_etabs_version_number=23.31,
        expected_present_units_enum=6,
        expected_runtime_provenance=runtime,
        expected_getter_matrix_sha256=baseline.etabs_w2a_getter_matrix_sha256_v1(),
        result_selections=list(_request().result_selections),
        approved_copy_confirmed=True,
    )


@pytest.mark.parametrize("output_container", [tuple, list], ids=["tuple", "list"])
def test_baseline_is_complete_deterministic_and_restores_units(
    output_container,
) -> None:
    sap_model = _FakeSapModel(output_container)
    observer = _FakeFileObserver()

    result = _extract(sap_model, observer=observer)

    assert result.status is baseline.ETABSBaselineBuildStatus.ACCEPTED
    assert result.issues == ()
    assert result.baseline is not None
    artifact = result.baseline
    assert artifact.model.model_locked is True
    assert artifact.model.file_evidence.freshness_verdict == "VERIFIED_UNCHANGED"
    assert artifact.units.original_present_units_enum == 6
    assert artifact.units.restored_present_units_enum == 6
    assert sap_model.unit_calls == [5, 6]
    assert observer.calls == [
        r"C:\Models\W2 Authorized Copy.edb",
        r"C:\Models\W2 Authorized Copy.edb",
    ]
    assert [story.name for story in artifact.stories] == ["L1", "L2"]
    assert [frame.member_id for frame in artifact.frames] == sorted(
        frame.member_id for frame in artifact.frames
    )
    assert {frame.source_unique_name for frame in artifact.frames} == {"B1", "B2", "C1"}
    assert [frame.kind for frame in artifact.frames].count(
        baseline.ETABSFrameKind.BEAM
    ) == 2
    assert {item.kind for item in artifact.connectivity} == {
        baseline.ETABSConnectivityKind.BEAM_TO_BEAM,
        baseline.ETABSConnectivityKind.BEAM_TO_COLUMN,
    }
    assert len(artifact.connectivity) == 3
    assert len(artifact.results) == 4
    assert sum(len(item.stations) for item in artifact.results) == 8
    assert all(
        station.m3_knm in {11.0, 12.0, 13.0, 14.0}
        for item in artifact.results
        for station in item.stations
    )
    assert any(
        row.reason_code == "FRAME_ORIENTATION_UNSUPPORTED"
        and row.disposition is baseline.ETABSBaselineDisposition.EXCLUDED
        for row in artifact.dispositions
    )
    assert (
        sum(
            row.reason_code == "RESULT_SELECTION_NOT_REQUESTED"
            for row in artifact.dispositions
        )
        == 2
    )
    assert (
        artifact.frame_analysis_verdict
        == baseline.ETABSFrameAnalysisVerdict.HELD_NOT_SUPPORTED
    )
    assert baseline.verify_etabs_beam_baseline_hash_v1(artifact)


def test_tuple_and_list_shapes_produce_the_same_frozen_hash() -> None:
    tuple_result = _extract(_FakeSapModel(tuple))
    list_result = _extract(_FakeSapModel(list))

    assert tuple_result.baseline is not None
    assert list_result.baseline is not None
    assert tuple_result.baseline.baseline_sha256 == list_result.baseline.baseline_sha256
    assert (
        tuple_result.baseline.baseline_sha256
        == "2a1ecee7c64e6268d860640dee48e868cb64fe53eed20f361de58d65076466a4"
    )


@pytest.mark.parametrize("output_container", [tuple, list], ids=["tuple", "list"])
def test_frame_story_must_exist_in_story_inventory_and_restores_units(
    output_container,
) -> None:
    sap_model = _FakeSapModel(output_container)
    original_get_label = sap_model.FrameObj.GetLabelFromName

    def get_label_with_unknown_story(name):
        label, story, return_code = original_get_label(name)
        return output_container(
            (label, "MISSING" if name == "B1" else story, return_code)
        )

    sap_model.FrameObj.GetLabelFromName = get_label_with_unknown_story

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model)

    assert exc_info.value.code == "ETABS_FRAME_STORY_NOT_IN_INVENTORY"
    assert sap_model.unit_calls == [5, 6]


@pytest.mark.parametrize("output_container", [tuple, list], ids=["tuple", "list"])
def test_story_inventory_requires_documented_leading_base_row(
    output_container,
) -> None:
    sap_model = _FakeSapModel(output_container)
    sap_model.Story.GetStories = lambda: output_container(
        (
            2,
            output_container(("NOT_BASE", "L1", "L2")),
            output_container((0.0, 0.0, 3000.0)),
            output_container((0.0, 3000.0, 3000.0)),
            output_container((False, True, False)),
            output_container(("", "", "L1")),
            output_container((False, False, False)),
            output_container((0.0, 0.0, 0.0)),
            0,
        )
    )

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model)

    assert exc_info.value.code == "ETABS_STORY_BASE_ROW_INVALID"
    assert sap_model.unit_calls == [5, 6]


def test_story_base_row_is_explicitly_excluded_from_retained_stories() -> None:
    result = _extract(_FakeSapModel())

    assert result.baseline is not None
    assert [story.name for story in result.baseline.stories] == ["L1", "L2"]
    base_row = next(
        row
        for row in result.baseline.dispositions
        if row.reason_code == "STORY_BASE_NOT_A_STORY"
    )
    assert base_row.source_id == "Base"
    assert base_row.disposition is baseline.ETABSBaselineDisposition.EXCLUDED


def test_getter_matrix_is_frozen_and_contains_no_result_selection_setter() -> None:
    matrix = baseline.etabs_w2a_getter_matrix_v1()

    assert [item.operation for item in matrix] == [
        "SapModel.GetModelFilename",
        "SapModel.GetVersion",
        "SapModel.GetModelIsLocked",
        "SapModel.GetPresentUnits",
        "Story.GetStories",
        "FrameObj.GetNameList",
        "FrameObj.GetLabelFromName",
        "FrameObj.GetPoints",
        "FrameObj.GetSection",
        "FrameObj.GetLocalAxes",
        "PointObj.GetCoordCartesian",
        "PropFrame.GetRectangle",
        "LoadCases.GetNameList",
        "RespCombo.GetNameList",
        "Analyze.GetCaseStatus",
        "Results.Setup.GetCaseSelectedForOutput",
        "Results.Setup.GetComboSelectedForOutput",
        "Results.FrameForce",
    ]
    assert all("SetCase" not in item.operation for item in matrix)
    assert all("SetCombo" not in item.operation for item in matrix)
    assert all(
        item.accepted_shapes == ("tuple", "list")
        for item in matrix
        if item.return_code_contract == "TRAILING_ZERO"
    )
    unit_policy = baseline.etabs_w2a_unit_mutation_policy_v1()
    assert unit_policy.only_allowed_setter is True
    assert unit_policy.restore_on_failure is True


def test_unselected_explicit_result_blocks_without_using_a_setter() -> None:
    sap_model = _FakeSapModel(case_selected=False)

    result = _extract(sap_model)

    assert result.status is baseline.ETABSBaselineBuildStatus.BLOCKED
    assert result.baseline is None
    assert "RESULT_SELECTION_NOT_ACTIVE" in {issue.code for issue in result.issues}
    assert sap_model.Results.Setup.calls == [("case", "DEAD"), ("combo", "ULS-1")]
    assert sap_model.unit_calls == [5, 6]
    assert sap_model.Results.frame_force_calls == []


def test_connected_excluded_frame_blocks_topology_and_restores_units() -> None:
    sap_model = _FakeSapModel(bad_column_section=True)

    result = _extract(sap_model)

    assert result.status is baseline.ETABSBaselineBuildStatus.BLOCKED
    assert result.baseline is None
    assert "CONNECTED_FRAME_EXCLUDED" in {issue.code for issue in result.issues}
    assert any(
        row.reason_code == "SECTION_NOT_RECTANGULAR_OR_UNAVAILABLE"
        and row.disposition is baseline.ETABSBaselineDisposition.EXCLUDED
        for row in result.dispositions
    )
    assert sap_model.unit_calls == [5, 6]
    assert sap_model.Results.frame_force_calls == []


def test_connected_advanced_local_axis_frame_blocks_incomplete_topology() -> None:
    sap_model = _FakeSapModel(advanced_axes_frame="C1")

    result = _extract(sap_model)

    assert result.status is baseline.ETABSBaselineBuildStatus.BLOCKED
    assert result.baseline is None
    assert "CONNECTED_FRAME_EXCLUDED" in {issue.code for issue in result.issues}
    assert any(
        row.reason_code == "FRAME_ADVANCED_LOCAL_AXES_UNSUPPORTED"
        and row.disposition is baseline.ETABSBaselineDisposition.EXCLUDED
        for row in result.dispositions
    )
    assert sap_model.unit_calls == [5, 6]
    assert sap_model.Results.frame_force_calls == []


def test_com_shape_failure_restores_original_units() -> None:
    sap_model = _FakeSapModel()
    sap_model.Story.GetStories = lambda: (1, 0)

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model)

    assert exc_info.value.code == "ETABS_COM_SIGNATURE_MISMATCH"
    assert sap_model.unit_calls == [5, 6]


def test_fractional_com_count_fails_closed_and_restores_units() -> None:
    sap_model = _FakeSapModel()
    sap_model.FrameObj.GetNameList = lambda: (4.5, ("D1", "C1", "B2", "B1"), 0)

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model)

    assert exc_info.value.code == "ETABS_VALUE_INVALID"
    assert sap_model.unit_calls == [5, 6]


def test_nonzero_return_code_restores_original_units() -> None:
    sap_model = _FakeSapModel()
    sap_model.FrameObj.GetNameList = lambda: (0, (), 7)

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model)

    assert exc_info.value.code == "ETABS_API_CALL_FAILED"
    assert sap_model.unit_calls == [5, 6]


def test_unit_normalization_failure_attempts_original_unit_restoration() -> None:
    sap_model = _FakeSapModel()

    def fail_normalization(units):
        sap_model.unit_calls.append(units)
        return 9 if units == 5 else 0

    sap_model.SetPresentUnits = fail_normalization

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model)

    assert exc_info.value.code == "ETABS_API_CALL_FAILED"
    assert sap_model.unit_calls == [5, 6]


def test_file_freshness_evidence_rejects_changed_hash() -> None:
    after = _file_snapshot("2026-08-29T05:02:00Z").model_copy(
        update={"sha256": "c" * 64}
    )

    with pytest.raises(ValidationError, match="hash, size, and timestamp"):
        baseline.ETABSModelFileEvidenceV1(
            before_read=_file_snapshot("2026-08-29T05:01:00Z"),
            after_read=after,
        )


def test_changed_post_read_file_identity_fails_after_units_are_restored() -> None:
    sap_model = _FakeSapModel()
    changed = _file_snapshot("2026-08-29T05:02:00Z").model_copy(
        update={"sha256": "c" * 64}
    )
    observer = _FakeFileObserver(after_read=changed)

    with pytest.raises(ETABSDataError) as exc_info:
        _extract(sap_model, observer=observer)

    assert exc_info.value.code == "ETABS_MODEL_FRESHNESS_FAILED"
    assert sap_model.unit_calls == [5, 6]
    assert len(observer.calls) == 2


def test_duplicate_result_name_is_rejected_before_etabs_calls() -> None:
    request = _request()

    with pytest.raises(ValidationError, match="selection names must be unique"):
        baseline.ETABSBeamBaselineRequestV1(
            authorized_model_file=request.authorized_model_file,
            runtime_provenance=request.runtime_provenance,
            result_selections=(
                ETABSResultSelectionV1(kind=ETABSResultSelectionKind.CASE, name="SAME"),
                ETABSResultSelectionV1(
                    kind=ETABSResultSelectionKind.COMBINATION, name="SAME"
                ),
            ),
        )


def test_baseline_schema_round_trip_retains_hash() -> None:
    result = _extract(_FakeSapModel())
    assert result.baseline is not None

    restored = baseline.ETABSBeamBaselineV1.model_validate_json(
        result.baseline.model_dump_json(), strict=False
    )

    assert baseline.verify_etabs_beam_baseline_hash_v1(restored)
    assert restored == result.baseline


def test_w2b_preflight_is_getter_only_and_retains_exact_source_identity(
    monkeypatch,
) -> None:
    sap_model = _FakeSapModel(list)
    observer = _FakeFileObserver()
    runtime = _request().runtime_provenance
    monkeypatch.setattr(beam_bridge, "_runtime_provenance", lambda: runtime)

    result = beam_bridge.inspect_etabs_beam_baseline_v1(
        session_factory=lambda: _FakeSession(sap_model),
        observe_model_file=observer,
    )

    assert result.schema_version == "etabs-beam-baseline-preflight/v1"
    assert result.observed_model_file.sha256 == "a" * 64
    assert result.model_locked is True
    assert result.present_units_enum == 6
    assert result.runtime_provenance == runtime
    assert result.frame_analysis_verdict == "HELD_NOT_SUPPORTED"
    assert observer.calls == [r"C:\Models\W2 Authorized Copy.edb"]
    assert sap_model.unit_calls == []


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows path contract")
def test_w2b_real_file_observer_hashes_exact_saved_edb_without_mutation(
    tmp_path,
) -> None:
    model_path = tmp_path / "W2 Authorized Copy.edb"
    content = b"read-only-w2-evidence"
    model_path.write_bytes(content)
    before = model_path.stat()

    snapshot = beam_bridge.observe_etabs_model_file_v1(str(model_path))

    after = model_path.stat()
    assert snapshot.model_path == str(model_path)
    assert snapshot.model_name == model_path.name
    assert snapshot.sha256 == sha256(content).hexdigest()
    assert snapshot.byte_count == len(content)
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)


def test_w2b_transport_preserves_exact_hash_basis_and_complete_row_counts(
    monkeypatch,
) -> None:
    sap_model = _FakeSapModel(tuple)
    observer = _FakeFileObserver()
    runtime = _request().runtime_provenance
    monkeypatch.setattr(beam_bridge, "_runtime_provenance", lambda: runtime)

    result = beam_bridge.run_etabs_beam_baseline_v1(
        _w2b_run_request(runtime),
        session_factory=lambda: _FakeSession(sap_model),
        observe_model_file=observer,
    )

    artifact = result.build_result.baseline
    assert artifact is not None
    assert result.build_result.status is baseline.ETABSBaselineBuildStatus.ACCEPTED
    assert result.counts.frames == len(artifact.frames)
    assert result.counts.connectivity_rows == len(artifact.connectivity)
    assert result.counts.result_station_rows == 8
    assert result.counts.disposition_rows == len(artifact.dispositions)
    assert result.baseline_hash_basis_json is not None
    encoded = result.baseline_hash_basis_json.encode("utf-8")
    assert len(encoded) == result.baseline_hash_basis_utf8_bytes
    assert sha256(encoded).hexdigest() == artifact.baseline_sha256
    assert observer.calls == [r"C:\Models\W2 Authorized Copy.edb"] * 3
    assert sap_model.unit_calls == [5, 6]


def test_w2b_unlocked_model_aborts_before_observer_units_or_result_reads(
    monkeypatch,
) -> None:
    sap_model = _FakeSapModel()
    sap_model.GetModelIsLocked = lambda: False
    observer = _FakeFileObserver()
    runtime = _request().runtime_provenance
    monkeypatch.setattr(beam_bridge, "_runtime_provenance", lambda: runtime)

    with pytest.raises(ETABSDataError, match="requires.*locked") as exc_info:
        beam_bridge.run_etabs_beam_baseline_v1(
            _w2b_run_request(runtime),
            session_factory=lambda: _FakeSession(sap_model),
            observe_model_file=observer,
        )

    assert exc_info.value.code == "ETABS_MODEL_NOT_LOCKED"
    assert observer.calls == []
    assert sap_model.unit_calls == []


def test_w2b_runtime_drift_aborts_before_com_session(monkeypatch) -> None:
    expected = _request().runtime_provenance
    current = expected.model_copy(update={"library_content_identity": "c" * 64})
    monkeypatch.setattr(beam_bridge, "_runtime_provenance", lambda: current)
    session_created = False

    def session_factory():
        nonlocal session_created
        session_created = True
        return _FakeSession(_FakeSapModel())

    with pytest.raises(ETABSDataError) as exc_info:
        beam_bridge.run_etabs_beam_baseline_v1(
            _w2b_run_request(expected), session_factory=session_factory
        )

    assert exc_info.value.code == "ETABS_RUNTIME_IDENTITY_MISMATCH"
    assert session_created is False


def test_w2b_post_read_unit_getter_proves_restoration(monkeypatch) -> None:
    sap_model = _FakeSapModel()
    unit_getter_calls = 0

    def present_units():
        nonlocal unit_getter_calls
        unit_getter_calls += 1
        return 6 if unit_getter_calls < 3 else 5

    sap_model.GetPresentUnits = present_units
    runtime = _request().runtime_provenance
    monkeypatch.setattr(beam_bridge, "_runtime_provenance", lambda: runtime)

    with pytest.raises(ETABSDataError) as exc_info:
        beam_bridge.run_etabs_beam_baseline_v1(
            _w2b_run_request(runtime),
            session_factory=lambda: _FakeSession(sap_model),
            observe_model_file=_FakeFileObserver(),
        )

    assert exc_info.value.code == "ETABS_UNIT_RESTORATION_FAILED"
    assert sap_model.unit_calls == [5, 6]


def test_w2b_capacity_failure_returns_no_partial_baseline(monkeypatch) -> None:
    build_result = _extract(_FakeSapModel())
    monkeypatch.setattr(beam_bridge, "ETABS_BASELINE_MAX_RESULT_STATIONS", 1)

    with pytest.raises(beam_bridge.ETABSBeamBaselineCapacityError) as exc_info:
        beam_bridge._enforce_capacity(build_result)

    assert exc_info.value.code == "ETABS_BASELINE_ROW_LIMIT_EXCEEDED"
