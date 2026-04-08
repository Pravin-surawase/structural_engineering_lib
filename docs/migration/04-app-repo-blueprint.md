# App Repository Blueprint

**Type:** Reference
**Version:** 2.0
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Repository Name

`structural-design-app` or `<PACKAGE_NAME>-app`

**Recommendation:** `<PACKAGE_NAME>-app` — maintains branding consistency with the library.

> ⚠️ **Name Update:** `rcdesign` is TAKEN on PyPI (v0.4.18, Satish Annigeri). New name pending — see [08-naming-and-accounts.md](08-naming-and-accounts.md). All references use `<PACKAGE_NAME>` placeholder.

---

## Folder Structure

```
rcdesign-app/
├── .github/
│   ├── copilot-instructions.md
│   ├── dependabot.yml
│   ├── workflows/
│   │   ├── ci-backend.yml             # FastAPI tests + lint
│   │   ├── ci-frontend.yml            # React build + vitest
│   │   └── deploy.yml                 # Docker build + deploy
│   ├── agents/
│   │   ├── backend.agent.md           # FastAPI + services
│   │   ├── frontend.agent.md          # React 19 + R3F + Tailwind
│   │   ├── api.agent.md               # API design, OpenAPI
│   │   ├── reviewer.agent.md          # Code review (read-only)
│   │   ├── tester.agent.md            # Test writing
│   │   └── devops.agent.md            # Docker, CI, deployment
│   ├── instructions/
│   │   ├── python.instructions.md     # applyTo: 'backend/**'
│   │   ├── react.instructions.md      # applyTo: 'frontend/**'
│   │   └── docker.instructions.md     # applyTo: 'Dockerfile*'
│   └── prompts/
│       ├── add-endpoint.prompt.md     # New API endpoint workflow
│       ├── add-component.prompt.md    # New React component workflow
│       └── session-end.prompt.md      # Session end checklist
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Settings, environment
│   │   ├── routers/                   # 13 routers, 60 endpoints
│   │   │   ├── __init__.py
│   │   │   ├── design.py             # POST /api/v1/design/beam
│   │   │   ├── column.py             # POST /api/v1/design/column/*
│   │   │   ├── detailing.py          # POST /api/v1/detailing/beam
│   │   │   ├── analysis.py           # POST /api/v1/analysis/*
│   │   │   ├── geometry.py           # POST /api/v1/geometry/*
│   │   │   ├── imports.py            # POST /api/v1/import/csv
│   │   │   ├── insights.py           # POST /api/v1/insights/*
│   │   │   ├── optimization.py       # POST /api/v1/optimization/*
│   │   │   ├── rebar.py              # POST /api/v1/rebar/*
│   │   │   ├── export.py             # POST /api/v1/export/*
│   │   │   ├── streaming.py          # SSE endpoints
│   │   │   ├── websocket.py          # WebSocket live updates
│   │   │   └── health.py             # GET /health
│   │   ├── models/                    # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── beam.py
│   │   │   ├── column.py
│   │   │   └── common.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── adapters.py            # CSV/ETABS/SAFE adapters (GenericCSVAdapter)
│   │       ├── visualization.py       # 3D geometry (beam_to_3d_geometry)
│   │       ├── insights.py            # Smart analysis, design suggestions
│   │       ├── reports.py             # HTML/PDF report generation
│   │       ├── dxf_export.py          # DXF drawing export
│   │       ├── bbs_export.py          # BBS CSV export
│   │       ├── optimization.py        # Cost optimizer
│   │       └── batch.py               # Batch processing
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_design_router.py
│   │   ├── test_import_router.py
│   │   └── test_export_router.py
│   └── pyproject.toml                 # depends on rcdesign>=1.0
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── design/                # DesignView, BeamForm, ResultsPanel
│   │   │   ├── import/                # ImportView, CSVImportPanel, BeamTable
│   │   │   ├── viewport/             # Viewport3D, WorkspaceLayout
│   │   │   ├── layout/               # TopBar, ModernAppLayout
│   │   │   ├── pages/                # Home, ModeSelect, Building, BeamDetail
│   │   │   └── ui/                   # BentoGrid, FileDropZone, Toast, etc.
│   │   ├── hooks/                     # Custom hooks (CSV, geometry, export)
│   │   ├── store/                     # Zustand stores
│   │   ├── types/                     # TypeScript type definitions
│   │   ├── utils/                     # Utility functions
│   │   ├── App.tsx                    # Root component
│   │   └── main.tsx                   # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── vitest.config.ts
├── docker-compose.yml                 # Production stack
├── docker-compose.dev.yml             # Dev with hot reload
├── Dockerfile.backend                 # FastAPI image
├── Dockerfile.frontend                # React build image
├── AGENTS.md                          # Cross-agent instructions
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE                            # MIT
└── README.md
```

---

## Key Dependency

```toml
# backend/pyproject.toml
[project]
name = "<PACKAGE_NAME>-app"
requires-python = ">=3.11"
dependencies = [
    "<PACKAGE_NAME>>=1.0,<2.0",   # The IS 456 library (from PyPI) — name TBD
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.0",
    "ezdxf>=1.0",                 # DXF export
    "jinja2>=3.1",                # Report templates
    "python-multipart>=0.0.9",    # File uploads
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "httpx>=0.27",                # TestClient
    "pytest-asyncio>=0.23",
    "ruff>=0.6",
    "mypy>=1.10",
]
```

