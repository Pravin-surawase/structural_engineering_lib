# Folder Structure Governance

**Type:** Guide
**Audience:** All Agents
**Status:** Production Ready
**Importance:** Critical
**Version:** 3.0
**Created:** 2025-12-01
**Last Updated:** 2026-02-11
**Enforcement:** Automated validators + pre-commit hooks

---

## I. Root Principles

1. **Progressive Disclosure** - Short entry docs, detailed content one level down
2. **Clear Ownership** - Every folder has a clear purpose and maintainer
3. **Automation First** - Rules are enforced by code, not conversation
4. **Long-term Stability** - Structure supports multi-year growth without major reorganization
5. **Discoverability** - Every document is reachable from a README index

### Source of Truth (Limits)

Numeric governance limits are defined in:
`docs/guidelines/governance-limits.json`

Both the validator (`scripts/check_governance.py`) and this guide must stay aligned to that file.

---

## II. Repository Root (/)

**Purpose:** Metadata, configuration, entry points
**Max files:** 15 (strictly enforced)
**Allowed files:**

| File | Purpose | Required? |
|------|---------|-----------|
| README.md | Project overview | YES |
| LICENSE | License text | YES |
| LICENSE_ENGINEERING.md | Engineering-specific license | OPTIONAL |
| CONTRIBUTING.md | Contribution guidelines | YES |
| CODE_OF_CONDUCT.md | Community guidelines | YES |
| CHANGELOG.md | Version history | YES |
| pyproject.toml | Python configuration | YES |
| .github/copilot-instructions.md | AI agent guidelines | YES |
| llms.txt | LLM-friendly documentation | OPTIONAL |
| CITATION.cff | Citation metadata | OPTIONAL |
| requirements.txt | Python deps bundle | OPTIONAL |
| pytest.ini | Pytest config | OPTIONAL |
| Dockerfile.fastapi | FastAPI container build | OPTIONAL |
| docker-compose.yml | Docker compose (prod) | OPTIONAL |
| docker-compose.dev.yml | Docker compose (dev) | OPTIONAL |

**Current count:** 15 files ✅
**Status:** COMPLIANT

---

## III. Documentation Root (docs/)

**Purpose:** All user-facing and developer documentation
**Max root files:** 3-5 (hub documents only)
**Structure:** Three levels
1. **Root (3-5 files):** Quick links, landing page, index
2. **Categories (15-20 folders):** Organized by audience/purpose
3. **Detail (files in folders):** Actual content

### III.A. Required Root Files (docs/)

| File | Purpose |
|------|---------|
| README.md | Hub index with quick-start paths |
| TASKS.md | Active task tracking |
| SESSION_LOG.md | Session history and decisions |

### III.B. Approved Doc Categories (Level 2)

| Folder | Purpose | Max Files | Sub-levels | Notes |
|--------|---------|-----------|------------|-------|
| **Core Learning** |
| getting-started/ | Onboarding for all users | 10 | 0 | Platform-specific quickstarts |
| learning/ | Structured learning paths | 10 | 0 | Beginner-friendly, self-paced |
| cookbook/ | Task-focused recipes | 15 | 0 | "How to" with examples |
| reference/ | API, CLI, formula reference | 20 | 1 | Searchable reference material |
| **Architecture & Design** |
| architecture/ | System design, decisions | 10 | 1 | Layer diagrams, trade-offs |
| adr/ | Architecture Decision Records | 50 | 0 | Searchable by decision type |
| **Contributing** |
| contributing/ | Developer guides | 20 | 1 | Testing, PR workflow, standards |
| guidelines/ | Development standards | 15 | 1 | API design, naming, patterns |
| **Verification** |
| verification/ | Test vectors, benchmarks | 15 | 1 | Hand calculations, edge cases |
| **Planning & Research** |
| planning/ | Roadmaps, sprints, briefs | 30 | 1 | Product roadmap, session planning |
| research/ | Research notes, findings | 100 | 2 | Exploratory work, deep dives |
| **Content** |
| blog-drafts/ | Blog posts in progress | 20 | 0 | Editorial pipeline |
| publications/ | Published content | 20 | 0 | Links to external publications |
| **Infrastructure** |
| _archive/ | Completed/deprecated docs | ∞ | 3 | Old versions, obsolete guides |
| _internal/ | Internal notes, checklists | 50 | 1 | Not for users, internal only |
| _references/ | Local research materials | 50 | 0 | PDFs, spreadsheets you own |
| **Agent-Specific** |
| agents/ | AI agent documentation | 5 (root) | 2 | Quick-start → guides → sessions |
| **Utility** |
| images/ | Images referenced by docs | - | 0 | Screenshots, diagrams |
| legal/ | Legal documents | 10 | 0 | Terms, privacy, licensing |

