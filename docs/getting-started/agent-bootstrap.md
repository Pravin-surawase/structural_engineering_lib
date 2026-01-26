# Agent Bootstrap

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Version:** 2.3.0
**Created:** 2026-01-08
**Last Updated:** 2026-01-26

---

> **Read this first.** This is the fastest path to productive work.

> **👤 For users onboarding a new agent:** See [../contributing/agent-onboarding-message.md](../contributing/agent-onboarding-message.md) for the exact message to send.

---

## 🚨 STOP — READ BEFORE CODING!

**Agents keep duplicating code.** We have a mature V3 stack. Check these FIRST:

### What We Have (DO NOT REINVENT!)

| Need | We Have | Location |
|------|---------|----------|
| CSV parsing | `GenericCSVAdapter` (40+ column names) | `structural_lib/adapters.py` |
| 3D bar positions | `beam_to_3d_geometry()` | `structural_lib/geometry_3d.py` |
| React CSV import | `useCSVFileImport()` hook | `react_app/src/hooks/useCSVImport.ts` |
| React 3D geometry | `useBeamGeometry()` hook | `react_app/src/hooks/useBeamGeometry.ts` |
| React file upload | `FileDropZone` component | `react_app/src/components/ui/FileDropZone.tsx` |
| React 3D viewport | `Viewport3D` component | `react_app/src/components/Viewport3D.tsx` |
| FastAPI CSV import | `POST /api/v1/import/csv` | `fastapi_app/routers/import_routes.py` |
| FastAPI geometry | `POST /api/v1/geometry/beam/full` | `fastapi_app/routers/geometry.py` |

**Quick check before coding:**
```bash
# Search React hooks
ls react_app/src/hooks/

# Search FastAPI routes
grep -r "def " fastapi_app/routers/ | head -20

# Search library functions
grep -r "^def " Python/structural_lib/api.py | head -20
```

---

## Guide Hierarchy

**You are here:** Quick Start (Bootstrap)

| Need | Guide | Use When |
|------|-------|----------|
| **Critical Rules** | [agent-essentials.md](agent-essentials.md) | V3 stack reference, golden rules |
| **Quick Start** | This document | First 30 seconds ← **YOU ARE HERE** |
| **Quick Reference** | [agent-quick-reference.md](../agents/guides/agent-quick-reference.md) | Cheat sheet, emergency commands |
| **Complete Guide** | [agent-workflow-master-guide.md](../agents/guides/agent-workflow-master-guide.md) | Decision trees, troubleshooting |

---

## ⚡ First 30 Seconds

```bash
# RECOMMENDED: Quick mode (6s)
./scripts/agent_start.sh --quick

# OPTIONAL: Full validation (13s, use when debugging)
./scripts/agent_start.sh
```

This shows: version, branch, active tasks, blockers, and agent-specific commands.

---

## 🏗️ V3 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (react_app/)              │
│  Vite + React 19 + React Three Fiber + Tailwind CSS        │
│  - useBeamGeometry() → Fetches 3D geometry from API        │
│  - useCSVFileImport() → Imports CSV via API adapters       │
│  - Viewport3D → R3F 3D scene with rebars/stirrups          │
│  - BentoGrid + FloatingDock → Modern Gen Z UI              │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/WebSocket
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (fastapi_app/)           │
│  - /api/v1/import/csv → CSV parsing with adapters          │
│  - /api/v1/geometry/beam/full → 3D rebar/stirrup positions │
│  - /api/v1/design/beam → Beam design (Mu, Vu, Ast)         │
│  - /ws/design/{session} → Live WebSocket updates           │
│  - /docs → OpenAPI auto-generated documentation            │
└──────────────┬──────────────────────────────────────────────┘
               │ Direct Python calls
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    structural_lib (Python/structural_lib/)  │
│  - api.py: 43 public functions (design, detail, optimize)  │
│  - adapters.py: GenericCSVAdapter, ETABSAdapter, SAFE      │
│  - geometry_3d.py: beam_to_3d_geometry() → RebarPath[]     │
│  - codes/is456/: flexure.py, shear.py, detailing.py        │
└─────────────────────────────────────────────────────────────┘
```

### Key Principle: Don't Duplicate, Integrate!

```
❌ WRONG: Write CSV parsing in React → Manual column mapping
✅ RIGHT: Use useCSVFileImport() → API → GenericCSVAdapter (40+ columns)

❌ WRONG: Calculate bar positions in Viewport3D manually
✅ RIGHT: Use useBeamGeometry() → API → geometry_3d.beam_to_3d_geometry()
```

---

## 📖 Required Context

| Priority | Document | Why |
|----------|----------|-----|
| 0 | [agent-essentials.md](agent-essentials.md) | V3 stack, critical rules |
| 1 | [ai-context-pack.md](ai-context-pack.md) | Project summary, layers |
| 2 | [TASKS.md](../TASKS.md) | Current work: Active, Up Next |
| 3 | [next-session-brief.md](../planning/next-session-brief.md) | What happened last |

---

## 🐳 Quick Start Commands

### FastAPI Backend
```bash
# Run with Docker (recommended)
docker compose up --build              # Production
docker compose -f docker-compose.dev.yml up  # Dev with hot reload

# Run locally
cd Python && .venv/bin/uvicorn fastapi_app.main:app --reload

# API docs at http://localhost:8000/docs
```

### React Frontend
```bash
cd react_app
npm install
npm run dev    # Dev server at http://localhost:5173
npm run build  # Production build
```

### Python Tests
```bash
cd Python && .venv/bin/pytest tests/ -v
```

---

## ⚠️ Frontend Compatibility (React + R3F + Drei)

```bash
# Check dependency versions
cd react_app && npm ls react react-dom @react-three/fiber @react-three/drei
```

**Current stack (Jan 2026):**
- React 19 + React Three Fiber 9 + Drei 10.7+
- Tailwind CSS 4 + Vite 7
- dockview (optional, replaced by BentoGrid/FloatingDock)

---

## 📚 Duplication Prevention

**Before creating ANY React component or Python function:**

```bash
# Check React hooks/components
ls react_app/src/hooks/
ls react_app/src/components/

# Check library functions
.venv/bin/python scripts/discover_api_signatures.py <function_name>

# Check FastAPI routes
grep -r "@router" fastapi_app/routers/
```

---

## 🌐 Verify Online for Volatile Info

If information is likely to change, verify it online:
- AI model names and availability
- Library/framework versions
- CLI flags and API endpoints

---

## 📍 Essential Links

- **Copilot rules:** [../../.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **Git workflow:** [../contributing/git-workflow-ai-agents.md](../contributing/git-workflow-ai-agents.md) ⚠️
- **V3 Roadmap:** [../planning/8-week-development-plan.md](../planning/8-week-development-plan.md) 🚀
- **API docs:** [../reference/api.md](../reference/api.md)
- **Docker guide:** [../learning/docker-fundamentals-guide.md](../learning/docker-fundamentals-guide.md) 🐳

---

## 📇 Machine-Readable Indexes

- `scripts/automation-map.json` (task → script)
- `docs/docs-canonical.json` (topic → canonical doc)
- `scripts/index.json` (automation catalog)

**Automation lookup:** `.venv/bin/python scripts/find_automation.py "your task"`

---

*Don't hardcode stats here — run `./scripts/agent_start.sh --quick` for live data.*
