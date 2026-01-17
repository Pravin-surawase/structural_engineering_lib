# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       audit
Description:  Verification & Audit Trail for engineering calculations (TASK-278)

Provides:
- SHA-256 hashing for calculation integrity verification
- Immutable audit logs for design decisions
- Reproducibility verification
- Design session tracking

Example:
    >>> from structural_lib.audit import AuditTrail, CalculationHash
    >>> trail = AuditTrail(project_id="PROJECT-001")
    >>> trail.log_design(beam_input, design_result)
    >>> trail.export_log("audit.json")
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Calculation Hash (SHA-256 based integrity verification)
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CalculationHash:
    """Immutable hash of calculation inputs and outputs.

    Used to verify calculation integrity and detect modifications.

    Attributes:
        input_hash: SHA-256 hash of input parameters
        output_hash: SHA-256 hash of calculation results
        combined_hash: Combined hash for quick verification
        algorithm: Hash algorithm used (always 'sha256')
        timestamp: When the hash was computed
    """

    input_hash: str
    output_hash: str
    combined_hash: str
    algorithm: str = "sha256"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def from_calculation(
        cls,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
    ) -> CalculationHash:
        """Create hash from calculation inputs and outputs.

        Args:
            inputs: Dictionary of input parameters
            outputs: Dictionary of calculation results

        Returns:
            CalculationHash with computed hashes
        """
        # Canonicalize JSON (sorted keys, no whitespace variance)
        input_json = json.dumps(inputs, sort_keys=True, default=str)
        output_json = json.dumps(outputs, sort_keys=True, default=str)

        input_hash = hashlib.sha256(input_json.encode()).hexdigest()
        output_hash = hashlib.sha256(output_json.encode()).hexdigest()

        # Combined hash = hash of concatenated hashes
        combined = hashlib.sha256(f"{input_hash}:{output_hash}".encode()).hexdigest()

        return cls(
            input_hash=input_hash,
            output_hash=output_hash,
            combined_hash=combined,
        )

    def verify_inputs(self, inputs: dict[str, Any]) -> bool:
        """Verify that inputs match the stored hash.

        Args:
            inputs: Input parameters to verify

        Returns:
            True if inputs match the stored hash
        """
        input_json = json.dumps(inputs, sort_keys=True, default=str)
        computed = hashlib.sha256(input_json.encode()).hexdigest()
        return computed == self.input_hash

    def verify_outputs(self, outputs: dict[str, Any]) -> bool:
        """Verify that outputs match the stored hash.

        Args:
            outputs: Output results to verify

        Returns:
            True if outputs match the stored hash
        """
        output_json = json.dumps(outputs, sort_keys=True, default=str)
        computed = hashlib.sha256(output_json.encode()).hexdigest()
        return computed == self.output_hash

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "combined_hash": self.combined_hash,
            "algorithm": self.algorithm,
            "timestamp": self.timestamp,
        }


def compute_hash(data: dict[str, Any]) -> str:
    """Compute SHA-256 hash of data dictionary.

    Args:
        data: Dictionary to hash (will be JSON-serialized)

    Returns:
        Hexadecimal hash string
    """
    json_data = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_data.encode()).hexdigest()


# -----------------------------------------------------------------------------
# Audit Log Entry
# -----------------------------------------------------------------------------


@dataclass
class AuditLogEntry:
    """Single entry in the audit log.

    Captures a design decision with full context for reproducibility.

    Attributes:
        entry_id: Unique identifier for this entry
        timestamp: When the action occurred (UTC)
        action: Type of action (design, verify, export, etc.)
        beam_id: Beam identifier
        story: Story/floor identifier
        inputs_summary: Summary of key inputs
        outputs_summary: Summary of key outputs
        hash: Calculation hash for verification
        library_version: Version of the library used
        metadata: Additional context
    """

    entry_id: str
    timestamp: str
    action: str
    beam_id: str
    story: str
    inputs_summary: dict[str, Any]
    outputs_summary: dict[str, Any]
    hash: CalculationHash
    library_version: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "action": self.action,
            "beam_id": self.beam_id,
            "story": self.story,
            "inputs_summary": self.inputs_summary,
            "outputs_summary": self.outputs_summary,
            "hash": self.hash.to_dict(),
            "library_version": self.library_version,
            "metadata": self.metadata,
        }


# -----------------------------------------------------------------------------
# Audit Trail Manager
# -----------------------------------------------------------------------------


