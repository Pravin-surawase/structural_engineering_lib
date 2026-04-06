# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-04-07 — v0.21.6 complete (unreleased, pending PyPI publish)

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items
- **No new Streamlit work** — all new features go to React. Bug fixes only for Streamlit-only features.

---

## Current Release

- **Version:** v0.21.6 ✅ COMPLETE → micro-releases v0.21.7–v0.21.8 → v0.22.0 Stabilization
- **Strategy:** Incremental micro-releases — each focuses on one quality dimension (tests, API, security, performance)
- **Focus:** API introspection → security hardening → performance baselines → stabilization
- **Target:** v0.21.7 next, then v0.21.8, then v0.22.0, then v0.23 (Slabs + Footing completion)
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution
- **Architecture:** [unified-architecture-v1.md](architecture/unified-architecture-v1.md) §20 — complete v0.21.5→v1.0 roadmap

### Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | ✅ Released (v0.20.0) | Batch design React UI, compliance checker, cost optimizer, 86 API tests |
| **v0.21** | React UX + Library Expansion | ✅ Released (v0.21.0) | Editor-centric UX, BeamDetailPanel, FloatingDock, PDF export, load calc, BOQ, torsion |
| **v0.21.4** | Stabilization | ✅ Released (v0.21.4) | CostProfile fix, float sanitization, footing API, bearing check, torsion shim |
| **v0.21.5** | Test Coverage & Regression Prevention | ✅ DONE | Golden vectors (42+), contract tests (18), 99% branch coverage |
| **v0.21.6** | API Quality & Introspection | ✅ DONE | check_code(), show_versions(), OpenAPI freeze, limitation docs |
| **v0.21.7** | Security Hardening | 📋 PLANNED | Input validation, body limits, CVE scanning |
| **v0.21.8** | Performance & Property Testing | 📋 PLANNED | Benchmarks, Hypothesis, performance baselines |
| **v0.22.0** | Stabilization Release | 📋 PLANNED | Provenance, SP:16 verification, release hardening |
| **v0.23** | IS 456 Slabs + Footing Completion | 📋 PLANNED | One-way slab, two-way slab, footing dowels + API, punching shear |
| **v0.24** | Multi-Code Infrastructure | 📋 PLANNED | CodeRegistry activation, DesignEnvelope, units.py, API v2 routes |
| **v0.25** | ACI 318-19 Beam | 📋 PLANNED | ACI beam flexure + shear, PCA Notes ±0.1% benchmarks |
| **v1.0** | Production Multi-Code | 📋 PLANNED | IS 456 complete, ACI 318 beam+column, EC2 beam, API stability guarantee |

### Migration Status (React vs Streamlit)

| Feature | Streamlit | React | API Ready | Priority |
|---------|-----------|-------|-----------|----------|
| Single beam design | ✅ | ✅ | ✅ | Done |
| CSV import (40+ cols) | ✅ | ✅ | ✅ | Done |
| 3D visualization | ✅ | ✅ R3F | ✅ | Done |
| Export (BBS/DXF/Report) | ✅ | ✅ | ✅ | Done |
| Dashboard insights | ✅ | ✅ | ✅ | Done |
| Rebar suggestions | ✅ | ✅ | ✅ | Done |
| **Batch design UI** | ✅ | ✅ | ✅ streaming.py | Done |
| **Compliance checker** | ✅ | ✅ DesignView panel | ✅ insights.py | Done |
| **Cost optimizer** | ✅ | ✅ DesignView rebar | ✅ optimization.py | Done |
| **AI Assistant** | ✅ | -- | Partial | ⏸ Deferred |
| Learning center | ✅ | -- | -- | 🟢 Low |

### v0.21 Remaining Items (Library Expansion)

| # | Task ID | Feature | Status |
|---|---------|---------|--------|
| 7 | TASK-520 | Report/3D Test Coverage | ✅ DONE (71 new tests) |
| 8 | TASK-521 | Beam Rationalization | 📋 [→ v0.22.0] |

> v0.21 React UX Overhaul (TASK-522–528, all ✅) and Library Expansion items 1–6 (TASK-514–519, all ✅) archived to [tasks-history.md](_archive/tasks-history.md).
> Detailed specs: [next-phase-improvements-plan.md](planning/next-phase-improvements-plan.md) Part 2.

---

## Completed (Archived)

> All completed items below have been archived. See [tasks-history.md](_archive/tasks-history.md) for full details.

