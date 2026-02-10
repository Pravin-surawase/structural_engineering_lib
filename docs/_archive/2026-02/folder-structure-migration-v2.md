# Folder Structure Migration Plan v2 — 4-Layer vs 5-Layer Analysis

**Type:** Research + Plan
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-02-10
**Last Updated:** 2026-02-10 (Phase 0 complete, deep audit done)

---

## 0. Context & Previous Research

**19 documents** (~8,910 lines) of folder structure research were completed Jan 10–13, 2026. Key sources:

| Document | Purpose |
|----------|---------|
| [enterprise-folder-structure-research.md](../research/enterprise-folder-structure-research.md) | Multi-code library patterns |
| [folder-structure-governance.md](../guidelines/folder-structure-governance.md) | Canonical governance spec (v2.0) |
| [folder-restructuring-plan.md](../research/folder-restructuring-plan.md) | Original restructuring plan |
| [folder-cleanup-research.md](../research/folder-cleanup-research.md) | Cleanup automation |
| [library-refactoring-strategy.md](../research/library-refactoring-strategy.md) | Python lib refactoring |
| [folder-migration-progress.md](../planning/folder-migration-progress.md) | Phase 1 migration tracker |

**What was done:** Phase 1 (docs reorganization) is ✅ COMPLETE. The docs/ tree was restructured from 45 root files to 3, governance rules enforced, 175 orphan files addressed.

**What remains:** The **code** folders (Python library, React app, FastAPI, scripts) have NOT been restructured. The Python library still has 48 `.py` files dumped in the root of `structural_lib/`.

---

## 1. Current State Audit (Feb 10, 2026)

### 1.1 Full Project Metrics

| Layer | Location | Files | Dirs | Problem |
|-------|----------|-------|------|---------|
| **Python Library** | `Python/structural_lib/` | 83 .py | 10 dirs | **48 files in root** (flat dump) |
| **React App** | `react_app/src/` | 55 files | 12 dirs | 14 components mixed in `components/` root |
| **FastAPI** | `fastapi_app/` | 32 .py | 7 dirs | OK — clean router/model split |
| **Scripts** | `scripts/` | 157 files | 1 dir | **FLAT — all 157 in one folder** |
| **Docs** | `docs/` | 630 .md | 27 dirs | ✅ Already restructured |
| **Root** | `/` | 16 dirs | - | Some questionable dirs (`tmp/`, `structural_engineering_lib/`) |

### 1.2 Python Library Structure (THE MAIN PROBLEM)

```
Python/structural_lib/           # ← 48 .py files dumped here!
├── codes/is456/                 # ✅ IS 456 code-specific (12 files, clean)
├── codes/aci318/                # Placeholder (1 file)
├── codes/ec2/                   # Placeholder (1 file)
├── core/                        # ✅ Base abstractions (5 files, clean)
├── insights/                    # ✅ Smart analysis (10 files, clean)
├── reports/                     # ✅ Report gen (2 files)
├── visualization/               # ✅ 3D geometry (2 files)
└── 48 root files!               # ❌ api.py, adapters.py, bbs.py, etc. ALL FLAT
```

**Problem:** The research from Jan 10 proposed moving files into `core/`, `integration/`, `utils/` but **only `codes/`, `core/`, `insights/`, `reports/`, `visualization/` were created.** 48 files remain unorganized.

### 1.3 React App Structure

```
react_app/src/
├── api/           # 1 file (client.ts) — OK
├── assets/        # 1 file (react.svg) — OK
├── components/    # 14 files MIXED + 3 subdirs
│   ├── layout/    # 2 files (TopBar, ModernAppLayout) — OK
│   ├── pages/     # 4 files (Home, ModeSelect, Building, BeamDetail) — OK
│   ├── ui/        # 7 files (BentoGrid, FileDropZone, etc.) — OK
│   └── 14 root files!  # ❌ DesignView, ImportView, Viewport3D, etc. ALL MIXED
├── hooks/         # 8 files — ✅ Clean
├── lib/           # 1 file (utils.ts) — OK
├── store/         # 2 files — ✅ Clean
├── types/         # 2 files — OK
└── utils/         # 3 files — OK
```

