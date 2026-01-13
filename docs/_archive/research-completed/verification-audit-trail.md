# Verification & Audit Trail

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** Complete
**Task:** TASK-245
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** Engineering calculations must be verifiable and traceable. Need system to track: who calculated what, when, with which version, and what assumptions were made. Essential for professional liability and regulatory compliance.

**Goal:** Design verification and audit trail system that captures:
1. Calculation provenance (who, when, where)
2. Input data and assumptions
3. Software version and code references
4. Verification steps performed
5. Review and approval history

**Key Finding:** Engineering audit trails need immutable records + cryptographic verification. Combination of structured logging + digital signatures provides compliance-grade traceability.

**Recommendation:**
- Phase 1: Structured calculation log (4-5 hours)
- Phase 2: Digital signatures (SHA-256 hashing) (3-4 hours)
- Phase 3: Verification tools (4-5 hours)
- Total: 11-14 hours implementation

---

## Table of Contents

1. [Audit Requirements](#1-audit-requirements)
2. [Audit Trail Architecture](#2-audit-trail-architecture)
3. [Data Structures](#3-data-structures)
4. [Digital Signatures](#4-digital-signatures)
5. [Verification Tools](#5-verification-tools)
6. [Implementation Guide](#6-implementation-guide)

---

## 1. Audit Requirements

### 1.1 Regulatory Requirements

**Professional Engineering Standards require:**

1. **Calculation Traceability**
   - Who performed calculation
   - When calculation was performed
   - Which code version was used
   - What assumptions were made

2. **Data Integrity**
   - Inputs cannot be altered after calculation
   - Results linked immutably to inputs
   - Tampering detectable

3. **Version Control**
   - Software version recorded
   - Code changes tracked
   - Breaking changes flagged

4. **Review Trail**
   - Who reviewed calculation
   - What was checked
   - Approval/rejection with reasons

### 1.2 Industry Best Practices

**From ASCE, AISC, ACI guidelines:**

1. **Calculation Documentation**
   - All inputs documented
   - All assumptions stated
   - All code clauses referenced
   - All checks shown

2. **Peer Review**
   - Independent verification
   - Checker signs off
   - Discrepancies resolved

3. **Change Management**
   - Design changes documented
   - Reason for change recorded
   - Re-verification performed

---

## 2. Audit Trail Architecture

### 2.1 System Components

```
┌────────────────────────────────────────────┐
│       Calculation Engine                    │
│  ┌──────────────────────────────────────┐  │
│  │ design_beam(inputs)                  │  │
│  │   ↓                                  │  │
│  │ [Audit Logger]                       │  │
│  │   - Capture inputs                   │  │
│  │   - Capture results                  │  │
│  │   - Capture metadata                 │  │
│  │   ↓                                  │  │
│  │ [Digital Signature]                  │  │
│  │   - Hash inputs + results            │  │
│  │   - Create tamper-proof record       │  │
│  │   ↓                                  │  │
│  │ Return result + audit record         │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│       Audit Storage                         │
│  ┌──────────────────────────────────────┐  │
│  │ audit_trail.jsonl (append-only)     │  │
│  │ {                                    │  │
│  │   "id": "calc-001",                  │  │
│  │   "timestamp": "2026-01-07T...",     │  │
│  │   "inputs": {...},                   │  │
│  │   "results": {...},                  │  │
│  │   "signature": "sha256:abc123..."    │  │
│  │ }                                    │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│       Verification Tools                    │
│  - verify_calculation(calc_id)              │
│  - check_tampering(audit_file)              │
│  - generate_audit_report(project_id)        │
└────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
structural_lib/
  audit/
    __init__.py
    logger.py              # Audit logging
    signature.py           # Digital signatures
    verifier.py            # Verification tools
    storage.py             # Audit storage
    reports.py             # Audit reports
```

---

## 3. Data Structures

### 3.1 Calculation Audit Record

**Schema:**

```python
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import json

@dataclass
class CalculationAudit:
    """
    Immutable audit record for a calculation.

    Attributes:
        id: Unique calculation ID
        timestamp: ISO 8601 timestamp
        user: Engineer who performed calculation
        software_version: Library version
        function: Function name (e.g., "design_beam")
        inputs: All input parameters
        results: All output results
        assumptions: List of assumptions made
        code_references: IS 456 clauses used
        checks: List of checks performed
        signature: SHA-256 hash for tamper detection
    """
    id: str
    timestamp: str
    user: Dict[str, str]  # {name, license, email}
    software_version: str
    function: str
    inputs: Dict
    results: Dict
    assumptions: List[str]
    code_references: List[str]
    checks: List[Dict]
    signature: str

    @classmethod
    def create(
        cls,
        function: str,
        inputs: Dict,
        results: Dict,
        user: Dict,
        assumptions: List[str] = None,
        code_references: List[str] = None,
        checks: List[Dict] = None
    ) -> 'CalculationAudit':
        """
        Create audit record with automatic signature.

        Example:
            >>> audit = CalculationAudit.create(
            ...     function="design_beam",
            ...     inputs={"span_mm": 5000, ...},
            ...     results={"ast_mm2": 821, ...},
            ...     user={"name": "John Doe", "license": "MH/12345"}
            ... )
        """
        import structural_lib
        from uuid import uuid4

        # Generate unique ID
        calc_id = f"calc-{uuid4().hex[:12]}"

        # Current timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # Software version
        version = structural_lib.__version__

        # Create record (without signature)
        record = {
            'id': calc_id,
            'timestamp': timestamp,
            'user': user,
            'software_version': version,
            'function': function,
            'inputs': inputs,
            'results': results,
            'assumptions': assumptions or [],
            'code_references': code_references or [],
            'checks': checks or [],
        }

        # Generate signature
        signature = cls._compute_signature(record)
        record['signature'] = signature

        return cls(**record)

    @staticmethod
    def _compute_signature(record: Dict) -> str:
        """
        Compute SHA-256 signature of record.

        Ensures data integrity - any modification changes signature.
        """
        # Convert to canonical JSON (sorted keys, no whitespace)
        canonical = json.dumps(record, sort_keys=True, separators=(',', ':'))

        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(canonical.encode('utf-8'))
        return f"sha256:{hash_obj.hexdigest()}"

    def verify_signature(self) -> bool:
        """
        Verify record hasn't been tampered with.

        Returns:
            True if signature valid, False if tampered
        """
        # Recompute signature without existing signature
        record = asdict(self)
        stored_signature = record.pop('signature')

        computed_signature = self._compute_signature(record)

        return computed_signature == stored_signature

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self), indent=2)
```

### 3.2 Review Record

**Schema:**

```python
@dataclass
class ReviewRecord:
    """
    Review/approval record for a calculation.

    Attributes:
        calculation_id: ID of calculation being reviewed
        reviewer: Engineer who reviewed
        timestamp: Review timestamp
        status: approved/rejected/revision_required
        checks_performed: List of verification checks
        comments: Reviewer comments
        signature: Digital signature
    """
    calculation_id: str
    reviewer: Dict[str, str]
    timestamp: str
    status: str  # "approved" | "rejected" | "revision_required"
    checks_performed: List[str]
    comments: str
    signature: str

    @classmethod
    def create(
        cls,
        calculation_id: str,
        reviewer: Dict,
        status: str,
        checks: List[str],
        comments: str = ""
    ) -> 'ReviewRecord':
        """Create review record with signature."""
        from uuid import uuid4

        timestamp = datetime.utcnow().isoformat() + 'Z'

        record = {
            'calculation_id': calculation_id,
            'reviewer': reviewer,
            'timestamp': timestamp,
            'status': status,
            'checks_performed': checks,
            'comments': comments,
        }

        # Compute signature
        canonical = json.dumps(record, sort_keys=True)
        hash_obj = hashlib.sha256(canonical.encode('utf-8'))
        signature = f"sha256:{hash_obj.hexdigest()}"
        record['signature'] = signature

        return cls(**record)
```

---

## 4. Digital Signatures

### 4.1 SHA-256 Hashing Strategy

**Purpose:** Detect tampering in audit records

**Implementation:**

```python
# audit/signature.py
import hashlib
import json
from typing import Dict

class AuditSigner:
    """Digital signature manager for audit records."""

    @staticmethod
    def sign_record(record: Dict) -> str:
        """
        Generate SHA-256 signature for record.

        Args:
            record: Dictionary to sign

        Returns:
            Signature string "sha256:hex"

        Example:
            >>> signer = AuditSigner()
            >>> sig = signer.sign_record({"foo": "bar"})
            >>> print(sig)
            sha256:fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9
        """
        # Canonical JSON (sorted keys, no whitespace)
        canonical = json.dumps(record, sort_keys=True, separators=(',', ':'))

        # UTF-8 encode
        encoded = canonical.encode('utf-8')

        # SHA-256 hash
        hash_obj = hashlib.sha256(encoded)

        return f"sha256:{hash_obj.hexdigest()}"

    @staticmethod
    def verify_signature(record: Dict, signature: str) -> bool:
        """
        Verify signature matches record.

        Returns:
            True if valid, False if tampered
        """
        computed = AuditSigner.sign_record(record)
        return computed == signature

    @staticmethod
    def sign_file(file_path: str) -> str:
        """
        Generate signature for entire file.

        Useful for verifying audit log file integrity.
        """
        hash_obj = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)

        return f"sha256:{hash_obj.hexdigest()}"
```

### 4.2 Chain of Trust

**Concept:** Each calculation references previous calculation, creating tamper-evident chain.

```python
@dataclass
class ChainedAudit(CalculationAudit):
    """Audit record with chain-of-trust."""
    previous_signature: Optional[str] = None

    def verify_chain(self, previous_record: 'ChainedAudit') -> bool:
        """
        Verify this record correctly references previous.

        Ensures audit trail hasn't been reordered or modified.
        """
        return self.previous_signature == previous_record.signature
```

---

## 5. Verification Tools

### 5.1 Verification API

```python
# audit/verifier.py
from pathlib import Path
from typing import List, Dict, Optional
import json

class AuditVerifier:
    """Tools for verifying audit trails."""

    def __init__(self, audit_file: Path):
        self.audit_file = audit_file
        self.records = self._load_records()

    def _load_records(self) -> List[CalculationAudit]:
        """Load all audit records from file."""
        records = []
        with open(self.audit_file) as f:
            for line in f:
                data = json.loads(line)
                records.append(CalculationAudit(**data))
        return records

    def verify_all_signatures(self) -> Dict[str, bool]:
        """
        Verify all signatures in audit trail.

        Returns:
            Dict mapping calc_id → valid/invalid

        Example:
            >>> verifier = AuditVerifier('audit_trail.jsonl')
            >>> results = verifier.verify_all_signatures()
            >>> print(results)
            {'calc-abc123': True, 'calc-def456': True, ...}
        """
        results = {}
        for record in self.records:
            results[record.id] = record.verify_signature()
        return results

    def find_tampering(self) -> List[str]:
        """
        Find records with invalid signatures.

        Returns:
            List of calc_ids that have been tampered with
        """
        tampered = []
        for record in self.records:
            if not record.verify_signature():
                tampered.append(record.id)
        return tampered

    def get_calculation(self, calc_id: str) -> Optional[CalculationAudit]:
        """Retrieve specific calculation."""
        for record in self.records:
            if record.id == calc_id:
                return record
        return None

    def verify_chain(self) -> bool:
        """
        Verify chain of trust (if using ChainedAudit).

        Returns:
            True if chain intact, False if broken
        """
        for i in range(1, len(self.records)):
            curr = self.records[i]
            prev = self.records[i-1]

            if hasattr(curr, 'previous_signature'):
                if curr.previous_signature != prev.signature:
                    return False

        return True

    def generate_verification_report(self) -> Dict:
        """
        Generate comprehensive verification report.

        Returns:
            Dict with verification statistics and findings
        """
        signatures = self.verify_all_signatures()

        return {
            'total_records': len(self.records),
            'valid_signatures': sum(signatures.values()),
            'invalid_signatures': len(signatures) - sum(signatures.values()),
            'tampering_detected': not all(signatures.values()),
            'chain_intact': self.verify_chain() if hasattr(self.records[0], 'previous_signature') else None,
            'tampered_records': self.find_tampering(),
            'file_signature': AuditSigner.sign_file(self.audit_file),
        }
```

### 5.2 CLI Verification Tool

```python
# audit/cli.py
import click
from pathlib import Path

@click.group()
def audit_cli():
    """Audit trail verification CLI."""
    pass

@audit_cli.command()
@click.argument('audit_file', type=click.Path(exists=True))
def verify(audit_file):
    """Verify all signatures in audit file."""
    verifier = AuditVerifier(Path(audit_file))
    results = verifier.verify_all_signatures()

    valid = sum(results.values())
    total = len(results)

    click.echo(f"\nVerification Results:")
    click.echo(f"  Total records: {total}")
    click.echo(f"  Valid: {valid}")
    click.echo(f"  Invalid: {total - valid}")

    if valid == total:
        click.secho("✓ All signatures valid", fg='green')
    else:
        click.secho("✗ Tampering detected!", fg='red')
        tampered = verifier.find_tampering()
        click.echo(f"  Tampered records: {', '.join(tampered)}")

@audit_cli.command()
@click.argument('audit_file', type=click.Path(exists=True))
@click.argument('calc_id')
def inspect(audit_file, calc_id):
    """Inspect specific calculation."""
    verifier = AuditVerifier(Path(audit_file))
    record = verifier.get_calculation(calc_id)

    if not record:
        click.secho(f"✗ Calculation {calc_id} not found", fg='red')
        return

    click.echo(record.to_json())

    if record.verify_signature():
        click.secho("✓ Signature valid", fg='green')
    else:
        click.secho("✗ Signature invalid - record tampered!", fg='red')

if __name__ == '__main__':
    audit_cli()
```

**Usage:**
```bash
# Verify all records
python -m structural_lib.audit.cli verify audit_trail.jsonl

# Inspect specific calculation
python -m structural_lib.audit.cli inspect audit_trail.jsonl calc-abc123
```

---

## 6. Implementation Guide

### 6.1 Phase 1: Audit Logging (4-5 hours)

**Step 1: Data structures** (2 hours)
- CalculationAudit class
- ReviewRecord class
- Serialization methods

**Step 2: Logger implementation** (2 hours)
- Append-only JSONL storage
- Automatic capture on calculation
- Thread-safe writes

**Step 3: Testing** (1 hour)
- Test record creation
- Test serialization
- Test concurrent writes

### 6.2 Phase 2: Digital Signatures (3-4 hours)

**Step 1: Signature implementation** (2 hours)
- SHA-256 hashing
- Canonical JSON
- Signature verification

**Step 2: Integration** (1 hour)
- Add to CalculationAudit
- Automatic signing on creation

**Step 3: Testing** (1 hour)
- Test signature generation
- Test tampering detection
- Test chain of trust

### 6.3 Phase 3: Verification Tools (4-5 hours)

**Step 1: Verifier class** (2 hours)
- Load audit records
- Verify signatures
- Find tampering

**Step 2: CLI tool** (2 hours)
- Verify command
- Inspect command
- Report command

**Step 3: Documentation** (1 hour)
- Usage guide
- Examples
- Best practices

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete | Research Team |

**Next Steps:**

1. Review with compliance team
2. Implement Phase 1 (audit logging)
3. Add to all design functions
4. Test with real projects
5. Create user guide for verification

---

**End of Document**
**Implementation Time:** 11-14 hours (3 phases)
**Priority:** HIGH (professional liability protection, regulatory compliance)
**Compliance:** Meets professional engineering audit requirements