| Section | Items | Summary |
|---------|-------|---------|
| Architecture Doc Enhancement | 1 ✅ | unified-architecture-v1.md enhanced 413→1108 lines, 8 new sections, 9-agent review (library-expert, security, structural-engineer, reviewer, frontend, api-developer, innovator, tester, governance) |
| v0.21.2 Packaging Fixes | TASK-PKG-1–6 ✅ | Wheel content, package discovery, CI tests |
| v0.21.2 External Audit | EA-1–23 ✅ | 23 audit findings fixed (test infra, imports, API, security, frontend, docs) |
| v0.21.5 Stabilization | 8 items ✅ | CostProfile, sanitize_float, footing wiring, bearing pressure |
| Recent Fixes | 21 items ✅ | Response envelope, CI, audit P0–P2, column math, git hardening, variable naming |
| Audit P1 Batch 1 | 4 items ✅ | clause_cli, FlexureResult limits, streaming 404, Three.js cleanup |
| External Audit Remediation | 8 items ✅ | ETABS units/batch/geometry, SmartDesigner CLI, .j2 packaging, README fixes, bbs import path |

---

## External Audit Remediation — v0.21.6 ✅ DONE

**Theme:** Fix 8 external audit findings across ETABS import, SmartDesigner CLI, packaging, and documentation.
**Completed:** 2026-04-07

| ID | Finding | Priority | Status |
|----|---------|----------|--------|
| EXT-P1-1 | ETABS job generator uses `"SI-mm"` units → fixed to `"IS456"` | P1 | ✅ DONE |
| EXT-P1-2 | ETABS batch groups by `beam_id` only → fixed to `(story, beam_id)` to prevent cross-story collision | P1 | ✅ DONE |
| EXT-P1-3 | Geometry merge keys by `label` only → fixed to `(story, label)` with fallback to prevent overwrite | P1 | ✅ DONE |
| EXT-P1-4 | SmartDesigner CLI uses wrong function → fixed to `design_single_beam()` returning `BeamDesignOutput` | P1 | ✅ DONE |
| EXT-P1-5 | Report `.j2` templates missing from wheel → added to `pyproject.toml` package-data | P1 | ✅ DONE |
| EXT-P2-1 | README batch example uses non-existent `parse_file()` → fixed to `load_combined()` | P2 | ✅ DONE |
| EXT-P2-2 | `bbs.py` imports from deprecated shim → fixed to canonical `codes/is456/beam/detailing` | P2 | ✅ DONE |
| EXT-P3-1 | README version `0.21.3` → updated to `0.21.5` | P3 | ✅ DONE |

---

## v0.21.5 — Test Coverage & Regression Prevention ✅ DONE

**Theme:** Golden vector baselines and contract tests. No future change can silently break existing calculations.
**Completed:** 2026-04-06
**Quality Gate:** `pytest -m golden` passes with 0 failures, branch coverage 99% on `codes/is456/` ✅

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-720 | Golden vector baselines for all IS 456 functions (`@pytest.mark.golden`) — 42+ tests (9 beam + 20 column + 13 footing) | @tester | ✅ DONE |
| TASK-721 | Contract tests for API surface stability (`@pytest.mark.contract`) — 18 contract tests | @tester | ✅ DONE |
| TASK-520 | Report & 3D visualization test coverage — 71 new tests | @tester | ✅ DONE |
| TASK-722 | conftest.py golden_vectors fixture with SP:16 values | @tester | ✅ DONE |
| TASK-723 | CI gate: `pytest -m golden` in GitHub Actions python-tests.yml | @ops | ✅ DONE |
| — | 90%+ branch coverage on `codes/is456/` — 99% achieved | @tester | ✅ DONE |
| — | Add `@clause("34.1")` to `size_footing()` | @structural-math | ✅ DONE |

## v0.21.6 — API Quality & Introspection ✅ DONE

**Theme:** Self-describing, self-validating library
**Completed:** 2026-04-06
**Quality Gate:** check_code("IS456") returns report, OpenAPI drift check in CI ✅

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-724 | Implement `check_code("IS456")` — validates code implementation contract | @backend | ✅ DONE |
| TASK-725 | Implement `show_versions()` — library + dependency info | @backend | ✅ DONE |
| TASK-726 | API surface freeze: OpenAPI baseline diff in CI | @ops | ✅ DONE |
| TASK-727 | Function limitation docs — what each function does NOT do | @doc-master | ✅ DONE |

## v0.21.7 — Security Hardening