### 1.4 Top-Level Root Issues

```
/  (16 directories)
├── structural_engineering_lib/   # ← What is this? Duplicate? Empty?
├── tmp/                          # ← Should be in .gitignore
├── git_operations_log/           # ← Operational, should be in logs/
├── clients/                      # ← python/ + typescript/ — minimal?
├── tests/                        # ← Root tests? Overlap with Python/tests?
```

---

## 2. The Question: 4-Layer or 5-Layer Architecture?

### 2.1 What Are the Layers?

**Current Architecture (3-layer, per CLAUDE.md):**

```
Layer 1: Core     → Python/structural_lib/codes/is456/  (pure math)
Layer 2: App      → api.py, beam_pipeline.py             (orchestration)
Layer 3: UI/IO    → react_app/, streamlit_app/, fastapi_app/  (interfaces)
```

**Proposed 4-Layer:**

```
Layer 1: Core     → Pure calculations (codes/is456/, core/)
Layer 2: Services → Integration, adapters, business logic (integration/)
Layer 3: API      → FastAPI endpoints, WebSocket handlers
Layer 4: UI       → React app, Streamlit app
```

**Proposed 5-Layer:**

```
Layer 1: Core     → Pure math, no I/O (codes/, core/)
Layer 2: Domain   → Domain models, types, validation (models/)
Layer 3: Services → Integration, adapters, orchestration (services/)
Layer 4: API      → FastAPI endpoints (fastapi_app/)
Layer 5: UI       → React, Streamlit (react_app/, streamlit_app/)
```

### 2.2 Analysis: 4-Layer vs 5-Layer

| Criterion | 4-Layer | 5-Layer |
|-----------|---------|---------|
| **Complexity** | Simpler, less indirection | More explicit separation |
| **Current codebase fit** | Good — maps to existing code | Over-engineering for 83 .py files |
| **Team size** | Perfect for small team/AI agents | Better for multi-team |
| **Migration effort** | ~2 hours, low risk | ~4 hours, medium risk |
| **Future multi-code** | Sufficient (codes/ handles it) | Slightly cleaner boundaries |
| **Dependency clarity** | Clear enough | Clearest possible |
| **Agent discoverability** | Good with proper indexes | Diminishing returns vs 4-layer |

### 2.3 Recommendation: **4-Layer Architecture**

**Why 4, not 5:**

1. **The "Domain" layer is already embedded.** `core/base.py`, `types.py`, `models.py`, `data_types.py` exist but don't warrant a separate layer. They naturally belong inside `core/`.
2. **48 root files split cleanly into 3 categories** (core utilities, integration/services, support tools) — no need for a 4th code-level split.
3. **Fewer layers = less confusion for AI agents.** Every layer boundary is a cognitive overhead. 3→4 is justified; 4→5 adds cost without proportional benefit.
4. **The project is NOT a microservices architecture.** It's a library with two UI frontends. Domain objects don't cross network boundaries; they're Python dataclasses shared in-process.

**When 5 would be justified:**
- If we had separate teams per layer
- If domain logic was shared across multiple independent services
- If we needed to version domain models independently of core math

---

## 3. Proposed 4-Layer Structure

### 3.1 Python Library (THE BIG CHANGE)

