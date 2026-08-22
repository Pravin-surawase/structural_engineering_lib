# Learning Curriculum — Structural Engineering Library

**Purpose:** A solo-developer learning path covering ALL knowledge domains needed to build, maintain, and explain this library.

**Duration:** ~30 days (flexible, self-paced)
**Audience:** You — the developer who needs to understand every layer
**Format:** Each day = one focused module with theory + library examples + simple examples + exercises

---

## Why This Exists

This library embeds knowledge from 5+ domains: structural engineering (IS 456), Python architecture, web APIs, 3D visualization, testing, and AI agent workflows. No single resource covers all of these. This curriculum connects them so you can confidently explain, debug, and extend any part of the system.

---

## Curriculum Overview

### Week 1: Civil Engineering Foundations (Days 1-7)
*What IS 456 says, why it matters, and how concrete design actually works.*

| Day | Module | Topics | Library Connection |
|-----|--------|--------|--------------------|
| 1 | [day-01-concrete-basics.md](day-01-concrete-basics.md) | Concrete & steel properties, stress-strain, safety factors | `materials.py`, `fck`, `fy`, `0.87*fy` |
| 2 | [day-02-beam-flexure.md](day-02-beam-flexure.md) | Bending theory, neutral axis, moment of resistance | `flexure.py`, `calculate_mu_lim()`, stress block |
| 3 | [day-03-beam-shear-torsion.md](day-03-beam-shear-torsion.md) | Shear stress, stirrup design, torsion interaction | `shear.py`, `torsion.py`, Table 19, Table 20 |
| 4 | [day-04-beam-detailing.md](day-04-beam-detailing.md) | Bar spacing, cover, anchorage, crack control | `detailing.py`, `serviceability.py`, Cl 26 |
| 5 | [day-05-columns.md](day-05-columns.md) | Axial, uniaxial, biaxial, slender columns | `column/axial.py`, `uniaxial.py`, `biaxial.py` |
| 6 | [day-06-footings.md](day-06-footings.md) | Bearing capacity, punching shear, spread footings | `footing/`, Cl 31, one-way/two-way shear |
| 7 | [day-07-is456-big-picture.md](day-07-is456-big-picture.md) | IS 456 structure, clauses, amendments, SP:16 | `traceability.py`, `clause-map.json`, parity dashboard |

### Week 2: Python Architecture & Core Library (Days 8-14)
*How the code is organized and why it matters.*

| Day | Module | Topics | Library Connection |
|-----|--------|--------|--------------------|
| 8 | [day-08-architecture-layers.md](day-08-architecture-layers.md) | 4-layer architecture, import rules, dependency direction | `core/` → `codes/` → `services/` → `ui/` |
| 9 | [day-09-type-system.md](day-09-type-system.md) | Dataclasses, Pydantic v2, TypedDicts, frozen models | `data_types.py`, `models.py`, `BeamDesignInput` |
| 10 | [day-10-error-handling.md](day-10-error-handling.md) | Exception hierarchy, validation, error messages | `errors.py`, `validation.py`, `error_messages.py` |
| 11 | [day-11-services-api.md](day-11-services-api.md) | Service layer, API surface, adapters, pipeline | `services/api.py`, `adapters.py`, `beam_pipeline.py` |
| 12 | [day-12-testing-patterns.md](day-12-testing-patterns.md) | Golden vectors, property testing, Hypothesis, fixtures | `tests/`, `conftest.py`, SP:16 benchmarks |
| 13 | [day-13-exports-reports.md](day-13-exports-reports.md) | BBS, DXF, PDF generation, SVG diagrams | `bbs.py`, `dxf_export.py`, `report.py` |
| 14 | [day-14-optimization.md](day-14-optimization.md) | Single/multi-objective, Pareto, NSGA-II, rebar optimizer | `optimization.py`, `multi_objective_optimizer.py` |

### Week 3: Full Stack — FastAPI + React + 3D (Days 15-21)
*How the web application brings the library to life.*

| Day | Module | Topics | Library Connection |
|-----|--------|--------|--------------------|
| 15 | [day-15-fastapi-basics.md](day-15-fastapi-basics.md) | REST design, Pydantic models, routers, OpenAPI | `fastapi_app/`, 13 routers, 60 endpoints |
| 16 | [day-16-fastapi-advanced.md](day-16-fastapi-advanced.md) | WebSocket, SSE, batch processing, error handling | `websocket.py`, `streaming.py`, `error_utils.py` |
| 17 | [day-17-react-architecture.md](day-17-react-architecture.md) | React 19, hooks, Zustand stores, TypeScript strict | `react_app/src/`, component tree, state flow |
| 18 | [day-18-react-hooks-deep.md](day-18-react-hooks-deep.md) | Custom hooks, data fetching, CSV import flow | `useCSVFileImport`, `useBatchDesign`, `useLiveDesign` |
| 19 | [day-19-3d-visualization.md](day-19-3d-visualization.md) | React Three Fiber, beam geometry, rebar rendering | `Viewport3D`, `useBeamGeometry`, `geometry_3d.py` |
| 20 | [day-20-data-flow-e2e.md](day-20-data-flow-e2e.md) | CSV upload → design → 3D view → export (full flow) | End-to-end tracing through all layers |
| 21 | [day-21-docker-deployment.md](day-21-docker-deployment.md) | Docker, Colima, compose, dev vs prod | `Dockerfile.fastapi`, `docker-compose.yml` |