---

## What Moves from Current Monorepo to App Repo

### APP-Classified Functions (30)

| Function / Module | Current Location | App Destination |
|----------|-----------------|-------------|
| `beam_to_3d_geometry` | `visualization/geometry_3d.py` | `backend/app/services/visualization.py` |
| `compute_bbs` | `services/bbs.py` | `backend/app/services/bbs_export.py` |
| `export_bbs_to_csv` | `services/bbs.py` | `backend/app/services/bbs_export.py` |
| `generate_report` | `services/report.py` | `backend/app/services/reports.py` |
| `export_dxf` | `services/dxf_export.py` | `backend/app/services/dxf_export.py` |
| `optimize_beam_cost` | `services/optimization.py` | `backend/app/services/optimization.py` |
| `suggest_design_improvements` | `insights/design_suggestions.py` | `backend/app/services/insights.py` |
| `smart_analyze_design` | `insights/smart_designer.py` | `backend/app/services/insights.py` |
| `GenericCSVAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `ETABSAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `SAFEAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `generate_insights` | `insights/` | `backend/app/services/insights.py` |
| `code_compliance_check` | `insights/compliance.py` | `backend/app/services/insights.py` |
| `rebar_suggestions` | `insights/rebar_advisor.py` | `backend/app/services/insights.py` |
| `design_comparison` | `insights/comparisons.py` | `backend/app/services/insights.py` |
| `batch_design` | `services/batch.py` | `backend/app/services/batch.py` |
| `stream_design_updates` | `services/streaming.py` | `backend/app/services/` |
| All 13 FastAPI routers | `fastapi_app/routers/` | `backend/app/routers/` |
| All Pydantic models | `fastapi_app/models/` | `backend/app/models/` |
| React app (entire) | `react_app/` | `frontend/` |

### What Stays in Library (NOT moved)

- All `codes/is456/` math functions
- All `core/` types, constants, materials
- All `services/api.py` orchestration functions
- BBS math (cut lengths, shape codes) — only BBS export moves
- Audit trail hashing (SHA-256 math) — only logging moves

---

## App ↔ Library Import Pattern

```python
# backend/app/routers/design.py
from <PACKAGE_NAME> import design_beam, BeamDesignResult

@router.post("/api/v1/design/beam")
async def design_beam_endpoint(request: BeamDesignRequest) -> BeamDesignResponse:
    result = design_beam(
        b_mm=request.b_mm,
        d_mm=request.d_mm,
        Mu_kNm=request.Mu_kNm,
        fck=request.fck,
        fy=request.fy,
    )
    return BeamDesignResponse.from_result(result)
```

This is the clean boundary: the app imports the library (`<PACKAGE_NAME>`) as a pip-installed dependency, never from local paths.

---

## Multi-Code Frontend Needs (v2.0)

When multi-code support lands in the library (Phase 3–4), the app frontend needs these additions:

### Code Selector Dropdown

- Global code selector: IS 456 / ACI 318 / EC2
- Persisted in Zustand store (`useDesignStore`)
- Affects all design forms — beam, column, footing, slab
- Default: IS 456 (maintains backward compatibility)

### Comparison View

- Side-by-side results panel showing design output from 2–3 codes simultaneously
- Highlights differences: required steel area, safety factors, governing clauses
- Color-coded: green (all codes safe), yellow (divergent results), red (any code fails)

### Grade Mapping Display

- Shows equivalent material grades across codes (e.g., M25 ≈ C25/30 ≈ f'c=25 MPa)
- Auto-maps user-selected grade to equivalent grades in other codes
- Displayed as a lookup panel accessible from any design form

---

## Multi-Code API Endpoints (v2.0)

New v2 API endpoints to support multi-code design:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v2/design/beam` | Beam design with `code` parameter (`IS456`, `ACI318`, `EC2`) |
| `POST` | `/api/v2/compare/beam` | Multi-code beam comparison — returns results from all requested codes |
| `GET` | `/api/v2/codes` | List available design codes with version info |
| `GET` | `/api/v2/grades/map` | Grade mapping lookup (e.g., M25 → C25/30 → f'c=25 MPa) |
| `POST` | `/api/v2/compare/column` | Multi-code column comparison |
| `POST` | `/api/v2/design/column` | Column design with `code` parameter |

### Example: Multi-Code Comparison Request

```json
{
  "b_mm": 300,
  "d_mm": 500,
  "Mu_kNm": 200,
  "fck": 25,
  "fy": 415,
  "codes": ["IS456", "ACI318", "EC2"]
}
```

### Example: Grade Mapping Response

```json
{
  "base_code": "IS456",
  "base_grade": "M25",
  "mappings": {
    "ACI318": {"grade": "f'c = 25 MPa", "note": "Direct equivalent"},
    "EC2": {"grade": "C25/30", "note": "fck=25, fck,cube=30"}
  }
}
```

> **Note:** v1 endpoints remain unchanged for backward compatibility. v2 endpoints are additive.