```
Python/structural_lib/
├── __init__.py                    # Package root
├── __main__.py                    # CLI entry point
│
├── core/                          # LAYER 1: Pure math + fundamentals
│   ├── __init__.py
│   ├── base.py                    # Abstract base classes
│   ├── geometry.py                # Cross-section geometry
│   ├── materials.py               # Material properties
│   ├── registry.py                # Code registry
│   ├── constants.py               # ← MOVE from root
│   ├── types.py                   # ← MOVE from root
│   ├── data_types.py              # ← MOVE from root
│   ├── models.py                  # ← MOVE from root
│   ├── errors.py                  # ← MOVE from root
│   ├── error_messages.py          # ← MOVE from root
│   ├── validation.py              # ← MOVE from root
│   ├── inputs.py                  # ← MOVE from root
│   ├── result_base.py             # ← MOVE from root
│   └── utilities.py               # ← MOVE from root
│
├── codes/                         # LAYER 1: Code-specific calculations
│   ├── __init__.py
│   ├── is456/                     # ✅ Already organized (12 files)
│   ├── aci318/                    # Future
│   └── ec2/                       # Future
│
├── services/                      # LAYER 2: Integration & business logic
│   ├── __init__.py
│   ├── api.py                     # ← MOVE (public API facade)
│   ├── api_results.py             # ← MOVE
│   ├── beam_pipeline.py           # ← MOVE (orchestration)
│   ├── adapters.py                # ← MOVE (CSV adapters)
│   ├── batch.py                   # ← MOVE (batch design)
│   ├── imports.py                 # ← MOVE (import handling)
│   ├── etabs_import.py            # ← MOVE
│   ├── rebar.py                   # ← MOVE (rebar operations)
│   ├── rebar_optimizer.py         # ← MOVE
│   ├── optimization.py            # ← MOVE
│   ├── multi_objective_optimizer.py # ← MOVE
│   ├── compliance.py              # ← MOVE
│   ├── audit.py                   # ← MOVE
│   ├── intelligence.py            # ← MOVE
│   ├── costing.py                 # ← MOVE
│   ├── serialization.py           # ← MOVE
│   ├── dashboard.py               # ← MOVE
│   └── testing_strategies.py      # ← MOVE
│
├── integration/                   # LAYER 2: External I/O
│   ├── __init__.py
│   ├── bbs.py                     # ← MOVE (bar bending schedule)
│   ├── dxf_export.py              # ← MOVE (CAD export)
│   ├── report.py                  # ← MOVE
│   ├── calculation_report.py      # ← MOVE
│   ├── report_svg.py              # ← MOVE
│   ├── excel_bridge.py            # ← MOVE
│   ├── excel_integration.py       # ← MOVE
│   ├── job_runner.py              # ← MOVE
│   └── job_cli.py                 # ← MOVE
│
├── insights/                      # ✅ ALREADY ORGANIZED (10 files)
│   └── ...
│
├── reports/                       # ✅ ALREADY ORGANIZED (2 files)
│   └── ...
│
└── visualization/                 # ✅ ALREADY ORGANIZED (2 files)
    └── ...
```

**File movement summary:**
- **15 files → `core/`** (types, models, errors, validation, utilities)
- **18 files → `services/`** (API, adapters, business logic)
- **9 files → `integration/`** (I/O, export, reports)
- **6 files stay because already organized** (codes/, insights/, reports/, visualization/)
- **Net: 48 root files → 0 root files** (except `__init__.py`, `__main__.py`)

**Remaining duplicates to resolve:**
- `flexure.py` (root) vs `codes/is456/flexure.py` — root is legacy, verify same content
- `shear.py` (root) vs `codes/is456/shear.py` — same
- `detailing.py`, `ductile.py`, `serviceability.py`, `torsion.py`, `slenderness.py`, `tables.py` — all duplicated

### 3.2 React App Structure

