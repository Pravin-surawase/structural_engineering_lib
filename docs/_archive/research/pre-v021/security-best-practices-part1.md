# Security Best Practices for Engineering Software

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** In Progress (Part 1/2)
**Task:** TASK-260
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** Engineering software handles sensitive data (project designs, calculations) and must be secure before public release. No current security review exists.

**Scope:** Research security best practices for Python libraries focusing on:
1. Input validation & sanitization
2. Dependency security
3. Code signing & distribution
4. Data privacy
5. Supply chain security

**Key Finding:** Engineering libraries have unique security needs—calculation integrity is as critical as traditional security. Malicious or buggy inputs could cause unsafe designs.

**Recommendation:**
- Phase 1: Input validation & sanitization (4-6 hours)
- Phase 2: Dependency scanning & updates (2-3 hours)
- Phase 3: Code signing & secure distribution (3-4 hours)
- Phase 4: Security documentation (2-3 hours)

---

## Table of Contents

1. [Security Threat Model](#1-security-threat-model)
2. [Input Validation & Sanitization](#2-input-validation--sanitization)
3. [Dependency Security](#3-dependency-security)
4. [Code Signing & Distribution](#4-code-signing--distribution)
5. [Data Privacy & Confidentiality](#5-data-privacy--confidentiality)
6. [Supply Chain Security](#6-supply-chain-security)
7. [Security Testing](#7-security-testing)
8. [Implementation Roadmap](#8-implementation-roadmap)

---

## 1. Security Threat Model

### 1.1 Threat Categories for Engineering Software

**Threat 1: Malicious Input**
- Attacker crafts input to cause:
  - Code execution (SQL injection, eval)
  - Denial of service (infinite loops, memory exhaustion)
  - Incorrect calculations (unsafe designs)

**Threat 2: Dependency Vulnerabilities**
- Third-party packages have known CVEs
- Transitive dependencies introduce vulner abilities
- Outdated packages lack security patches

**Threat 3: Supply Chain Attacks**
- Malicious PyPI package (typosquatting)
- Compromised maintainer account
- Malicious code injection in CI/CD

**Threat 4: Data Exfiltration**
- Design files contain proprietary information
- Calculations reveal business intelligence
- Project data sent to unauthorized servers

**Threat 5: Integrity Attacks**
- Tampered library produces incorrect results
- Malicious actor modifies source code
- Man-in-the-middle attacks during distribution

### 1.2 Unique Engineering Software Risks

**Risk 1: Calculation Integrity = Safety**

Unlike typical software bugs, calculation errors can cause:
- Building failures
- Structural collapse
- Loss of life
- Legal liability

**Example Attack Scenario:**
```python
# Malicious input exploits calculation bug
beam_data = {
    'span_mm': 1e100,  # Unrealistic value causes overflow
    'width_mm': 0.001,  # Causes division by zero
    'depth_mm': -500,   # Negative value bypasses checks
}

# Result: Library crashes OR produces unsafe design
result = design_beam(beam_data)
# Result claims beam is safe when it's not!
```

**Risk 2: Professional Liability**

Engineers using the library are professionally liable for designs. If library produces incorrect results due to security vulnerability, engineer's license at risk.

**Risk 3: Silent Failures**

Security bugs in engineering code may not cause crashes—they produce wrong numbers:
```python
# Bug: Integer overflow not caught
strength = calculate_strength(very_large_input)
# Returns wrong value but no error
# Engineer uses wrong value → Unsafe design
```

---

## 2. Input Validation & Sanitization

### 2.1 Validation Strategy

**Principle:** Validate all inputs at the boundary (earliest point possible).

**Three-Layer Validation:**

**Layer 1: Type Validation**
```python
from typing import Union

def design_beam(
    span_mm: float,
    width_mm: float,
    ...
) -> BeamDesignResult:
    # Type checking via type hints (static)
    # Runtime checking (if needed)
    if not isinstance(span_mm, (int, float)):
        raise TypeError(
            f"span_mm must be numeric, got {type(span_mm).__name__}"
        )
```

**Layer 2: Range Validation**
```python
def design_beam(span_mm: float, ...) -> BeamDesignResult:
    # Physical constraints
    if span_mm <= 0:
        raise ValueError("span_mm must be positive")

    if span_mm > 50000:  # Unrealistic for RC beams
        raise ValueError(
            f"span_mm={span_mm} exceeds maximum (50000 mm). "
            "Check units or use specialized analysis."
        )

    # Overflow protection
    if span_mm > 1e10:
        raise ValueError("span_mm too large (potential overflow)")
```

**Layer 3: Cross-Parameter Validation**
```python
def design_beam(
    span_mm: float,
    width_mm: float,
    depth_mm: float,
    ...
) -> BeamDesignResult:
    # Relationship constraints
    if depth_mm > span_mm:
        raise ValueError(
            f"Depth ({depth_mm}) cannot exceed span ({span_mm}). "
            "Check dimensions."
        )

    # Aspect ratio sanity check
    ratio = span_mm / depth_mm
    if ratio > 50:
        import warnings
        warnings.warn(
            f"Unusual span/depth ratio: {ratio:.1f}. "
            "Typical range: 10-25. Verify inputs.",
            UserWarning
        )
```

### 2.2 String Input Sanitization

**Risk:** String inputs (material names, file paths) can be attack vectors.

**Pattern 1: Enum/Literal for Material Grades**
```python
from typing import Literal

def design_beam(
    fck: Literal['M15', 'M20', 'M25', 'M30', 'M35', 'M40'],  # Only these values allowed
    fy: Literal['Fe250', 'Fe415', 'Fe500', 'Fe550'],
    ...
):
    # Type checker ensures only valid values passed
    # No risk of SQL injection or code injection
    pass
```

**Pattern 2: Whitelist for File Paths**
```python
import os
from pathlib import Path

def load_beam_data(file_path: str) -> dict:
    """
    Load beam data from file.

    Security: Only allows files in approved directories.
    """
    path = Path(file_path).resolve()

    # Whitelist approved directories
    allowed_dirs = [
        Path.home() / 'structural_projects',
        Path('/tmp/structural_lib'),
    ]

    if not any(path.is_relative_to(d) for d in allowed_dirs):
        raise PermissionError(
            f"File access denied: {path}. "
            f"Allowed directories: {allowed_dirs}"
        )

    # Prevent directory traversal
    if '..' in str(path):
        raise ValueError("Path traversal not allowed")

    # Check file extension
    if path.suffix not in ['.json', '.xlsx', '.csv']:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            "Allowed: .json, .xlsx, .csv"
        )

    # Load file
    ...
```

### 2.3 Numeric Overflow Protection

**Risk:** Large numbers can cause integer/float overflow.

**Protection Strategy:**
```python
import sys

MAX_SAFE_FLOAT = 1e15  # Conservative limit

def validate_numeric(value: float, name: str) -> None:
    """Validate numeric input for overflow protection."""
    if abs(value) > MAX_SAFE_FLOAT:
        raise ValueError(
            f"{name}={value} exceeds safe range. "
            f"Maximum: {MAX_SAFE_FLOAT}"
        )

    if not math.isfinite(value):
        raise ValueError(
            f"{name}={value} is not finite (inf/nan detected)"
        )
```

### 2.4 Injection Prevention

**Risk:** If library uses eval(), exec(), or subprocess, attacker can inject code.

**Rule: Never use eval/exec on user input**

```python
# ❌ DANGEROUS - Never do this
def calculate_custom_formula(formula: str, params: dict):
    # User provides formula="__import__('os').system('rm -rf /')"
    result = eval(formula, params)  # Code execution!
    return result

# ✅ SAFE - Use ast.literal_eval or safe expression parser
import ast

def calculate_custom_formula(formula: str, params: dict):
    # Only allow simple math expressions
    try:
        tree = ast.parse(formula, mode='eval')
        # Check tree only contains allowed operations
        if not is_safe_expression(tree):
            raise ValueError("Unsafe expression")
        result = eval(compile(tree, '', 'eval'), {"__builtins__": {}}, params)
        return result
    except:
        raise ValueError("Invalid formula")
```

---

## 3. Dependency Security

### 3.1 Dependency Scanning

**Tool 1: pip-audit** (Official Python Security Tool)

```bash
# Install
pip install pip-audit

# Scan for vulnerabilities
pip-audit

# Example output:
# Found 2 vulnerabilities
# ├── numpy (1.22.0)
# │   └── CVE-2021-33430 (HIGH)
# │       Upgrade to numpy>=1.22.1
# └── pillow (8.3.0)
#     └── CVE-2022-22817 (CRITICAL)
#         Upgrade to pillow>=9.0.0
```

**Tool 2: Safety** (Alternative)

```bash
pip install safety

# Check dependencies
safety check

# Check requirements file
safety check -r requirements.txt
```

### 3.2 Dependency Pinning Strategy

**Approach:** Pin major/minor versions, allow patch updates.

**requirements.txt:**
```txt
# Pin major.minor, allow patches
numpy>=1.23,<1.24
pandas>=2.0,<2.1
ezdxf>=1.1,<1.2

# Critical dependencies: pin exact version
cryptography==41.0.7
```

**pyproject.toml:**
```toml
[project]
dependencies = [
    "numpy>=1.23,<1.24",
    "pandas>=2.0,<2.1",
    "ezdxf>=1.1,<1.2",
]
```

**Why This Strategy:**
- ✅ Get security patches automatically (patch version)
- ✅ Avoid breaking changes (major/minor pinned)
- ❌ Don't pin exact patch (miss security updates)

### 3.3 Automated Dependency Updates

**Tool: Dependabot** (GitHub built-in)

**.github/dependabot.yml:**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/Python"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    # Auto-merge security updates
    reviewers:
      - "maintainer-team"
    labels:
      - "dependencies"
      - "security"
```

**Benefits:**
- Automatic PRs for dependency updates
- Security alerts in GitHub
- Can auto-merge security patches

### 3.4 Supply Chain Verification

**Verify Package Integrity:**
```bash
# Check package hashes
pip install --require-hashes -r requirements.txt

# requirements.txt with hashes:
numpy==1.23.5 \
    --hash=sha256:1234abcd...
```

**Verify Package Source:**
```python
# Check where package was installed from
import numpy
print(numpy.__file__)
# /Users/.../site-packages/numpy/__init__.py

# Verify it's from PyPI (not local or malicious source)
```

---

## 4. Code Signing & Distribution

### 4.1 PyPI Package Signing

**Goal:** Users can verify package authenticity.

**Current State:** PyPI doesn't support package signing yet (PEP 480 deferred).

**Workaround: Provide Checksums**

```bash
# Generate SHA256 checksums
sha256sum dist/structural_lib-0.15.0-py3-none-any.whl > checksums.txt

# Users verify:
sha256sum -c checksums.txt
```

**Future: Sigstore/in-toto**

When PEP 480 adopted:
```bash
# Sign package
python -m build --sign

# Users verify signature
pip install structural-lib-is456 --verify-signature
```

### 4.2 GitHub Release Security

**Secure Release Workflow:**

1. **Tag release with GPG signature:**
```bash
# Create signed tag
git tag -s v0.15.0 -m "Release v0.15.0"

# Push tag
git push origin v0.15.0
```

2. **Build in CI (not locally):**
``yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

**Why CI-built:**
- ✅ Reproducible builds
- ✅ No local machine compromise
- ✅ Audit trail in GitHub Actions logs

---

**(Part 1/2 complete - continuing in next file)**