### III.C. Current Compliance Check

**Compliant categories (✅):**
- getting-started/ (8 files)
- learning/ (9 files)
- cookbook/ (3 files)
- reference/ (9 files)
- architecture/ (12 files)
- adr/ (1 file)
- contributing/ (16 files)
- guidelines/ (11 files)
- verification/ (5 files)
- planning/ (12 files)
- research/ (20+ files)

**Status (verified 2026-01-11):**
- blog-drafts/ - 4 files ✅
- publications/ - archived ✅
- agents/ - 3 root files + 2 folders ✅ (README.md, index.md, index.json, roles/, agent-9/)
- _archive/ - properly structured ✅
- _internal/ - exists, used ✅
- _references/ - exists, used ✅

---

## IV. Python Library (Python/structural_lib/)

**Purpose:** IS 456 RC beam design library with 4-layer architecture
**Structure:** 4 layers — Core, Codes, Services, Insights
**Migration:** Completed Feb 10, 2026 (Phases 1-3 of folder-structure-migration-v2)

### IV.A. Architecture Layers

| Layer | Location | Purpose | Import Rule |
|-------|----------|---------|-------------|
| **Core** | `core/` | Pure math, types, validation, errors | Cannot import from Services or Codes |
| **Codes** | `codes/is456/` (+ future `aci318/`, `ec2/`) | Design code calculations | Can import Core only |
| **Services** | `services/` | Orchestration, adapters, I/O, business logic | Can import Core + Codes |
| **Insights** | `insights/`, `reports/`, `visualization/` | Analysis, reports, 3D geometry | Can import Core + Codes + Services |

### IV.B. Directory Structure

```
Python/structural_lib/
├── __init__.py                    # Package root (re-exports from core/ + services/)
├── __main__.py                    # CLI entry point
│
├── core/                          # LAYER 1: Types, models, validation, errors (15 files)
│   ├── base.py                    # Abstract base classes
│   ├── constants.py               # Engineering constants
│   ├── data_types.py              # Data type definitions
│   ├── error_messages.py          # Error message catalog
│   ├── errors.py                  # Exception classes
│   ├── geometry.py                # Cross-section geometry
│   ├── inputs.py                  # Input validation types
│   ├── materials.py               # Material properties
│   ├── models.py                  # Domain models
│   ├── registry.py                # Code registry
│   ├── result_base.py             # Result base classes
│   ├── types.py                   # Type definitions
│   ├── utilities.py               # Pure utility functions
│   └── validation.py              # Input validation logic
│
├── codes/                         # LAYER 1: Code-specific calculations
│   ├── is456/                     # IS 456:2000 (12 files)
│   │   ├── flexure.py, shear.py, detailing.py, torsion.py
│   │   ├── ductile.py, serviceability.py, slenderness.py
│   │   ├── tables.py, compliance.py, materials.py
│   │   └── design_checks.py, cost_optimizer.py
│   ├── aci318/                    # ACI 318 (placeholder)
│   └── ec2/                       # Eurocode 2 (placeholder)
│
├── services/                      # LAYER 2: Integration & business logic (27 files)
│   ├── api.py                     # Public API facade (43 functions)
│   ├── api_results.py             # Result formatting
│   ├── adapters.py                # CSV adapters (Generic, ETABS, SAFE)
│   ├── batch.py                   # Batch design operations
│   ├── beam_pipeline.py           # Design orchestration
│   ├── bbs.py                     # Bar bending schedule
│   ├── dxf_export.py              # CAD export
│   ├── report.py, report_svg.py, calculation_report.py  # Reports
│   ├── excel_bridge.py, excel_integration.py             # Excel I/O
│   ├── job_runner.py, job_cli.py                         # Job execution
│   ├── rebar.py, rebar_optimizer.py                      # Rebar operations
│   ├── optimization.py, multi_objective_optimizer.py     # Optimization
│   ├── imports.py, etabs_import.py                       # Import handling
│   ├── costing.py, compliance.py, audit.py               # Business logic
│   ├── intelligence.py, dashboard.py                     # Smart features
│   ├── serialization.py, testing_strategies.py           # Support
│   └── __init__.py
│
├── insights/                      # LAYER 3: Smart analysis (10 files)
├── reports/                       # LAYER 3: Report generation (2 files)
├── visualization/                 # LAYER 3: 3D geometry (2 files)
│
└── 48 backward-compat stubs      # Re-export from core/ or services/
    ├── api.py → services.api      # Old imports still work
    ├── types.py → core.types      # Deprecation warnings added
    └── ...                        # Safe to remove after v1.0
```