```
react_app/src/
├── api/                            # HTTP/WS client
│   └── client.ts
│
├── components/
│   ├── layout/                     # App shell, navigation
│   │   ├── TopBar.tsx
│   │   └── ModernAppLayout.tsx
│   │
│   ├── pages/                      # Route-level page components
│   │   ├── HomePage.tsx
│   │   ├── ModeSelectPage.tsx
│   │   ├── BuildingEditorPage.tsx
│   │   └── BeamDetailPage.tsx
│   │
│   ├── design/                     # ← NEW: Design feature group
│   │   ├── DesignView.tsx          # ← MOVE from components/
│   │   ├── BeamForm.tsx            # ← MOVE
│   │   ├── ResultsPanel.tsx        # ← MOVE
│   │   └── CrossSectionView.tsx    # ← MOVE
│   │
│   ├── import/                     # ← NEW: Import feature group
│   │   ├── ImportView.tsx          # ← MOVE
│   │   ├── CSVImportPanel.tsx      # ← MOVE
│   │   └── BeamTable.tsx           # ← MOVE
│   │
│   ├── viewport/                   # ← NEW: 3D visualization
│   │   ├── Viewport3D.tsx          # ← MOVE
│   │   ├── WorkspaceLayout.tsx     # ← MOVE
│   │   └── LandingView.tsx         # ← MOVE
│   │
│   ├── ui/                         # Shared/primitive UI components
│   │   ├── BentoGrid.tsx
│   │   ├── FloatingDock.tsx
│   │   ├── ConnectionStatus.tsx
│   │   ├── Toast.tsx
│   │   ├── FileDropZone.tsx
│   │   ├── Skeleton.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── index.ts
│   │
│   ├── CommandPalette.tsx          # Global overlay (OK in root)
│   └── index.ts
│
├── hooks/                          # ✅ Already clean (8 files)
├── store/                          # ✅ Already clean (2 files)
├── types/                          # ✅ OK (2 files)
├── utils/                          # ✅ OK (3 files)
├── lib/                            # ✅ OK (1 file)
└── assets/                         # ✅ OK (1 file)
```

**React movement summary:**
- 4 files → `components/design/` (DesignView, BeamForm, ResultsPanel, CrossSectionView)
- 3 files → `components/import/` (ImportView, CSVImportPanel, BeamTable)
- 3 files → `components/viewport/` (Viewport3D, WorkspaceLayout, LandingView)
- 5 CSS files → DELETE after migrating to Tailwind classes
- **Net: 14 root component files → 1** (CommandPalette stays as global overlay)

### 3.3 FastAPI (NO CHANGE NEEDED)

Already well-organized:
```
fastapi_app/
├── main.py, config.py, auth.py
├── models/     (5 files — beam, geometry, analysis, optimization, common)
├── routers/    (11 files — one per domain)
└── tests/      (7 files)
```

### 3.4 Top-Level Root Cleanup

| Current | Action | Why |
|---------|--------|-----|
| `structural_engineering_lib/` | DELETE or investigate | Appears empty/duplicate |
| `tmp/` | Add to `.gitignore` | Temp files, not source |
| `git_operations_log/` | Keep (agent debugging) | Low priority |
| `clients/` | Keep | TypeScript/Python client SDKs |
| `tests/` (root) | Merge into `Python/tests/` if overlap | Single test root |

---

## 4. Migration Benefits vs Risks

### 4.1 Benefits

| Benefit | Impact |
|---------|--------|
| **AI agent discoverability** | Agents find code 3x faster with organized folders |
| **Import clarity** | `from structural_lib.services.api import design_beam_is456` vs `from structural_lib.api import ...` |
| **New contributor onboarding** | "Where does X go?" has an obvious answer |
| **Multi-code readiness** | `codes/aci318/` can be added without touching existing structure |
| **Test organization** | Tests mirror source: `tests/services/test_api.py` |
| **React feature isolation** | Modify design flow without touching import flow |
| **CSS elimination** | 5 CSS files → 0 after Tailwind migration |

### 4.2 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Broken imports** (Python) | HIGH | Backward-compat `__init__.py` re-exports |
| **Broken links** (docs) | MEDIUM | `safe_file_move.py` handles this |
| **Broken React imports** | LOW | TypeScript compiler catches immediately |
| **Test failures** | MEDIUM | Run full test suite after each phase |
| **Git blame history** | LOW | `git log --follow` works; unavoidable cost |
| **CI pipeline breaks** | MEDIUM | Test in branch, merge via PR |

