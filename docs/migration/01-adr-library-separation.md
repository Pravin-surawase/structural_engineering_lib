---
owner: Pravin Surawase
status: proposed
version: "2.0"
last_updated: 2026-04-08
doc_type: adr
complexity: critical
tags: [architecture, packaging, separation, library, professional, is456, pypi, multi-code, aci318, ec2]
---

# ADR 0004: Library Separation & Professional Packaging Strategy

**Date:** 2026-04-07
**Version:** 2.0
**Status:** Proposed
**Owners:** Pravin Surawase
**Supersedes:** Extends ADR 0001 (3-Layer Architecture)
**Impact:** Critical — affects repository structure, CI/CD, imports, PyPI publishing, versioning, naming, API surface
**Research Basis:** Online best practices survey, library-expert assessment, structural-engineer audit, complete function audit (123 current IS 456 exports, 564 target multi-code functions)

## Version History

- **v2.0 (2026-04-08):** Added multi-code scope (ACI 318, EC2), 5-layer architecture, 564 target functions, name blocker documented, Protocol + Registry pattern
- **v1.0 (2026-04-07):** Initial ADR — IS 456 only, 123 functions, rcdesign naming

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Decision: Two-Repository Split](#2-decision-two-repository-split)
3. [Naming Strategy](#3-naming-strategy)
4. [Library Repository — Complete Structure](#4-library-repository--complete-structure)
5. [Application Repository](#5-application-repository)
6. [Complete Classification Table — 123 Exports Audited](#6-complete-classification-table--123-exports-audited)
7. [BBS Split Decision](#7-bbs-split-decision)
8. [Audit Trail Split Decision](#8-audit-trail-split-decision)
9. [IS 456 Completeness Scorecard](#9-is-456-completeness-scorecard)
10. [Gap Analysis & Roadmap](#10-gap-analysis--roadmap)
11. [Professional Library Standards](#11-professional-library-standards)
12. [Verification & Benchmarks](#12-verification--benchmarks)
13. [Migration Plan — 4 Phases](#13-migration-plan--4-phases)
14. [API Naming Convention](#14-api-naming-convention)
15. [Versioning & Release Strategy](#15-versioning--release-strategy)
16. [Risks & Mitigations](#16-risks--mitigations)
17. [Decision Matrix — Options Considered](#17-decision-matrix--options-considered)
18. [Success Criteria](#18-success-criteria)
19. [Open Questions](#19-open-questions)
20. [Appendices](#20-appendices)

---

## 1. Problem Statement

The monorepo `structural_engineering_lib` has grown from a **pure IS 456 calculation library** into a **full-stack application** (React 19 + FastAPI + Python library). This creates compounding problems across three stakeholder groups.

### For Library Users (Engineers, Researchers, Developers)

- **`pip install structural-lib-is456`** pulls in 149 Python source files when they need ~50
- The package bundles visualization, reports, CSV adapters, insights, BBS exporters — none required for `design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)`
- 176+ scripts, 16 AI agents, a React app — all irrelevant to a calculation library
- Hard to trust a "library" that ships with a web application inside it
- Can't assess library quality because it's buried under application code
- Indian engineers searching PyPI for "is456" won't find `structural-lib-is456` (name is too long and unmemorable)

### For Application Developers (Us)

- Library changes require full-stack CI (React build, Docker, FastAPI tests)
- A typo fix in `flexure.py` triggers 143 test files, React builds, Docker compose
- Agent infrastructure (16 agents, 14 skills, 176 scripts) bloats the repository
- Hard to onboard contributors — "which part am I working on?"
- Version bumps affect both library and app simultaneously

### For Professional Credibility

- No serious engineering library ships with a React app in the same repo
- Libraries like `scipy`, `numpy`, `openseespy`, `sectionproperties`, `COMPAS` are all standalone
- A structural engineering library needs to inspire trust — bloat undermines that
- Missing critical IS 456 elements (slabs: 0/100, load combinations: 0/100) while shipping optional extras

### The Core Issue

> **We are shipping a kitchen when users asked for a knife.**

The library (`codes/is456/`, `core/`, `services/api.py`) is ~50 files of clean, well-tested math with 73 core functions. Everything else — adapters, visualization, insights, reports, 30 APP functions, agents, React, FastAPI — is **application infrastructure** that happens to use the library.

---

## 2. Decision: Two-Repository Split

### The Two Repositories

| | Repository A: **Library** | Repository B: **Application** |
|---|---|---|
| **PyPI name** | `<PACKAGE_NAME>` ⚠️ | N/A (Docker-distributed) |
| **Package import** | `import <PACKAGE_NAME>` or `from <PACKAGE_NAME> import ...` | N/A |
| **Purpose** | Pure IS 456:2000 structural calculations | Full-stack engineering platform |
| **Users** | Engineers, researchers, Python devs | End-users via browser |
| **Distribution** | PyPI: `pip install rcdesign` | Docker / hosted |
| **Dependencies** | `pydantic` only | FastAPI, React, the library, ezdxf, jinja2, etc. |
| **Size** | ~50 files, <500KB | Full stack, any size |
| **CI time** | <60 seconds (pytest + mypy) | 5-10 minutes (full stack) |
| **Release cadence** | Stable, strict semver | Frequent, feature-driven |
| **Quality bar** | IS 456 compliance, SP:16 benchmarks, 95%+ coverage | UX, performance, integration |

### Why Two Repos (Not Monorepo with Better Boundaries)

1. **Independent versioning** — Library reaches v1.0 stable while app is v0.5 experimental
2. **Independent CI** — Library CI runs in 30 seconds, not 10 minutes
3. **Independent contributors** — Math people don't need Node.js, Docker, or Colima
4. **Independent releases** — Fix a formula → publish to PyPI in minutes
5. **Clean `pip install`** — Users get exactly what they need, nothing more
6. **Trust signal** — A focused repo with 50 files inspires more trust than one with 500
7. **Competitor parity** — `sectionproperties`, `COMPAS`, `openseespy` all use this pattern

### Multi-Code Expansion Decision

> **Added in v2.0** — Extends the library scope beyond IS 456 to support ACI 318-19 and Eurocode 2 (EN 1992-1-1).

The library will support **multi-code design** via a **Protocol + CodeRegistry** pattern, enabling engineers to switch between design codes while using the same API surface.

**9 Protocol Interfaces Defined:**

| Protocol | Purpose | IS 456 | ACI 318 | EC2 |
|----------|---------|--------|---------|-----|
| `MaterialCode` | Concrete/steel grade definitions | ✅ | Phase 3 | Phase 4 |
| `FlexuralCode` | Beam flexure design | ✅ | Phase 3 | Phase 4 |
| `ShearCode` | Shear design & detailing | ✅ | Phase 3 | Phase 4 |
| `TorsionCode` | Torsion design | ✅ | Phase 3 | Phase 4 |
| `ColumnCode` | Column design (axial + bending) | ✅ | Phase 3 | Phase 4 |
| `SlabCode` | Slab design (one-way + two-way) | Phase 2 | Phase 4 | Phase 4 |
| `FootingCode` | Footing/foundation design | ✅ | Phase 4 | Phase 4 |
| `ServiceabilityCode` | Deflection + crack width | ✅ | Phase 3 | Phase 4 |
| `DetailingCode` | Rebar detailing rules | ✅ | Phase 3 | Phase 4 |

**Implementation Order:**
1. **Phase 1:** IS 456 beams + columns (current — 123 functions)
2. **Phase 2:** IS 456 all elements (slabs, load combos, remaining gaps)
3. **Phase 3:** ACI 318 beams + columns (~150 additional functions)
4. **Phase 4:** EC2 beams + columns (~150 additional functions)

**Total target: 564 functions** across all three codes.

**Cross-code comparison** is a first-class feature:
```python
from <PACKAGE_NAME> import compare_beam_design

results = compare_beam_design(
    b_mm=300, d_mm=500, Mu_kNm=200,
    codes=["IS456", "ACI318", "EC2"]
)
# Returns comparison table with each code's Ast, safety factor, governing clause
```

> See [03-library-repo-blueprint.md](03-library-repo-blueprint.md) for detailed 5-layer architecture.

### 5-Layer Architecture (v2.0)

The library adopts a **5-layer architecture** to support multi-code design:

```
Layer 1: core/          ← Base types, constants, errors (no code-specific math)
Layer 2: common/        ← Shared math: stress blocks, reinforcement, tables
Layer 3: codes/         ← Code-specific pure math (is456/, aci318/, ec2/)
Layer 4: services/      ← Orchestration: design_beam(), compare_codes()
Layer 5: ui/            ← External interfaces (NOT in library repo)
```

**Import rule:** Each layer may only import from layers below it. `codes/` cannot import from `services/`. `common/` cannot import from `codes/`.

> This extends the original 4-layer architecture (v1.0) by adding the `common/` layer between `core/` and `codes/`, which is essential for sharing stress block calculations and reinforcement utilities across IS 456, ACI 318, and EC2 implementations.

---

## 3. Naming Strategy

> ⚠️ **Name Blocker (v2.0):** `rcdesign` is **TAKEN on PyPI** (v0.4.18, by Satish Annigeri). The package name decision is blocked pending resolution. All references to `rcdesign` in this ADR should be read as `<PACKAGE_NAME>` until a new name is chosen. See [08-naming-and-accounts.md](08-naming-and-accounts.md) for the naming investigation and fallback options.

### Recommended: `rcdesign` on PyPI

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **PyPI name** | `rcdesign` | 8 characters, professional, universally understood ("RC Design") |
| **Import name** | `rcdesign` | Same as PyPI name — no discrepancy, clean DX |
| **Install command** | `pip install rcdesign` | Short, memorable, professional |
| **Fallback if taken** | `rcdesign-py` → `rc-design` | Checked in order |

### Why `rcdesign` over `is456`

- `is456` starts with digits — can't be a Python identifier (`import is456` fails)
- `rcdesign` is universally understood in civil/structural engineering
- Expandable to other codes (ACI 318, Eurocode 2) without renaming
- Same name for PyPI and import — no confusion
- Short (8 chars) — compare `numpy` (5), `scipy` (5), `flask` (5)
- `is456` remains as a keyword/classifier for discoverability

### Import Patterns

```python
# Primary — concise
import rcdesign as rc
result = rc.design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)

# Direct import — for scripts
from rcdesign import design_beam, check_shear, tau_c

# Submodule access — for power users
from rcdesign.beam import flexure
Mu_lim = flexure.calculate_mu_lim(b_mm=230, d_mm=450, fck=25)

# Table lookups — engineering symbols
from rcdesign import tau_c, Mu_lim
stress = tau_c(fck=25, pt=0.8)
```

---

## 4. Library Repository — Complete Structure

### Mission

> A **professional, accurate, minimal** structural design library for Python.
> IS 456:2000 first, with multi-code expansion to ACI 318-19 and EC2 (EN 1992-1-1).
> Zero unnecessary dependencies. Every function traceable to a clause. Every result verifiable.
> 123 current IS 456 exports → 564 target multi-code functions.

### Directory Structure (src/ layout)

The `src/` layout is now industry standard (used by Flask, Pyramid, Twisted, NASA, `sectionproperties`, `COMPAS`). It prevents import parity issues and ensures the installed code is what's tested.

```
rcdesign/                            # GitHub repo name
├── README.md                        # Professional README with badges, examples, benchmarks
├── LICENSE                          # MIT
├── pyproject.toml                   # PEP 621 modern format (packaging.python.org full spec)
├── CHANGELOG.md                     # Semantic versioning log
├── CITATION.cff                     # Academic citation (already have)
├── py.typed                         # PEP 561 marker (at repo root for discoverability)
│
├── src/
│   └── rcdesign/
│       ├── __init__.py              # Clean public API — 40 functions, __version__, show_versions()
│       ├── py.typed                 # PEP 561 marker (in package)
│       ├── _version.py              # Single source of truth for version
│       │
│       ├── core/                    # Base types, constants, materials — NO IS 456 math
│       │   ├── __init__.py
│       │   ├── types.py             # BeamInput, ColumnInput, FootingInput, LoadCase, etc.
│       │   ├── constants.py         # IS 456 constants (γc=1.5, γs=1.15, εcu=0.0035)
│       │   ├── materials.py         # ConcreteGrade, SteelGrade definitions
│       │   ├── sections.py          # RectSection, TSection, CircSection
│       │   ├── reinforcement.py     # Bar, BarGroup, bar area database
│       │   ├── errors.py            # DimensionError, MaterialError, DesignError hierarchy
│       │   ├── numerics.py          # safe_divide, clamp, interpolation utilities
│       │   └── validation.py        # Input validators (dimensions, material ranges)
│       │
│       ├── beam/                    # IS 456 beam design (Cl 22, 23, 26, 37–41, Annex C/F/G)
│       │   ├── __init__.py          # Re-exports: design_beam, check_shear, design_torsion, ...
│       │   ├── flexure.py           # 8 functions (see §6)
│       │   ├── shear.py             # 5 functions
│       │   ├── torsion.py           # 6 functions
│       │   ├── serviceability.py    # Deflection (Cl 23.2), crack width (Annex F)
│       │   └── detailing.py         # Spacing, cover, curtailment (Cl 26.2–26.5)
│       │
│       ├── column/                  # IS 456 column design (Cl 25, 39, IS 13920 Cl 6–7)
│       │   ├── __init__.py
│       │   ├── axial.py             # Short column axial capacity (Cl 39.3)
│       │   ├── uniaxial.py          # Uniaxial bending (Cl 39.5)
│       │   ├── biaxial.py           # Biaxial interaction (Cl 39.6)
│       │   ├── slenderness.py       # Effective length, classification (Cl 25, Table 28)
│       │   ├── long_column.py       # Additional moments (Cl 39.7)
│       │   ├── helical.py           # Helical reinforcement (Cl 39.4)
│       │   ├── detailing.py         # Cl 26.5.3 rules
│       │   └── ductile.py           # IS 13920 ductile detailing (Cl 6–7)
│       │
│       ├── footing/                 # IS 456 footing design (Cl 34, 31.6)
│       │   ├── __init__.py
│       │   ├── bearing.py           # Bearing pressure checks
│       │   ├── flexure.py           # Critical section flexure
│       │   ├── one_way_shear.py     # One-way shear check
│       │   └── punching_shear.py    # Punching shear (Cl 31.6)
│       │
│       ├── slab/                    # IS 456 slab design — NEW (Cl 24, Annex D)
│       │   ├── __init__.py
│       │   ├── one_way.py           # One-way slab (Cl 24)
│       │   └── two_way.py           # Two-way slab (Cl 24 + Table 26, Annex D)
│       │
│       ├── common/                  # Cross-element shared math
│       │   ├── __init__.py
│       │   ├── stress_blocks.py     # Rectangular stress block (Cl 38.1) — 5 functions
│       │   ├── reinforcement.py     # Steel stress-strain, bar areas, IS 2502
│       │   ├── loads.py             # Load combinations (IS 456 Table 18) — NEW
│       │   ├── tables.py            # IS 456 lookup tables (Table 19, 20, 23, 26)
│       │   ├── bbs.py               # BBS math: cut lengths, shape codes, bar weights (IS 2502)
│       │   └── detailing.py         # General detailing rules shared across elements
│       │
│       ├── _internals/              # Private utilities (not in public API)
│       │   ├── traceability.py      # Clause reference tracking
│       │   ├── compliance.py        # Code compliance checking (service-layer → moved here)
│       │   └── audit.py             # CalculationHash, CalculationRecord (SHA-256, no I/O)
│       │
│       └── data/
│           └── clauses.json         # IS 456 clause metadata
│
├── tests/
│   ├── conftest.py                  # Shared fixtures (standard beams, columns)
│   ├── test_beam_flexure.py         # SP:16 Chart-verified cases
│   ├── test_beam_shear.py           # Table 19/20 exact match
│   ├── test_beam_torsion.py
│   ├── test_beam_serviceability.py
│   ├── test_column_axial.py
│   ├── test_column_uniaxial.py
│   ├── test_column_biaxial.py
│   ├── test_column_slenderness.py
│   ├── test_footing.py
│   ├── test_slab.py                 # NEW — one-way + two-way
│   ├── test_load_combinations.py    # NEW — Table 18
│   ├── test_bbs_math.py             # BBS cut lengths, shape codes
│   ├── test_stress_blocks.py
│   ├── test_tables.py               # IS 456 table lookups exact match
│   ├── test_benchmarks_sp16.py      # SP:16 Charts 1–62 known-answer tests (±0.1%)
│   ├── test_benchmarks_textbook.py  # Pillai & Menon examples (±1%)
│   ├── test_edge_cases.py           # Boundary conditions, zero inputs
│   ├── test_monotonicity.py         # Property-based: increasing load → increasing steel
│   ├── test_dimensional.py          # Dimensional consistency checks
│   └── test_regression.py           # Regression tests
│
├── benchmarks/
│   ├── sp16_handbook_cases.json     # SP:16 worked examples (Charts 1–62)
│   ├── pillai_menon_examples.json   # Textbook verification cases
│   └── verify_accuracy.py           # Benchmark runner
│
├── docs/
│   ├── getting-started.md
│   ├── api-reference.md             # Auto-generated from docstrings (mkdocstrings)
│   ├── examples/
│   │   ├── basic_beam_design.py
│   │   ├── column_interaction.py
│   │   ├── footing_design.py
│   │   └── slab_design.py           # NEW
│   ├── theory/
│   │   ├── beam-flexure-derivation.md
│   │   ├── column-interaction-theory.md
│   │   ├── stress-block-assumptions.md
│   │   └── clause-mapping.md        # Function → IS 456 clause reference
│   └── verification/
│       ├── benchmark-results.md
│       └── known-limitations.md
│
└── .github/
    └── workflows/
        ├── test.yml                 # pytest on every push (<60 seconds)
        ├── typecheck.yml            # mypy --strict + pyright
        ├── lint.yml                 # ruff check + ruff format --check
        ├── benchmark.yml            # SP:16 accuracy benchmarks on release
        └── publish.yml              # PyPI publish on tag (trusted publisher)
```

### Complete Function Inventory — What Stays in the Library

#### `beam/flexure.py` — 8 functions

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `calculate_mu_lim` | Cl 38.1, G-1.1 | Limiting moment of resistance |
| `calculate_ast_required` | Cl 38.1 | Required tension steel area |
| `design_singly_reinforced` | Cl 38.1 | Full singly reinforced beam design |
| `design_doubly_reinforced` | Cl 38.1, G-1.2 | Compression steel when Mu > Mu_lim |
| `calculate_mu_lim_flanged` | Cl 38.1, Annex G | Mu_lim for T-beams and L-beams |
| `design_flanged_beam` | Annex G | Complete flanged beam design |
| `calculate_effective_flange_width` | Cl 23.1.2 | Effective flange width (T/L beams) |
| `calculate_effective_depth_multilayer` | Cl 26.2 | Centroid of multi-layer reinforcement |

#### `beam/shear.py` — 5 functions

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `calculate_tv` | Cl 40.1 | Nominal shear stress |
| `design_shear` | Cl 40.1–40.4 | Complete shear design with stirrups |
| `enhanced_shear_strength` | Cl 40.5 | Enhanced shear near supports |
| `round_to_practical_spacing` | — | Practical stirrup spacing rounding |
| `select_stirrup_diameter` | Cl 26.5.1.6 | Stirrup bar diameter selection |

#### `beam/torsion.py` — 6 functions

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `calculate_equivalent_shear` | Cl 41.3.1 | Equivalent shear from torsion |
| `calculate_equivalent_moment` | Cl 41.4.2 | Equivalent moment from torsion |
| `torsion_shear_stress` | Cl 41.3 | Torsional shear stress |
| `torsion_stirrup_area` | Cl 41.4.3 | Transverse reinforcement for torsion |
| `longitudinal_torsion_steel` | Cl 41.4.2 | Longitudinal steel for torsion |
| `design_torsion` | Cl 41 | Complete torsion design |

#### `beam/serviceability.py` + `beam/detailing.py`

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `check_deflection_span_depth` | Cl 23.2 | Basic span/depth ratio check |
| `check_crack_width` | Annex F | Crack width estimation |
| `check_beam_slenderness` | Cl 23.3 | Lateral stability check |
| `check_beam_ductility` | Annex G | Ductility index verification |
| `check_anchorage_at_simple_support` | Cl 26.2.3.3 | Ld check at supports |
| `compute_critical` | Cl 22.6 | Critical section for shear |
| `enhanced_shear_strength_is456` | Cl 40.5 | av/d enhanced shear |

#### `column/` — 10 functions

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `design_short_column_uniaxial` | Cl 39.5 | Uniaxial bending design |
| `design_column_axial` | Cl 39.3 | Short column pure axial |
| `biaxial_bending_check` | Cl 39.6 | Bresler's equation check |
| `pm_interaction_curve` | Cl 39.5 | P-M interaction diagram generation |
| `calculate_additional_moment` | Cl 39.7.1 | Slender column additional moments |
| `design_long_column` | Cl 39.7 | Complete long column design |
| `check_helical_reinforcement` | Cl 39.4 | Helical column capacity increase |
| `create_column_detailing` | Cl 26.5.3 | Detailing rules verification |
| `calculate_effective_length` | Table 28 | Effective length per end conditions |
| `classify_column` | Cl 25.1.2 | Short/slender classification |

#### `column/ductile.py` — IS 13920

| Function | IS 13920 Reference | Description |
|----------|-------------------|-------------|
| `check_column_ductility_is13920` | Cl 6, 7 | Seismic ductile detailing |
| `min_eccentricity` | Cl 25.4 | Minimum eccentricity per IS 456 |

#### `footing/` — 10 functions across 4 files

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `check_bearing_pressure` | Cl 34.1 | Soil bearing pressure vs SBC |
| `design_footing_flexure` | Cl 34.2.3 | Critical section bending |
| `check_one_way_shear` | Cl 34.2.4 | One-way shear at d from face |
| `check_punching_shear` | Cl 31.6 | Two-way punching shear |
| `design_isolated_footing` | Cl 34 | Complete isolated footing design |
| `compute_footing_depth` | — | Minimum depth from shear |
| `compute_footing_reinforcement` | Cl 34.3 | Steel area in each direction |
| `check_development_length` | Cl 26.2 | Ld check for footing bars |
| `bearing_stress_at_column` | Cl 34.4 | Column-footing bearing |
| `compute_transfer_reinforcement` | Cl 34.4.1 | Dowel bar requirement |

#### `common/stress_blocks.py` — 5 functions

| Function | IS 456 Reference | Description |
|----------|-----------------|-------------|
| `neutral_axis_depth` | Cl 38.1 | xu from strain compatibility |
| `xu_max_ratio` | Cl 38.1 | Limiting xu/d for given fy |
| `compression_force` | Cl 38.1 | 0.36·fck·b·xu |
| `lever_arm` | Cl 38.1 | d − 0.42·xu |
| `moment_capacity` | Cl 38.1 | Force × lever arm |

#### Orchestration Functions (35 — stay as high-level API)

| Function | Description |
|----------|-------------|
| `design_beam` | Complete beam design (flexure + shear + detailing) |
| `check_beam` | Check existing beam against loads |
| `detail_beam` | Generate detailing summary |
| `design_and_detail_beam` | Design + detail in one call |
| `compute_detailing` | Detailing computation |
| `build_detailing_input` | Construct detailing input from design result |
| `check_compliance_report` | IS 456 compliance report generation |
| `design_column` | Unified column design |
| `design_long_column` | Long column with additional moments |
| `detail_column` | Column detailing summary |
| `design_beams` | Batch beam design (list input) |
| `design_beams_iter` | Batch beam design (generator) |

### Public API Surface (Target: ~40 functions)

```python
import rcdesign as rc

# ─── Beam Design ───────────────────────────────────
result = rc.design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)
# result.Ast_mm2, result.is_safe(), result.clause_ref, result.summary()

shear = rc.check_shear(b_mm=230, d_mm=450, Vu_kN=120, fck=25, Ast_mm2=result.Ast_mm2)
# shear.tau_v, shear.tau_c, shear.stirrup_spacing_mm

torsion = rc.design_torsion(b_mm=230, d_mm=450, Tu_kNm=15, Vu_kN=80, Mu_kNm=85, fck=25, fy=415)
deflection = rc.check_deflection(b_mm=230, d_mm=450, span_mm=5000, Ast_mm2=462, fck=25, fy=415)
crack = rc.check_crack_width(b_mm=230, d_mm=450, Ast_mm2=462, bar_dia=16, spacing=150)

# ─── Column Design ─────────────────────────────────
col = rc.design_column_axial(b_mm=300, D_mm=300, Pu_kN=1500, fck=25, fy=415)
col_uni = rc.design_column_uniaxial(b_mm=300, D_mm=500, Pu_kN=800, Mu_kNm=120, fck=25, fy=415)
curve = rc.interaction_curve(b_mm=300, D_mm=500, fck=25, fy=415, Ast_mm2=2400)
ok = rc.check_biaxial(b_mm=300, D_mm=500, Pu_kN=800, Mux_kNm=80, Muy_kNm=60, fck=25, fy=415)
rc.check_slenderness(length_mm=4000, b_mm=300, end_conditions="fixed-fixed")
rc.design_long_column(b_mm=300, D_mm=500, Pu_kN=800, Mu_kNm=120, length_mm=6000, fck=25, fy=415)

# ─── Footing Design ────────────────────────────────
ftg = rc.check_bearing_pressure(length_mm=2000, width_mm=2000, Pu_kN=800, SBC_kPa=150)
punch = rc.check_punching_shear(d_mm=400, col_b=300, col_D=300, Pu_kN=800, fck=25)

# ─── Common / Table Lookups (engineering symbols) ──
Mu_lim = rc.Mu_lim(b_mm=230, d_mm=450, fck=25)
stress = rc.tau_c(fck=25, pt=0.8)                   # IS 456 Table 19
factors = rc.load_combination(dead=25, live=10, eq=5) # Table 18

# ─── BBS Math (CORE — IS 2502) ─────────────────────
cut_len = rc.cut_length(bar_dia=16, shape_code='51', dimensions={'a': 500, 'b': 300})
weight = rc.bar_weight(bar_dia=16, length_mm=3500)

# ─── Batch Design ──────────────────────────────────
results = rc.design_beams([beam1, beam2, beam3])

# ─── Version & Metadata ────────────────────────────
rc.__version__   # "1.0.0"
rc.show_versions()
```

### What The Library Does NOT Do

| Concern | Why Not | Where It Goes |
|---------|---------|---------------|
| CSV/ETABS/SAFE file parsing | I/O is not math | App repo (adapters) |
| 3D geometry for visualization | Three.js/WebGL data = frontend concern | App repo |
| HTML/PDF report generation | Presentation concern | App repo (reports) |
| DXF export | CAD integration | App repo (export) |
| BBS export (`export_bbs_to_csv`, etc.) | File I/O concern | App repo (export) |
| Design insights/suggestions | UX feature | App repo (insights) |
| Cost estimation | Business logic | App repo (services) |
| Multi-objective optimization | UI workflow | App repo (optimization) |
| Excel COM bridge | Platform-specific I/O | App repo |
| Bill of quantities formatting | Construction management | App repo |
| WebSocket live design | Real-time UX | App repo (websocket) |
| Job runner / pipeline | Infrastructure | App repo |

### pyproject.toml

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "rcdesign"
dynamic = ["version"]
description = "Professional IS 456:2000 structural design library for Python"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Pravin Surawase" },
]
keywords = ["structural-engineering", "reinforced-concrete", "is456", "beam-design", "column-design"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Typing :: Typed",
]
dependencies = [
    "pydantic>=2.0",      # Data validation — the ONLY runtime dependency
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "hypothesis>=6.0",    # Property-based testing
    "mypy>=1.10",
    "ruff>=0.4",
    "pyright>=1.1",
]
docs = [
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.25",
]

[project.urls]
Documentation = "https://rcdesign.readthedocs.io"
Repository = "https://github.com/user/rcdesign"
Changelog = "https://github.com/user/rcdesign/blob/main/CHANGELOG.md"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/rcdesign/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/rcdesign"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "TCH", "RUF"]

[tool.mypy]
strict = true
python_version = "3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers --cov=rcdesign --cov-report=term-missing"
```

**One runtime dependency.** The library is installable anywhere Python 3.11+ runs.

---

## 5. Application Repository

### Mission

> A **full-stack structural engineering platform** powered by `rcdesign`.
> Import CSV → Design → Visualize 3D → Export Reports → Iterate.

### Directory Structure

```
structural-engineering-app/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── Dockerfile.fastapi
│
├── fastapi_app/                     # REST + WebSocket API
│   ├── main.py
│   ├── config.py
│   ├── routers/                     # 13 routers, 60 endpoints
│   ├── models/                      # Pydantic request/response models
│   ├── services/                    # App-layer services (all moved from lib)
│   │   ├── adapters.py              # GenericCSVAdapter (71KB, 40+ column mappings)
│   │   ├── etabs_import.py          # ETABS-specific parsing
│   │   ├── visualization.py         # beam_to_3d_geometry(), compute_rebar_positions()
│   │   ├── insights/                # Design suggestions, intelligence (9 files)
│   │   ├── reports/                 # HTML/PDF/SVG generation + templates
│   │   ├── export/                  # DXF, BBS export, report export
│   │   ├── costing.py               # Cost estimation
│   │   ├── optimization.py          # Multi-objective optimization
│   │   ├── rebar_optimizer.py       # Rebar selection optimization
│   │   ├── serialization.py         # JSON persistence
│   │   ├── job_runner.py            # Batch job execution
│   │   ├── dashboard.py             # UI analytics aggregation
│   │   ├── excel_bridge.py          # Excel COM bridge
│   │   └── audit_trail.py           # AuditTrail (stateful I/O — see §8)
│   └── tests/
│
├── react_app/                       # React 19 + R3F + Tailwind
│   └── src/ ...
│
├── scripts/                         # Deployment, tooling, agents
├── agents/                          # 16 AI agent configs
├── docs/                            # App-specific docs
│
└── requirements.txt
    # rcdesign>=1.0,<2.0               ← THE LIBRARY AS A DEPENDENCY
    # fastapi>=0.115
    # uvicorn[standard]
    # ezdxf>=1.0
    # jinja2>=3.1
    # reportlab>=4.0
    # etc.
```

### Key Principle

The app repo consumes the library like any other pip package:

```python
# fastapi_app/routers/design.py
from rcdesign import design_beam   # ← pip-installed library
from ..services.adapters import parse_etabs_csv  # ← app-layer

@router.post("/api/v1/design/beam")
async def design_beam_endpoint(req: BeamRequest):
    result = design_beam(
        b_mm=req.b_mm, d_mm=req.d_mm,
        Mu_kNm=req.Mu_kNm, fck=req.fck, fy=req.fy
    )
    return result
```

---

## 6. Complete Classification Table — 123 Exports Audited (564 Target)

Every export in the current `structural_lib` has been classified into one of three categories. Multi-code expansion (ACI 318, EC2) targets 564 total functions — see §2 Multi-Code Expansion Decision.

### CORE — 73 Functions (Stay in Library)

| Module | # | Functions |
|--------|---|-----------|
| `codes/is456/beam/flexure.py` | 8 | `calculate_mu_lim`, `calculate_ast_required`, `design_singly_reinforced`, `design_doubly_reinforced`, `calculate_mu_lim_flanged`, `design_flanged_beam`, `calculate_effective_flange_width`, `calculate_effective_depth_multilayer` |
| `codes/is456/beam/shear.py` | 5 | `calculate_tv`, `design_shear`, `enhanced_shear_strength`, `round_to_practical_spacing`, `select_stirrup_diameter` |
| `codes/is456/beam/torsion.py` | 6 | `calculate_equivalent_shear`, `calculate_equivalent_moment`, `torsion_shear_stress`, `torsion_stirrup_area`, `longitudinal_torsion_steel`, `design_torsion` |
| `codes/is456/column/` | 7 | `biaxial_bending_check`, `calculate_additional_moment`, `check_helical_reinforcement`, `create_column_detailing`, `design_long_column`, `design_short_column_uniaxial`, `pm_interaction_curve` |
| `codes/is456/footing/` | 10 | `check_bearing_pressure`, `design_footing_flexure`, `check_one_way_shear`, `check_punching_shear`, `design_isolated_footing`, `compute_footing_depth`, `compute_footing_reinforcement`, `check_development_length`, `bearing_stress_at_column`, `compute_transfer_reinforcement` |
| `codes/is456/common/stress_blocks.py` | 5 | `neutral_axis_depth`, `xu_max_ratio`, `compression_force`, `lever_arm`, `moment_capacity` |
| `beam_api.py` (CORE functions) | 7 | `check_beam_ductility`, `check_beam_slenderness`, `check_deflection_span_depth`, `check_crack_width`, `enhanced_shear_strength_is456`, `compute_critical`, `check_anchorage_at_simple_support` |
| `column_api.py` (CORE functions) | 10 | `calculate_effective_length_is456`, `classify_column_is456`, `min_eccentricity_is456`, `design_column_axial_is456`, `design_short_column_uniaxial_is456`, `pm_interaction_curve_is456`, `biaxial_bending_check_is456`, `calculate_additional_moment_is456`, `check_helical_reinforcement_is456`, `check_column_ductility_is13920` |
| `core/` types & utilities | 15+ | `BeamInput`, `ColumnInput`, `ConcreteGrade`, `SteelGrade`, `DimensionError`, `MaterialError`, etc. |

### ORCHESTRATION — 35 Functions (Stay as Library High-Level API)

| Function | Description | New Name (§14) |
|----------|-------------|-----------------|
| `design_beam_is456` | Complete beam design pipeline | `design_beam` |
| `check_beam_is456` | Check existing beam | `check_beam` |
| `detail_beam_is456` | Generate detailing summary | `detail_beam` |
| `design_and_detail_beam_is456` | Design + detail combined | `design_and_detail_beam` |
| `compute_detailing` | Detailing computation | `compute_detailing` |
| `build_detailing_input` | Construct detailing input | `build_detailing_input` |
| `check_compliance_report` | IS 456 compliance report | `check_compliance` |
| `design_long_column_is456` | Long column design | `design_long_column` |
| `design_column_is456` | Unified column design | `design_column` |
| `detail_column_is456` | Column detailing | `detail_column` |
| `design_beams` | Batch design (list) | `design_beams` |
| `design_beams_iter` | Batch design (generator) | `design_beams_iter` |

### APP — 30 Functions (Move to Application Repository)

| Module | # | Functions | Reason |
|--------|---|-----------|--------|
| `services/bbs.py` | 22 | `compute_bbs`, `export_bbs`, `export_bbs_to_csv`, `export_bbs_to_json`, `generate_bbs_document`, + 17 formatting/export functions | File I/O and formatting |
| `services/report.py` | 1 | `compute_report` | HTML/PDF generation |
| `services/dxf_export.py` | 1 | `compute_dxf` | CAD file export |
| `services/optimization.py` | 3 | `optimize_beam_cost`, `suggest_beam_design_improvements`, `smart_analyze_design` | UI workflow |
| `visualization/geometry_3d.py` | 2 | `beam_to_3d_geometry`, `compute_rebar_positions` | Three.js data generation |
| `insights/*` | ~6 | All insight/suggestion functions | UX feature |
| `services/adapters.py` | ~5 | `GenericCSVAdapter`, all parsers | File I/O |

### DEPRECATED / REMOVE

| Current Path | Reason |
|-------------|--------|
| `structural_lib/api.py` (stub) | Backward-compat shim → remove in v1.0 |
| `structural_lib/flexure.py` (shim) | Already in `codes/is456/beam/` |
| `structural_lib/shear.py` (shim) | Already moved |
| `structural_lib/detailing.py` (shim) | Already moved |
| `structural_lib/beam_pipeline.py` | App-layer orchestration |
| 23 root-level files (shims) | Audit individually — most are duplicates |
| `scripts/_archive/` (120+ files) | Historical baggage — delete |

---

## 7. BBS Split Decision

### Decision: SPLIT — Math Stays, Export Moves

Per the library-expert assessment, BBS functions are classified using the **scipy litmus test**: "Would scipy include it? scipy computes properties (yes to cut lengths), but never generates CSV files (no to export)."

#### CORE (Stay in Library) — `common/bbs.py`

| Function | IS 2502 Reference | Description |
|----------|-------------------|-------------|
| `cut_length()` | IS 2502 | Calculate cut length from bar shape code + dimensions |
| `bar_weight()` | IS 2502 | Weight from diameter + length |
| `shape_code_classify()` | IS 2502 | Classify bar into standard shape codes |
| `bbs_line_item()` | — | Compute single BBS line item (diameter, shape, cut length, weight) |

These are **pure calculations** based on IS 2502 formulas. A Jupyter notebook user doing reinforcement takeoff needs them.

#### APP (Move to Application) — `export/bbs_export.py`

| Function | Description |
|----------|-------------|
| `export_bbs_to_csv()` | Write BBS to CSV file |
| `export_bbs_to_json()` | Serialize BBS to JSON |
| `generate_bbs_document()` | Full BBS document with headers/totals |
| All formatting functions | Table rendering, PDF templates |

These do **file I/O and document formatting** — clearly application concerns.

---

## 8. Audit Trail Split Decision

### Decision: SPLIT — Hash/Record Stays, I/O Moves

Professional engineering firms require verifiable, reproducible calculations. The audit trail has two distinct layers.

#### CORE (Stay in Library) — `_internals/audit.py`

| Component | Description |
|-----------|-------------|
| `CalculationHash` | SHA-256 hash of input parameters + results for integrity verification |
| `CalculationRecord` | Immutable record: inputs, outputs, IS 456 clause ref, timestamp, hash |

These are **pure computations** — hashable, serializable, no file I/O. A library user can verify that a result hasn't been tampered with.

#### APP (Move to Application) — `services/audit_trail.py`

| Component | Description |
|-----------|-------------|
| `AuditTrail` | Stateful accumulator of `CalculationRecord`s — manages state |
| `AuditTrail.save()` | Write trail to file |
| `AuditTrail.load()` | Read trail from file |
| `AuditTrail.export_pdf()` | Generate audit report |

These perform **stateful accumulation and file writing** — application infrastructure.

---

## 9. IS 456 Completeness Scorecard

Assessment by structural-engineer with 80+ implemented functions audited.

### Current Implementation Status

| Element | Clauses Covered | Score | Assessment |
|---------|----------------|-------|------------|
| **Beam** | Cl 6.2, 22, 23.1.2, 23.2, 26.2–26.5, 38.1, 40.1–40.4, 41, Annex C, F, G, Table 19/20 | **95/100** | EXCELLENT — near-complete |
| **Column** | Cl 25, 39.3–39.7, Table 28, IS 13920 Cl 6 | **90/100** | VERY GOOD — IS 13920 Cl 7 missing |
| **Footing** | Cl 34, 31.6 | **75/100** | BASIC — isolated only |
| **Slab** | — | **0/100** | CRITICAL GAP |
| **Load combinations** | — | **0/100** | CRITICAL GAP |

### Architecture Score: 90/100

- 4-layer architecture is correct for standalone library
- `load_analysis.py` should move to `core/` (structural mechanics, not IS 456-specific) ✓ planned
- `compliance.py` is service-layer disguised as code-layer — move to `_internals/` ✓ planned
- Remove backward-compat shims for clean v1.0 release ✓ planned

---

## 10. Gap Analysis & Roadmap

### Minimum Viable Set for "Professional" Library

#### Tier 1 — Must Have for v1.0 (Critical)

| Element | IS 456 Clauses | Priority | Status |
|---------|---------------|----------|--------|
| Current beam (as-is) | Cl 22–26, 38–41, Annex C/F/G | — | ✅ Done (95/100) |
| Current column (as-is) | Cl 25, 39, Table 28 | — | ✅ Done (90/100) |
| Current footing (as-is) | Cl 34, 31.6 | — | ✅ Done (75/100) |
| **One-way slab** | Cl 24 | P1 | ❌ Not started |
| **Two-way slab** | Cl 24 + Table 26, Annex D | P1 | ❌ Not started |
| **Load combinations** | Table 18 | P1 | ❌ Not started |
| **Nominal cover table** | Table 16, 16A | P1 | ❌ Not started |
| **BBS math** | IS 2502 | P1 | ⚠️ Needs extraction from services/bbs.py |
| IS 13920 column ductile | Cl 7 | P1 | ⚠️ Partially implemented |

#### Tier 2 — Competitive (v1.1–v1.3)

| Element | IS 456 Clauses | Priority |
|---------|---------------|----------|
| Continuous beams | Cl 30 | P2 |
| Flat slab | Cl 31 | P2 |
| Wall design | Cl 32 | P2 |
| Combined footings | Cl 34 (extended) | P2 |

#### Tier 3 — Complete (v2.0)

| Element | IS 456 Clauses | Priority |
|---------|---------------|----------|
| Staircase | Cl 33 | P3 |
| Deep beam | Cl 29 | P3 |
| Fire resistance | Annex B | P3 |
| Pile caps | Cl 34 (extended) | P3 |
| Retaining walls | — | P3 |

### Completeness Target

| Version | Element Coverage | Clause Coverage | Professional Readiness |
|---------|-----------------|-----------------|----------------------|
| **v1.0** | Beam + Column + Footing + Slab + Loads | ~70% of IS 456 | ✅ Professional for buildings |
| **v1.3** | + Continuous beams + Flat slabs + Walls | ~85% | ✅ Competitive with commercial |
| **v2.0** | + Staircase + Deep beam + Fire + Piles | ~95% | ✅ Reference implementation |

---

## 11. Professional Library Standards

### Industry Best Practices (Researched)

| Standard | Source | Our Plan |
|----------|--------|----------|
| **src/ layout** | ionelmc.ro, hynek.me, Flask, NASA | `src/rcdesign/` — prevents import parity issues |
| **py.typed** | PEP 561 | Include in package root — mandatory for typed libraries |
| **pyproject.toml** | packaging.python.org | Modern PEP 621 format (no setup.py, no setup.cfg) |
| **SPEC-0000** | Scientific Python | Python version support = 3 years; core dep support = 2 years |
| **CITATION.cff** | GitHub/Zenodo | Already have — enables academic citations |
| **ruff** | `sectionproperties` | Linting + formatting in one tool |
| **mypy --strict** | Industry standard | Full type annotations enforced in CI |
| **pre-commit hooks** | `sectionproperties`, `COMPAS` | ruff, mypy, test on every commit |
| **codecov** | `sectionproperties` | Coverage badge in README |
| **Hypothesis** | Property-based testing | For edge cases in numerical code |
| **Deprecation warnings** | `warnings.warn()` | Graceful migration path |

### Competitor Analysis

| Library | Stars | Structure | Build System | Key Features |
|---------|-------|-----------|-------------|-------------|
| **sectionproperties** | 520 | src/ layout | uv | CITATION.cff, ruff, pre-commit, codecov. Pure cross-section properties. |
| **PyNite** | 684 | Flat layout | setuptools | Optional deps via `[all]` extras. `pip install PyNiteFEA[all]` |
| **COMPAS** | 356 | src/ layout | conda-forge | Separates core from CAD plugins (compas_rhino, compas_blender as separate packages) |
| **openseespy** | — | Separate repos | C++ bindings | Library + examples split across repos |
| **Our target** | — | src/ layout | hatchling | `pip install rcdesign` — pydantic only, <500KB |

### Quality Gates for Library Releases

```
BEFORE ANY LIBRARY RELEASE:
 ✅ All tests pass (pytest -v --strict-markers)
 ✅ Type check passes (mypy --strict src/)
 ✅ Lint passes (ruff check src/ && ruff format --check src/)
 ✅ Coverage ≥ 95% (pytest --cov=rcdesign)
 ✅ SP:16 benchmark suite passes (±0.1%)
 ✅ Textbook benchmark suite passes (±1%)
 ✅ Monotonicity tests pass (property-based)
 ✅ No new runtime dependencies added
 ✅ CHANGELOG.md updated
 ✅ API docs regenerated
 ✅ pip install from built wheel works in clean venv
 ✅ import rcdesign; rcdesign.show_versions() works
```

### README Template for Library Repo

```markdown
# rcdesign

Professional IS 456:2000 structural design library for Python.

[![PyPI](https://img.shields.io/pypi/v/rcdesign)](https://pypi.org/project/rcdesign/)
[![Tests](https://img.shields.io/github/actions/workflow/status/.../test.yml)](...)
[![Coverage](https://img.shields.io/codecov/c/github/.../rcdesign)](...)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/rcdesign)](...)
[![Typed](https://img.shields.io/badge/typing-typed-green)](...)

## Features

- **Beam design**: Flexure, shear, torsion, serviceability (Cl 22–41, Annex C/F/G)
- **Column design**: Axial, uniaxial, biaxial, slenderness, IS 13920 (Cl 25, 39)
- **Footing design**: Bearing, flexure, punching shear (Cl 34)
- **Slab design**: One-way, two-way (Cl 24, Table 26)
- **Load combinations**: IS 456 Table 18
- **BBS math**: Cut lengths, bar weights, shape codes (IS 2502)
- **Verified**: Against SP:16 Charts 1–62 (±0.1%) and textbook examples (±1%)
- **Typed**: Full type annotations, PEP 561 compatible, mypy strict
- **Minimal**: Only dependency is `pydantic`

## Quick Start

    pip install rcdesign

    import rcdesign as rc

    result = rc.design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)
    print(f"Steel required: {result.Ast_mm2:.0f} mm²")
    print(f"Safe: {result.is_safe()}")
    print(f"Reference: {result.clause_ref}")

## Verification

All results verified against IS 456:2000 SP:16 handbook examples.
See [benchmark results](docs/verification/benchmark-results.md).
```

---

## 12. Verification & Benchmarks

### Verification Strategy (Per Structural-Engineer Assessment)

| Test Category | Tolerance | Source | Count |
|--------------|-----------|--------|-------|
| **SP:16 Charts 1–62** | ±0.1% | IS 456 SP:16:1980 handbook | 62 test cases |
| **IS 456 Table 19/20** | Exact match | IS 456:2000 tables | ~50 lookup tests |
| **Pillai & Menon Examples** | ±1% | Textbook, 8th Edition | ~30 test cases |
| **Monotonicity tests** | Directional | Property-based (Hypothesis) | ~20 properties |
| **Boundary conditions** | Exact | Edge cases (zero, min, max) | ~40 test cases |
| **Dimensional consistency** | Exact | Units verification | ~15 test cases |
| **Regression tests** | Exact | Previously-found bugs | Grows over time |

### SP:16 Benchmark Suite (Required for v1.0)

```python
# tests/test_benchmarks_sp16.py

@pytest.mark.parametrize("case", load_sp16_cases("chart_1_singly_reinforced"))
def test_sp16_chart_1(case):
    """SP:16 Chart 1: Mu/bd² vs pt for fck=15, fy=250."""
    result = design_singly_reinforced(
        b_mm=case.b, d_mm=case.d, Mu_kNm=case.Mu, fck=case.fck, fy=case.fy
    )
    assert result.Ast_mm2 == pytest.approx(case.expected_Ast, rel=0.001)  # ±0.1%
```

### Textbook Verification

```python
# tests/test_benchmarks_textbook.py

def test_pillai_menon_example_5_1():
    """Pillai & Menon, 8th Ed., Example 5.1, p.178.
    Singly reinforced beam: b=250, d=450, M=140 kNm, M25, Fe415.
    Expected: Ast = 982 mm²
    """
    result = design_beam(b_mm=250, d_mm=450, Mu_kNm=140, fck=25, fy=415)
    assert result.Ast_mm2 == pytest.approx(982, rel=0.01)  # ±1%
```

### Property-Based Tests (Hypothesis)

```python
from hypothesis import given, strategies as st

@given(
    fck=st.sampled_from([15, 20, 25, 30, 35, 40]),
    Mu1=st.floats(min_value=10, max_value=200),
    Mu2=st.floats(min_value=10, max_value=200),
)
def test_increasing_moment_increases_steel(fck, Mu1, Mu2):
    """Monotonicity: higher moment → more steel (or equal)."""
    if Mu1 < Mu2:
        r1 = design_beam(b_mm=230, d_mm=450, Mu_kNm=Mu1, fck=fck, fy=415)
        r2 = design_beam(b_mm=230, d_mm=450, Mu_kNm=Mu2, fck=fck, fy=415)
        assert r2.Ast_mm2 >= r1.Ast_mm2
```

---

## 13. Migration Plan — 4 Phases

### Phase 0: Audit & Cleanup (Week 1)

| # | Task | Status |
|---|------|--------|
| 0.1 | Complete file audit — classify every file as CORE / APP / DEPRECATED | ✅ Done (§6) |
| 0.2 | Remove all deprecated shim files at `structural_lib/` root (pre-migration cleanup) | ☐ |
| 0.3 | Remove `scripts/_archive/` (120+ dead files) | ☐ |
| 0.4 | Remove backward-compat `structural_lib/api.py` stub | ☐ |
| 0.5 | Document exact current API surface (123 IS 456 exports → 73 CORE + 35 ORCH + 30 APP; 564 target multi-code) | ✅ Done (§6) |
| 0.6 | Create SP:16 benchmark test suite (Charts 1–62) | ☐ |
| 0.7 | Create Pillai & Menon textbook test suite | ☐ |
| 0.8 | Run full test suite — confirm 100% pass | ☐ |
| 0.9 | Extract BBS math from `services/bbs.py` into `common/bbs.py` | ☐ |
| 0.10 | Split `services/audit.py` into hash (CORE) and trail (APP) | ☐ |
| 0.11 | Move `compliance.py` from codes to `_internals/` | ☐ |
| 0.12 | Move `load_analysis.py` to `common/loads.py` | ☐ |

### Phase 1: Internal Separation (Weeks 2–3)

| # | Task | Status |
|---|------|--------|
| 1.1 | Move all 30 APP functions out of `structural_lib/` into `fastapi_app/services/` (pre-split cleanup) | ☐ |
| 1.2 | Move `visualization/` → `fastapi_app/services/visualization/` | ☐ |
| 1.3 | Move `insights/` (9 files) → `fastapi_app/services/insights/` | ☐ |
| 1.4 | Move `reports/` → `fastapi_app/services/reports/` | ☐ |
| 1.5 | Move `services/adapters.py` (71KB) → `fastapi_app/services/adapters.py` | ☐ |
| 1.6 | Move all export/serialization/optimization services | ☐ |
| 1.7 | Move BBS export functions to `fastapi_app/services/export/bbs.py` | ☐ |
| 1.8 | Move `AuditTrail` I/O to `fastapi_app/services/audit_trail.py` | ☐ |
| 1.9 | Update all imports in `fastapi_app/routers/` | ☐ |
| 1.10 | Run full test suite — confirm 100% pass | ☐ |
| 1.11 | Remove optional dependency groups from pyproject.toml (dxf, render, report, pdf, cad) | ☐ |
| 1.12 | Verify `pip install` produces clean, minimal wheel (<500KB) | ☐ |
| 1.13 | Rename public API: drop `_is456` suffix (see §14) | ☐ |

### Phase 2: Repository Split (Week 4)

| # | Task | Status |
|---|------|--------|
| 2.1 | Create new GitHub repo: `rcdesign` | ☐ |
| 2.2 | Copy library code into `src/rcdesign/` layout | ☐ |
| 2.3 | Add `py.typed` marker | ☐ |
| 2.4 | Set up CI: pytest, mypy --strict, ruff, coverage, benchmarks | ☐ |
| 2.5 | Set up PyPI trusted publisher workflow | ☐ |
| 2.6 | Add pre-commit hooks (ruff, mypy) | ☐ |
| 2.7 | Publish `v1.0.0-rc1` to Test PyPI | ☐ |
| 2.8 | Test: `pip install rcdesign` in clean venv → `import rcdesign` works | ☐ |
| 2.9 | Update app repo to depend on published package | ☐ |
| 2.10 | Verify: all 60 API endpoints still work with pip-installed library | ☐ |

### Phase 3: Polish & Ship (Weeks 5–6)

| # | Task | Status |
|---|------|--------|
| 3.1 | Library README with badges, examples, verification results | ☐ |
| 3.2 | Generate API docs with mkdocstrings | ☐ |
| 3.3 | Write theory docs (beam flexure derivation, stress block assumptions) | ☐ |
| 3.4 | Implement Tier 1 gaps: one-way slab, two-way slab | ☐ |
| 3.5 | Implement Tier 1 gaps: load combinations (Table 18) | ☐ |
| 3.6 | Implement Tier 1 gaps: nominal cover table (Table 16/16A) | ☐ |
| 3.7 | Publish library `v1.0.0` to PyPI | ☐ |
| 3.8 | App repo: rename current monorepo or create new `structural-engineering-app` | ☐ |
| 3.9 | App repo: remove library source code (now pip dependency) | ☐ |
| 3.10 | App repo: set up full-stack CI (React build, FastAPI tests, Docker) | ☐ |
| 3.11 | Archive or redirect old monorepo | ☐ |
| 3.12 | Update all external references (docs, links, citations) | ☐ |

---

## 14. API Naming Convention

### Decision: Drop `_is456` Suffix

The package IS about IS 456 — the suffix is redundant. As the library-expert noted: "It's like scipy having `optimize_minimize_scipy()`."

### Pattern: `{verb}_{element}_{specific}()`

| Current Name | New Name | Rationale |
|-------------|----------|-----------|
| `design_beam_is456()` | `design_beam()` | Package context implies IS 456 |
| `check_beam_is456()` | `check_beam()` | Cleaner |
| `detail_beam_is456()` | `detail_beam()` | Cleaner |
| `design_and_detail_beam_is456()` | `design_and_detail_beam()` | Cleaner |
| `design_column_is456()` | `design_column()` | Cleaner |
| `design_long_column_is456()` | `design_long_column()` | Cleaner |
| `detail_column_is456()` | `detail_column()` | Cleaner |
| `calculate_effective_length_is456()` | `calculate_effective_length()` | Cleaner |
| `classify_column_is456()` | `classify_column()` | Cleaner |
| `min_eccentricity_is456()` | `min_eccentricity()` | Cleaner |
| `design_column_axial_is456()` | `design_column_axial()` | Cleaner |
| `design_short_column_uniaxial_is456()` | `design_column_uniaxial()` | Simplified |
| `pm_interaction_curve_is456()` | `interaction_curve()` | Shortened |
| `biaxial_bending_check_is456()` | `check_biaxial()` | Verb first |
| `calculate_additional_moment_is456()` | `calculate_additional_moment()` | Cleaner |
| `check_helical_reinforcement_is456()` | `check_helical()` | Shortened |
| `check_column_ductility_is13920()` | `check_ductility_is13920()` | Keep IS 13920 suffix (different code) |
| `enhanced_shear_strength_is456()` | `enhanced_shear_strength()` | Cleaner |

### Table Lookups Use Engineering Symbols

| Function | Returns | IS 456 Reference |
|----------|---------|-----------------|
| `tau_c(fck, pt)` | Design shear stress | Table 19 |
| `tau_c_max(fck)` | Maximum shear stress | Table 20 |
| `Mu_lim(b_mm, d_mm, fck)` | Limiting moment | Cl 38.1 |
| `xu_max(d_mm, fy)` | Maximum neutral axis depth | Table on p.70 |
| `alpha_n(Pu, Puz)` | Biaxial exponent | Cl 39.6 |

### Migration: Deprecation Aliases

```python
# In rcdesign/__init__.py during transition period

def design_beam_is456(*args, **kwargs):
    """Deprecated: Use design_beam() instead."""
    import warnings
    warnings.warn(
        "design_beam_is456() is deprecated, use design_beam()",
        DeprecationWarning, stacklevel=2,
    )
    return design_beam(*args, **kwargs)
```

---

## 15. Versioning & Release Strategy

### Library: Strict Semantic Versioning

```
MAJOR (2.0.0): Breaking API changes (renamed functions, changed return types)
MINOR (1.1.0): New functions, new element types (slab.one_way, slab.two_way)
PATCH (1.0.1): Bug fixes, accuracy improvements, documentation

Pre-release: 1.0.0rc1, 1.0.0b1 (PEP 440 format)
```

### Python Version Support (SPEC-0000)

Per Scientific Python SPEC-0000:
- Support Python versions released in the last **3 years**
- Support core dependencies (pydantic) released in the last **2 years**
- Current: Python 3.11+ (3.11 released Oct 2022, within 3-year window)
- Drop 3.11 no earlier than Oct 2025

### App: Independent Feature Versioning

```
Pin library dependency: rcdesign>=1.0,<2.0
App versions independently and moves faster.
```

### Dependency Update Flow

```
Library publishes v1.1.0 (adds one-way slab design)
    ↓
App repo: bump rcdesign to >=1.1.0
    ↓
App adds new POST /api/v1/design/slab/one-way endpoint
    ↓
React adds SlabForm component
```

### Release Cadence

| Repo | Frequency | Trigger |
|------|-----------|---------|
| Library | Monthly or on IS 456 additions | New clause, accuracy fix |
| App | Weekly or bi-weekly | New UI features, UX improvements |

---

## 16. Risks & Mitigations

### Risk 1: Breaking Existing Users During Migration

- **Impact:** High — anyone using `from structural_lib.services.adapters import ...` breaks
- **Likelihood:** Certain (users exist on current PyPI package)
- **Mitigation:**
  - v0.22.0: Add `DeprecationWarning` for all functions being renamed/moved
  - v0.23.0: Move code internally, keep deprecated aliases
  - v1.0.0: Remove deprecated aliases, clean break
  - Publish migration guide with exact old → new import paths
  - `rcdesign.compat` shim module available for one major version

### Risk 2: Two Repos = Double the Maintenance

- **Impact:** Medium — two CIs, two changelogs, two sets of issues
- **Likelihood:** Ongoing
- **Mitigation:**
  - Library CI is trivial (pytest + mypy = 30 seconds, not 10 minutes)
  - Library changes are infrequent (math doesn't change often — IS 456 is from 2000)
  - Clear ownership: library = accuracy, app = features
  - Reduces total maintenance by decoupling concerns

### Risk 3: Version Mismatch Between Library and App

- **Impact:** Medium — app expects function that doesn't exist in pinned version
- **Likelihood:** Low if version ranges are managed
- **Mitigation:**
  - Pin library version: `rcdesign>=1.0,<2.0`
  - Integration tests in app CI against pinned version
  - Contract tests (ADR 0003)

### Risk 4: Local Development Friction

- **Impact:** Low-Medium — changing both simultaneously requires coordination
- **Likelihood:** Moderate during active development
- **Mitigation:**
  - `pip install -e /path/to/rcdesign` for local development
  - Document this workflow in CONTRIBUTING.md
  - CI tests against published version, dev tests against editable install

### Risk 5: PyPI Name `rcdesign` Already Taken

- **Impact:** High — **CONFIRMED BLOCKER** (v2.0 update)
- **Likelihood:** ~~Low~~ → **Certain** — `rcdesign` v0.4.18 exists on PyPI (Satish Annigeri)
- **Mitigation:**
  - ⚠️ Must choose alternative name — see [08-naming-and-accounts.md](08-naming-and-accounts.md)
  - All docs use `<PACKAGE_NAME>` placeholder until resolved
  - Fallback chain being evaluated in doc 08

### Risk 6: Agent Infrastructure Disruption

- **Impact:** Low — 16 agents, 14 skills, 176 scripts need rethinking
- **Likelihood:** Certain
- **Mitigation:**
  - All agents move to app repo (they're dev tooling for the full stack)
  - Library repo gets simple CI — no agent complexity needed
  - Dramatically reduces cognitive load for library contributors

---

## 17. Decision Matrix — Options Considered

| Criterion (Weight) | A: Monorepo Better Boundaries | B: Workspace Packages | **C: Two Repos (Selected)** | D: Git Submodule |
|----|----|----|----|-----|
| **Clean pip install** (25%) | ⬤⬤○○○ | ⬤⬤⬤○○ | ⬤⬤⬤⬤⬤ | ⬤⬤○○○ |
| **Independent CI** (20%) | ⬤○○○○ | ⬤⬤○○○ | ⬤⬤⬤⬤⬤ | ⬤⬤⬤○○ |
| **Independent versioning** (15%) | ⬤○○○○ | ⬤⬤⬤○○ | ⬤⬤⬤⬤⬤ | ⬤⬤⬤⬤○ |
| **Contributor clarity** (15%) | ⬤⬤○○○ | ⬤⬤○○○ | ⬤⬤⬤⬤⬤ | ⬤○○○○ |
| **Migration effort** (10%) | ⬤⬤⬤⬤⬤ | ⬤⬤⬤○○ | ⬤⬤○○○ | ⬤⬤○○○ |
| **Local dev experience** (10%) | ⬤⬤⬤⬤⬤ | ⬤⬤⬤⬤○ | ⬤⬤⬤○○ | ⬤○○○○ |
| **Professional credibility** (5%) | ⬤⬤○○○ | ⬤⬤⬤○○ | ⬤⬤⬤⬤⬤ | ⬤⬤○○○ |
| **Weighted Score** | **2.05** | **2.45** | **4.30** | **1.90** |

### Option A: Stay Monorepo, Better Boundaries (Rejected)

Addresses symptoms, not root cause. `pip install` still ships everything. CI still takes 10 minutes for a math fix.

### Option B: Monorepo with Workspace Packages (Rejected)

Right idea for JavaScript (turborepo), but Python workspace tooling (uv workspaces, poetry) is immature. Still one `git clone` with 500+ files.

### Option C: Two Repositories (Selected ✅)

Best long-term architecture. One-time migration cost (4–6 weeks) pays for itself in every subsequent cycle through faster CI, cleaner releases, and professional presentation. Matches what `sectionproperties`, `COMPAS`, and `openseespy` all do.

### Option D: Extract Library as Submodule (Rejected)

Git submodules are universally hated. Confusing CI, confusing contributors. Doesn't solve `pip install` bloat.

---

## 18. Success Criteria

### Library Repo (Measurable)

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| `pip install rcdesign` time | <5 seconds | Timed on CI |
| Installed package size | <500KB | `du -sh` after install |
| Runtime dependencies | 1 (pydantic) | `pip show rcdesign` |
| `import rcdesign` | Zero config, zero warnings | CI test |
| SP:16 benchmark accuracy | ±0.1% | 62 test cases pass |
| Textbook benchmark accuracy | ±1% | ~30 test cases pass |
| Test suite coverage | ≥95% on core math | pytest --cov |
| CI completion time | <60 seconds | GitHub Actions timing |
| mypy --strict | Zero errors | CI gate |
| ruff check + format | Zero issues | CI gate |
| Public functions with clause ref docstrings | 100% | Audit script |
| README examples | All runnable | CI test |
| IS 456 clause coverage | ≥70% for v1.0 | Parity dashboard |

### App Repo (Measurable)

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| `docker compose up --build` | Starts in <2 min | CI test |
| API endpoints functional | All 60 | Integration test suite |
| React build | Zero errors | `npm run build` |
| Library consumed via pip | Not source code | Check `requirements.txt` |
| Integration tests pass | 100% | CI gate |

### User Experience (Observable)

| Scenario | Target |
|----------|--------|
| Engineer: `pip install` → beam design | <2 minutes from zero |
| Researcher: Verify against SP:16 example | Run benchmark suite |
| App user: CSV → design → 3D → export | All in browser |
| Contributor: Know which repo to clone | Clear from README |

---

## 19. Open Questions

Most previously-open questions have been answered by the research. Remaining:

| # | Question | Status | Notes |
|---|----------|--------|-------|
| 1 | **PyPI name availability** | ❌ BLOCKED | `rcdesign` is TAKEN (v0.4.18, Satish Annigeri). New name pending — see [08-naming-and-accounts.md](08-naming-and-accounts.md) |
| 2 | **Current repo disposition** | Open | Rename to app repo? Archive + redirect? |
| 3 | **GitHub organization** | Open | Both repos under same user? Dedicated org `rcdesign-org`? |
| 4 | **Backward compat timeline** | Resolved | v0.22.0 deprecation warnings → v1.0.0 removal (1 minor version transition) |
| 5 | **BBS classification** | ✅ Resolved | Math (cut lengths, shape codes) = CORE. Export (CSV, JSON, PDF) = APP. §7 |
| 6 | **Load combinations** | ✅ Resolved | CORE — IS 456 Table 18 is pure math. → `common/loads.py` |
| 7 | **Audit trail split** | ✅ Resolved | `CalculationHash` = CORE. `AuditTrail` I/O = APP. §8 |
| 8 | **API naming** | ✅ Resolved | Drop `_is456` suffix. Pattern: `verb_element_specific()`. §14 |
| 9 | **Contract testing** | Open | Pact-style vs version-pinning? Lean toward version-pinning + integration tests |
| 10 | **slab/ directory** | ✅ Resolved | Include in library structure now (Tier 1 for v1.0). §4, §10 |

---

## 20. Appendices

### Appendix A: Import Migration Map

```python
# ═══════════════════════════════════════════════════════
# BEFORE (monorepo, current)
# ═══════════════════════════════════════════════════════

# Library functions (in user scripts)
from structural_lib import design_beam_is456
result = design_beam_is456(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)

# App-layer imports (in FastAPI routers)
from structural_lib.services.adapters import GenericCSVAdapter
from structural_lib.visualization.geometry_3d import beam_to_3d_geometry
from structural_lib.insights.design_suggestions import suggest
from structural_lib.services.report import generate_report
from structural_lib.services.dxf_export import export_dxf
from structural_lib.services.bbs import compute_bbs, export_bbs_to_csv

# ═══════════════════════════════════════════════════════
# AFTER (two repos)
# ═══════════════════════════════════════════════════════

# Library functions (in user scripts — cleaner names)
from rcdesign import design_beam
result = design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)

# Or with alias
import rcdesign as rc
result = rc.design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)
tau = rc.tau_c(fck=25, pt=0.8)

# BBS math stays in library
cut = rc.cut_length(bar_dia=16, shape_code='51', dimensions={'a': 500, 'b': 300})

# App-layer imports (in FastAPI routers — moved to app repo)
from fastapi_app.services.adapters import GenericCSVAdapter
from fastapi_app.services.visualization import beam_to_3d_geometry
from fastapi_app.services.insights import suggest
from fastapi_app.services.reports import generate_report
from fastapi_app.services.export.dxf import export_dxf
from fastapi_app.services.export.bbs import export_bbs_to_csv
```

### Appendix B: Competitor Comparison

| Feature | sectionproperties | PyNite | COMPAS | **rcdesign (target)** |
|---------|-------------------|--------|--------|---------------------|
| PyPI name | `sectionproperties` | `PyNiteFEA` | `compas` | `rcdesign` |
| Stars | 520 | 684 | 356 | — |
| Releases | 50+ | 90 | 96 | v1.0.0 upcoming |
| Layout | src/ | flat | src/ | **src/** |
| Build system | uv | setuptools | conda-forge | **hatchling** |
| Runtime deps | numpy, shapely | numpy, matplotlib | numpy | **pydantic only** |
| Type stubs | py.typed | No | py.typed | **py.typed** |
| Citation | CITATION.cff | No | CITATION.cff | **CITATION.cff** |
| Linter | ruff | — | ruff | **ruff** |
| Pre-commit | Yes | No | Yes | **Yes** |
| Coverage tool | codecov | — | codecov | **codecov** |
| Scope | Cross-section props | FEA analysis | Geometry + fabrication | **IS 456 RC design** |
| App separation | N/A (pure lib) | N/A (pure lib) | Core + CAD plugins (separate packages) | **Lib + App (2 repos)** |

### Appendix C: Files Audit Decision Flowchart

```
For each file in Python/structural_lib/:

  Does it compute a structural quantity per IS 456?
    YES → CORE (stays in library)
    NO ↓

  Does it compute using IS 2502 (BBS) formulas?
    YES → CORE (stays in common/bbs.py)
    NO ↓

  Does it parse external file formats (CSV, ETABS, Excel)?
    YES → APP (move to fastapi_app/services/)
    NO ↓

  Does it generate output files (HTML, PDF, DXF, CSV)?
    YES → APP (move to fastapi_app/services/)
    NO ↓

  Does it depend on libraries beyond pydantic?
    YES → APP
    NO ↓

  Is it used ONLY by React/FastAPI?
    YES → APP
    NO ↓

  Is it a deprecated backward-compat shim?
    YES → REMOVE in v1.0
    NO ↓

  Would scipy/sectionproperties include this kind of code?
    YES → Probably CORE
    NO → Probably APP

  Could a Jupyter notebook user need this function?
    YES → Probably CORE
    NO → Probably APP
```

### Appendix D: Complete Module Classification

| Current File | Classification | New Location | File Count |
|-------------|---------------|-------------|-----------|
| `codes/is456/beam/flexure.py` | CORE | `src/rcdesign/beam/flexure.py` | 1 |
| `codes/is456/beam/shear.py` | CORE | `src/rcdesign/beam/shear.py` | 1 |
| `codes/is456/beam/torsion.py` | CORE | `src/rcdesign/beam/torsion.py` | 1 |
| `codes/is456/column/*.py` | CORE | `src/rcdesign/column/` | 7 |
| `codes/is456/footing/*.py` | CORE | `src/rcdesign/footing/` | 4 |
| `codes/is456/common/stress_blocks.py` | CORE | `src/rcdesign/common/stress_blocks.py` | 1 |
| `codes/is456/common/reinforcement.py` | CORE | `src/rcdesign/common/reinforcement.py` | 1 |
| `codes/is456/tables.py` | CORE | `src/rcdesign/common/tables.py` | 1 |
| `codes/is456/load_analysis.py` | CORE | `src/rcdesign/common/loads.py` | 1 |
| `codes/is456/serviceability.py` | CORE | `src/rcdesign/beam/serviceability.py` | 1 |
| `codes/is456/detailing.py` | CORE | `src/rcdesign/common/detailing.py` | 1 |
| `codes/is456/ductile.py` | CORE | `src/rcdesign/column/ductile.py` | 1 |
| `codes/is456/traceability.py` | CORE | `src/rcdesign/_internals/traceability.py` | 1 |
| `codes/is456/compliance.py` | CORE | `src/rcdesign/_internals/compliance.py` | 1 |
| `codes/is456/clauses.json` | CORE | `src/rcdesign/data/clauses.json` | 1 |
| `core/*.py` | CORE | `src/rcdesign/core/` | ~8 |
| `services/api.py` | ORCH | `src/rcdesign/__init__.py` | 1 |
| `services/beam_api.py` | ORCH | `src/rcdesign/beam/__init__.py` | 1 |
| `services/column_api.py` | ORCH | `src/rcdesign/column/__init__.py` | 1 |
| `services/common_api.py` | ORCH | `src/rcdesign/common/__init__.py` | 1 |
| `services/batch.py` | ORCH | `src/rcdesign/batch.py` | 1 |
| `services/audit.py` (hash part) | CORE | `src/rcdesign/_internals/audit.py` | 1 |
| `services/audit.py` (trail part) | APP | `fastapi_app/services/audit_trail.py` | 1 |
| `services/bbs.py` (math part) | CORE | `src/rcdesign/common/bbs.py` | 1 |
| `services/bbs.py` (export part) | APP | `fastapi_app/services/export/bbs.py` | 1 |
| `visualization/*.py` | APP | `fastapi_app/services/visualization/` | 2 |
| `insights/*.py` | APP | `fastapi_app/services/insights/` | 9 |
| `reports/*.py` | APP | `fastapi_app/services/reports/` | 2 |
| `services/adapters.py` | APP | `fastapi_app/services/adapters.py` | 1 |
| `services/etabs_import.py` | APP | `fastapi_app/services/etabs_import.py` | 1 |
| `services/excel_*.py` | APP | `fastapi_app/services/excel_*.py` | 2 |
| `services/report*.py` | APP | `fastapi_app/services/reports/` | 3 |
| `services/dxf_export.py` | APP | `fastapi_app/services/export/dxf.py` | 1 |
| `services/serialization.py` | APP | `fastapi_app/services/serialization.py` | 1 |
| `services/job_runner.py` | APP | `fastapi_app/services/job_runner.py` | 1 |
| `services/costing.py` | APP | `fastapi_app/services/costing.py` | 1 |
| `services/*optimizer*.py` | APP | `fastapi_app/services/optimization/` | 3 |
| `services/dashboard.py` | APP | `fastapi_app/services/dashboard.py` | 1 |
| `services/intelligence.py` | APP | `fastapi_app/services/intelligence.py` | 1 |
| `api.py` (root stub) | REMOVE | — | 1 |
| `flexure.py` (root shim) | REMOVE | — | 1 |
| `shear.py` (root shim) | REMOVE | — | 1 |
| `detailing.py` (root shim) | REMOVE | — | 1 |
| `beam_pipeline.py` | APP/REMOVE | `fastapi_app/services/` or remove | 1 |

**Totals: ~52 CORE files, ~30 APP files, ~5 REMOVE**

---

**Decision:** Proceed with Option C (Two-Repository Split) per the phased migration plan.

**PyPI name:** `rcdesign` (fallback: `rcdesign-py`, `rc-design`)
**Package import:** `import rcdesign` / `import rcdesign as rc`

**Next Steps:**
1. ✅ Research complete (4 sources integrated + 2026 toolchain report + state-of-art report)
2. ✅ Function audit complete (123 IS 456 exports classified; 564 multi-code target identified)
3. ❌ **BLOCKED:** Choose package name — `rcdesign` is taken on PyPI. See [08-naming-and-accounts.md](08-naming-and-accounts.md)
4. ☐ Review this ADR with stakeholders
5. ☐ Begin Phase 0: cleanup and benchmark suite creation
6. ☐ Execute Phase 1–3 across 4–6 weeks
7. ☐ Plan Phase 4: multi-code expansion (ACI 318, EC2)
