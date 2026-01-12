# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for audit module (TASK-278)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from structural_lib.audit import (
    AuditLogEntry,
    AuditTrail,
    CalculationHash,
    compute_hash,
    create_calculation_certificate,
    verify_calculation,
)


class TestCalculationHash:
    """Tests for CalculationHash class."""

    def test_hash_creation(self) -> None:
        """Test creating a hash from inputs and outputs."""
        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856, "is_ok": True}

        calc_hash = CalculationHash.from_calculation(inputs, outputs)

        assert calc_hash.input_hash
        assert calc_hash.output_hash
        assert calc_hash.combined_hash
        assert len(calc_hash.input_hash) == 64  # SHA-256 = 64 hex chars
        assert len(calc_hash.output_hash) == 64
        assert calc_hash.algorithm == "sha256"

    def test_hash_deterministic(self) -> None:
        """Test that same inputs produce same hash."""
        inputs = {"b_mm": 300, "D_mm": 500, "fck": 25}
        outputs = {"result": 100}

        hash1 = CalculationHash.from_calculation(inputs, outputs)
        hash2 = CalculationHash.from_calculation(inputs, outputs)

        assert hash1.input_hash == hash2.input_hash
        assert hash1.output_hash == hash2.output_hash
        assert hash1.combined_hash == hash2.combined_hash

    def test_hash_different_for_different_inputs(self) -> None:
        """Test that different inputs produce different hashes."""
        inputs1 = {"b_mm": 300}
        inputs2 = {"b_mm": 350}
        outputs = {"result": 100}

        hash1 = CalculationHash.from_calculation(inputs1, outputs)
        hash2 = CalculationHash.from_calculation(inputs2, outputs)

        assert hash1.input_hash != hash2.input_hash
        assert hash1.combined_hash != hash2.combined_hash

    def test_verify_inputs_success(self) -> None:
        """Test verifying inputs matches."""
        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856}

        calc_hash = CalculationHash.from_calculation(inputs, outputs)

        assert calc_hash.verify_inputs(inputs) is True
        assert calc_hash.verify_inputs({"b_mm": 350, "D_mm": 500}) is False

    def test_verify_outputs_success(self) -> None:
        """Test verifying outputs matches."""
        inputs = {"b_mm": 300}
        outputs = {"ast_required": 856, "is_ok": True}

        calc_hash = CalculationHash.from_calculation(inputs, outputs)

        assert calc_hash.verify_outputs(outputs) is True
        assert calc_hash.verify_outputs({"ast_required": 900}) is False

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        inputs = {"b_mm": 300}
        outputs = {"result": 100}

        calc_hash = CalculationHash.from_calculation(inputs, outputs)
        data = calc_hash.to_dict()

        assert "input_hash" in data
        assert "output_hash" in data
        assert "combined_hash" in data
        assert "algorithm" in data
        assert "timestamp" in data

    def test_hash_handles_complex_types(self) -> None:
        """Test that hash handles complex types (dates, paths, etc.)."""
        inputs = {
            "path": Path("/some/path"),
            "value": 123.456,
            "nested": {"a": [1, 2, 3]},
        }
        outputs = {"success": True}

        # Should not raise
        calc_hash = CalculationHash.from_calculation(inputs, outputs)
        assert calc_hash.input_hash