### 4.3 Issues NOT Using This Structure

| Problem | Cost of Inaction |
|---------|-----------------|
| 48 flat Python files | Every new developer asks "where does X go?" |
| Duplicate code-specific files | `flexure.py` exists in BOTH root AND `codes/is456/` |
| No feature grouping in React | All 14 components in one flat folder |
| 157 flat scripts | Impossible to find the right script |
| Import confusion | `from structural_lib.api` vs `from structural_lib.codes.is456.flexure` — inconsistent |

---

## 5. Existing Automation (All Tested ✅)

### 5.1 Pre-Existing Scripts (7 scripts, all working)

| Script | Status | Purpose |
|--------|--------|---------|
| `scripts/safe_file_move.py` | ✅ Tested | Move files + update all markdown links |
| `scripts/safe_file_delete.py` | ✅ Tested | Delete with reference check + backup |
| `scripts/batch_archive.py` | ✅ Tested | Batch archive files using git mv |
| `scripts/fix_broken_links.py` | ✅ Tested | Auto-fix broken links with best-match |
| `scripts/check_folder_structure.py` | ✅ Tested (11/11 pass) | Validate Python lib structure |
| `scripts/validate_folder_structure.py` | ✅ Tested (pass) | Pre-commit folder validation |
| `scripts/find_orphan_files.py` | ✅ Tested (184 orphans) | Find unreferenced docs |

### 5.2 New Scripts Created (4 scripts, all tested)

| Script | Status | Purpose |
|--------|--------|---------|
| `scripts/migrate_python_module.py` | ✅ Created & Tested | Move .py + update ALL Python imports + create backward-compat stub |
| `scripts/migrate_react_component.py` | ✅ Created & Tested | Move .tsx + update ALL import paths + move co-located CSS |
| `scripts/validate_imports.py` | ✅ Created & Tested | Scan for broken imports (found 290 in streamlit, 0 in structural_lib) |
| `scripts/generate_enhanced_index.py` | ✅ Created & Tested | Generate AI-optimized index.json + index.md (handles .py, .ts, .md) |

**Feature highlights of new scripts:**
- `migrate_python_module.py`: `--dry-run` support, automatic `__init__.py` creation, backward-compat stubs with deprecation warnings
- `migrate_react_component.py`: Barrel export generation, co-located CSS handling, relative import rewriting
- `validate_imports.py`: `--scope` filtering (structural_lib, tests, fastapi, all), "did you mean?" suggestions
- `generate_enhanced_index.py`: `--all` flag covers 32 key folders, `--recursive` mode, extracts classes/functions/params from Python AST

### 5.3 Index Coverage (for AI Agent Efficiency)

**Before this session:** Only docs/ folders had `index.json`/`index.md` files (~16 folders)

**After `--all` generation:** 32 key folders will have indexes covering:
- Python packages (classes, functions, params, docstrings)
- React components (exports, hooks, props types)
- FastAPI routes (endpoints, models)
- Shell/Python scripts (descriptions, purposes)

### 5.4 Scripts Still Needed

| Script | Purpose | Priority |
|--------|---------|----------|
| `scripts/stress_test_migration.sh` | Run all tests + validations after each phase | MEDIUM |
| `scripts/migrate_css_to_tailwind.py` | Convert CSS file to Tailwind classes | LOW |

---

## 6. Deep Audit Findings (Feb 10, 2026)

### 6.1 Python Duplicate Files — Confirmed as Backward-Compat Shims

9 root-level files are already backward-compat stubs (~20-36 lines each, re-exporting from `codes/is456/`):