@dataclass
class AuditTrail:
    """Manages immutable audit trail for design calculations.

    Provides logging, verification, and export capabilities for
    engineering calculations requiring traceability.

    Attributes:
        project_id: Project identifier
        entries: List of audit log entries (append-only)
        created_at: When the trail was initialized
        library_version: Library version at initialization

    Example:
        >>> trail = AuditTrail(project_id="PROJECT-001")
        >>> # After each design calculation:
        >>> trail.log_design(
        ...     beam_id="B1",
        ...     story="GF",
        ...     inputs={"b_mm": 300, "D_mm": 500, ...},
        ...     outputs={"ast_required": 856, "is_ok": True, ...},
        ... )
        >>> # Export for records
        >>> trail.export_log("audit.json")
    """

    project_id: str
    entries: list[AuditLogEntry] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    library_version: str = ""

    def __post_init__(self) -> None:
        """Initialize library version if not provided."""
        if not self.library_version:
            try:
                from importlib.metadata import version

                self.library_version = version("structural-lib-is456")
            except Exception:
                self.library_version = "unknown"

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        return f"AUDIT-{self.project_id}-{timestamp}-{len(self.entries):04d}"

    def log_design(
        self,
        beam_id: str,
        story: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        """Log a design calculation.

        Args:
            beam_id: Beam identifier
            story: Story/floor identifier
            inputs: Full input parameters
            outputs: Full calculation results
            metadata: Optional additional context

        Returns:
            The created audit log entry
        """
        calc_hash = CalculationHash.from_calculation(inputs, outputs)

        # Create summary of key inputs
        inputs_summary = {
            "b_mm": inputs.get("b_mm"),
            "D_mm": inputs.get("D_mm"),
            "span_mm": inputs.get("span_mm"),
            "fck_nmm2": inputs.get("fck_nmm2"),
            "fy_nmm2": inputs.get("fy_nmm2"),
            "mu_knm": inputs.get("mu_knm"),
            "vu_kn": inputs.get("vu_kn"),
        }

        # Create summary of key outputs
        outputs_summary = {
            "is_ok": outputs.get("is_ok"),
            "ast_required": outputs.get("ast_required"),
            "governing_check": outputs.get("governing_check"),
        }

        entry = AuditLogEntry(
            entry_id=self._generate_entry_id(),
            timestamp=datetime.now(UTC).isoformat(),
            action="design",
            beam_id=beam_id,
            story=story,
            inputs_summary=inputs_summary,
            outputs_summary=outputs_summary,
            hash=calc_hash,
            library_version=self.library_version,
            metadata=metadata or {},
        )

        self.entries.append(entry)
        _logger.info(
            f"Audit logged: {entry.entry_id} - {beam_id}@{story} - hash={calc_hash.combined_hash[:12]}..."
        )

        return entry

    def log_verification(
        self,
        beam_id: str,
        story: str,
        original_hash: str,
        verification_result: bool,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        """Log a verification check.

        Args:
            beam_id: Beam identifier
            story: Story/floor identifier
            original_hash: Hash being verified against
            verification_result: Whether verification passed
            metadata: Optional additional context

        Returns:
            The created audit log entry
        """
        # Create a hash for the verification action itself
        verification_data = {
            "original_hash": original_hash,
            "verification_result": verification_result,
            "beam_id": beam_id,
            "story": story,
        }
        calc_hash = CalculationHash.from_calculation(
            {"action": "verify"}, verification_data
        )

        entry = AuditLogEntry(
            entry_id=self._generate_entry_id(),
            timestamp=datetime.now(UTC).isoformat(),
            action="verify",
            beam_id=beam_id,
            story=story,
            inputs_summary={"original_hash": original_hash[:16] + "..."},
            outputs_summary={"passed": verification_result},
            hash=calc_hash,
            library_version=self.library_version,
            metadata=metadata or {},
        )

        self.entries.append(entry)
        status = "PASSED" if verification_result else "FAILED"
        _logger.info(f"Audit verification: {beam_id}@{story} - {status}")

        return entry

    def get_entry_by_id(self, entry_id: str) -> AuditLogEntry | None:
        """Find entry by ID.

        Args:
            entry_id: Entry ID to find

        Returns:
            Entry if found, None otherwise
        """
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_entries_for_beam(
        self, beam_id: str, story: str | None = None
    ) -> list[AuditLogEntry]:
        """Get all entries for a specific beam.

        Args:
            beam_id: Beam identifier
            story: Optional story filter

        Returns:
            List of matching entries
        """
        results = []
        for entry in self.entries:
            if entry.beam_id == beam_id:
                if story is None or entry.story == story:
                    results.append(entry)
        return results

    def verify_entry(
        self,
        entry_id: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
    ) -> tuple[bool, str]:
        """Verify that inputs/outputs match a logged entry.

        Args:
            entry_id: Entry ID to verify against
            inputs: Inputs to verify
            outputs: Outputs to verify

        Returns:
            Tuple of (passed, message)
        """
        entry = self.get_entry_by_id(entry_id)
        if entry is None:
            return False, f"Entry {entry_id} not found"

        input_ok = entry.hash.verify_inputs(inputs)
        output_ok = entry.hash.verify_outputs(outputs)

        if input_ok and output_ok:
            return True, "Verification passed: inputs and outputs match"
        elif not input_ok and not output_ok:
            return False, "Verification failed: both inputs and outputs modified"
        elif not input_ok:
            return False, "Verification failed: inputs modified"
        else:
            return False, "Verification failed: outputs modified"

    def to_dict(self) -> dict[str, Any]:
        """Serialize audit trail to dictionary."""
        return {
            "project_id": self.project_id,
            "created_at": self.created_at,
            "library_version": self.library_version,
            "entry_count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent)

    def export_log(self, path: str | Path) -> Path:
        """Export audit trail to JSON file.

        Args:
            path: Output file path

        Returns:
            Path to created file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

        _logger.info(f"Audit trail exported to {path}")
        return path

    @classmethod
    def from_json_file(cls, path: str | Path) -> AuditTrail:
        """Load audit trail from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            Loaded AuditTrail instance
        """
        path = Path(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        trail = cls(
            project_id=data["project_id"],
            created_at=data.get("created_at", ""),
            library_version=data.get("library_version", ""),
        )

        # Reconstruct entries
        for entry_data in data.get("entries", []):
            hash_data = entry_data["hash"]
            calc_hash = CalculationHash(
                input_hash=hash_data["input_hash"],
                output_hash=hash_data["output_hash"],
                combined_hash=hash_data["combined_hash"],
                algorithm=hash_data.get("algorithm", "sha256"),
                timestamp=hash_data.get("timestamp", ""),
            )

            entry = AuditLogEntry(
                entry_id=entry_data["entry_id"],
                timestamp=entry_data["timestamp"],
                action=entry_data["action"],
                beam_id=entry_data["beam_id"],
                story=entry_data["story"],
                inputs_summary=entry_data["inputs_summary"],
                outputs_summary=entry_data["outputs_summary"],
                hash=calc_hash,
                library_version=entry_data.get("library_version", ""),
                metadata=entry_data.get("metadata", {}),
            )
            trail.entries.append(entry)

        return trail


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------


def create_calculation_certificate(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    project_id: str = "",
    beam_id: str = "",
    engineer: str = "",
) -> dict[str, Any]:
    """Create a calculation certificate for verification.

    A certificate is a compact document that can be used to verify
    that a calculation was performed with specific inputs and produced
    specific outputs.

    Args:
        inputs: Full input parameters
        outputs: Full calculation results
        project_id: Project identifier
        beam_id: Beam identifier
        engineer: Engineer name/ID

    Returns:
        Certificate dictionary with hashes and metadata
    """
    calc_hash = CalculationHash.from_calculation(inputs, outputs)

    try:
        from importlib.metadata import version

        lib_version = version("structural-lib-is456")
    except Exception:
        lib_version = "unknown"

    return {
        "certificate_type": "structural_calculation",
        "version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "project_id": project_id,
        "beam_id": beam_id,
        "engineer": engineer,
        "library_version": lib_version,
        "hash": calc_hash.to_dict(),
        "verification_instructions": (
            "To verify this certificate, compute SHA-256 hashes of the "
            "canonicalized JSON inputs and outputs. Compare with stored hashes."
        ),
    }


def verify_calculation(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    certificate: dict[str, Any],
) -> tuple[bool, str]:
    """Verify a calculation against a certificate.

    Args:
        inputs: Inputs to verify
        outputs: Outputs to verify
        certificate: Certificate from create_calculation_certificate

    Returns:
        Tuple of (passed, message)
    """
    hash_data = certificate.get("hash", {})
    stored_input_hash = hash_data.get("input_hash", "")
    stored_output_hash = hash_data.get("output_hash", "")

    if not stored_input_hash or not stored_output_hash:
        return False, "Certificate missing hash data"

    # Compute current hashes
    input_json = json.dumps(inputs, sort_keys=True, default=str)
    output_json = json.dumps(outputs, sort_keys=True, default=str)

    computed_input = hashlib.sha256(input_json.encode()).hexdigest()
    computed_output = hashlib.sha256(output_json.encode()).hexdigest()

    input_match = computed_input == stored_input_hash
    output_match = computed_output == stored_output_hash

    if input_match and output_match:
        return True, "Verification passed: calculation is authentic"
    elif not input_match and not output_match:
        return False, "Verification failed: both inputs and outputs differ"
    elif not input_match:
        return False, "Verification failed: inputs have been modified"
    else:
        return False, "Verification failed: outputs have been modified"