### IV.C. Backward Compatibility

All 48 root-level `.py` files are **backward-compat shims** that re-export from `core/` or `services/`. This ensures:
- `from structural_lib.api import design_beam_is456` still works
- `from structural_lib.types import BeamInput` still works
- Deprecation warnings guide users to new paths

### IV.D. Enforcement

| Rule | Check | Script |
|------|-------|--------|
| Layer boundaries | `validate_imports.py --scope structural_lib` | 0 violations |
| No orphan imports | `validate_imports.py --scope all` | Excludes legacy streamlit |
| Folder structure | `check_governance.py --structure` | Pre-commit hook |
| New modules | Use `migrate_python_module.py` for moves | Creates stubs automatically |

---

## V. React App (react_app/src/)

**Purpose:** V3 frontend — React 19 + React Three Fiber + Tailwind v4
**Structure:** Feature-grouped components
**Migration:** Completed Feb 10, 2026 (Phase 4 of folder-structure-migration-v2)

### V.A. Directory Structure

```
react_app/src/
├── api/                           # HTTP/WS client (1 file)
│   └── client.ts
│
├── components/                    # UI components (feature-grouped)
│   ├── design/                    # Beam design feature
│   │   ├── DesignView.tsx         # Design page (form + viewport + results)
│   │   ├── BeamForm.tsx           # Input form with live validation
│   │   ├── ResultsPanel.tsx       # Design results display
│   │   ├── CrossSectionView.tsx   # Cross-section visualization
│   │   └── index.ts              # Barrel export
│   │
│   ├── import/                    # Data import feature
│   │   ├── ImportView.tsx         # Import page
│   │   ├── CSVImportPanel.tsx     # Drag-drop CSV import
│   │   ├── BeamTable.tsx          # Imported beams table
│   │   └── index.ts              # Barrel export
│   │
│   ├── viewport/                  # 3D visualization feature
│   │   ├── Viewport3D.tsx         # 3D beam/building visualization (R3F)
│   │   ├── WorkspaceLayout.tsx    # Dockview IDE-like layout
│   │   ├── LandingView.tsx        # Landing page content
│   │   └── index.ts              # Barrel export
│   │
│   ├── layout/                    # App shell & navigation
│   │   ├── TopBar.tsx
│   │   └── ModernAppLayout.tsx
│   │
│   ├── pages/                     # Route-level pages
│   │   ├── HomePage.tsx
│   │   ├── ModeSelectPage.tsx
│   │   ├── BuildingEditorPage.tsx
│   │   └── BeamDetailPage.tsx
│   │
│   ├── ui/                        # Shared/primitive UI components
│   │   ├── BentoGrid.tsx, FloatingDock.tsx, Toast.tsx
│   │   ├── ConnectionStatus.tsx, FileDropZone.tsx
│   │   ├── Skeleton.tsx, ErrorBoundary.tsx
│   │   └── index.ts
│   │
│   ├── CommandPalette.tsx         # Global overlay (stays in root)
│   └── index.ts                   # Master barrel export
│
├── hooks/                         # Custom hooks (8 files)
│   ├── useCSVImport.ts            # CSV import via API adapters
│   ├── useBeamGeometry.ts         # 3D rebar/stirrup geometry from API
│   ├── useLiveDesign.ts           # WebSocket live design
│   ├── useAutoDesign.ts           # Auto-trigger on input change
│   ├── useGeometryAdvanced.ts     # Building & cross-section geometry
│   └── useRebarEditor.ts          # Rebar edit validation
│
├── store/                         # Zustand state stores (2 files)
│   ├── designStore.ts             # Single beam design inputs/results
│   └── importedBeamsStore.ts      # Imported CSV beams + selection
│
├── types/                         # TypeScript types (2 files)
├── utils/                         # Utility functions (3 files)
├── lib/                           # External lib wrappers (1 file)
└── assets/                        # Static assets (1 file)
```

