# AI Agent Coding Guide

**Type:** Guide
**Audience:** AI Agents (Claude, GPT, Copilot) and Developers
**Status:** Active
**Importance:** Critical
**Created:** 2026-01-21
**Last Updated:** 2026-01-21
**Scope:** All code contributions to structural_engineering_lib

---

## Executive Summary

This guide ensures consistent, high-quality code from all AI agents working on this project. Every AI agent MUST read and follow this guide before writing any code.

**Core Principles:**
1. Library-first: All logic belongs in `structural_lib`, UI is a thin wrapper
2. Reuse over rewrite: Search existing code before creating new
3. Test before commit: No code without tests
4. Plan before code: Understand the full context before making changes
5. Document as you go: Code without docs is incomplete

---

## Infrastructure Audit Summary (Snapshot)

**Snapshot date:** 2026-01-21

### Tests (134 test files)

| Category | Files | Location |
| --- | --- | --- |
| Unit | 22 | `Python/tests/unit/` |
| Integration | 38 | `Python/tests/integration/` |
| Regression | 8 | `Python/tests/regression/` |
| Property (Hypothesis) | 5 | `Python/tests/property/` |
| Performance | 1 | `Python/tests/performance/` |
| Root tests | 17 | `Python/tests/` |
| Streamlit | 43 | `streamlit_app/tests/` |

### CI/CD (13 GitHub workflows)

`python-tests.yml`, `fast-checks.yml`, `nightly.yml`, `security.yml`, `codeql.yml`,
`streamlit-validation.yml`, `publish.yml`, `governance-health.yml`,
`leading-indicator-alerts.yml`, `auto-format.yml`, `root-file-limit.yml`,
`git-workflow-tests.yml`, `cost-optimizer-analysis.yml`

### Pre-commit hooks

30+ hooks (see `.pre-commit-config.yaml`).

### Scripts (156 total)

- Python: 90 scripts
- Shell: 55 scripts
- Key scripts: `ai_commit.sh`, `safe_push.sh`, `ci_local.sh`, `agent_start.sh`

### Library (structural_lib)

- 79 Python files covering flexure, shear, torsion, detailing, serviceability.
- Adapters: ETABS, SAFE, STAAD, Generic CSV.
- Insights: cost optimization, smart designer, sensitivity, constructability.
- Codes: IS 456 with multi-code architecture stubs.

### Documentation

- Guides: 4 (`AI_AGENT_CODING_GUIDE`, `TESTING_AND_CICD_STRATEGY`,
  `CODE_REUSE_AND_LIBRARY_STRUCTURE`, `etabs-vba-user-guide`)
- Planning: 35 docs
- Research: 97 docs

**Note:** Counts are a snapshot. Refresh using:
`find Python/tests streamlit_app/tests -type f -name "test_*.py" | wc -l`

---

## Table of Contents