**Theme:** Close all OWASP-relevant gaps (see architecture doc §12)
**Target:** 2-3 sessions after v0.21.6
**Quality Gate:** `audit_input_validation.py` reports 0 unresolved findings. `pip-audit` clean.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-728 | JSON body size limit middleware (1MB default) | @api-developer | 📋 |
| TASK-729 | Cross-field plausibility guards (API boundary validation) | @api-developer | 📋 |
| TASK-730 | Input validation audit completion (`audit_input_validation.py`) | @security | 📋 |
| TASK-731 | Dependency CVE scanning in CI (`pip-audit`) | @ops | 📋 |
| — | WebSocket message rate limit (5 msg/s per session) | @api-developer | 📋 |
| — | Computation timeout (prevent pathological inputs) | @api-developer | 📋 |

## v0.21.8 — Performance & Property Testing

**Theme:** Performance baselines and property-based invariants
**Target:** 2-3 sessions after v0.21.7
**Quality Gate:** All benchmarks baselined. Hypothesis tests pass 10,000 examples.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-732 | pytest-benchmark integration for hot-path functions | @tester | 📋 |
| TASK-733 | Property-based testing with Hypothesis (flexure/shear/column) | @tester | 📋 |
| TASK-734 | Performance regression baselines in CI (>20% slowdown blocks merge) | @ops | 📋 |
| — | Benchmark results stored in `Python/test_stats.json` | @tester | 📋 |

## v0.22.0 — Stabilization Release

**Theme:** Production-quality release with full provenance and CI gates
**Target:** After all v0.21.x complete
**Quality Gate:** All v0.21.x quality gates pass simultaneously. SP:16 verification ±0.1%. Release preflight clean.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-735 | CalculationProvenance foundation (`core/provenance.py`) — see arch doc §11 | @backend | 📋 |
| TASK-736 | SP:16 full verification | @structural-engineer | 📋 |
| TASK-521 | Beam rationalization | @backend | 📋 [CARRIED OVER] |
| TASK-643 | SP:16 chart verification completion | @structural-engineer | 📋 [CARRIED OVER] |
| — | Deprecate old architecture docs | @doc-master | 📋 |
| — | Full CI/CD pipeline with all quality gates active | @ops | 📋 |
| — | Release checklist automation | @ops | 📋 |

## Library Expansion — Multi-Code, Multi-Element

> **v5.0:** Multi-code (IS 456 + ACI 318 + EC2), multi-element expansion. Every function goes through a 9-step quality pipeline.
> See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full plan.
> Use `/function-quality-pipeline` skill for every new function.

### Completed Phases (Summary)

| Phase | Scope | Tasks | Status |
|-------|-------|-------|--------|
| Phase 0 | Quality Infrastructure | TASK-600–610 (11/11) | ✅ Done |
| Phase 1 | Foundation Cleanup | TASK-611–625 (15/15) | ✅ Done |
| Phase 1.5 | IS 456 Beam Restructure | TASK-700–712 (13/13) | ✅ Done |
| Phase 2 | Column Design | TASK-630–646 (14/14) | ✅ Done |
| Phase 3 (partial) | Footing Design | TASK-650–654 (5/7) | 🔄 5/7 |
| Variable Naming | IS 456 convention migration | TASK-660 (1/1) | ✅ Done |
| Agent Evolver | Self-evolving agent system | TASK-800.P3–P11 | ✅ Done (P12 burn-in) |
| Agent Infrastructure | claw-code adaptation | TASK-850–872 (23/23) | ✅ Done |
| Git Hardening | Git workflow automation | TASK-900–913 (13/14) | ✅ 13/14 |

> Full details for all completed phases: [tasks-history.md](_archive/tasks-history.md)

### Phase 3: Footing Design (Remaining)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-655 | Dowel bars | `check_dowel_bars` | Cl 34.2.5 | 📋 |
| TASK-656 | Footing FastAPI endpoint | `POST /api/v1/design/footing` | — | 📋 |

> Phase 3: 5/7 tasks done (TASK-650–654 ✅). Covers: types+errors, bearing sizing (Cl 34.1), flexure (Cl 34.2.3.1), one-way shear (Cl 34.2.4.1(a)), punching shear (Cl 31.6.1), bearing pressure (Cl 34.4). 89+ tests. Remaining: TASK-655 (dowel bars), TASK-656 (FastAPI endpoint).

---

## v0.23 — IS 456 Slabs & Footing Completion

**Ref:** Architecture doc §20.6

### Footing Remaining

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-655 | Dowel bars | `check_dowel_bars` | Cl 34.2.5 | 📋 |
| TASK-656 | Footing FastAPI endpoint | `POST /api/v1/design/footing` | — | 📋 |
| — | Combined footing design | — | — | 📋 |
| — | Footing `@clause` coverage to 100% | — | — | 📋 |