### V.B. Component Grouping Rules

| Group | Purpose | When to add here |
|-------|---------|------------------|
| `design/` | Single beam design flow | Forms, results, design-specific views |
| `import/` | Data import flow | CSV, JSON, file handling components |
| `viewport/` | 3D visualization | R3F-based rendering, 3D layouts |
| `layout/` | App shell | Top bars, sidebars, navigation |
| `pages/` | Route-level components | Full pages rendered by React Router |
| `ui/` | Shared primitives | Reusable across multiple features |

### V.C. Enforcement

| Rule | Check | Script |
|------|-------|--------|
| TypeScript compilation | `npm run build` (catches all import errors) | 2754 modules |
| Component moves | Use `migrate_react_component.py` | Updates all imports + barrel exports |
| Index generation | `generate_enhanced_index.py` | Per-folder index.json + index.md |

---

## VI. FastAPI App (fastapi_app/)

**Purpose:** REST + WebSocket API layer
**Status:** Already well-organized — no changes needed

```
fastapi_app/
├── main.py                        # App entry point
├── config.py                      # Configuration
├── auth.py                        # Authentication
├── models/                        # Pydantic models (5 files)
│   ├── beam.py, geometry.py, analysis.py
│   ├── optimization.py, common.py
│   └── __init__.py
├── routers/                       # API routes (11 files, one per domain)
│   ├── design.py, geometry.py, import_router.py
│   ├── insights.py, optimization.py, export.py
│   └── ...
└── tests/                         # Route tests (7 files)
```

---

## VII. Agents Folder (agents/)

**Purpose:** Agent definitions, role descriptions, index
**Structure (ENFORCED):**

```
agents/
├── README.md                    ← Hub (list all agents)
├── index.md                     ← Registry (metadata JSON/YAML format)
├── roles/                       ← REQUIRED
│   ├── README.md                (hub for roles)
│   ├── ARCHITECT.md
│   ├── CLIENT.md
│   ├── DEV.md
│   ├── DEVOPS.md
│   ├── DOCS.md
│   ├── INTEGRATION.md
│   ├── PM.md
│   ├── RESEARCHER.md
│   ├── SUPPORT.md
│   ├── TESTER.md
│   └── UI.md
├── guides/                      ← Agent guides (docs/agents/guides/)
│   └── *.md                     (Not in agents/ root!)
├── templates/                   ← PLANNED (not yet populated)
│   ├── prompt-template.md
│   └── session-log-template.md
└── agent-9/                     ← Agent-specific folders
    ├── README.md
    └── ...
```

**Current status (verified 2026-01-11):**

