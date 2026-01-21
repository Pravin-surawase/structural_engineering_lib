# Product Strategy Follow-up - Detailed Answers

**Type:** Research
**Audience:** Product Owner, Developers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-15
**Related Tasks:** Product Strategy

---

## Table of Contents

1. [Columns & Slabs Expansion Strategy](#1-columns--slabs-expansion-strategy)
2. [3D Visualization Layout & Architecture](#2-3d-visualization-layout--architecture)
3. [Minimum Proof of Concept](#3-minimum-proof-of-concept)
4. [Competition Analysis](#4-competition-analysis)
5. [Library-LLM Relationship](#5-library-llm-relationship)
6. [Agent Coding Standards Guide](#6-agent-coding-standards-guide)
7. [Solo Developer + AI Strategy](#7-solo-developer--ai-strategy)
8. [Additional Suggestions](#8-additional-suggestions)

---

## 1. Columns & Slabs Expansion Strategy

### Reality Check

You're right—columns and slabs are **heavy tasks** requiring manual verification. Here's a realistic approach:

### Phased API Approach (Start Small, Verify, Expand)

#### Phase 1: Column Core (2-3 APIs, 1 week dev + 2 weeks manual verification)

```python
# Start with just these 3 functions
def design_short_column_axial(
    width: float,      # mm
    depth: float,      # mm
    pu: float,         # kN (factored axial load)
    fck: float,        # N/mm²
    fy: float,         # N/mm²
) -> ColumnResult:
    """Short column under pure axial compression (IS 456 Cl 39.3)."""

def design_short_column_uniaxial(
    width: float,
    depth: float,
    pu: float,         # kN
    mu: float,         # kN·m (moment about one axis)
    fck: float,
    fy: float,
) -> ColumnResult:
    """Short column with uniaxial bending (IS 456 Cl 39.5)."""

def check_column_slenderness(
    unsupported_length: float,  # mm
    width: float,               # mm
    end_conditions: str,        # "fixed-fixed", "fixed-pinned", etc.
) -> SlendernessResult:
    """Check if column is short or slender (IS 456 Cl 25.1.2)."""
```

**Manual verification checklist:**
- [ ] 10 hand-calculated examples per function
- [ ] Cross-check with SP 16 charts
- [ ] Edge cases: minimum steel, maximum steel, over-reinforced
- [ ] Comparison with ETABS/STAAD output

#### Phase 2: Column Complete (After Phase 1 verified, 2 more weeks)

# Product Strategy Follow-up - Consolidation Notice

**Type:** Research
**Audience:** Product Owner, Developers
**Status:** Deprecated
**Importance:** Low
**Created:** 2026-01-15
**Last Updated:** 2026-01-15
**Related Tasks:** Product Strategy

---

This document has been consolidated into the single source of truth:

- [docs/research/chat-ui-product-strategy-research.md](chat-ui-product-strategy-research.md)

Please use that file for all current research and planning.
    """One-way slab design (span/depth > 2)."""