### One-Way Slab Design (IS 456 Cl 24.1–24.2)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-737 | One-way slab design (umbrella) | — | Cl 24.1–24.2 | 📋 |
| TASK-750 | Slab types + errors | Types (SlabClassification, SlabDesignResult) | — | 📋 |
| TASK-751 | classify_slab | `classify_slab()` | ly/lx ratio | 📋 |
| TASK-752 | One-way coefficients | `oneway_coefficients()` | Table 12/13 | 📋 |
| TASK-753 | Design one-way slab | `design_oneway_slab()` | Cl 24.1–24.2 | 📋 |
| TASK-754 | Slab detailing | `slab_detailing()` | Cl 26.5 | 📋 |

### Two-Way Slab Design (IS 456 Cl 24.3, Annex D)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-738 | Two-way slab design (umbrella) | — | Cl 24.3, Annex D | 📋 |
| TASK-760 | Two-way moment coefficients | `twoway_moment_coefficients()` | Table 26 | 📋 |
| TASK-761 | Two-way shear coefficients | `twoway_shear_coefficients()` | Table 27 | 📋 |
| TASK-762 | Design two-way slab | `design_twoway_slab()` | Annex D-1 | 📋 |
| TASK-763 | Torsion reinforcement | `torsion_reinforcement()` | Annex D-1.7/D-1.8 | 📋 |
| TASK-764 | Strip distribution | `strip_distribution()` | Annex D-1.2 | 📋 |
| — | Flat slab with drop panels | — | IS 456 Cl 31 | 📋 |

### Punching Shear (Shared — Slab + Footing)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-770 | General punching shear module | `punching_shear_check()` | Cl 31.6 | 📋 |

### Slab FastAPI + React

| ID | Task | Status |
|----|------|--------|
| TASK-780 | Slab API wiring (services/api.py) | 📋 |
| TASK-781 | Slab FastAPI endpoints | 📋 |
| TASK-782 | Slab React form + results panel | 📋 |

### Additional v0.23 Deliverables (from architecture doc §20.6)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| — | Progress callbacks for batch operations (§13.2) | @backend | 📋 |
| — | Complete error hierarchy (§13.3) | @backend | 📋 |
| — | Property-based testing expansion to all modules (§14.1) | @tester | 📋 |
| — | Performance benchmarks baselined (§14.2) | @tester | 📋 |

---

## v0.24 — Multi-Code Infrastructure

**Ref:** Architecture doc §20.7 + [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) Phase 2

| ID | Task | Description | Owner | Status |
|----|------|-------------|-------|--------|
| TASK-739 | CodeRegistry thread-safe locking | Make CodeRegistry safe for concurrent use | @backend | 📋 |
| TASK-740 | DesignEnvelope wrapper | Multi-code result wrapper (§5.3) | @backend | 📋 |
| TASK-741 | core/units.py | Unit conversion at boundary (in→mm, psi→MPa) | @backend | 📋 |
| TASK-800-INFRA-1 | Activate CodeRegistry | `services/api.py` uses `CodeRegistry.get()` for dispatch | @backend | 📋 |
| TASK-800-INFRA-2 | IS456Code implements ABCs | FlexureDesigner, ShearDesigner, ColumnDesigner | @backend | 📋 |
| TASK-800-INFRA-3 | Code-specific input dataclasses | IS456BeamInput, ACI318BeamInput, EC2BeamInput | @backend | 📋 |
| — | Code Amendment Tracking metadata (§11.2) | @structural-math | 📋 |
| — | National annex support infrastructure | @backend | 📋 |
| — | Entry-point plugin discovery for third-party codes (§16.7) | @backend | 📋 |
| — | Auto-generated client SDKs (Python + TypeScript, §13.1) | @api-developer | 📋 |
| — | API v2 routes: `/api/v2/{code}/design/beam` | @api-developer | 📋 |
| TASK-800-INFRA-6 | Namespace clauses.json v2 | Add code field to clause entries | @backend | 📋 |
| TASK-800-INFRA-7 | Code discovery API | `list_codes()`, `get_capabilities()` | @backend | 📋 |
| TASK-800-INFRA-8 | FastAPI v2 routes | `/api/v2/{code}/design/beam` | @api-developer | 📋 |
| TASK-800-INFRA-9 | Feature flags for experimental codes | EXPERIMENTAL_CODES config | @ops | 📋 |

---

## v0.25 — ACI 318-19 Beam

**Ref:** Architecture doc §20.8 + [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) Phase 3

