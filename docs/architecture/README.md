# Architecture

Deep dives into project structure, design decisions, and system architecture.

**Files:** 8 | **Updated:** 2026-01-11

---

## 🏗️ Quick Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         IS 456 DESIGN PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│   CSV/JSON ──► Design ──► Compliance ──► Detailing ──► DXF/Schedule    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer Architecture

| Layer | Modules | Rules |
|-------|---------|-------|
| **Core** | flexure, shear, detailing, tables | Pure functions, no I/O |
| **Application** | api, job_runner, bbs | Orchestrates core |
| **UI/I-O** | excel_integration, dxf_export, job_cli | External data |

---

## 📋 Contents

### High-Level Architecture

| Document | Description |
|----------|-------------|
| [project-overview.md](project-overview.md) | High-level scope, layers, and workflows |
| [mission-and-principles.md](mission-and-principles.md) | Core principles and non-negotiables |

### Detailed Architecture

| Document | Description |
|----------|-------------|
| [deep-project-map.md](deep-project-map.md) | Consolidated architecture and data flow |
| [visual-architecture.md](visual-architecture.md) | Mermaid diagrams for layers and modules |
| [data-flow-diagrams.md](data-flow-diagrams.md) | Job runner + smart designer data flow |
| [dependencies.md](dependencies.md) | Module dependency graph |

### Historical

| Document | Description |
|----------|-------------|
| [architecture-review-2025-12-27.md](architecture-review-2025-12-27.md) | Architecture review notes |

---

## 🎯 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Deterministic outputs** | Same input → same output (testable, predictable) |
| **Explicit units** | No hidden conversions (mm, N, N/mm²) |
| **Python/VBA parity** | Matching behavior across platforms |
| **Layer separation** | Core has no I/O dependencies (pure calculations) |
| **IS 456 compliance** | Every calculation traceable to code clause |

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [API Reference](../reference/api.md) | Function signatures |
| [IS 456 Formulas](../reference/is456-formulas.md) | Formula reference |
| [Contributing Guide](../contributing/README.md) | Development workflow |

---

**Parent:** [docs/README.md](../README.md)
