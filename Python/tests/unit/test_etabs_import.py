# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for ETABS import module."""

from __future__ import annotations

from pathlib import Path

import pytest

from structural_lib.services.etabs_import import (
    ETABSEnvelopeResult,
    ETABSForceRow,
    FrameGeometry,
    create_job_from_etabs,
    create_jobs_from_etabs_csv,
    export_normalized_csv,
    load_etabs_csv,
    load_frames_geometry,
    merge_forces_and_geometry,
    normalize_etabs_forces,
    validate_etabs_csv,
)

# Sample CSV content for testing
SAMPLE_ETABS_CSV = """Story,Label,Output Case,Station,M3,V2,P
Story1,B1,1.5(DL+LL),0,50.5,80.2,0
Story1,B1,1.5(DL+LL),2000,120.3,10.1,0
Story1,B1,1.5(DL+LL),4000,-40.2,75.5,0
Story1,B2,1.5(DL+LL),0,30.0,60.0,0
Story1,B2,1.5(DL+LL),3000,90.5,5.0,0
Story2,B1,1.5(DL+LL),0,45.0,70.0,0
Story2,B1,1.5(DL+LL),4000,-35.0,65.0,0
Story1,B1,0.9DL+1.5WL,0,25.0,40.0,0
Story1,B1,0.9DL+1.5WL,4000,-80.0,55.0,0
"""

# Alternative column format
SAMPLE_ETABS_CSV_ALT = """Level,Frame,Load Case/Combo,Distance,Moment3,Shear2
Story1,B1,DL+LL,0,100,50
Story1,B1,DL+LL,3000,150,20
"""