| ID | Task | Description | Owner | Status |
|----|------|-------------|-------|--------|
| TASK-742 | ACI 318-19 beam flexure | `codes/aci318/beam_flexure.py` | @structural-math | 📋 |
| TASK-743 | ACI 318-19 beam shear | `codes/aci318/beam_shear.py` | @structural-math | 📋 |
| — | PCA Notes (12th Ed.) benchmarks ±0.1% | @tester | 📋 |
| — | `@register_code("ACI318")` activation | @backend | 📋 |
| — | ACI318 FastAPI endpoints | @api-developer | 📋 |

### v0.26–v0.28 (Future)

| Version | Code | Elements | Benchmark Source |
|---------|------|----------|-----------------|
| v0.26 | ACI 318-19 | Column + Slab | PCA Notes |
| v0.27 | EC2 | Beam (flexure + shear) | Concrete Centre ±0.1% |
| v0.28 | EC2 | Column + Slab | Concrete Centre |

---

## v1.0 — Production Multi-Code Release

**Ref:** Architecture doc §20.9

| ID | Task | Owner | Status |
|----|------|-------|--------|
| — | IS 456 complete (beam + column + slab + footing) | @structural-math | 📋 |
| — | ACI 318 beam + column | @structural-math | 📋 |
| — | EC2 beam (basic) | @structural-math | 📋 |
| — | CalculationProvenance on all results (§11) | @backend | 📋 |
| — | Export integrity/watermarking (§11.3) | @backend | 📋 |
| — | Full OWASP compliance (§12) | @security | 📋 |
| — | API stability guarantee (no breaking changes without major version) | @backend | 📋 |
| — | Complete documentation coverage | @doc-master | 📋 |
| — | Performance benchmarks all met (§14.2) | @tester | 📋 |
| — | RBAC / scope enforcement (§3.5) | @api-developer | 📋 |
| — | Design audit trail middleware (§11.1) | @api-developer | 📋 |

### Post-v1.0 Research (from architecture doc §20.10)

| Item | Description | Status |
|------|-------------|--------|
| WASM compilation path | Layer 2 pure math → Pyodide/Rust for client-side calc | 🔲 Research |
| msgspec serialization | Benchmark vs frozen dataclass for batch perf | 🔲 Research |
| structuralcodes integration | Material models as optional backend | 🔲 Research |
| IS 16700 (tall buildings) | Wind/seismic response spectra | 🔲 Research |
| IS 1893 integration | Seismic load generation | 🔲 Research |

---

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-513 | React: AI assistant port | ⏸ Deferred | Deferred — needs LLM API design, not in v0.22 scope |
| TASK-908 | bats-core tests for git scripts | 🟢 Low | Deferred — requires bats-core install |
| API-5 | OpenAPI examples on Pydantic models | 🟢 Low | Moved from v0.22 — non-blocking |
| OPS-3 | Python dependency lock file | 🟢 Low | Moved from v0.22 — non-blocking |
| DOC-4 | Footing section in api.md | 🟢 Low | Moved from v0.22 — non-blocking |
| DOC-5 | Clause-to-function mapping | 🟢 Low | Moved from v0.22 — non-blocking |
| — | E2E integration test (React against live FastAPI) | 🟡 Medium | Target v0.21.6+ |
| — | Wire BuildingEditor Cost tab (placeholder → real data) | 🟢 Low | Use `/optimization/cost-rates` |
| — | 28 unit conversion warnings | 🟢 Low | Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |
| — | 287 legacy import warnings (Streamlit) | 🟢 Low | Won't fix — will go away when Streamlit is deprecated |
| — | IS 456 extended elements (Wall Cl 32, Staircase Cl 33, Deep beam Cl 29) | 🟢 Low | Post v1.0 |
| — | Companion codes (IS 875, IS 1893, ASCE 7, EN 1990/1991) | 🟢 Low | Post v1.0 |

---

## Archive

Sessions 32–73 and legacy TASK items have been completed. See [docs/_archive/tasks-history.md](_archive/tasks-history.md) for details.

Key milestones from archived sessions:
- **Session 73** (Jan 24): FastAPI skeleton (20 routes, 31 tests), WebSocket endpoint, `discover_api_signatures.py`
- **Session 66** (Jan 24): V3 automation foundation, 143 scripts audited, API latency validated
- **Session 65** (Jan 23): Agent effectiveness research, `docs-canonical.json`, `automation-map.json`
- **Session 63** (Jan 23): Rebar consolidation, scanner fixes, TASK-350/351/352 resolved
- **Sessions 32–62c** (Jan 22): Rebar editor, DXF export, cost optimizer, section geometry

---

**Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history.
**Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