class TestComputeHash:
    """Tests for compute_hash function."""

    def test_compute_hash_basic(self) -> None:
        """Test basic hash computation."""
        data = {"key": "value", "number": 42}
        result = compute_hash(data)

        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_compute_hash_deterministic(self) -> None:
        """Test that same data produces same hash."""
        data = {"a": 1, "b": 2}

        hash1 = compute_hash(data)
        hash2 = compute_hash(data)

        assert hash1 == hash2

    def test_compute_hash_order_independent(self) -> None:
        """Test that dict order doesn't affect hash (sorted keys)."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}

        assert compute_hash(data1) == compute_hash(data2)


class TestAuditLogEntry:
    """Tests for AuditLogEntry class."""

    def test_entry_creation(self) -> None:
        """Test creating an audit log entry."""
        calc_hash = CalculationHash.from_calculation({"b_mm": 300}, {"result": 100})

        entry = AuditLogEntry(
            entry_id="AUDIT-001",
            timestamp="2026-01-12T10:00:00Z",
            action="design",
            beam_id="B1",
            story="GF",
            inputs_summary={"b_mm": 300},
            outputs_summary={"result": 100},
            hash=calc_hash,
            library_version="0.16.6",
        )

        assert entry.entry_id == "AUDIT-001"
        assert entry.beam_id == "B1"
        assert entry.action == "design"

    def test_entry_to_dict(self) -> None:
        """Test serialization to dictionary."""
        calc_hash = CalculationHash.from_calculation({}, {})

        entry = AuditLogEntry(
            entry_id="AUDIT-001",
            timestamp="2026-01-12T10:00:00Z",
            action="design",
            beam_id="B1",
            story="GF",
            inputs_summary={},
            outputs_summary={},
            hash=calc_hash,
            library_version="0.16.6",
        )

        data = entry.to_dict()

        assert data["entry_id"] == "AUDIT-001"
        assert data["beam_id"] == "B1"
        assert "hash" in data
        assert data["hash"]["algorithm"] == "sha256"


class TestAuditTrail:
    """Tests for AuditTrail class."""

    def test_trail_creation(self) -> None:
        """Test creating an audit trail."""
        trail = AuditTrail(project_id="PROJECT-001")

        assert trail.project_id == "PROJECT-001"
        assert len(trail.entries) == 0
        assert trail.created_at

    def test_log_design(self) -> None:
        """Test logging a design calculation."""
        trail = AuditTrail(project_id="PROJECT-001")

        inputs = {"b_mm": 300, "D_mm": 500, "mu_knm": 150}
        outputs = {"ast_required": 856, "is_ok": True}

        entry = trail.log_design(
            beam_id="B1",
            story="GF",
            inputs=inputs,
            outputs=outputs,
        )

        assert len(trail.entries) == 1
        assert entry.beam_id == "B1"
        assert entry.action == "design"
        assert "AUDIT-PROJECT-001" in entry.entry_id

    def test_log_verification(self) -> None:
        """Test logging a verification check."""
        trail = AuditTrail(project_id="PROJECT-001")

        entry = trail.log_verification(
            beam_id="B1",
            story="GF",
            original_hash="abc123",
            verification_result=True,
        )

        assert entry.action == "verify"
        assert entry.outputs_summary["passed"] is True

    def test_get_entry_by_id(self) -> None:
        """Test finding entry by ID."""
        trail = AuditTrail(project_id="PROJECT-001")

        entry = trail.log_design(
            beam_id="B1",
            story="GF",
            inputs={"b_mm": 300},
            outputs={"result": 100},
        )

        found = trail.get_entry_by_id(entry.entry_id)
        assert found is not None
        assert found.entry_id == entry.entry_id

        not_found = trail.get_entry_by_id("NONEXISTENT")
        assert not_found is None

    def test_get_entries_for_beam(self) -> None:
        """Test getting all entries for a beam."""
        trail = AuditTrail(project_id="PROJECT-001")

        # Log entries for different beams
        trail.log_design("B1", "GF", {"b_mm": 300}, {"result": 100})
        trail.log_design("B1", "1F", {"b_mm": 300}, {"result": 110})
        trail.log_design("B2", "GF", {"b_mm": 350}, {"result": 120})

        b1_entries = trail.get_entries_for_beam("B1")
        assert len(b1_entries) == 2

        b1_gf_entries = trail.get_entries_for_beam("B1", story="GF")
        assert len(b1_gf_entries) == 1

        b2_entries = trail.get_entries_for_beam("B2")
        assert len(b2_entries) == 1

    def test_verify_entry(self) -> None:
        """Test verifying an entry against inputs/outputs."""
        trail = AuditTrail(project_id="PROJECT-001")

        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856, "is_ok": True}

        entry = trail.log_design("B1", "GF", inputs, outputs)

        # Verify with same data
        passed, msg = trail.verify_entry(entry.entry_id, inputs, outputs)
        assert passed is True
        assert "passed" in msg.lower()

        # Verify with modified inputs
        modified_inputs = {"b_mm": 350, "D_mm": 500}
        passed, msg = trail.verify_entry(entry.entry_id, modified_inputs, outputs)
        assert passed is False
        assert "inputs" in msg.lower()

        # Verify with modified outputs
        modified_outputs = {"ast_required": 900, "is_ok": True}
        passed, msg = trail.verify_entry(entry.entry_id, inputs, modified_outputs)
        assert passed is False
        assert "outputs" in msg.lower()

    def test_to_dict_and_json(self) -> None:
        """Test serialization to dict and JSON."""
        trail = AuditTrail(project_id="PROJECT-001")
        trail.log_design("B1", "GF", {"b_mm": 300}, {"result": 100})

        data = trail.to_dict()
        assert data["project_id"] == "PROJECT-001"
        assert data["entry_count"] == 1
        assert len(data["entries"]) == 1

        json_str = trail.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["project_id"] == "PROJECT-001"

    def test_export_and_import(self) -> None:
        """Test exporting and importing audit trail."""
        trail = AuditTrail(project_id="PROJECT-001")
        trail.log_design("B1", "GF", {"b_mm": 300}, {"result": 100})
        trail.log_design("B2", "1F", {"b_mm": 350}, {"result": 120})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.json"
            trail.export_log(path)

            assert path.exists()

            # Load and verify
            loaded = AuditTrail.from_json_file(path)
            assert loaded.project_id == "PROJECT-001"
            assert len(loaded.entries) == 2
            assert loaded.entries[0].beam_id == "B1"
            assert loaded.entries[1].beam_id == "B2"


class TestCalculationCertificate:
    """Tests for calculation certificate functions."""

    def test_create_certificate(self) -> None:
        """Test creating a calculation certificate."""
        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856, "is_ok": True}

        cert = create_calculation_certificate(
            inputs=inputs,
            outputs=outputs,
            project_id="PROJECT-001",
            beam_id="B1",
            engineer="J. Smith",
        )

        assert cert["certificate_type"] == "structural_calculation"
        assert cert["project_id"] == "PROJECT-001"
        assert cert["beam_id"] == "B1"
        assert cert["engineer"] == "J. Smith"
        assert "hash" in cert
        assert cert["hash"]["algorithm"] == "sha256"

    def test_verify_calculation_success(self) -> None:
        """Test verifying a valid certificate."""
        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856, "is_ok": True}

        cert = create_calculation_certificate(inputs, outputs)

        passed, msg = verify_calculation(inputs, outputs, cert)
        assert passed is True
        assert "authentic" in msg.lower()

    def test_verify_calculation_modified_inputs(self) -> None:
        """Test verification fails for modified inputs."""
        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856}

        cert = create_calculation_certificate(inputs, outputs)

        modified_inputs = {"b_mm": 350, "D_mm": 500}
        passed, msg = verify_calculation(modified_inputs, outputs, cert)
        assert passed is False
        assert "inputs" in msg.lower()

    def test_verify_calculation_modified_outputs(self) -> None:
        """Test verification fails for modified outputs."""
        inputs = {"b_mm": 300, "D_mm": 500}
        outputs = {"ast_required": 856}

        cert = create_calculation_certificate(inputs, outputs)

        modified_outputs = {"ast_required": 900}
        passed, msg = verify_calculation(inputs, modified_outputs, cert)
        assert passed is False
        assert "outputs" in msg.lower()

    def test_verify_calculation_both_modified(self) -> None:
        """Test verification fails when both are modified."""
        inputs = {"b_mm": 300}
        outputs = {"result": 100}

        cert = create_calculation_certificate(inputs, outputs)

        passed, msg = verify_calculation({"b_mm": 350}, {"result": 120}, cert)
        assert passed is False
        assert "both" in msg.lower()

    def test_verify_calculation_missing_hash(self) -> None:
        """Test verification fails for invalid certificate."""
        cert = {"certificate_type": "structural_calculation"}

        passed, msg = verify_calculation({}, {}, cert)
        assert passed is False
        assert "missing" in msg.lower()


class TestIntegrationWithApi:
    """Integration tests with api module."""

    def test_api_exports_audit_classes(self) -> None:
        """Test that api exports audit classes."""
        from structural_lib import api

        assert hasattr(api, "AuditTrail")
        assert hasattr(api, "CalculationHash")
        assert hasattr(api, "AuditLogEntry")
        assert hasattr(api, "compute_hash")
        assert hasattr(api, "create_calculation_certificate")
        assert hasattr(api, "verify_calculation")

    def test_audit_with_real_design(self) -> None:
        """Test audit trail with actual design calculation."""
        from structural_lib import api

        # Create audit trail
        trail = api.AuditTrail(project_id="TEST-PROJECT")

        # Perform design
        result = api.design_beam_is456(
            units="IS456",
            case_id="CASE-1",
            mu_knm=150.0,
            vu_kn=80.0,
            b_mm=300.0,
            D_mm=500.0,
            d_mm=460.0,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
        )

        # Log the design
        inputs = {
            "units": "IS456",
            "mu_knm": 150.0,
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 460.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }
        outputs = {
            "is_ok": result.is_ok,
            "ast_required": result.flexure.ast_required,
        }

        entry = trail.log_design(
            beam_id="B1",
            story="GF",
            inputs=inputs,
            outputs=outputs,
        )

        # Verify entry exists
        assert len(trail.entries) == 1
        assert entry.action == "design"

        # Verify hash can be used for verification
        passed, _ = trail.verify_entry(entry.entry_id, inputs, outputs)
        assert passed is True