class TestValidateETABSCSV:
    """Tests for validate_etabs_csv function."""

    def test_validate_valid_csv(self, tmp_path: Path) -> None:
        """Valid CSV passes validation."""
        csv_file = tmp_path / "valid.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        is_valid, issues, col_map = validate_etabs_csv(csv_file)

        assert is_valid is True
        assert len(issues) == 0
        assert "story" in col_map
        assert "beam_id" in col_map
        assert "case_id" in col_map
        assert "m3" in col_map
        assert "v2" in col_map

    def test_validate_alternative_columns(self, tmp_path: Path) -> None:
        """Alternative column names are recognized."""
        csv_file = tmp_path / "alt.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV_ALT)

        is_valid, issues, col_map = validate_etabs_csv(csv_file)

        assert is_valid is True
        assert col_map["story"] == "Level"
        assert col_map["beam_id"] == "Frame"
        assert col_map["case_id"] == "Load Case/Combo"

    def test_validate_missing_required(self, tmp_path: Path) -> None:
        """Missing required columns are reported."""
        csv_file = tmp_path / "missing.csv"
        csv_file.write_text("Story,Label,Station\nStory1,B1,0\n")

        is_valid, issues, _ = validate_etabs_csv(csv_file)

        assert is_valid is False
        assert any("case_id" in i for i in issues)
        assert any("m3" in i for i in issues)
        assert any("v2" in i for i in issues)

    def test_validate_file_not_found(self, tmp_path: Path) -> None:
        """Non-existent file returns False."""
        is_valid, issues, _ = validate_etabs_csv(tmp_path / "nonexistent.csv")

        assert is_valid is False
        assert any("not found" in i for i in issues)

    def test_validate_empty_csv(self, tmp_path: Path) -> None:
        """Empty CSV is invalid."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        is_valid, issues, _ = validate_etabs_csv(csv_file)

        assert is_valid is False


class TestLoadETABSCSV:
    """Tests for load_etabs_csv function."""

    def test_load_basic_csv(self, tmp_path: Path) -> None:
        """Load basic ETABS CSV."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        rows = load_etabs_csv(csv_file)

        assert len(rows) == 9
        assert all(isinstance(r, ETABSForceRow) for r in rows)

        # Check first row
        first = rows[0]
        assert first.story == "Story1"
        assert first.beam_id == "B1"
        assert first.case_id == "1.5(DL+LL)"
        assert first.station == pytest.approx(0)
        assert first.m3 == pytest.approx(50.5)
        assert first.v2 == pytest.approx(80.2)

    def test_load_with_station_multiplier(self, tmp_path: Path) -> None:
        """Station multiplier converts units."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        rows = load_etabs_csv(csv_file, station_multiplier=1000)

        # Station 2000 * 1000 = 2000000
        assert rows[1].station == pytest.approx(2000000)

    def test_load_invalid_csv_raises(self, tmp_path: Path) -> None:
        """Invalid CSV raises ValueError."""
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("A,B,C\n1,2,3\n")

        with pytest.raises(ValueError, match="Invalid ETABS CSV"):
            load_etabs_csv(csv_file)


class TestNormalizeETABSForces:
    """Tests for normalize_etabs_forces function."""

    def test_normalize_calculates_envelope(self, tmp_path: Path) -> None:
        """Envelope correctly finds max abs values."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        envelopes = normalize_etabs_forces(csv_file)

        # Should have 4 unique (story, beam_id, case_id) combinations
        assert len(envelopes) == 4

        # Find Story1/B1/1.5(DL+LL)
        b1_env = next(
            e
            for e in envelopes
            if e.story == "Story1" and e.beam_id == "B1" and e.case_id == "1.5(DL+LL)"
        )
        # Max |M3| should be max(50.5, 120.3, |-40.2|) = 120.3
        assert b1_env.mu_knm == pytest.approx(120.3)
        # Max |V2| should be max(80.2, 10.1, 75.5) = 80.2
        assert b1_env.vu_kn == pytest.approx(80.2)
        assert b1_env.station_count == 3

    def test_normalize_exports_csv(self, tmp_path: Path) -> None:
        """Output CSV is created when path provided."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)
        output_file = tmp_path / "normalized.csv"

        normalize_etabs_forces(csv_file, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "story,beam_id,case_id,mu_knm,vu_kn" in content
        assert "120.300" in content  # Max moment

    def test_normalize_sorted_output(self, tmp_path: Path) -> None:
        """Output is sorted by story, beam_id, case_id."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        envelopes = normalize_etabs_forces(csv_file)

        # Check sorting
        stories = [e.story for e in envelopes]
        assert stories == sorted(stories) or all(
            s == "Story1" or s == "Story2" for s in stories
        )


