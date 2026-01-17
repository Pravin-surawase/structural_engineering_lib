# Deferred Integrations Tracker

**Type:** Reference
**Audience:** Developers
**Status:** In Progress
**Importance:** Medium
**Created:** 2026-01-06
**Last Updated:** 2026-01-13

---

**Purpose:** Track feature integrations deferred to future releases with clear rationale and target versions.

---

## v0.16 Target (Planned)

### Constructability Scoring Integration

**Location:** `insights/comparison.py:171-172`

**Current State:**
- Uses conservative default (0.7) in comparison scoring
- Full integration requires `BeamDesignOutput` availability

**Rationale for Deferral:**
- Constructability API (`insights/constructability.py`) stabilized in v0.14
- Comparison module predates full API maturity
- Integration requires refactoring comparison to accept `BeamDesignOutput` instead of param dicts

**Work Required:**
1. Update `compare_designs()` signature to accept `list[BeamDesignOutput]`
2. Extract constructability scores from design outputs
3. Update comparison tests to use full design outputs

**Estimated Effort:** 2-3 hours

**Dependencies:**
- None (constructability API is stable)

**Tracking Issue:** #TBD

---

### Robustness/Sensitivity Scoring Integration

**Location:** `insights/comparison.py:175-176`

**Current State:**
- Uses conservative default (0.6) in comparison scoring
- Full integration requires sensitivity analysis API

**Rationale for Deferral:**
- Sensitivity module (`insights/sensitivity.py`) exists but requires heavy computation
- Comparison module designed for quick parameter-based comparison
- Running full sensitivity per design alternative would slow comparison significantly

**Work Required:**
1. Evaluate performance impact of per-design sensitivity analysis
2. Consider caching or simplified robustness metric
3. Update comparison API to optionally enable robustness scoring

**Estimated Effort:** 4-6 hours (includes performance optimization)

**Dependencies:**
- Performance profiling to ensure acceptable latency

**Tracking Issue:** #TBD

---

### CLI Constructability Scoring

**Location:** `__main__.py:273-275`

**Current State:**
- CLI `smart` command uses simplified param-based sensitivity
- Constructability scoring returns `None` in CLI context

**Rationale for Deferral:**
- CLI smart command operates on parameters only (not full `BeamDesignOutput`)
- Constructability requires complete design result (detailing, compliance checks, etc.)
- Adding full design pipeline to CLI would significantly increase complexity

**Work Required:**
1. Decide: (a) Keep CLI simple (param-only), or (b) Add full design path to CLI
2. If (b): Refactor CLI smart command to run full design pipeline
3. Update CLI tests to verify constructability scoring

**Estimated Effort:**
- Option (a): No work (document as intentional limitation)
- Option (b): 6-8 hours (significant refactoring)

**Dependencies:**
- Product decision: Should CLI smart be lightweight (current) or comprehensive?

**Tracking Issue:** #TBD

---

## Decision Log

### 2026-01-06: Conservative Defaults Chosen

**Decision:** Use conservative default scores (0.7 for constructability, 0.6 for robustness) rather than placeholder `None` or raising errors.

**Rationale:**
- Comparison still provides value with partial scoring
- Conservative defaults don't artificially boost scores
- Users get immediate functionality vs waiting for v0.16

**Alternative Considered:** Raise `NotImplementedError` to force users to wait for full integration.

**Rejected Because:** Breaking change for existing users; comparison is useful even with defaults.

---

## How to Update This Document

When integrating deferred features:

1. **Move to "Completed Integrations"** section (create if needed)
2. **Document actual vs estimated effort**
3. **Note any design changes made**
4. **Update version number** where completed

When adding new deferrals:

1. **Create section** with clear heading
2. **Provide context:** Location, current state, rationale
3. **Estimate effort** and list dependencies
4. **Create tracking issue** in GitHub

---

## See Also

- [Known Pitfalls](known-pitfalls.md) - User-facing limitations
- [TASKS.md](../TASKS.md) - Active work tracking
- [Project Roadmap](../_archive/planning/production-roadmap.md) - Release planning
