# Code Clause Database Architecture

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** Complete
**Task:** TASK-240
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** IS 456 clause references are hardcoded in comments throughout codebase. No searchable/traceable system exists. Questions like "Which clause governs minimum steel?" require grepping code.

**Goal:** Design a structured, searchable database/system for code clause references that enables:
1. Traceability (code → clause, clause → code)
2. Documentation generation
3. Compliance verification
4. Code update tracking

**Key Finding:** Engineering libraries benefit from structured clause metadata. JSON-based clause database + decorator pattern provides best balance of flexibility and developer experience.

**Recommendation:**
- Phase 1: JSON clause database (4-5 hours)
- Phase 2: Decorator pattern for functions (3-4 hours)
- Phase 3: Search/report tools (4-5 hours)
- Total: 11-14 hours implementation

---

## Table of Contents

1. [Problem Analysis](#1-problem-analysis)
2. [Architecture Options](#2-architecture-options)
3. [Recommended Architecture](#3-recommended-architecture)
4. [Database Schema](#4-database-schema)
5. [API Design](#5-api-design)
6. [Query Examples](#6-query-examples)
7. [Implementation Guide](#7-implementation-guide)

---

## 1. Problem Analysis

### 1.1 Current State

**Hardcoded References:**
```python
def calculate_min_steel(b: float, d: float, fy: float) -> float:
    """
    Calculate minimum tensile reinforcement per IS 456:2000 Cl. 26.5.1.1.

    Ast,min = 0.85 * b * d / fy (IS 456 Cl. 26.5.1.1a)
    """
    # IS 456:2000 Cl. 26.5.1.1 (a)
    return 0.85 * b * d / fy
```

**Problems:**
- ❌ Can't search "which functions use Cl. 26.5.1.1?"
- ❌ Can't generate "clause coverage report"
- ❌ Can't track "which clauses changed in code update?"
- ❌ Manual effort to verify all clauses implemented

### 1.2 Desired Capabilities

**Capability 1: Bidirectional Search**
```python
# Find functions using a clause
functions = find_by_clause("IS 456 Cl. 26.5.1.1")
# → [calculate_min_steel, design_beam, ...]

# Find clauses used by function
clauses = find_by_function("calculate_min_steel")
# → ["IS 456 Cl. 26.5.1.1", "IS 456 Table 19"]
```

**Capability 2: Coverage Report**
```
IS 456:2000 Clause Coverage:
- Section 26 (Design of Beams): 15/18 clauses implemented
- Section 40 (Shear): 8/10 clauses implemented
- Section 38 (Flexure): 12/12 clauses implemented ✓
```

**Capability 3: Code Update Tracking**
```
IS 456:2000 → IS 456:2024 update impact:
- Cl. 26.5.1.1 changed: Affects 3 functions
- Cl. 40.2 deprecated: Affects 2 functions
- New Cl. 26.7: Not yet implemented
```

---

## 2. Architecture Options

### 2.1 Option 1: Decorator-Based Metadata

**Approach:** Python decorators store clause references

```python
@clause_reference("IS 456:2000", ["Cl. 26.5.1.1a", "Table 19"])
def calculate_min_steel(b: float, d: float, fy: float) -> float:
    """Calculate minimum steel."""
    return 0.85 * b * d / fy
```

**Pros:**
- ✅ Decorator syntax is Pythonic
- ✅ Metadata attached to function
- ✅ Can be queried programmatically

**Cons:**
- ❌ Decorators clutter code
- ❌ Hard to maintain large reference lists
- ❌ Not easily exportable to other formats

### 2.2 Option 2: External JSON Database

**Approach:** JSON file maps clauses ↔ functions

```json
{
  "IS 456:2000": {
    "Cl. 26.5.1.1": {
      "title": "Minimum Tension Reinforcement",
      "functions": ["calculate_min_steel", "design_beam"],
      "formula": "Ast,min = 0.85*b*d/fy",
      "tables": ["Table 19"]
    }
  }
}
```

**Pros:**
- ✅ Centralized reference
- ✅ Easy to edit/maintain
- ✅ Can generate docs from JSON
- ✅ Version control friendly

**Cons:**
- ❌ Separate from code (can drift)
- ❌ Manual sync required

### 2.3 Option 3: Database (SQL/NoSQL)

**Approach:** Store in SQLite/MongoDB

**Pros:**
- ✅ Powerful queries
- ✅ Relational data

**Cons:**
- ❌ Overkill for this use case
- ❌ Adds dependency
- ❌ Harder to version control

### 2.4 Recommended: Hybrid (JSON + Decorators)

**Best of both:**
- JSON database for clause metadata
- Lightweight decorators for function tagging
- Automatic sync validation in tests

---

## 3. Recommended Architecture

### 3.1 System Components

```
┌─────────────────────────────────────────────┐
│         Clause Database (JSON)              │
│  ┌───────────────────────────────────────┐  │
│  │ IS 456:2000 metadata                  │  │
│  │ - Clause text                         │  │
│  │ - Formulas                            │  │
│  │ - Tables                              │  │
│  │ - Amendments                          │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│      Function Annotations (Decorators)      │
│  @clause("26.5.1.1")                        │
│  def calculate_min_steel(...):              │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│          Query API / Tools                  │
│  - find_by_clause(clause_id)                │
│  - find_by_function(func_name)              │
│  - generate_coverage_report()               │
│  - generate_traceability_matrix()           │
└─────────────────────────────────────────────┘
```

### 3.2 Directory Structure

```
structural_lib/
  clauses/
    __init__.py              # Clause registry & API
    database/
      is456_2000.json        # IS 456:2000 clause database
      is13920_2016.json      # IS 13920:2016 (if needed)
    decorators.py            # @clause decorator
    query.py                 # Query functions
    reports.py               # Generate reports
```

---

## 4. Database Schema

### 4.1 Clause Database Schema (JSON)

**File: `clauses/database/is456_2000.json`**

```json
{
  "code": {
    "name": "IS 456",
    "year": 2000,
    "title": "Plain and Reinforced Concrete - Code of Practice",
    "version": "4th Revision",
    "last_updated": "2000"
  },
  "sections": {
    "26": {
      "title": "Design of Beams for Flexure",
      "clauses": {
        "26.5.1.1": {
          "title": "Minimum Tension Reinforcement",
          "text": "The minimum area of tension reinforcement shall be not less than that given by the following: Ast >= 0.85*bd/fy",
          "subclauses": {
            "a": {
              "formula": "Ast,min = 0.85*b*d/fy",
              "units": {
                "Ast": "mm²",
                "b": "mm",
                "d": "mm",
                "fy": "N/mm²"
              },
              "applicability": "For Fe 415 steel",
              "notes": ["For Fe 500, factor is 0.7", "For beams, not columns"]
            }
          },
          "references": ["Table 19"],
          "amendments": [],
          "superseded_by": null,
          "related_clauses": ["26.5.1.2", "26.5.2.1"]
        }
      }
    }
  },
  "tables": {
    "19": {
      "title": "Minimum Percentage of Reinforcement",
      "data": [
        {"fy": 250, "percent": 0.34},
        {"fy": 415, "percent": 0.205},
        {"fy": 500, "percent": 0.17}
      ]
    }
  }
}
```

**Schema Benefits:**
- ✅ Complete clause metadata
- ✅ Formulas with units
- ✅ Applicability notes
- ✅ Cross-references
- ✅ Amendment tracking

### 4.2 Function Mapping Schema

**Option A: Inline in clause database**
```json
{
  "26.5.1.1": {
    "...": "...",
    "implemented_by": [
      {
        "function": "structural_lib.flexure.calculate_min_steel",
        "module": "flexure",
        "line": 245,
        "since_version": "0.10.0"
      }
    ]
  }
}
```

**Option B: Separate mapping file**
```json
{
  "function_to_clause": {
    "structural_lib.flexure.calculate_min_steel": {
      "clauses": ["26.5.1.1"],
      "tables": ["19"],
      "version_added": "0.10.0"
    }
  }
}
```

**Recommendation:** Option B (separate mapping, easier to maintain)

---

## 5. API Design

### 5.1 Decorator Pattern

**Simple decorator:**
```python
from structural_lib.clauses import clause

@clause("26.5.1.1")
def calculate_min_steel(b: float, d: float, fy: float) -> float:
    """Calculate minimum steel per IS 456 Cl. 26.5.1.1."""
    return 0.85 * b * d / fy
```

**With multiple clauses:**
```python
@clause("26.5.1.1", "26.5.1.2")
@clause.table("19")
def design_beam(beam_data: dict) -> BeamDesignResult:
    """Design beam per IS 456."""
    ...
```

**Implementation:**
```python
# clauses/decorators.py
from functools import wraps
from typing import Callable, List

def clause(*clause_ids: str) -> Callable:
    """
    Decorator to tag function with IS 456 clause references.

    Example:
        @clause("26.5.1.1")
        def calculate_min_steel(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Store clause IDs in function metadata
        if not hasattr(func, '_clauses'):
            func._clauses = []
        func._clauses.extend(clause_ids)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator

# Extension for tables
clause.table = lambda *table_ids: clause(*[f"Table_{t}" for t in table_ids])
```

### 5.2 Query API

**Query functions:**
```python
# clauses/query.py
from typing import List, Dict
import importlib
import inspect

class ClauseRegistry:
    """Registry of all clause references in codebase."""

    def __init__(self):
        self._clause_db = self._load_database()
        self._function_map = self._build_function_map()

    def find_by_clause(self, clause_id: str) -> List[Dict]:
        """
        Find all functions implementing a clause.

        Args:
            clause_id: Clause ID (e.g., "26.5.1.1")

        Returns:
            List of dicts with function info

        Example:
            >>> registry = ClauseRegistry()
            >>> funcs = registry.find_by_clause("26.5.1.1")
            >>> for f in funcs:
            ...     print(f"{f['module']}.{f['name']}")
        """
        ...

    def find_by_function(self, func_name: str) -> List[str]:
        """
        Find all clauses used by a function.

        Example:
            >>> clauses = registry.find_by_function("calculate_min_steel")
            >>> print(clauses)
            ['26.5.1.1', 'Table_19']
        """
        ...

    def get_clause_info(self, clause_id: str) -> Dict:
        """
        Get full clause metadata from database.

        Returns:
            Clause dict with text, formula, units, etc.
        """
        ...

    def coverage_report(self) -> Dict:
        """
        Generate clause coverage report.

        Returns:
            Dict mapping sections to coverage stats

        Example:
            >>> report = registry.coverage_report()
            >>> print(report['26']['coverage_percent'])
            83.3  # 15/18 clauses implemented
        """
        ...
```

---

## 6. Query Examples

### 6.1 Find Functions by Clause

```python
from structural_lib.clauses import ClauseRegistry

registry = ClauseRegistry()

# Find all functions using Cl. 26.5.1.1
functions = registry.find_by_clause("26.5.1.1")

for func in functions:
    print(f"{func['module']}.{func['name']} (line {func['line']})")

# Output:
# flexure.calculate_min_steel (line 245)
# flexure.design_beam (line 580)
# compliance.check_min_steel (line 92)
```

### 6.2 Find Clauses by Function

```python
# Find clauses for a function
clauses = registry.find_by_function("design_beam")

for clause_id in clauses:
    clause_info = registry.get_clause_info(clause_id)
    print(f"{clause_id}: {clause_info['title']}")

# Output:
# 26.5.1.1: Minimum Tension Reinforcement
# 26.5.2.1: Maximum Tension Reinforcement
# 40.2: Design Shear Strength
```

### 6.3 Coverage Report

```python
report = registry.coverage_report()

for section_id, section in report.items():
    print(f"\nSection {section_id}: {section['title']}")
    print(f"  Implemented: {section['implemented']}/{section['total']}")
    print(f"  Coverage: {section['coverage_percent']:.1f}%")

    if section['missing']:
        print(f"  Missing clauses: {', '.join(section['missing'])}")

# Output:
# Section 26: Design of Beams for Flexure
#   Implemented: 15/18
#   Coverage: 83.3%
#   Missing clauses: 26.3.1, 26.4.2, 26.5.3
#
# Section 40: Shear and Torsion
#   Implemented: 8/10
#   Coverage: 80.0%
#   Missing clauses: 40.4, 40.5
```

### 6.4 Traceability Matrix

```python
# Generate Excel traceability matrix
from structural_lib.clauses.reports import generate_traceability_matrix

matrix = generate_traceability_matrix(output_file="traceability.xlsx")

# Creates Excel with columns:
# | Clause ID | Clause Title | Functions | Test Coverage | Notes |
# |-----------|--------------|-----------|---------------|-------|
# | 26.5.1.1  | Min Steel    | 3 funcs   | 95%          | ✓     |
# | 26.5.2.1  | Max Steel    | 2 funcs   | 90%          | ✓     |
# | 26.3.1    | Deflection   | -         | -            | TODO  |
```

---

## 7. Implementation Guide

### 7.1 Phase 1: Clause Database (4-5 hours)

**Step 1: Create JSON schema** (1 hour)
- Define structure
- Add IS 456 metadata
- Add 5-10 sample clauses

**Step 2: Populate database** (2-3 hours)
- Add all Section 26 clauses (flexure)
- Add all Section 40 clauses (shear)
- Add key tables (19, 20, 21)

**Step 3: Validation** (1 hour)
- JSON schema validation
- Unit tests for database loading
- Verify cross-references

### 7.2 Phase 2: Decorator System (3-4 hours)

**Step 1: Implement decorator** (1 hour)
- `@clause()` decorator
- Metadata storage
- Tests

**Step 2: Tag existing functions** (2 hours)
- Add decorators to all flexure functions
- Add decorators to shear functions
- Document pattern

**Step 3: Validation** (1 hour)
- Ensure all decorated functions in database
- Check for orphan clauses
- Test decorator behavior

### 7.3 Phase 3: Query & Reports (4-5 hours)

**Step 1: Query API** (2 hours)
- Implement ClauseRegistry
- find_by_clause()
- find_by_function()
- get_clause_info()

**Step 2: Reports** (2 hours)
- coverage_report()
- generate_traceability_matrix()
- Export to Excel/PDF

**Step 3: Documentation** (1 hour)
- Usage examples
- API docs
- Developer guide

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete | Research Team |

**Next Steps:**

1. Review architecture with team
2. Create Phase 1 implementation task
3. Start with 5-10 sample clauses
4. Expand to full IS 456 coverage
5. Add to CI (clause coverage check)

---

**End of Document**
**Implementation Time:** 11-14 hours (3 phases)
**Benefit:** Searchable clause database, traceability, compliance verification
**Priority:** MEDIUM (nice-to-have for v1.0, critical for professional certification)