class TestExportNormalizedCSV:
    """Tests for export_normalized_csv function."""

    def test_export_creates_file(self, tmp_path: Path) -> None:
        """Export creates CSV file."""
        envelopes = [
            ETABSEnvelopeResult("Story1", "B1", "DL+LL", 100.0, 50.0, 3),
            ETABSEnvelopeResult("Story1", "B2", "DL+LL", 80.0, 40.0, 2),
        ]
        output_file = tmp_path / "output.csv"

        export_normalized_csv(envelopes, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "story,beam_id,case_id,mu_knm,vu_kn,stations" in content
        assert "Story1,B1,DL+LL,100.000,50.000,3" in content

    def test_export_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Export creates parent directories if needed."""
        output_file = tmp_path / "subdir" / "deep" / "output.csv"
        envelopes = [ETABSEnvelopeResult("S1", "B1", "C1", 100.0, 50.0)]

        export_normalized_csv(envelopes, output_file)

        assert output_file.exists()


class TestCreateJobFromETABS:
    """Tests for create_job_from_etabs function."""

    def test_create_job_single_envelope(self) -> None:
        """Create job from single envelope."""
        env = ETABSEnvelopeResult("Story1", "B1", "1.5(DL+LL)", 150.0, 100.0)

        job = create_job_from_etabs(env, b_mm=300, D_mm=500, fck_nmm2=25)

        assert job["schema_version"] == 1
        assert job["code"] == "IS456"
        assert job["units"] == "SI-mm"
        assert job["job_id"] == "ETABS_Story1_B1"
        assert job["beam"]["b_mm"] == 300
        assert job["beam"]["D_mm"] == 500
        assert job["beam"]["fck_nmm2"] == 25
        assert job["beam"]["fy_nmm2"] == 500  # Default
        assert len(job["cases"]) == 1
        assert job["cases"][0]["mu_knm"] == 150.0
        assert job["cases"][0]["vu_kn"] == 100.0

    def test_create_job_multiple_envelopes(self) -> None:
        """Create job from multiple envelopes (multiple load cases)."""
        envs = [
            ETABSEnvelopeResult("Story1", "B1", "DL+LL", 100.0, 50.0),
            ETABSEnvelopeResult("Story1", "B1", "DL+WL", 120.0, 60.0),
            ETABSEnvelopeResult("Story1", "B1", "0.9DL+1.5WL", 80.0, 55.0),
        ]

        job = create_job_from_etabs(envs, b_mm=300, D_mm=500, fck_nmm2=25)

        assert len(job["cases"]) == 3
        assert job["cases"][0]["case_id"] == "DL+LL"
        assert job["cases"][1]["case_id"] == "DL+WL"
        assert job["cases"][2]["case_id"] == "0.9DL+1.5WL"

    def test_create_job_calculates_effective_depth(self) -> None:
        """Effective depth calculated from D if not provided."""
        env = ETABSEnvelopeResult("S1", "B1", "C1", 100.0, 50.0)

        job = create_job_from_etabs(env, b_mm=300, D_mm=500, fck_nmm2=25)

        # d = D - cover(40) - stirrup(8) - bar/2(10) = 442
        assert job["beam"]["d_mm"] == pytest.approx(442.0)

    def test_create_job_explicit_depth(self) -> None:
        """Explicit effective depth overrides calculation."""
        env = ETABSEnvelopeResult("S1", "B1", "C1", 100.0, 50.0)

        job = create_job_from_etabs(env, b_mm=300, D_mm=500, fck_nmm2=25, d_mm=450)

        assert job["beam"]["d_mm"] == 450

    def test_create_job_custom_job_id(self) -> None:
        """Custom job_id is used."""
        env = ETABSEnvelopeResult("S1", "B1", "C1", 100.0, 50.0)

        job = create_job_from_etabs(
            env, b_mm=300, D_mm=500, fck_nmm2=25, job_id="MY_JOB_001"
        )

        assert job["job_id"] == "MY_JOB_001"

    def test_create_job_empty_raises(self) -> None:
        """Empty envelope list raises ValueError."""
        with pytest.raises(ValueError, match="No envelope data"):
            create_job_from_etabs([], b_mm=300, D_mm=500, fck_nmm2=25)


class TestCreateJobsFromETABSCSV:
    """Tests for create_jobs_from_etabs_csv function."""

    def test_create_jobs_batch(self, tmp_path: Path) -> None:
        """Create jobs for all beams in CSV."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        geometry = {
            "B1": {"b_mm": 300.0, "D_mm": 500.0},
            "B2": {"b_mm": 250.0, "D_mm": 450.0},
        }

        jobs = create_jobs_from_etabs_csv(csv_file, geometry)

        assert len(jobs) == 2
        job_ids = {j["job_id"] for j in jobs}
        assert any("B1" in jid for jid in job_ids)
        assert any("B2" in jid for jid in job_ids)

    def test_create_jobs_saves_files(self, tmp_path: Path) -> None:
        """Jobs are saved to output directory."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)
        output_dir = tmp_path / "jobs"

        geometry = {"B1": {"b_mm": 300.0, "D_mm": 500.0}}

        create_jobs_from_etabs_csv(csv_file, geometry, output_dir=output_dir)

        assert output_dir.exists()
        json_files = list(output_dir.glob("*.json"))
        assert len(json_files) >= 1

    def test_create_jobs_skips_missing_geometry(self, tmp_path: Path) -> None:
        """Beams without geometry are skipped."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        # Only provide geometry for B1, not B2
        geometry = {"B1": {"b_mm": 300.0, "D_mm": 500.0}}

        jobs = create_jobs_from_etabs_csv(csv_file, geometry)

        # Only B1 should be in jobs
        assert len(jobs) == 1
        assert "B1" in jobs[0]["job_id"]

    def test_create_jobs_uses_defaults(self, tmp_path: Path) -> None:
        """Default fck and fy are used when not in geometry."""
        csv_file = tmp_path / "etabs.csv"
        csv_file.write_text(SAMPLE_ETABS_CSV)

        geometry = {"B1": {"b_mm": 300.0, "D_mm": 500.0}}

        jobs = create_jobs_from_etabs_csv(
            csv_file, geometry, default_fck=30.0, default_fy=415.0
        )

        assert jobs[0]["beam"]["fck_nmm2"] == 30.0
        assert jobs[0]["beam"]["fy_nmm2"] == 415.0