1. ✅ **agents/roles/ exists** - All 12 role files properly organized
2. ✅ **agents/roles/GOVERNANCE.md** - In correct location
3. ✅ **docs/agents/guides/** - All agent guides properly nested
4. ✅ **agents/ root** - Only 4 files (README.md, index.json, index.md, roles/, agent-9/)

**Note:** Historical governance docs archived at `docs/_archive/2026-01/agent-9-governance-legacy/`

**Enforcement rules:**

| Rule | Check | Consequence |
|------|-------|-------------|
| Only 3-5 files in agents/ root | Automated | CI failure if violated |
| All role .md in agents/roles/ | Automated | Warning in validator |
| agents/GOVERNANCE.md moved | Link check | Broken link detected |
| guides/ properly nested | Structure check | Non-compliant flag |

---

## VIII. Document Metadata Standard

**NEW (Session 11):** Every document should have a metadata section.

```markdown
# Document Title

**Type:** [Guide | Reference | Research | Archive]
**Audience:** [All | Users | Developers | Maintainers]
**Last Updated:** YYYY-MM-DD
**Status:** [Active | Obsolete | Superseded | In Progress]
**Importance:** [Critical | High | Medium | Low]
**Version:** [Original | v2 | Supersedes: doc-name.md]

---

[Rest of document...]

---

**Archive:** [If obsolete, link to new location or explain why]
**Related:** [Link to related docs or tasks]
**Next Review:** YYYY-MM-DD (or "Quarterly")
```

---

## IX. Validation Checklist

### Automated Checks (Pre-commit)

- [ ] Root has ≤15 files
- [ ] docs/ root has ≤5 files
- [ ] All categories use proper structure
- [ ] agents/ roles in agents/roles/ folder
- [ ] No redirect stubs (single source rule)
- [ ] All internal links valid
- [ ] governance spec and validator synchronized

### Manual Review (Quarterly)

- [ ] New doc categories reviewed and approved
- [ ] Orphan docs migrated or archived
- [ ] Link structure audit
- [ ] Navigation usability check

---

## X. Rule Updates & Governance

### Changing the Spec

1. **Propose change** in GitHub issue with rationale
2. **Update folder-structure-governance.md first** (this file)
3. **Update validators to match**
4. **Run full validation**
5. **Execute moves if needed**
6. **Document in CHANGELOG**

### When to Create a New Category

**Required answers:**

1. Does this fit in an existing category? (Prefer reuse)
2. Is it audience-specific or purpose-specific?
3. Will it have 5+ documents? (Or just temporary?)
4. Does it need governance rules?
5. Can validators check compliance?

---

## XI. Current Status

**Last Updated:** 2026-02-10 (Session 89 — Folder Structure Migration v2 complete)

| Aspect | Status | Notes |
|--------|--------|-------|
| Root files (≤15) | ✅ PASS | 15 files |
| docs/ root (≤5) | ✅ PASS | 3 files |
| Link validity | ✅ PASS | 801 links, 0 broken |
| agents/ roles | ✅ PASS | 12 files in agents/roles/ |
| Governance consolidated | ✅ PASS | Single location: docs/guidelines/ |
| docs/agents structure | ✅ PASS | All agent guides in docs/agents/guides/ |
| Spec/validator sync | ✅ PASS | values loaded from governance-limits.json |
| Naming convention | ✅ PASS | All files kebab-case |
| Doc metadata | ⚠️ IN PROGRESS | New standard being applied |
| **Python library** | ✅ PASS | 4-layer: core/ + codes/ + services/ + insights/ |
| **React feature groups** | ✅ PASS | design/ + import/ + viewport/ + layout/ + pages/ + ui/ |
| **FastAPI** | ✅ PASS | Already well-organized (no changes needed) |
| **Backward compat** | ✅ PASS | 48 root stubs re-export from core/ + services/ |

---

## XII. Migration History

### Phase 1: Docs Reorganization (Sessions 11-12, Jan 2026)

| Phase | Task | Status |
|-------|------|--------|
| 1 | Publish governance spec | ✅ Complete |
| 2 | Update validators | ✅ Complete |
| 3 | Create migration tools | ✅ Complete (safe_file_move.py) |
| 4 | Migrate agents/ roles (12 files) | ✅ Complete |
| 5 | Reorganize docs/agents (6 files) | ✅ Complete |
| 6 | Move agents/GOVERNANCE.md | ✅ Complete |
| 7 | Apply document metadata standard | ⏳ In Progress |
| 8 | Reduce root files (14 → 10) | ✅ Complete |

### Phase 2: Code Folder Structure (Session 88-89, Feb 2026)

| Phase | Task | Status |
|-------|------|--------|
| 0 | Create migration automation scripts | ✅ Complete |
| 1 | Python library — core/ expansion (15 files) | ✅ Complete |
| 2 | Python library — services/ creation (18 files) | ✅ Complete |
| 3 | Python library — integration merged into services/ (9 files) | ✅ Complete |
| 4 | React app — feature grouping (10 components) | ✅ Complete |
| 5 | Root cleanup — stale dirs deleted, indexes generated | ✅ Complete |

**Validation:** 3196 Python tests passed, React build 2754 modules, 0 broken imports in structural_lib. PR #426 merged.

---

**Owner:** Project Governance Team
**Review Schedule:** Quarterly (2026-04-11)
**Validator:** scripts/check_governance.py --structure + pre-commit hooks