| Root File | Re-exports From | Lines | Safe to Keep |
|-----------|-----------------|-------|-------------|
| `flexure.py` | `codes.is456.flexure` | ~30 | Yes (shim pattern) |
| `shear.py` | `codes.is456.shear` | ~30 | Yes (shim pattern) |
| `detailing.py` | `codes.is456.detailing` | ~36 | Yes (shim pattern) |
| `ductile.py` | `codes.is456.ductile` | ~25 | Yes (shim pattern) |
| `serviceability.py` | `codes.is456.serviceability` | ~30 | Yes (shim pattern) |
| `torsion.py` | `codes.is456.torsion` | ~30 | Yes (shim pattern) |
| `slenderness.py` | `codes.is456.slenderness` | ~25 | Yes (shim pattern) |
| `tables.py` | `codes.is456.tables` | ~20 | Yes (shim pattern) |
| `compliance.py` | `codes.is456.compliance` | ~30 | Yes (shim pattern) |

**Action:** These follow the exact pattern that `migrate_python_module.py` generates. Keep as-is during migration. They prove the backward-compat approach works.

### 6.2 Import Validation Results

| Scope | Total Imports | Internal | Broken | Notes |
|-------|---------------|----------|--------|-------|
| structural_lib | 383 | 84 | **0** | Clean |
| all (full project) | 2,775 | 954 | **290** | Mostly streamlit_app (legacy) |

**290 broken imports** are concentrated in:
- `streamlit_app/` — Uses old module paths that no longer exist
- `scripts/test_import_3d_pipeline.py` — References non-existent `utils.api_wrapper`
- Root `tests/` — Some test files reference streamlit components

### 6.3 Orphan Files (184 found)

Found by `find_orphan_files.py --all`. Mostly in:
- `docs/_archive/` — Old session docs (expected)
- `docs/research/` — One-off research docs
- `agents/` — Some role definitions not linked from anywhere

### 6.4 Stale Directories

| Directory | Contents | Action |
|-----------|----------|--------|
| `structural_engineering_lib/` | Only `docs/learning/` with 5 files (subset of `docs/learning/` which has 9 files) | **DELETE** — confirmed stale duplicate |
| `tmp/` | 4 backup files from `safe_file_delete.py` | Add to `.gitignore` |
| `logs/` | 20+ hook output logs | Add to `.gitignore` |

### 6.5 Script Proliferation

**161 scripts** (108 .py + 53 .sh) in flat `scripts/` folder:

| Category | Count | Examples |
|----------|-------|---------|
| `check_*` | 37 | doc_metadata, api_signatures, folder_structure |
| `validate_*` | 10 | imports, folder_structure, api_contracts |
| `generate_*` | 7 | enhanced_index, folder_index, release_notes |
| `audit_*` | 3 | error_handling, input_validation, readiness |
| `migrate_*` | 3 | python_module, react_component, old migrate |
| `analyze_*` | 3 | doc_redundancy, navigation, release cadence |
| `safe_*` | 2 | file_move, file_delete |
| Other | 96 | Various utilities, tests, benchmarks |

**Potential consolidation opportunities:**
- 7 `check_doc_*` scripts could merge into `check_docs.py --all`
- 3 `check_api_*` scripts overlap significantly
- Some scripts appear one-off and could be archived

### 6.6 React CSS Files (5 legacy, migration needed)

| File | Status |
|------|--------|
| `App.css` | Mostly empty/reset — safe to delete |
| `CSVImportPanel.css` | Migrateable to Tailwind |
| `ResultsPanel.css` | Migrateable to Tailwind |
| `BeamForm.css` | Migrateable to Tailwind |
| `Viewport3D.css` | Custom 3D styles — keep or migrate carefully |
| `WorkspaceLayout.css` | Migrateable to Tailwind |
| `index.css` | Contains `@import "tailwindcss"` — KEEP |

### 6.7 Online Research: Index-per-Folder Best Practices

**llms.txt Standard** (llmstxt.org):
- Defines a `/llms.txt` at project root (we already have one)
- Curated markdown for context-window-friendly AI consumption
- Our `index.json` + `index.md` per folder extends this concept deeper