0. [Infrastructure Audit Summary (Snapshot)](#infrastructure-audit-summary-snapshot)
1. [Before Writing Any Code](#1-before-writing-any-code)
2. [Code Organization](#2-code-organization)
3. [Python Coding Standards](#3-python-coding-standards)
4. [TypeScript/JavaScript Standards](#4-typescriptjavascript-standards)
5. [Testing Requirements](#5-testing-requirements)
6. [Error Handling](#6-error-handling)
7. [Documentation Standards](#7-documentation-standards)
8. [API Design Patterns](#8-api-design-patterns)
9. [Performance Guidelines](#9-performance-guidelines)
10. [Security Checklist](#10-security-checklist)
11. [Pre-Commit Checklist](#11-pre-commit-checklist)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Debugging Guide](#13-debugging-guide)
14. [Code Review Criteria](#14-code-review-criteria)

---

## 1. Before Writing Any Code

### 1.1 Mandatory Context Check

Before writing ANY code, you MUST:

```
□ Read the relevant research docs in docs/research/
□ Read docs/guides/TESTING_AND_CICD_STRATEGY.md
□ Read docs/guides/CODE_REUSE_AND_LIBRARY_STRUCTURE.md
□ Check docs/planning/8-week-development-plan.md for current phase
□ Search existing code for similar functionality
□ Review docs/adr/ for architectural decisions
□ Understand the full file you're modifying (not just the function)
```

### 1.2 Questions to Ask Yourself

1. **Does this already exist?** Search before creating.
2. **Does this belong in the library?** If it's computation/logic, YES.
3. **Will this break existing code?** Check all callers.
4. **Is this the simplest solution?** Avoid over-engineering.
5. **Can I reuse existing patterns?** Copy proven patterns.

### 1.3 File Search Commands

```bash
# Search for existing functions
rg -n "def function_name" Python/structural_lib/

# Search for similar patterns
rg -n "pattern_keyword" --glob="*.py" .

# Find all usages of a function
rg -n "function_name\\(" --glob="*.py" .
```

---

## 2. Code Organization

### 2.1 Project Structure

```
structural_engineering_lib/
├── Python/
│   └── structural_lib/           # CORE LIBRARY (all computation here)
│       ├── api.py                # Public API (entry points)
│       ├── flexure.py            # Flexure calculations
│       ├── shear.py              # Shear calculations
│       ├── detailing.py          # Rebar detailing
│       ├── adapters.py           # ETABS, SAFE, STAAD import
│       ├── insights/             # Smart analysis, optimization
│       ├── visualization/        # Geometry generation (not rendering)
│       └── codes/is456/          # Code compliance
├── streamlit_app/                # UI ONLY (thin wrapper)
│   ├── components/               # UI components
│   ├── ai/                       # AI tools and handlers
│   └── static/                   # Static assets
├── tests/                        # All tests
└── docs/                         # Documentation
```

### 2.2 Where Code Should Go

| Code Type | Location | Example |
| --- | --- | --- |
| Design calculations | `structural_lib/` | `design_beam_is456()` |
| IS 456 compliance | `structural_lib/codes/is456/` | `check_clause_26_5_1()` |
| Data import/export | `structural_lib/adapters.py` | `ETABSAdapter` |
| 3D geometry generation | `structural_lib/visualization/` | `beam_to_3d_geometry()` |
| Cost optimization | `structural_lib/insights/` | `optimize_beam_cost()` |
| UI rendering | `streamlit_app/components/` | `render_beam_editor()` |
| AI tool definitions | `streamlit_app/ai/tools.py` | `TOOLS` list |
| AI tool handlers | `streamlit_app/ai/handlers.py` | `handle_tool_call()` |

### 2.3 The Library-First Rule

**WRONG:**
```python
# In streamlit_app/components/beam_editor.py
def calculate_required_steel(mu_knm, b_mm, d_mm, fck, fy):
    # ... calculation logic directly in UI component
```

**CORRECT:**
```python
# In Python/structural_lib/api.py
def calculate_required_steel(mu_knm, b_mm, d_mm, fck, fy) -> RequiredSteelResult:
    """Calculate required steel area per IS 456."""
    # ... calculation logic

# In streamlit_app/components/beam_editor.py
from structural_lib.api import calculate_required_steel
result = calculate_required_steel(mu_knm, b_mm, d_mm, fck, fy)
```

---

## 3. Python Coding Standards

### 3.1 Formatting

```python
# Use black formatter with line length 100
# Run: black --line-length 100 .

# Use ruff for linting
# Run: ruff check --fix .
```

### 3.2 Imports Order

```python
# 1. Standard library
import json
from dataclasses import dataclass
from typing import Optional, List, Dict

# 2. Third-party
import numpy as np
import pandas as pd

# 3. Local imports (absolute)
from structural_lib.flexure import compute_xu
from structural_lib.types import BeamDesignOutput
```

### 3.3 Type Hints (REQUIRED)

```python
# WRONG - No type hints
def design_beam(mu, vu, b, D, fck, fy):
    pass

# CORRECT - Full type hints
def design_beam(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    fck: float = 25.0,
    fy: float = 500.0,
) -> BeamDesignOutput:
    """Design beam per IS 456."""
    pass
```

### 3.4 Dataclasses for Return Types

```python
# WRONG - Returning dict
def design_beam(...) -> dict:
    return {"ast": ast, "status": "safe"}

# CORRECT - Returning dataclass
@dataclass
class BeamDesignOutput:
    ast_mm2: float
    status: str
    utilization: float
    citations: List[str]

    def to_dict(self) -> dict:
        return asdict(self)

def design_beam(...) -> BeamDesignOutput:
    return BeamDesignOutput(ast_mm2=ast, status="safe", ...)
```

### 3.5 Naming Conventions

```python
# Functions: snake_case with verb prefix
def calculate_required_steel() -> ...
def validate_beam_design() -> ...
def get_beam_by_id() -> ...
def is_design_safe() -> ...

# Classes: PascalCase
class BeamDesignOutput:
class ETABSAdapter:

# Constants: UPPER_SNAKE_CASE
MAX_UTILIZATION_RATIO = 1.0
DEFAULT_COVER_MM = 40

# Private functions: leading underscore
def _compute_internal_lever_arm() -> ...
```

### 3.6 Unit Suffixes

Always include unit in parameter name:

```python
# WRONG
def design_beam(b, D, cover, moment):
    pass

# CORRECT
def design_beam(b_mm, D_mm, cover_mm, moment_knm):
    pass
```

---

## 4. TypeScript/JavaScript Standards

### 4.1 TypeScript Required

All new frontend code must be TypeScript, not JavaScript.

### 4.2 Type Definitions

```typescript
// Define interfaces for all data structures
interface BeamDesignRequest {
    beamId: string;
    b_mm: number;
    D_mm: number;
    mu_knm: number;
    vu_kn: number;
}

interface BeamDesignResponse {
    ast_mm2: number;
    status: 'safe' | 'unsafe' | 'warning';
    utilization: number;
}

// Use types in function signatures
async function designBeam(params: BeamDesignRequest): Promise<BeamDesignResponse> {
    // ...
}
```

### 4.3 React Component Patterns

```typescript
// Props interface required
interface BeamEditorProps {
    beamId: string;
    onSave: (config: RebarConfig) => void;
    initialConfig?: RebarConfig;
}

// Functional components with explicit return type
const BeamEditor: React.FC<BeamEditorProps> = ({ beamId, onSave, initialConfig }) => {
    // ...
};
```

---

## 5. Testing Requirements

### 5.1 Coverage Requirements

| Code Type | Minimum Coverage |
| --- | --- |
| Library (`structural_lib/`) | 80% |
| Critical calculations | 100% |
| API endpoints | 90% |
| UI components | 60% |

### 5.2 Test File Location

```
Python/tests/
├── unit/
├── integration/
├── regression/
├── property/
├── performance/
└── test_*.py

streamlit_app/tests/
├── test_*.py
```

### 5.3 Test Naming

```python
# Pattern: test_<function>_<scenario>_<expected>
def test_design_beam_normal_load_returns_safe():
    pass

def test_design_beam_overloaded_returns_unsafe():
    pass

def test_design_beam_missing_params_raises_error():
    pass
```

### 5.4 Test Structure (AAA Pattern)

```python
def test_calculate_xu_normal_case():
    # Arrange
    ast_mm2 = 1000.0
    b_mm = 300.0
    fck = 25.0
    fy = 500.0

    # Act
    xu = calculate_xu(ast_mm2, b_mm, fck, fy)

    # Assert
    assert xu > 0
    assert xu < 200  # Reasonable range
```

### 5.5 Running Tests

```bash
# Run all library tests
.venv/bin/python -m pytest Python/tests -v

# Run Streamlit tests
.venv/bin/python -m pytest streamlit_app/tests -v

# Run specific test file
.venv/bin/python -m pytest Python/tests/unit/test_flexure.py -v

# Run tests matching pattern
.venv/bin/python -m pytest Python/tests -k "test_design_beam" -v
```

---

## 6. Error Handling

### 6.1 Custom Exception Hierarchy

```python
# In structural_lib/exceptions.py
class StructuralLibError(Exception):
    """Base exception for all library errors."""
    pass

class DesignError(StructuralLibError):
    """Error in design calculation."""
    pass

class ValidationError(StructuralLibError):
    """Input validation failed."""
    pass

class CodeComplianceError(StructuralLibError):
    """Design violates code requirements."""
    def __init__(self, clause: str, message: str):
        self.clause = clause
        super().__init__(f"IS 456 {clause}: {message}")
```

### 6.2 Error Handling Patterns

```python
# WRONG - Generic exception
try:
    result = design_beam(...)
except Exception as e:
    print(f"Error: {e}")

# CORRECT - Specific exceptions with context
from structural_lib.exceptions import DesignError, ValidationError

try:
    result = design_beam(...)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}", extra={"beam_id": beam_id})
    return {"status": "validation_error", "message": str(e)}
except DesignError as e:
    logger.error(f"Design calculation failed: {e}", extra={"beam_id": beam_id})
    raise
```

### 6.3 Input Validation

```python
def design_beam(b_mm: float, D_mm: float, mu_knm: float) -> BeamDesignOutput:
    # Validate at function entry
    if b_mm <= 0:
        raise ValidationError(f"b_mm must be positive, got {b_mm}")
    if D_mm <= 0:
        raise ValidationError(f"D_mm must be positive, got {D_mm}")
    if D_mm < b_mm:
        raise ValidationError(f"D_mm ({D_mm}) should be >= b_mm ({b_mm})")

    # ... rest of function
```

---

## 7. Documentation Standards

### 7.1 Docstring Format (Google Style)

```python
def design_beam_is456(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    fck: float = 25.0,
    fy: float = 500.0,
) -> BeamDesignOutput:
    """Design a beam section per IS 456:2000.

    Calculates required reinforcement for flexure and shear,
    checks code compliance, and returns detailed design output.

    Args:
        mu_knm: Ultimate moment in kN-m.
        vu_kn: Ultimate shear in kN.
        b_mm: Width of beam in mm.
        D_mm: Overall depth of beam in mm.
        fck: Characteristic compressive strength of concrete in MPa.
        fy: Yield strength of steel in MPa.

    Returns:
        BeamDesignOutput containing:
            - ast_mm2: Required tension steel area
            - asv_mm2_per_m: Required shear reinforcement
            - status: "safe" or "unsafe"
            - utilization: Ratio of applied/capacity
            - citations: List of IS 456 clauses used

    Raises:
        ValidationError: If input parameters are invalid.
        DesignError: If design calculation fails.

    Example:
        >>> result = design_beam_is456(
        ...     mu_knm=150.0,
        ...     vu_kn=100.0,
        ...     b_mm=300.0,
        ...     D_mm=500.0,
        ... )
        >>> print(result.status)
        'safe'
        >>> print(result.ast_mm2)
        1256.6

    References:
        IS 456:2000, Clause 26.5.1 - Flexure design
        IS 456:2000, Clause 40 - Shear design
    """
```

### 7.2 Module Docstrings

Every module must have a docstring explaining its purpose:

```python
"""Flexure design calculations per IS 456:2000.

This module provides functions for:
- Computing neutral axis depth (xu)
- Calculating moment capacity
- Determining required steel area
- Checking flexure code compliance

Usage:
    from structural_lib.flexure import compute_xu, compute_moment_capacity

    xu = compute_xu(ast_mm2=1000, b_mm=300, fck=25, fy=500)
    mu = compute_moment_capacity(ast_mm2=1000, d_mm=450, fck=25, fy=500)

Dependencies:
    - numpy for numerical calculations

References:
    - IS 456:2000, Clause 38.1 - Assumptions
    - IS 456:2000, Clause 26.5.1 - Flexure
"""
```

---

## 8. API Design Patterns

### 8.1 Function Signature Consistency

```python
# Pattern: Required params first, optional with defaults after
def design_beam(
    # Required - no defaults
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    # Optional - with sensible defaults
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
    # Configuration options last
    include_detailed_report: bool = False,
) -> BeamDesignOutput:
```

### 8.2 Return Type Consistency

```python
# Always return a dataclass, never raw dict
# Always include status, never just values
# Always include citations for engineering calculations

@dataclass
class DesignResult:
    # Primary output
    value: float
    unit: str

    # Status
    status: Literal["safe", "unsafe", "warning"]
    utilization: float

    # Traceability
    citations: List[str]
    calculation_steps: Optional[List[str]] = None

    # Serialization
    def to_dict(self) -> dict:
        return asdict(self)
```

### 8.3 Batch Operations

```python
# For operations that can be batched, provide both single and batch versions
def design_beam(beam_input: BeamInput) -> BeamOutput:
    """Design a single beam."""
    pass

def design_beams_batch(
    beam_inputs: List[BeamInput],
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[BeamOutput]:
    """Design multiple beams with progress tracking."""
    results = []
    for i, beam_input in enumerate(beam_inputs):
        results.append(design_beam(beam_input))
        if progress_callback:
            progress_callback(i + 1, len(beam_inputs))
    return results
```

---

## 9. Performance Guidelines

### 9.1 Performance Targets

| Operation | Target | Maximum |
| --- | --- | --- |
| Single beam design | < 20ms | 50ms |
| Beam validation | < 10ms | 20ms |
| 3D geometry generation | < 50ms | 100ms |
| Batch design (100 beams) | < 2s | 5s |
| ETABS import (1000 rows) | < 1s | 3s |

### 9.2 Performance Best Practices

```python
# Use numpy for array operations
# WRONG
total = 0
for x in large_list:
    total += x * x

# CORRECT
total = np.sum(np.array(large_list) ** 2)

# Cache expensive calculations
from functools import lru_cache

@lru_cache(maxsize=1000)
def compute_xu(ast_mm2: float, b_mm: float, fck: float, fy: float) -> float:
    # Expensive calculation
    pass

# Use generators for large datasets
def process_beams(beam_data: pd.DataFrame):
    for _, row in beam_data.iterrows():
        yield design_beam(row)
```

### 9.3 Memory Guidelines

```python
# Don't load entire files into memory for large datasets
# WRONG
with open("large_file.csv") as f:
    data = f.read()

# CORRECT - Use chunked reading
for chunk in pd.read_csv("large_file.csv", chunksize=1000):
    process_chunk(chunk)
```

---

## 10. Security Checklist

### 10.1 Input Validation

```python
# Validate all external inputs
def import_etabs_csv(file_path: str) -> pd.DataFrame:
    # Validate file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Validate file extension
    if not file_path.endswith(".csv"):
        raise ValidationError("Only CSV files are supported")

    # Validate file size (prevent memory attacks)
    if os.path.getsize(file_path) > 100_000_000:  # 100MB
        raise ValidationError("File too large")

    return pd.read_csv(file_path)
```

### 10.2 No Hardcoded Secrets

```python
# WRONG
api_key = "sk-1234567890"

# CORRECT
import os
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not set")
```

### 10.3 SQL Injection Prevention

```python
# WRONG - String interpolation
query = f"SELECT * FROM beams WHERE id = '{beam_id}'"

# CORRECT - Parameterized query
query = "SELECT * FROM beams WHERE id = ?"
cursor.execute(query, (beam_id,))
```

---

## 11. Pre-Commit Checklist

Before every commit, verify:

```
□ Tests pass: .venv/bin/python -m pytest Python/tests -v
□ Coverage check: .venv/bin/python -m pytest Python/tests --cov=structural_lib --cov-fail-under=80
□ Linting passes: ruff check .
□ Formatting: black --check .
□ Type checking: mypy structural_lib/
□ No debug code: rg -n "print\\(" Python/structural_lib/ (should be minimal)
□ No TODOs without issue: rg -n "TODO" --glob="*.py" .
□ Docstrings present: Check new public functions
□ Tests for new code: Check Python/tests/ or streamlit_app/tests/
□ SESSION_LOG updated: docs/SESSION_LOG.md
```

### Automated Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

echo "Running pre-commit checks..."

# Format check
black --check Python/

# Lint
ruff check Python/

# Type check
mypy Python/structural_lib/

# Tests
.venv/bin/python -m pytest Python/tests -v --tb=short

echo "All checks passed!"
```

---

## 12. Common Mistakes to Avoid

### 12.1 Code Duplication

```python
# WRONG - Duplicated validation in multiple functions
def design_beam(...):
    if b_mm <= 0:
        raise ValidationError("b_mm must be positive")
    # ...

def validate_beam(...):
    if b_mm <= 0:
        raise ValidationError("b_mm must be positive")
    # ...

# CORRECT - Single validation function
def validate_beam_dimensions(b_mm: float, D_mm: float) -> None:
    """Validate beam dimensions."""
    if b_mm <= 0:
        raise ValidationError("b_mm must be positive")
    if D_mm <= 0:
        raise ValidationError("D_mm must be positive")

def design_beam(...):
    validate_beam_dimensions(b_mm, D_mm)
    # ...
```

### 12.2 Modifying Function Signature Without Checking Callers

```python
# Before changing any function signature:
# 1. Search for all callers
rg -n "function_name\\(" --glob="*.py" .

# 2. Update all callers
# 3. Add deprecation warning if needed
```

### 12.3 Adding UI Logic to Library

```python
# WRONG - UI concerns in library
def design_beam(...):
    result = calculate_design(...)
    st.success(f"Design complete: {result}")  # NO! UI in library
    return result

# CORRECT - Library returns data, UI handles presentation
def design_beam(...) -> BeamDesignOutput:
    return calculate_design(...)

# In UI:
result = design_beam(...)
st.success(f"Design complete: {result.status}")
```

### 12.4 Not Using Existing Utilities

```python
# WRONG - Reimplementing existing functionality
def my_custom_xu_calc(ast, b, fck, fy):
    # Custom implementation
    pass

# CORRECT - Use existing library function
from structural_lib.flexure import compute_xu
xu = compute_xu(ast, b, fck, fy)
```

---

## 13. Debugging Guide

### 13.1 Logging Setup

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def design_beam(...):
    logger.debug(f"Starting design: b={b_mm}, D={D_mm}, mu={mu_knm}")

    result = calculate_design(...)

    logger.info(f"Design complete: status={result.status}, util={result.utilization}")
    return result
```

### 13.2 Debug Techniques

```python
# Use breakpoints
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json

# Print intermediate values (remove before commit)
logger.debug(f"Intermediate xu = {xu}")

# Validate assumptions
assert xu > 0, f"xu must be positive, got {xu}"
assert xu < d_mm, f"xu ({xu}) must be less than d ({d_mm})"
```

### 13.3 Common Issues and Solutions

| Issue | Likely Cause | Solution |
| --- | --- | --- |
| ImportError | Circular import | Reorganize imports, use TYPE_CHECKING |
| KeyError in dict | Missing key | Use `.get()` with default |
| ZeroDivisionError | Missing validation | Add input validation |
| Unexpected None | Optional not handled | Add None check |
| Test flakiness | State leakage | Use fresh fixtures |

---

## 14. Code Review Criteria

### 14.1 Automatic Checks (CI/CD)

- [ ] Tests pass
- [ ] Coverage >= 80%
- [ ] Linting passes
- [ ] Type checking passes
- [ ] No security vulnerabilities

### 14.2 Manual Review Checklist

- [ ] Code follows project structure (library vs UI)
- [ ] Type hints on all functions
- [ ] Docstrings with examples
- [ ] Tests cover new code paths
- [ ] Error handling is appropriate
- [ ] No hardcoded values (use constants)
- [ ] Performance considerations addressed
- [ ] Breaking changes documented
- [ ] SESSION_LOG updated

### 14.3 API Change Review

For any API changes:

- [ ] All callers updated
- [ ] Deprecation warning added (if breaking)
- [ ] Migration guide written
- [ ] ADR created for architectural decisions

---

## Quick Reference

### Commands

```bash
# Run tests
.venv/bin/python -m pytest Python/tests -v
.venv/bin/python -m pytest streamlit_app/tests -v

# Check coverage
.venv/bin/python -m pytest Python/tests --cov=structural_lib --cov-fail-under=80

# Format code
black --line-length 100 .

# Lint code
ruff check --fix .

# Type check
mypy Python/structural_lib/

# Find all usages
rg -n "function_name\\(" --glob="*.py" .
```

### Key Files

| Purpose | Location |
| --- | --- |
| Research docs | `docs/research/` |
| Development plan | `docs/planning/8-week-development-plan.md` |
| Coding guide | `docs/guides/AI_AGENT_CODING_GUIDE.md` |
| Testing strategy | `docs/guides/TESTING_AND_CICD_STRATEGY.md` |
| Session log | `docs/SESSION_LOG.md` |
| Library API | `Python/structural_lib/api.py` |
| AI tools | `streamlit_app/ai/tools.py` |
| Tests | `Python/tests/` |
| Streamlit tests | `streamlit_app/tests/` |
| Root tests | `tests/` |

---

**Remember:** Good code is code that others (including future you and other AI agents) can understand, maintain, and extend. When in doubt, ask for clarification rather than making assumptions.