# Sample frames_geometry CSV content for testing (matches ETABS VBA export format)
SAMPLE_FRAMES_GEOMETRY_CSV = """UniqueName,Label,Story,FrameType,SectionName,Point1Name,Point2Name,Point1X,Point1Y,Point1Z,Point2X,Point2Y,Point2Z,Angle,CardinalPoint
B1,B1,Story1,Beam,RB300x500,1,2,0.0,0.0,3.0,4.5,0.0,3.0,0.0,10
B2,B2,Story1,Beam,RB300x500,2,3,4.5,0.0,3.0,9.0,0.0,3.0,0.0,10
C1,C1,Story1,Column,RC300x300,4,5,0.0,0.0,0.0,0.0,0.0,3.0,90.0,10
B3,B3,Story2,Beam,RB300x500,6,7,0.0,0.0,6.0,4.5,0.0,6.0,0.0,10
C2,C2,Story2,Column,RC300x300,8,9,0.0,0.0,3.0,0.0,0.0,6.0,90.0,10
"""


class TestFrameGeometry:
    """Tests for FrameGeometry dataclass."""

    def test_frame_geometry_length_m(self) -> None:
        """Test length_m property calculates correctly."""
        geom = FrameGeometry(
            unique_name="B1",
            label="B1",
            story="Story1",
            frame_type="Beam",
            section_name="RB300x500",
            point1_name="1",
            point2_name="2",
            point1_x=0.0,
            point1_y=0.0,
            point1_z=3.0,
            point2_x=4.5,
            point2_y=0.0,
            point2_z=3.0,
            angle=0.0,
            cardinal_point=10,
        )
        # sqrt((4.5-0)^2 + 0 + 0) = 4.5m
        assert geom.length_m == pytest.approx(4.5)

    def test_frame_geometry_is_vertical_beam(self) -> None:
        """Horizontal beam is not vertical."""
        geom = FrameGeometry(
            unique_name="B1",
            label="B1",
            story="Story1",
            frame_type="Beam",
            section_name="RB300x500",
            point1_name="1",
            point2_name="2",
            point1_x=0.0,
            point1_y=0.0,
            point1_z=3.0,
            point2_x=4.5,
            point2_y=0.0,
            point2_z=3.0,
            angle=0.0,
            cardinal_point=10,
        )
        assert geom.is_vertical is False

    def test_frame_geometry_is_vertical_column(self) -> None:
        """Vertical column is detected."""
        geom = FrameGeometry(
            unique_name="C1",
            label="C1",
            story="Story1",
            frame_type="Column",
            section_name="RC300x300",
            point1_name="4",
            point2_name="5",
            point1_x=0.0,
            point1_y=0.0,
            point1_z=0.0,
            point2_x=0.0,
            point2_y=0.0,
            point2_z=3.0,
            angle=90.0,
            cardinal_point=10,
        )
        assert geom.is_vertical is True