### Week 4: Tooling, Quality & Advanced Topics (Days 22-30)
*The infrastructure that makes everything work reliably.*

| Day | Module | Topics | Library Connection |
|-----|--------|--------|--------------------|
| 22 | [day-22-git-automation.md](day-22-git-automation.md) | ai_commit.sh, PR workflow, conventional commits | `scripts/ai_commit.sh`, hooks framework |
| 23 | [day-23-ci-cd.md](day-23-ci-cd.md) | GitHub Actions, 28 checks, pre-commit hooks | `.github/workflows/`, `check_all.py` |
| 24 | [day-24-ai-agents.md](day-24-ai-agents.md) | 16 agents, registry, router, permissions, skills | `agents/`, `.github/agents/`, orchestrator pipeline |
| 25 | [day-25-code-quality.md](day-25-code-quality.md) | ruff, basedpyright, mypy, architecture boundaries | `pyrightconfig.json`, `check_architecture_boundaries.py` |
| 26 | [day-26-pypi-packaging.md](day-26-pypi-packaging.md) | pyproject.toml, wheel building, Trusted Publishers | `Python/pyproject.toml`, `MANIFEST.in`, release flow |
| 27 | [day-27-multi-code-design.md](day-27-multi-code-design.md) | IS 456 vs ACI 318 vs EC2, code registry pattern | `core/registry.py`, `core/base.py`, migration docs |
| 28 | [day-28-innovation-tools.md](day-28-innovation-tools.md) | Symbolic crosscheck, metamorphic testing, provenance | `docs/migration/12-innovation-ideas.md` |
| 29 | [day-29-performance-scale.md](day-29-performance-scale.md) | Profiling, batch 1000 beams, memory, async patterns | `tests/performance/`, `beam_pipeline.py` |
| 30 | [day-30-mastery-review.md](day-30-mastery-review.md) | Full review, knowledge map, explain-to-anyone guide | All modules, discussion prep, FAQ |

---

## How to Use This Curriculum

1. **Read the module** — theory first, then examples
2. **Run the library examples** — each module has runnable code snippets
3. **Try the exercises** — hands-on practice with the actual codebase
4. **Check your understanding** — each module ends with "Can You Explain?" questions
5. **Mark progress** — check off completed days below

## Progress Tracker

- [ ] Day 1 — Concrete Basics
- [ ] Day 2 — Beam Flexure
- [ ] Day 3 — Shear & Torsion
- [ ] Day 4 — Detailing
- [ ] Day 5 — Columns
- [ ] Day 6 — Footings
- [ ] Day 7 — IS 456 Big Picture
- [ ] Day 8 — Architecture Layers
- [ ] Day 9 — Type System
- [ ] Day 10 — Error Handling
- [ ] Day 11 — Services & API
- [ ] Day 12 — Testing Patterns
- [ ] Day 13 — Exports & Reports
- [ ] Day 14 — Optimization
- [ ] Day 15 — FastAPI Basics
- [ ] Day 16 — FastAPI Advanced
- [ ] Day 17 — React Architecture
- [ ] Day 18 — React Hooks Deep Dive
- [ ] Day 19 — 3D Visualization
- [ ] Day 20 — End-to-End Data Flow
- [ ] Day 21 — Docker & Deployment
- [ ] Day 22 — Git Automation
- [ ] Day 23 — CI/CD Pipeline
- [ ] Day 24 — AI Agents System
- [ ] Day 25 — Code Quality Tools
- [ ] Day 26 — PyPI Packaging
- [ ] Day 27 — Multi-Code Design
- [ ] Day 28 — Innovation Tools
- [ ] Day 29 — Performance & Scale
- [ ] Day 30 — Mastery Review

---

## Legend

Each module contains:
- **📖 Theory** — Concepts explained from scratch (no prior knowledge assumed)
- **🏗️ Library Example** — How this concept appears in our codebase (with file links)
- **🎯 Simple Example** — Easy standalone example you can run and modify
- **🔧 Exercise** — Practice task using the actual library
- **💬 Can You Explain?** — Discussion questions to test understanding
- **📎 References** — IS 456 clauses, documentation, external resources

---

*Created: 2026-04-08 | Updated: 2026-04-08*