**MCP Resources Protocol:**
- JSON-based resource listing with `uri`, `name`, `description`, `mimeType`
- Supports annotations: `audience` (user/assistant), `priority` (0-1), `lastModified`
- Our `index.json` schema is compatible — could be extended for MCP in future

**Key insight:** Our enhanced index approach is ahead of industry standard. Most projects have at best a single llms.txt. We're generating per-folder machine-readable indexes with AST-extracted function signatures, class hierarchies, and parameter names. This is exactly what agents need for the "read indexes FIRST" workflow.

---

## 7. Execution Plan (Phased, Safe)

### Phase 0: Preparation ✅ COMPLETE
- [x] Create `migrate_python_module.py` script — tested with dry-run
- [x] Create `migrate_react_component.py` script — tested with dry-run
- [x] Create `validate_imports.py` script — tested, 0 broken in structural_lib
- [x] Create `generate_enhanced_index.py` script — tested, 32 folders indexed
- [x] Update AI agent instructions (CLAUDE.md, copilot-instructions.md, python-core, react)
- [x] Full project audit: duplicate analysis, orphan scan, import validation
- [x] Create feature branch: `refactor/folder-structure-v2`

### Phase 1: Python Library — `core/` expansion ✅ COMPLETE (prior session)
- [x] Move 15 files (types, models, errors, validation) to `core/`
- [x] Generate backward-compat stubs at old locations (using migrate_python_module.py)
- [x] Run full Python test suite — 3196 passed
- [x] Verify: `cd Python && .venv/bin/pytest tests/ -v` passes
- [x] Verify: `from structural_lib.types import ...` still works (backward compat)
- [x] Run: `.venv/bin/python scripts/validate_imports.py --scope all`

### Phase 2: Python Library — `services/` creation ✅ COMPLETE (prior session)
- [x] Create `services/` directory
- [x] Move 18 files (api, adapters, batch, etc.) to `services/`
- [x] Update FastAPI imports (they import from `structural_lib.api`)
- [x] Generate backward-compat re-exports
- [x] Run full test suite + FastAPI tests

### Phase 3: Python Library — `integration/` → merged into `services/` ✅ COMPLETE (prior session)
- [x] 9 integration files (bbs, dxf, reports, excel, job_runner, etc.) moved to `services/`
- [x] Decision: separate `integration/` not needed — `services/` handles both
- [x] Keep existing 9 backward-compat shims (flexure.py, shear.py, etc.)
- [x] Run full test suite — 3196 passed
- [x] Verify no orphan imports

### Phase 4: React App — Feature Grouping ✅ COMPLETE (Feb 10, 2026)
- [x] Create `components/design/`, `components/import/`, `components/viewport/`
- [x] Move 10 component files to feature groups
- [x] Update all React imports (13 files updated)
- [x] Create barrel exports (index.ts) for each feature group
- [x] CSS files moved with their components (Tailwind migration deferred)
- [x] Run `npm run build` — 2754 modules, ✅ passes

### Phase 5: Root Cleanup + Indexes ✅ COMPLETE (Feb 10, 2026)
- [x] DELETE `structural_engineering_lib/` (confirmed stale duplicate — 6 files all in docs/learning/)
- [x] `tmp/`, `logs/` already in `.gitignore`
- [x] Run `generate_enhanced_index.py` for new React feature directories
- [ ] Update `folder-structure-governance.md` to reflect new structure
- [ ] Archive this plan to `docs/_archive/`

---

## 8. Stress Testing Strategy

### 7.1 Python Tests

```bash
# Full test suite (85% branch coverage gate)
cd Python && .venv/bin/pytest tests/ -v --tb=short

# Import validation (every public function still importable)
.venv/bin/python -c "from structural_lib.api import design_beam_is456; print('OK')"
.venv/bin/python -c "from structural_lib.adapters import GenericCSVAdapter; print('OK')"
.venv/bin/python -c "from structural_lib.types import BeamInput; print('OK')"

# Backward compat test (old imports still work)
.venv/bin/python scripts/validate_imports.py --check-backward-compat

# FastAPI integration
cd fastapi_app && .venv/bin/pytest tests/ -v
```