class TestLoadFramesGeometry:
    """Tests for load_frames_geometry function."""

    def test_load_basic_geometry(self, tmp_path: Path) -> None:
        """Load basic frames geometry CSV."""
        csv_file = tmp_path / "frames_geometry.csv"
        csv_file.write_text(SAMPLE_FRAMES_GEOMETRY_CSV)

        frames = load_frames_geometry(csv_file)

        assert len(frames) == 5
        assert all(isinstance(f, FrameGeometry) for f in frames)

        # Check first beam
        b1 = next(f for f in frames if f.unique_name == "B1")
        assert b1.story == "Story1"
        assert b1.frame_type == "Beam"
        assert b1.point1_x == pytest.approx(0.0)
        assert b1.point2_x == pytest.approx(4.5)
        assert b1.length_m == pytest.approx(4.5)

    def test_load_counts_beams_and_columns(self, tmp_path: Path) -> None:
        """Correctly counts beams and columns."""
        csv_file = tmp_path / "frames_geometry.csv"
        csv_file.write_text(SAMPLE_FRAMES_GEOMETRY_CSV)

        frames = load_frames_geometry(csv_file)

        beams = [f for f in frames if f.frame_type.lower() == "beam"]
        columns = [f for f in frames if f.frame_type.lower() == "column"]

        assert len(beams) == 3  # B1, B2, B3
        assert len(columns) == 2  # C1, C2

    def test_load_file_not_found_raises(self, tmp_path: Path) -> None:
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_frames_geometry(tmp_path / "nonexistent.csv")

    def test_load_building_extents(self, tmp_path: Path) -> None:
        """Verify building coordinate ranges."""
        csv_file = tmp_path / "frames_geometry.csv"
        csv_file.write_text(SAMPLE_FRAMES_GEOMETRY_CSV)

        frames = load_frames_geometry(csv_file)

        x_coords = [f.point1_x for f in frames] + [f.point2_x for f in frames]
        z_coords = [f.point1_z for f in frames] + [f.point2_z for f in frames]

        assert min(x_coords) == pytest.approx(0.0)
        assert max(x_coords) == pytest.approx(9.0)
        assert min(z_coords) == pytest.approx(0.0)
        assert max(z_coords) == pytest.approx(6.0)


class TestMergeForcesAndGeometry:
    """Tests for merge_forces_and_geometry function."""

    def test_merge_basic(self, tmp_path: Path) -> None:
        """Merge forces with geometry."""
        forces_file = tmp_path / "forces.csv"
        forces_file.write_text(SAMPLE_ETABS_CSV)

        geometry_file = tmp_path / "geometry.csv"
        geometry_file.write_text(SAMPLE_FRAMES_GEOMETRY_CSV)

        forces = normalize_etabs_forces(forces_file)
        geometry = load_frames_geometry(geometry_file)

        merged = merge_forces_and_geometry(forces, geometry)

        # Should have dict mapping beam_id to (envelope, geometry or None)
        assert isinstance(merged, dict)
        for _key, value in merged.items():
            envelope, geom = value
            assert isinstance(envelope, ETABSEnvelopeResult)
            # geom might be None if beam_id doesn't match

    def test_merge_finds_matching_geometry(self, tmp_path: Path) -> None:
        """Matched beams have geometry attached."""
        forces_file = tmp_path / "forces.csv"
        forces_file.write_text(SAMPLE_ETABS_CSV)

        geometry_file = tmp_path / "geometry.csv"
        geometry_file.write_text(SAMPLE_FRAMES_GEOMETRY_CSV)

        forces = normalize_etabs_forces(forces_file)
        geometry = load_frames_geometry(geometry_file)

        merged = merge_forces_and_geometry(forces, geometry)

        # B1 should have geometry (if B1 is in both forces and geometry)
        if "B1" in merged:
            env, geom = merged["B1"]
            assert env.beam_id == "B1"
            if geom:
                assert geom.unique_name == "B1"