### 7.2 React Tests

```bash
# TypeScript compile check (catches ALL import errors)
cd react_app && npm run build

# Verify dev server starts
cd react_app && timeout 10 npm run dev
```

### 7.3 Full Integration

```bash
# Docker build (catches import issues in container)
docker compose build

# Link validation (catches broken doc references)
.venv/bin/python scripts/fix_broken_links.py --check-only

# Folder structure validation
.venv/bin/python scripts/validate_folder_structure.py
```

### 7.4 Automated Stress Test Script

```bash
# To create: scripts/stress_test_migration.sh
# Runs ALL of the above in sequence, fails on first error
# Should be run after EACH phase
```

---

## 9. Migration Safety Principles

1. **One phase at a time.** Never move Python AND React files in the same commit.
2. **Backward-compatible imports.** Old `from structural_lib.api import X` MUST still work via re-exports in `__init__.py`. Deprecation warnings added, but never break.
3. **PR per phase.** Each phase gets its own PR with full CI.
4. **Dry-run first.** Every `safe_file_move.py` call uses `--dry-run` initially.
5. **Test after EVERY move.** Not at the end — after each individual file.
6. **No manual git.** All commits via `./scripts/ai_commit.sh`.

---

## 10. Next Moves (Roadmap)

### Completed (This Session — Feb 10, 2026)
1. ✅ Created this plan document (4-layer architecture)
2. ✅ User approved 4-layer approach
3. ✅ Created 4 migration automation scripts (Phase 0)
4. ✅ Tested all scripts (dry-run + live)
5. ✅ Full deep audit: duplicates, orphans, imports, indexes
6. ✅ Updated AI agent instructions (CLAUDE.md, copilot-instructions, python-core, react)
7. ✅ Online research: llms.txt, MCP Resources standards

### Completed (Prior Sessions)
8. ✅ Phases 1-3 Python library migration (core/, services/) — all complete with backward-compat stubs
9. ✅ 3196 Python tests passing, 0 broken imports in structural_lib

### Completed (Feb 10, 2026 — Session 89)
10. ✅ Phase 4: React feature grouping — 10 components → design/, import/, viewport/
11. ✅ Phase 5: Root cleanup — deleted stale `structural_engineering_lib/`, generated indexes
12. ✅ All validation: React build (2754 modules), Python tests (3196 passed)

### Post-Migration (Remaining)
13. Consider `scripts/` reorganization (161 files → categorized subdirs)
14. Archive orphan docs (184 identified)
15. Clean up 290 broken imports in legacy streamlit_app
16. Migrate 5 CSS files to Tailwind classes (BeamForm.css, ResultsPanel.css, CSVImportPanel.css, Viewport3D.css, WorkspaceLayout.css)
17. Update `folder-structure-governance.md` to reflect final structure
18. Archive this plan to `docs/_archive/`

---

## 11. Decision Matrix

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **4-layer vs 5-layer** | 4-layer | Sufficient for single-library, avoids over-engineering |
| **Python backward compat** | Yes, via `__init__.py` re-exports | Never break existing code |
| **React CSS files** | Migrate to Tailwind, then delete | Already using Tailwind v4 |
| **FastAPI changes** | None needed | Already well-organized |
| **Scripts reorganization** | Defer to post-migration | High risk, low urgency |
| **Branch strategy** | Feature branch per phase | Safe rollback |
| **Integration/ vs Services/** | Merged into services/ | Simpler, integration files fit naturally |

---

**Status:** ALL PHASES COMPLETE (0-5). React feature grouping and root cleanup done Feb 10, 2026. Post-migration cleanup items remain (scripts reorg, CSS→Tailwind, orphan docs).
